"""Paper-faithful quantum modules — Figs. 5-9 of [MAIN].

All modules follow ``notes/algorithm_breakdown.md`` §2 and the resolution
overrides in ``notes/todo.md`` §0. Uses a **custom alternating-carry
ripple-carry adder** (Cuccaro-CDKM 2004 style, in-place) instead of
Qiskit's ``HalfAdderGate`` so the ancilla budget stays at the paper's
``6q + 2`` design target per ``notes/todo.md`` §0.2 / §0.5.

API conventions
---------------
Builders are ``append_*`` functions that emit gates onto an existing
``QuantumCircuit``. They never allocate new registers — the caller passes
in the qubits / sub-registers to use. Each function documents its ancilla
contract (what must enter ``|0⟩`` and what exits ``|0⟩``).

Tested against statevector simulation on small ``q`` in
``tests/test_modules_v2.py``.

References
----------
[MAIN] Yuan et al., Sobel paper, §3.1 (modules), §3.2 (gradient circuit).
[CDKM] Cuccaro, Draper, Kutin, Moulton (2004) arXiv:quant-ph/0410184 —
       in-place ripple-carry adder with MAJ/UMA primitives.
"""

from qiskit import QuantumCircuit, QuantumRegister


# ---------------------------------------------------------------------------
# Fig. 5 — Quantum cloning module U_c  [MAIN §3.1.1, Eq. 2]
# ---------------------------------------------------------------------------
def append_cloning(qc, src, tgt, width):
    """``U_c |C⟩ |0⟩^width → |C⟩ |C⟩`` via ``width`` parallel CNOTs.

    Paper Fig. 5: bitwise computational-basis copy. ``src`` preserved.
    ``tgt`` must be ``|0⟩^width`` on entry.
    """
    if len(src) < width or len(tgt) < width:
        raise ValueError(
            f"append_cloning: src ({len(src)}) and tgt ({len(tgt)}) must "
            f"each have at least width={width} qubits"
        )
    for i in range(width):
        qc.cx(src[i], tgt[i])


def quantum_cloning_module(width):
    """Standalone Fig. 5 gate for inspection. Width = `width` qubits each side."""
    src = QuantumRegister(width, "src")
    tgt = QuantumRegister(width, "tgt")
    qc = QuantumCircuit(src, tgt, name=f"U_c({width})")
    append_cloning(qc, src, tgt, width)
    return qc


# ---------------------------------------------------------------------------
# Fig. 6 — Quantum adder ADD  [MAIN §3.1.2, Eq. 3]
# ---------------------------------------------------------------------------
# Implementation: Cuccaro-CDKM 2004 in-place ripple-carry adder. Uses
# exactly 2 ancillas (``z`` carry-in slot + ``c_out`` high-bit slot),
# matching the paper's "two alternating carry bits" claim of [MAIN
# §3.1.2] and ``notes/todo.md`` §0.2.
#
# MAJ(c, b, a) — majority + propagate forward:
#     CX(a, b); CX(a, c); CCX(c, b, a)
# UMA(c, b, a) — uncompute majority + extract sum bit:
#     CCX(c, b, a); CX(a, c); CX(c, b)
#
# After a forward MAJ chain over bit positions 0..m-1 followed by a
# carry-out extraction and a reverse UMA chain over m-1..0, the result
# is: ``b ← (a + b) mod 2^m``, carry-out XORed into ``c_out``, and the
# carry-in ancilla ``z`` is restored to |0⟩.

def _maj(qc, c, b, a):
    """Majority gate: a := MAJ(a_old, b_old, c_old); b ⊕= a_old; c ⊕= a_old."""
    qc.cx(a, b)
    qc.cx(a, c)
    qc.ccx(c, b, a)


def _maj_inv(qc, c, b, a):
    """Inverse of _maj (reverses the gate list since CX/CCX are self-inverse)."""
    qc.ccx(c, b, a)
    qc.cx(a, c)
    qc.cx(a, b)


def _uma(qc, c, b, a):
    """Uncompute-majority-and-add. Restores ``a`` to its original value,
    writes the sum bit into ``b``, and restores ``c`` to its incoming carry.
    """
    qc.ccx(c, b, a)
    qc.cx(a, c)
    qc.cx(c, b)


def _uma_inv(qc, c, b, a):
    """Inverse of _uma (reverses the gate list)."""
    qc.cx(c, b)
    qc.cx(a, c)
    qc.ccx(c, b, a)


