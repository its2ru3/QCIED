"""OCQR encoding (Eq. 1 + Eq. 6) with the row-by-row info-transfer scheme.

Implements the storage method from Section 2 of Yuan et al. 2025 (Sobel paper)
and Section 2.1 of Yuan et al. 2022 (median-filtering paper, ref. [13]).

The scheme uses 4 reusable auxiliary qubits a0..a3 that act as an
"information-transfer ladder":

    a3 := (Y == y_target)                       — row indicator
    a2 := a3 AND (X == x_target)                — pixel indicator
    a1 := a2 AND (lambda == channel_target)     — pixel-channel indicator
    C^i_neighbor := a1                          — CNOT for each intensity bit set

Between successive (pixel, channel, image) iterations the relevant ancillas
are reset, so the four auxiliary qubits are reused throughout the entire
encoding. Critically these same four aux qubits are part of the global
auxiliary pool (`aux` register) — the paper's 19-qubit total budget reuses
them later for arithmetic.

Public API
----------
* `encode_ocqr_neighborhoods(qc, pos, ch, intensity_regs, aux4, rgb_matrix, n, q)`
  Drives Algorithm 1 to encode the core image and its 8 neighborhoods (Eq. 6)
  on the *same* shared `pos`, `ch` registers and 9 separate intensity regs.
* `prepare_test_matrix_4x4()` — the 4×4 RGB test matrix matching Fig. 1.
* `prepare_neighborhood_images(rgb_matrix)` — classical helper that returns
  the 9 shifted RGB matrices (used to extract intensity values to encode;
  this is NOT used as 9 separate quantum encodings — the encoder uses these
  values to drive a single shared-superposition encoding).
* LUT helpers (`get_3bit_to_8bit_lut`, etc.) for image visualisation.
"""

import numpy as np
from PIL import Image
from qiskit import QuantumCircuit, QuantumRegister


# ---------------------------------------------------------------------------
# Test fixtures and LUT helpers
# ---------------------------------------------------------------------------
def prepare_test_matrix_4x4():
    """4x4 test matrix matching Fig. 1 of the paper."""
    return np.array([
        [[1, 2, 1], [2, 3, 2], [2, 6, 0], [0, 7, 2]],
        [[3, 5, 0], [3, 4, 1], [2, 4, 2], [3, 7, 5]],
        [[4, 7, 4], [2, 6, 1], [7, 7, 7], [3, 5, 5]],
        [[3, 7, 5], [3, 5, 0], [0, 7, 2], [0, 2, 0]],
    ], dtype=np.uint8)


def prepare_neighborhood_images(rgb_matrix):
    """Return the 9 neighborhood matrices: [core, N, NE, E, SE, S, SW, W, NW].

    Ordering follows Eq. 6 of the median-filtering paper:
        C_{Y,X}, C_{Y-1,X}, C_{Y-1,X+1}, C_{Y,X+1}, C_{Y+1,X+1},
        C_{Y+1,X}, C_{Y+1,X-1}, C_{Y,X-1}, C_{Y-1,X-1}
    """
    h, w = rgb_matrix.shape[:2]
    shifts = [
        (0, 0), (-1, 0), (-1, 1), (0, 1), (1, 1),
        (1, 0), (1, -1), (0, -1), (-1, -1),
    ]
    out = []
    for dy, dx in shifts:
        shifted = np.zeros_like(rgb_matrix)
        for y in range(h):
            for x in range(w):
                sy, sx = y + dy, x + dx
                if 0 <= sy < h and 0 <= sx < w:
                    shifted[y, x] = rgb_matrix[sy, sx]
        out.append(shifted)
    return out


def get_3bit_to_8bit_lut():
    return np.round(np.linspace(0, 255, 8)).astype(np.uint8)


def get_8bit_to_3bit_lut(lut3=None):
    if lut3 is None:
        lut3 = get_3bit_to_8bit_lut()
    lut3 = np.asarray(lut3, dtype=np.int16)
    vals = np.arange(256, dtype=np.int16)[:, None]
    return np.abs(vals - lut3[None, :]).argmin(axis=1).astype(np.uint8)


