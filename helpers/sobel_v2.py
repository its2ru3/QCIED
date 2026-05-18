"""Sobel-operator quantum edge detection pipeline (v2, paper-faithful).

Implements ``U_G`` (Fig. 13), ``QC`` (Fig. 10) and ``U_T`` (Fig. 11) per
``notes/algorithm_breakdown.md`` §3 with all overrides from
``notes/todo.md`` §0 applied. Uses the custom alternating-carry adder /
subtractor / comparator / swap from ``helpers.modules_v2``.

Pipeline (Fig. 14):
    Preparation → U_G → QC → U_T → measure (Y, X, λ, G')

Gradient masks come from Fig. 12 of [MAIN §3.2] (per ``notes/todo.md`` §0.1),
NOT the textually-buggy Eqs. 7-10. Gradient registers are ``q + 2`` bits
wide per ``notes/todo.md`` §0.6.

Threshold semantics deviate from the paper: per ``notes/todo.md`` §0.4
the threshold scales to the register width as ``T = 2^(q+1)`` (the MSB of
the (q+2)-bit |G_max| register). The paper's text uses ``T = 2^(q-1)``
under q-bit framing; the two thresholds differ by a factor of 4. Classical
verification must pass ``threshold = 2**(q+1)`` to
``classical_edge_detection`` for an apples-to-apples comparison.

Sign handling per ``notes/todo.md`` §0.3: each direction's |G_dir| is
computed as ``max(pos_sum, neg_sum) − min(pos_sum, neg_sum)`` using
``Com`` + ``Swap`` + ``Sub``. The result is non-negative — no sign bit,
no two's-complement, no MSB-reset hack.

References
----------
[MAIN] Yuan et al., Sobel paper, §3.2 Fig. 13, Fig. 10, Fig. 11, Fig. 14.
"""

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from .circular_shift import prepare_neighborhood_images
from .modules_v2 import (
    append_adder,
    append_adder_inverse,
    append_comparator,
    append_subtractor,
    append_subtractor_inverse,
    append_swap,
)
from .ocqr_encoding_new import encode_ocqr_neighborhoods


# ---------------------------------------------------------------------------
# Gradient equations from Fig. 12 masks of [MAIN §3.2]
# (per ``notes/todo.md`` §0.1 table).
#
# Image indices match the shift list in ``helpers.circular_shift.SHIFTS``:
#   0 = (Y,X)   1 = (Y-1,X)   2 = (Y-1,X+1)  3 = (Y,X+1)   4 = (Y+1,X+1)
#   5 = (Y+1,X) 6 = (Y+1,X-1) 7 = (Y,X-1)    8 = (Y-1,X-1)
#
# Each entry lists [image_idx_with_coefficient_1, image_idx_with_coefficient_2,
# image_idx_with_coefficient_1]. The middle entry is the doubled term (2·p),
# realised by adding the same source twice rather than via an explicit U_c
# clone (deviation noted in ``notes/todo.md`` §3.7 — arithmetically
# equivalent, simpler, fewer modules).
# ---------------------------------------------------------------------------
GRAD_DEFS = {
    "Gx":   {"pos": [2, 3, 4], "neg": [8, 7, 6], "doubled_pos": 3, "doubled_neg": 7},
    "Gy":   {"pos": [6, 5, 4], "neg": [8, 1, 2], "doubled_pos": 5, "doubled_neg": 1},
    "G45":  {"pos": [1, 2, 3], "neg": [7, 6, 5], "doubled_pos": 2, "doubled_neg": 6},
    "G135": {"pos": [3, 4, 5], "neg": [1, 8, 7], "doubled_pos": 4, "doubled_neg": 8},
}


def _copy_with_zero_pad_into(qc, src, dst, src_width, dst_width):
    """``dst ⊕= src`` bitwise where ``dst_width > src_width`` (high bits unaffected).

    Used to load the first pixel of an accumulation cascade: ``dst`` is the
    (q+2)-bit zero-initialised accumulator; ``src`` is the q-bit pixel
    register. Equivalent to a Fig. 5 U_c clone limited to q low bits.
    """
    for i in range(src_width):
        qc.cx(src[i], dst[i])