def append_adder(qc, a, b, z, c_out, width):
    """In-place ripple-carry adder: ``b := (a + b) mod 2^width``;
    carry-out XORed into ``c_out``.

    Paper Fig. 6 generalised to ``width`` bits; ``notes/todo.md`` §0.2.

    Parameters
    ----------
    qc : QuantumCircuit
    a : sequence of ``width`` qubits (preserved).
    b : sequence of ``width`` qubits (low ``width`` bits of sum).
    z : single ancilla qubit — must be ``|0⟩`` on entry, exits ``|0⟩``.
    c_out : single qubit — high bit of the sum is XORed into it. If the
        caller passes ``|0⟩`` and reads it after, this IS the carry-out.
        If the caller passes a pre-existing bit (e.g. the next slot of a
        wider accumulator), it is XORed in place per ripple-carry semantics.
    width : int, the bit-width of the adder.

    Ancilla contract: 2 qubits used (``z``, ``c_out``). Only ``z`` must
    be ``|0⟩`` in/out; ``c_out`` is caller's choice per the XOR semantics
    above.

    Reference: [CDKM] §3 (MAJ/UMA decomposition). For the inverse use
    ``append_adder_inverse``.
    """
    if width <= 0:
        raise ValueError(f"append_adder: width must be positive, got {width}")
    if len(a) < width or len(b) < width:
        raise ValueError(
            f"append_adder: a ({len(a)}) and b ({len(b)}) need at least "
            f"width={width} qubits each"
        )

    # Forward MAJ chain — builds carries up through `a`'s qubits.
    # Per-bit roles: c=carry-in slot, b=augend bit, a=addend bit (gets carry).
    _maj(qc, z, b[0], a[0])
    for i in range(1, width):
        _maj(qc, a[i - 1], b[i], a[i])

    # Extract the carry-out: it now lives on a[width-1].
    qc.cx(a[width - 1], c_out)

    # Reverse UMA chain — extracts sum bits into `b`, uncomputes `a` back
    # to original, restores z to |0⟩.
    for i in range(width - 1, 0, -1):
        _uma(qc, a[i - 1], b[i], a[i])
    _uma(qc, z, b[0], a[0])


def append_adder_inverse(qc, a, b, z, c_out, width):
    """Inverse of ``append_adder``: ``b := (b - a) mod 2^width``;
    carry-out XORed into ``c_out`` is undone (XOR is self-inverse).

    Used for un-computing temporary sums during gradient calculation.
    """
    if width <= 0:
        raise ValueError(f"append_adder_inverse: width must be positive, got {width}")

    # Forward sequence was:
    #     MAJ(z, b[0], a[0])                                  -- (i=0)
    #     MAJ(a[i-1], b[i], a[i])  for i = 1..w-1
    #     CX(a[w-1], c_out)
    #     UMA(a[i-1], b[i], a[i])  for i = w-1..1
    #     UMA(z, b[0], a[0])
    # The inverse reverses the gate-list and inverts each gate. CX is
    # self-inverse; MAJ⁻¹ and UMA⁻¹ are the in-order reversals (helpers
    # below). So the inverse is:
    #     UMA⁻¹(z, b[0], a[0])
    #     UMA⁻¹(a[i-1], b[i], a[i]) for i = 1..w-1
    #     CX(a[w-1], c_out)
    #     MAJ⁻¹(a[i-1], b[i], a[i]) for i = w-1..1
    #     MAJ⁻¹(z, b[0], a[0])
    _uma_inv(qc, z, b[0], a[0])
    for i in range(1, width):
        _uma_inv(qc, a[i - 1], b[i], a[i])

    qc.cx(a[width - 1], c_out)

    for i in range(width - 1, 0, -1):
        _maj_inv(qc, a[i - 1], b[i], a[i])
    _maj_inv(qc, z, b[0], a[0])


def quantum_adder(width):
    """Standalone Fig. 6 gate for inspection."""
    a = QuantumRegister(width, "a")
    b = QuantumRegister(width, "b")
    z = QuantumRegister(1, "z")
    c = QuantumRegister(1, "c")
    qc = QuantumCircuit(a, b, z, c, name=f"ADD({width})")
    append_adder(qc, a, b, z[0], c[0], width)
    return qc


# ---------------------------------------------------------------------------
# Fig. 7 — Quantum subtractor SUB  [MAIN §3.1.3, Eq. 4]
# ---------------------------------------------------------------------------
def append_subtractor(qc, a, b, z, borrow_out, width):
    """In-place subtractor: ``b := (b - a) mod 2^width``;
    borrow-out XORed into ``borrow_out``.

    Identity: ``b - a = NOT((NOT b) + a)``. We X-invert ``b`` around an
    ``append_adder`` call. Borrow polarity: ``borrow_out = 1`` iff ``b < a``.

    Same 2-ancilla footprint as the adder (``z`` + ``borrow_out``);
    matches Fig. 7 of [MAIN §3.1.3].
    """
    if width <= 0:
        raise ValueError(f"append_subtractor: width must be positive, got {width}")
    if len(a) < width or len(b) < width:
        raise ValueError(
            f"append_subtractor: a ({len(a)}) and b ({len(b)}) need at least "
            f"width={width} qubits each"
        )

    for i in range(width):
        qc.x(b[i])
    append_adder(qc, a, b, z, borrow_out, width)
    for i in range(width):
        qc.x(b[i])
    # Carry-out from the adder above is 1 iff (a + NOT(b_orig)) >= 2^width
    # iff a > b_orig iff b_orig < a — exactly the borrow flag we want.
    # No extra X needed; ``borrow_out`` already holds the borrow polarity.