def convert_3bit_to_8bit(img3, lut3=None):
    if lut3 is None:
        lut3 = get_3bit_to_8bit_lut()
    return np.asarray(lut3, dtype=np.uint8)[img3]


def convert_8bit_to_3bit(img8, lut8=None, lut3=None):
    if lut8 is None:
        lut8 = get_8bit_to_3bit_lut(lut3=lut3)
    return np.asarray(lut8, dtype=np.uint8)[img8]


# ---------------------------------------------------------------------------
# Row-by-row OCQR neighborhood encoder (Algorithm 1, generalised to 9 images)
# ---------------------------------------------------------------------------
def _apply_x_mask(qc, qubits, bit_string_lsb_first):
    """Apply X gates so that the listed qubits are in state |1> iff each
    corresponds to a '1' in the original target pattern. Used to "flip
    controls" so that a Toffoli/MCX with positive controls effectively tests
    for the desired bit pattern.

    `bit_string_lsb_first[i]` matches `qubits[i]`. We flip qubits whose bit is 0,
    so the original-0 controls become 1 (and a positive-control MCX/Toffoli
    fires on the target pattern). The caller must call this twice (sandwiching
    the controlled op) to leave the qubits unchanged.
    """
    for i, b in enumerate(bit_string_lsb_first):
        if b == '0':
            qc.x(qubits[i])


def _multi_controlled_and(qc, controls, target, scratch=None):
    """Set `target` ^= AND(controls).

    `scratch` is an optional qubit (assumed |0> on entry and restored to |0>
    on exit) used to chain Toffolis when len(controls) > 2 without invoking
    qiskit's mcx (which requires synthesis ancillas that are not always
    available on extended_stabilizer). For len(controls) == 3 exactly one
    scratch is needed. For larger control counts the caller must enlarge the
    scratch policy.
    """
    n = len(controls)
    if n == 0:
        qc.x(target)
    elif n == 1:
        qc.cx(controls[0], target)
    elif n == 2:
        qc.ccx(controls[0], controls[1], target)
    elif n == 3:
        assert scratch is not None, "3-control MCX requires a scratch ancilla"
        # scratch := c0 AND c1
        qc.ccx(controls[0], controls[1], scratch)
        # target ^= scratch AND c2
        qc.ccx(scratch, controls[2], target)
        # uncompute scratch
        qc.ccx(controls[0], controls[1], scratch)
    else:
        # >3 controls — uses qiskit's mcx synthesis. Caller is responsible for
        # making sure the chosen simulator can handle the resulting gate.
        qc.mcx(list(controls), target)


def _multi_controlled_and_inv(qc, controls, target, scratch=None):
    """Inverse of `_multi_controlled_and` (same op since CCX/CNOT are self-inverse).

    Provided for readability when un-computing.
    """
    _multi_controlled_and(qc, controls, target, scratch=scratch)