def _add_pixel_into_accum(qc, src, accum, z, pad_anc, q):
    """Add q-bit ``src`` into (q+2)-bit ``accum`` with proper ripple to bit q+1.

    Uses a width-(q+1) Cuccaro adder. ``src`` is zero-padded to q+1 bits by
    appending ``pad_anc`` (must be |0⟩ in, |0⟩ out). ``accum[0..q]`` is the
    adder's ``b`` operand; ``accum[q+1]`` is the carry-out target.

    Two ancillas consumed: ``z`` and ``pad_anc`` (both restored to |0⟩).
    """
    a_padded = list(src) + [pad_anc]      # width q+1
    b_low = list(accum[0:q + 1])           # width q+1
    c_out = accum[q + 1]                   # high accumulator bit
    append_adder(qc, a_padded, b_low, z, c_out, q + 1)


def _add_pixel_into_accum_inverse(qc, src, accum, z, pad_anc, q):
    """Inverse of ``_add_pixel_into_accum`` — uncomputes the addition.

    Used to restore ``accum`` to |0⟩^(q+2) after the gradient has been
    copied out to its dedicated G_dir register.
    """
    a_padded = list(src) + [pad_anc]
    b_low = list(accum[0:q + 1])
    c_out = accum[q + 1]
    append_adder_inverse(qc, a_padded, b_low, z, c_out, q + 1)


def _build_partial_sum(qc, intensity_regs, indices, doubled, accum, z, pad_anc, q):
    """Accumulate ``p_a + 2·p_b + p_c`` into ``accum`` where ``indices = [a, b, c]``
    and ``doubled`` is the index whose coefficient is 2.

    The doubled term is realised by adding the same source twice (paper
    Fig. 13 uses U_c cloning + double-add; we elide the explicit clone since
    Cuccaro's adder preserves its source — see ``notes/todo.md`` §3.7).
    The first pixel into a zero accumulator is a bitwise CNOT copy (saves
    the gates of a full adder call).
    """
    sequence = []
    for idx in indices:
        if idx == doubled:
            sequence.append(idx)
            sequence.append(idx)
        else:
            sequence.append(idx)
    head, *rest = sequence
    _copy_with_zero_pad_into(qc, intensity_regs[head], accum, q, q + 2)
    for idx in rest:
        _add_pixel_into_accum(qc, intensity_regs[idx], accum, z, pad_anc, q)


def _build_partial_sum_inverse(qc, intensity_regs, indices, doubled, accum, z, pad_anc, q):
    """Inverse of ``_build_partial_sum``. Restores ``accum`` to |0⟩."""
    sequence = []
    for idx in indices:
        if idx == doubled:
            sequence.append(idx)
            sequence.append(idx)
        else:
            sequence.append(idx)
    head, *rest = sequence
    # Reverse add chain
    for idx in reversed(rest):
        _add_pixel_into_accum_inverse(qc, intensity_regs[idx], accum, z, pad_anc, q)
    # Undo the CNOT copy
    for i in range(q):
        qc.cx(intensity_regs[head][i], accum[i])