def quantum_subtractor(width):
    """Standalone Fig. 7 gate."""
    a = QuantumRegister(width, "a")
    b = QuantumRegister(width, "b")
    z = QuantumRegister(1, "z")
    bo = QuantumRegister(1, "bo")
    qc = QuantumCircuit(a, b, z, bo, name=f"SUB({width})")
    append_subtractor(qc, a, b, z[0], bo[0], width)
    return qc


# ---------------------------------------------------------------------------
# Fig. 8 — Quantum comparator Com  [MAIN §3.1.4]
# ---------------------------------------------------------------------------
def append_comparator(qc, a, b, z, internal_borrow, c_out, width):
    """``c_out ^= [a < b]`` with ``a, b`` preserved.

    Per ``notes/algorithm_breakdown.md`` §2.4: ``C_out = 1`` iff
    ``a < b`` (i.e. ``C_YX < C_Y'X'``), ``0`` otherwise.

    Implementation (subtractor-sandwich):

      1. ``Sub`` computes ``a := a - b mod 2^w`` and writes the borrow flag
         (= 1 iff ``a < b``) into ``internal_borrow``.
      2. ``CNOT(internal_borrow, c_out)`` copies the flag out.
      3. ``Sub^{-1}`` restores ``a`` and clears ``internal_borrow`` back to |0⟩.

    Ancilla contract: 2 ancillas (``z``, ``internal_borrow``) must be |0⟩
    in/out. ``c_out`` is XORed with the comparison flag — caller usually
    passes |0⟩ for a clean assignment.

    Note (``notes/todo.md`` §2.7): structural deviation from Fig. 8's
    direct MSB-to-LSB cascade — uses 3 live ancilla slots (``z``,
    ``internal_borrow``, ``c_out``) instead of the paper's 2. Re-uses the
    verified custom Sub. Track for Phase 4 if the budget gets tight.
    """
    if width <= 0:
        raise ValueError(f"append_comparator: width must be positive, got {width}")

    # ``append_subtractor(qc, A, B, ...)`` computes ``B := B - A``; borrow
    # flag = ``1 iff B_orig < A``. Call with A=b_reg, B=a_reg so the flag is
    # ``1 iff a_reg < b_reg`` — exactly the comparator's spec.
    append_subtractor(qc, b, a, z, internal_borrow, width)
    qc.cx(internal_borrow, c_out)
    append_subtractor_inverse(qc, b, a, z, internal_borrow, width)


def append_subtractor_inverse(qc, a, b, z, borrow_out, width):
    """Inverse of ``append_subtractor`` — un-computes the subtraction.

    Used by ``append_comparator`` to restore the input registers after
    extracting the comparison flag.
    """
    if width <= 0:
        raise ValueError(f"append_subtractor_inverse: width must be positive, got {width}")
    # Inverse of: X b; ADD(a, b, z, bo); X b
    # is:         X b; ADD†(a, b, z, bo); X b
    for i in range(width):
        qc.x(b[i])
    append_adder_inverse(qc, a, b, z, borrow_out, width)
    for i in range(width):
        qc.x(b[i])


def quantum_comparator(width):
    """Standalone Fig. 8 gate."""
    a = QuantumRegister(width, "a")
    b = QuantumRegister(width, "b")
    z = QuantumRegister(1, "z")
    ib = QuantumRegister(1, "ib")
    cout = QuantumRegister(1, "cout")
    qc = QuantumCircuit(a, b, z, ib, cout, name=f"CMP({width})")
    append_comparator(qc, a, b, z[0], ib[0], cout[0], width)
    return qc


# ---------------------------------------------------------------------------
# Fig. 9 — Quantum controlled swap Swap  [MAIN §3.1.5]
# ---------------------------------------------------------------------------
def append_swap(qc, ctrl, a, b, width):
    """``width`` parallel Fredkin (CSWAP) gates sharing ``ctrl``.

    When ``ctrl = 1``, swaps the contents of ``a`` and ``b`` bit-for-bit.
    When ``ctrl = 0``, no-op. Paper Fig. 9 / [MAIN §3.1.5].
    """
    if width <= 0:
        raise ValueError(f"append_swap: width must be positive, got {width}")
    for i in range(width):
        qc.cswap(ctrl, a[i], b[i])


def quantum_swap(width):
    """Standalone Fig. 9 gate."""
    ctrl = QuantumRegister(1, "ctrl")
    a = QuantumRegister(width, "a")
    b = QuantumRegister(width, "b")
    qc = QuantumCircuit(ctrl, a, b, name=f"SWAP({width})")
    append_swap(qc, ctrl[0], a, b, width)
    return qc


__all__ = [
    "append_cloning", "quantum_cloning_module",
    "append_adder", "append_adder_inverse", "quantum_adder",
    "append_subtractor", "append_subtractor_inverse", "quantum_subtractor",
    "append_comparator", "quantum_comparator",
    "append_swap", "quantum_swap",
]