def encode_ocqr_neighborhoods(qc, pos, ch, intensity_regs, aux4,
                              rgb_matrix, n, q):
    """Encode the OCQR state of Eq. 6 (core image + 8 neighborhoods).

    Args
    ----
    qc            : QuantumCircuit being built. The function appends gates to
                    this circuit. Position/channel/intensity/aux registers
                    MUST already be allocated on `qc`.
    pos           : QuantumRegister of size 2n. Layout: pos[0..n-1] = Y bits
                    (LSB first), pos[n..2n-1] = X bits (LSB first).
    ch            : QuantumRegister of size 2 — the channel register
                    (ch[0]=lambda_0, ch[1]=lambda_1, lambda value in [0,3]).
                    Maps 00->R, 01->G, 10->B, 11->redundant (left at zero).
    intensity_regs: list of 9 QuantumRegisters, each of size q. Order matches
                    `prepare_neighborhood_images` (core first, then 8 shifts).
    aux4          : QuantumRegister of size >= 4 containing the four
                    information-transfer auxiliaries a0..a3. After this
                    function returns, all four aux qubits are |0>.
    rgb_matrix    : (2^n, 2^n, 3) numpy array of intensity values in [0, 2^q-1].
    n, q          : OCQR parameters.

    Strategy (per Algorithm 1 of ref. [13], generalised to 9 images):
      1. H on pos and ch (uniform superposition).
      2. For each row y in [0, 2^n - 1]:
           (a) Compute a3 := (Y == y).  When n == 1 this is a single CNOT; for
               n == 2 it's a Toffoli with the relevant X-flips; for larger n,
               an MCX of n controls.
           (b) For each x in [0, 2^n - 1]:
                 (i) Compute a2 := a3 AND (X == x).  (Toffoli/MCX over a3 and
                     X bits with X-flips.)
                 (ii) For each channel ch_target in {0=R, 1=G, 2=B}:
                       - a1 := a2 AND (lambda == ch_target). 3-input MCX.
                       - For each image idx, find the value at this image's
                         (y,x,ch_target). For each '1' bit in that value,
                         CNOT a1 -> intensity_regs[idx][bit_idx].
                       - Reset a0, a1.
                 (iii) Uncompute a2 (reverse the Toffoli with the same X-flips).
           (c) Uncompute a3.

    The reset operations use qiskit's `reset` instruction; this is supported
    by the `simulator_extended_stabilizer` backend.
    """
    assert len(intensity_regs) == 9
    size = 2 ** n
    assert rgb_matrix.shape == (size, size, 3)

    # 1. Hadamard for uniform superposition over pos/channel.
    qc.h(pos)
    qc.h(ch)

    a0, a1, a2, a3 = aux4[0], aux4[1], aux4[2], aux4[3]
    # a0 is mentioned in Algorithm 1 as something that gets reset together
    # with a1, but no signal is ever explicitly written to it. We follow the
    # paper's text but only use a1, a2, a3 for active logic.

    # Pre-compute the 9 shifted intensity matrices once (classical).
    neighborhoods = prepare_neighborhood_images(rgb_matrix)

    Y_qubits = list(pos[0:n])  # LSB-first Y bits
    X_qubits = list(pos[n:2 * n])  # LSB-first X bits
    ch_qubits = [ch[0], ch[1]]  # ch[0]=lambda_0 (LSB), ch[1]=lambda_1 (MSB)

    for y in range(size):
        y_bits = format(y, f'0{n}b')[::-1]  # LSB first
        # ---- (a) compute a3 := (Y == y) ----
        _apply_x_mask(qc, Y_qubits, y_bits)
        _multi_controlled_and(qc, Y_qubits, a3)
        _apply_x_mask(qc, Y_qubits, y_bits)  # restore Y qubits

        for x in range(size):
            x_bits = format(x, f'0{n}b')[::-1]
            # ---- (b)(i) compute a2 := a3 AND (X == x) ----
            # For n==1: controls=[a3, X0] -> CCX.
            # For n==2: controls=[a3, X0, X1] -> 3-ctrl, use a0 as scratch.
            # For larger n: falls back to mcx.
            _apply_x_mask(qc, X_qubits, x_bits)
            _multi_controlled_and(qc, [a3] + X_qubits, a2, scratch=a0)
            _apply_x_mask(qc, X_qubits, x_bits)

            for ch_idx in range(3):
                ch_bits = format(ch_idx, '02b')[::-1]  # LSB first
                # ---- compute a1 := a2 AND (lambda == ch_idx) ----
                # 3 controls: a2 + lambda0 + lambda1. Use a0 as scratch.
                _apply_x_mask(qc, ch_qubits, ch_bits)
                _multi_controlled_and(qc, [a2] + ch_qubits, a1, scratch=a0)
                _apply_x_mask(qc, ch_qubits, ch_bits)

                # For each neighborhood image, emit CNOT(a1) -> intensity bits
                # whose binary representation contains a 1.
                for img_idx in range(9):
                    val = int(neighborhoods[img_idx][y, x, ch_idx])
                    if val == 0:
                        continue
                    bit_str = format(val, f'0{q}b')[::-1]  # LSB first
                    target_reg = intensity_regs[img_idx]
                    for bit_pos, bit in enumerate(bit_str):
                        if bit == '1':
                            qc.cx(a1, target_reg[bit_pos])

                # reset a0, a1 (per Algorithm 1; a0 is always 0 so reset is no-op,
                # but we issue it for fidelity)
                qc.reset(a0)
                qc.reset(a1)

            # ---- uncompute a2 (so it's |0> for the next pixel) ----
            qc.reset(a2)

        # ---- uncompute a3 ----
        qc.reset(a3)