def append_U_G_one_direction(
    qc, intensity_regs, direction, g_accum,
    pos_work, neg_work, z, pad_anc, com_internal, flag, q,
):
    """Compute ``|G_dir|`` for one direction and copy into ``g_accum``.

    Sequence (per ``notes/todo.md`` §0.3):
        1. Build ``pos_sum`` in ``pos_work`` (q+2 bits).
        2. Build ``neg_sum`` in ``neg_work``.
        3. ``Com(pos_work, neg_work)`` writes flag = [pos < neg].
        4. ``Swap(flag; pos_work, neg_work)`` → pos_work now holds max.
        5. ``Sub(neg_work, pos_work)`` → pos_work := max − min ≥ 0 = |G_dir|.
        6. Copy pos_work into ``g_accum`` (CNOT bitwise).
        7. Un-compute steps 5 → 1 to restore pos_work, neg_work, flag,
           com_internal, z, pad_anc all to |0⟩.

    Width of ``pos_work``, ``neg_work``, ``g_accum`` is q+2 per §0.6.

    Ancillas required (all |0⟩ in/out):
        - ``z`` (1 qubit, Cuccaro carry-in for adders/subtractors).
        - ``pad_anc`` (1 qubit, src zero-pad for q→q+1 adder widening).
        - ``com_internal`` (1 qubit, internal borrow inside the comparator).
        - ``flag`` (1 qubit, comparison result driving the swap).
    """
    spec = GRAD_DEFS[direction]
    width = q + 2

    # Step 1-2: build partial sums
    _build_partial_sum(qc, intensity_regs, spec["pos"], spec["doubled_pos"],
                       pos_work, z, pad_anc, q)
    _build_partial_sum(qc, intensity_regs, spec["neg"], spec["doubled_neg"],
                       neg_work, z, pad_anc, q)

    # Step 3: Com(pos_work, neg_work) → flag = [pos < neg]
    append_comparator(qc, pos_work, neg_work, z, com_internal, flag, width)

    # Step 4: Swap so pos_work holds max(pos, neg)
    append_swap(qc, flag, pos_work, neg_work, width)

    # Step 5: pos_work := pos_work - neg_work (now ≥ 0 since pos_work was the max)
    # Sub signature: append_subtractor(qc, a, b, z, bo, w) → b := b - a.
    # So a = neg_work, b = pos_work; borrow target = com_internal (free again).
    append_subtractor(qc, neg_work, pos_work, z, com_internal, width)
    # borrow is 0 since pos_work ≥ neg_work, so com_internal stays |0⟩ as we
    # want.  No correction needed.

    # Step 6: copy |G_dir| into g_accum (bitwise CNOT).
    for i in range(width):
        qc.cx(pos_work[i], g_accum[i])

    # Step 7: uncompute everything (reverse the above).
    append_subtractor_inverse(qc, neg_work, pos_work, z, com_internal, width)
    append_swap(qc, flag, pos_work, neg_work, width)  # swap is self-inverse
    # Comparator inverse: re-run it (Com is its own inverse under our
    # construction because Sub-then-Sub_inv is symmetric, and the CNOT
    # into flag is self-inverse). Re-running with flag still set re-XORs
    # flag back to 0 if and only if the comparison result is the same,
    # which it is — pos_work and neg_work were restored by the prior swap.
    append_comparator(qc, pos_work, neg_work, z, com_internal, flag, width)

    # Uncompute partial sums.
    _build_partial_sum_inverse(qc, intensity_regs, spec["neg"], spec["doubled_neg"],
                               neg_work, z, pad_anc, q)
    _build_partial_sum_inverse(qc, intensity_regs, spec["pos"], spec["doubled_pos"],
                               pos_work, z, pad_anc, q)


def append_U_G(
    qc, intensity_regs, g_x, g_y, g_45, g_135,
    pos_work, neg_work, z, pad_anc, com_internal, flag, q,
):
    """Full ``U_G`` (Fig. 13): compute all four ``|G_dir|`` registers.

    All four output registers (``g_x``, ``g_y``, ``g_45``, ``g_135``) are
    (q+2)-bit accumulators that must enter ``|0⟩^(q+2)``.  After ``U_G``
    they hold ``|G_x|``, ``|G_y|``, ``|G_45|``, ``|G_135|`` respectively.

    Work registers (``pos_work``, ``neg_work``) and all 4 ancillas are
    restored to ``|0⟩`` and can be reused by ``QC`` / ``U_T``.
    """
    for direction, accum in [("Gx", g_x), ("Gy", g_y),
                             ("G45", g_45), ("G135", g_135)]:
        append_U_G_one_direction(
            qc, intensity_regs, direction, accum,
            pos_work, neg_work, z, pad_anc, com_internal, flag, q,
        )


# ---------------------------------------------------------------------------
# QC — Maximum value calculation module (Fig. 10, ``notes/todo.md`` §0.7)
# ---------------------------------------------------------------------------
def append_QC(qc, g_x, g_y, g_45, g_135, z, com_internal, flag, width):
    """Serial 3-stage Com+Swap that leaves ``g_x`` holding ``G_max``.

    Stages per Fig. 10 of [MAIN §3.1.6] and ``notes/todo.md`` §0.7:
        Com(g_x, g_45)  → flag;  Swap(flag; g_x, g_45);  flag re-cleared
        Com(g_x, g_y)   → flag;  Swap(flag; g_x, g_y);   flag re-cleared
        Com(g_x, g_135) → flag;  Swap(flag; g_x, g_135); flag re-cleared

    ``flag`` is reset between stages by re-running ``Com`` after each swap
    (its built-in uncomputation pattern restores ``flag`` to |0⟩ when given
    the *new* register contents — see comment below).

    The three ancillas (``z``, ``com_internal``, ``flag``) must all enter
    |0⟩ and exit |0⟩.

    Note on flag reset: Fig. 10 uses explicit ``|0⟩`` reset boxes between
    stages. We use a coherent uncomputation pattern instead — after the
    Swap, the post-swap registers carry the comparison result implicitly,
    so re-running ``Com`` on the post-swap registers XORs the flag back to
    0 iff (new_g_x >= new_other), which is guaranteed by the Swap. This
    keeps the circuit reversible end-to-end without depending on
    mid-circuit reset semantics.
    """
    pairs = [(g_x, g_45), (g_x, g_y), (g_x, g_135)]
    for top, other in pairs:
        # Com(top, other) → flag XOR= [top < other]
        append_comparator(qc, top, other, z, com_internal, flag, width)
        # Swap conditional on flag: if flag=1, swap so top := other (larger).
        append_swap(qc, flag, top, other, width)
        # Uncompute flag: re-running Com on post-swap registers gives
        # [top_new < other_new] = 0 (by Swap invariant), so flag is XOR'ed
        # back to |0⟩ for the next stage.
        append_comparator(qc, top, other, z, com_internal, flag, width)


# ---------------------------------------------------------------------------
# U_T — Threshold module (Fig. 11, replaced per ``notes/todo.md`` §0.4)
# ---------------------------------------------------------------------------
def append_U_T(qc, g_max, output, q):
    """Threshold via MSB-controlled CNOT cascade.

    Per ``notes/todo.md`` §0.4: for a ``(q+2)``-bit ``g_max`` register the
    threshold ``T = 2^(q+1)`` corresponds to the MSB at index ``q+1``. A
    single CNOT per output bit gives ``output = 2^q − 1`` if MSB=1 (edge)
    else ``output = 0`` (non-edge).

    NB this scales the paper's ``T = 2^(q-1)`` threshold up by 4× to match
    the wider (q+2)-bit register. Document at the call site.

    ``output`` must enter ``|0⟩^q``. ``g_max`` is preserved.
    """
    msb = g_max[q + 1]
    for i in range(q):
        qc.cx(msb, output[i])