# ---------------------------------------------------------------------------
# Standalone helpers (single-image encoding for tests/visualisation)
# ---------------------------------------------------------------------------
def encode_ocqr_from_matrix(rgb_matrix, n=2, q=3):
    """Build a standalone QuantumCircuit holding the OCQR encoding of a 4x4 image.

    This convenience function allocates ONE intensity register (no
    neighborhoods) for visualisation/testing. The main pipeline uses
    `encode_ocqr_neighborhoods` instead.
    """
    size = 2 ** n
    assert rgb_matrix.shape == (size, size, 3)
    pos = QuantumRegister(2 * n, "pos")
    ch = QuantumRegister(2, "ch")
    intensity = QuantumRegister(q, "I0")
    aux = QuantumRegister(4, "a")
    qc = QuantumCircuit(pos, ch, intensity, aux)
    # Build a dummy 9-list with the same image in every slot so we can reuse
    # the multi-image encoder for the single-image case. Then only the core
    # slot is materially encoded.
    fake = np.zeros_like(rgb_matrix)
    encode_ocqr_neighborhoods(qc, pos, ch, [intensity] + [QuantumRegister(q, f"_dummy{i}") for i in range(8)],
                              aux, rgb_matrix, n, q)
    # Note: above call ignores the dummy register allocations as they are not
    # part of qc. Use only when intentionally encoding a single image: build
    # a circuit with 9 intensity regs and ignore the 8 extras.
    return qc


def encode_ocqr_from_image(image_path, n=2, q=3):
    """Load an image, scale to 2^n × 2^n with q-bit colour depth, and OCQR-encode."""
    img = Image.open(image_path).convert('RGB')
    target = 2 ** n
    img = img.resize((target, target))
    arr = np.array(img, dtype=np.uint8)
    max_val = 2 ** q - 1
    if arr.max() > max_val:
        arr = (arr * max_val / 255).astype(np.uint8)
    return encode_ocqr_from_matrix(arr, n, q), arr


def decode_ocqr_to_classical(counts, n=2, q=3):
    """Decode counts into a (2^n)x(2^n)x3 RGB matrix.

    Counts string format (most-significant bit on the left): the measurement
    string is `pos_bits + ch_bits + intensity_bits` from the perspective of
    qiskit's classical register, but qiskit prints the register bits with the
    MSB on the left, so we reverse.
    """
    size = 2 ** n
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    bitlen = 2 * n + 2 + q
    for state_str, _count in counts.items():
        clean = state_str.replace(' ', '')
        if len(clean) != bitlen:
            continue
        rev = clean[::-1]  # rev[0] = qubit 0
        # qubit 0 .. 2n-1 -> pos (Y0..Y_{n-1}, X0..X_{n-1})
        # qubit 2n .. 2n+1 -> channel
        # qubit 2n+2 .. 2n+1+q -> intensity
        y_val = int(rev[0:n][::-1], 2)
        x_val = int(rev[n:2 * n][::-1], 2)
        ch_val = int(rev[2 * n:2 * n + 2][::-1], 2)
        c_val = int(rev[2 * n + 2:2 * n + 2 + q][::-1], 2)
        if 0 <= ch_val <= 2:
            rgb[y_val, x_val, ch_val] = c_val
    return rgb