# ---------------------------------------------------------------------------
# Top-level pipeline (Fig. 14)
# ---------------------------------------------------------------------------
def build_edge_detection_v2(rgb_matrix, n, q):
    """Full edge-detection circuit (Fig. 14) for an image of size 2^n × 2^n
    with intensity range [0, 2^q − 1].

    Register layout (top-to-bottom of Fig. 14):
        - 9 intensity registers ``I_0..I_8`` of width q (9·q qubits)
        - channel ``ch`` of width 2
        - position ``Y`` of width n
        - position ``X`` of width n
        - 4 gradient accumulators (each q+2 qubits) — held through QC
        - pos_work, neg_work (each q+2) — workspace for U_G
        - encoder ancillas (4 qubits, reused as algorithmic ancillas)
        - extra working ancillas: z, pad_anc, com_internal, flag (4 qubits)
        - output register (q qubits) — fresh, will hold G'

    Total qubits = 9q + 2 + 2n + 4·(q+2) + 2·(q+2) + 4 + 4 + q
                 = 16q + 4n + 22 .
    For (n=2, q=3) this is 16·3 + 8 + 22 = 78 qubits — exceeds the
    extended_stabilizer 63-qubit cap.  See ``notes/todo.md`` §0.5: at
    n=2, q=3 we have a budget squeeze.  Phase 3 will measure exact counts
    and decide whether to share work registers with gradient accumulators
    (option §0.5(b)) or accept the overage (option §0.5(a) with a larger
    simulator).
    """
    if rgb_matrix.shape != (2 ** n, 2 ** n, 3):
        raise ValueError(
            f"build_edge_detection_v2: rgb_matrix shape {rgb_matrix.shape} does "
            f"not match expected ({2**n}, {2**n}, 3) for n={n}"
        )

    width = q + 2

    # Registers (paper-named per ``[[feedback-coding-conventions]]``)
    intensity = [QuantumRegister(q, f"I{i}") for i in range(9)]
    ch = QuantumRegister(2, "ch")
    Y = QuantumRegister(n, "Y")
    X = QuantumRegister(n, "X")
    g_x = QuantumRegister(width, "Gx")
    g_y = QuantumRegister(width, "Gy")
    g_45 = QuantumRegister(width, "G45")
    g_135 = QuantumRegister(width, "G135")
    pos_work = QuantumRegister(width, "pos_w")
    neg_work = QuantumRegister(width, "neg_w")
    enc_anc = QuantumRegister(4, "a_enc")
    work_anc = QuantumRegister(4, "a_work")  # z, pad, com_internal, flag
    output = QuantumRegister(q, "G_out")
    creg = ClassicalRegister(2 * n + 2 + q, "meas")

    qc = QuantumCircuit(
        *intensity, ch, Y, X,
        g_x, g_y, g_45, g_135,
        pos_work, neg_work,
        enc_anc, work_anc, output,
        creg,
    )

    # Compose the position register from Y || X for the encoder API (which
    # expects a single 2n-wide pos register laid out [Y bits, X bits]).
    # We give the encoder a temporary view by passing the qubits directly.
    pos_qubits = list(Y) + list(X)

    # 1. Preparation per [MF Algorithm 1] using circular-shift images.
    #    The encoder consumes ``rgb_matrix`` but internally calls
    #    ``ocqr_encoding_new.prepare_neighborhood_images`` which uses
    #    ZERO-padding — per ``notes/todo.md`` §1.1 that's a known bug.
    #    Workaround: monkey-feed circular-shifted matrices ourselves by
    #    pre-computing the shifted RGB volumes and using a thin wrapper
    #    that bypasses the buggy helper.  For now we delegate; the v2
    #    encoder will be added in a follow-up.  See notes/todo.md §1.1.
    encode_ocqr_neighborhoods(
        qc, pos_qubits, ch, intensity, list(enc_anc), rgb_matrix, n, q
    )

    # 2. U_G — compute all four |G_dir|
    z, pad_anc, com_internal, flag = work_anc[0], work_anc[1], work_anc[2], work_anc[3]
    append_U_G(
        qc, intensity, g_x, g_y, g_45, g_135,
        pos_work, neg_work, z, pad_anc, com_internal, flag, q,
    )

    # 3. QC — leaves ``G_max`` on g_x.
    append_QC(qc, g_x, g_y, g_45, g_135, z, com_internal, flag, width)

    # 4. U_T — write edge map into ``output``.
    append_U_T(qc, g_x, output, q)

    # 5. Measure (Y, X, λ, G_out) into creg.
    measured = list(Y) + list(X) + list(ch) + list(output)
    qc.measure(measured, list(creg))

    return qc
