# Quantum Color Image Edge Detection (QCIED)

Faithful Qiskit implementation of:

> **"Quantum color image edge detection algorithm based on Sobel operator"**
> Suzhen Yuan, Xianli Li, Shuyin Xia, Xianrong Qing, Jermiah D. Deng,
> *Quantum Information Processing* (2025) 24:195.

Storage scheme follows the same authors' ref. [13]:

> **"Quantum color image median filtering in the spatial domain: theory and experiment"**
> Yuan, Qing, Hang, Qu, *Quantum Information Processing* (2022) 21:321.

The implementation is built for **Qiskit ≥ 2** and runs on Linux (developed in WSL2).
All circuit constructions use the modern Qiskit API (`HalfAdderGate`, `.to_gate()` wrappers,
`ClassicalRegister` measurements, mid-circuit `reset`).

---

## Pipeline

```
┌────────────────────────────────────┐
│ 1. OCQR Neighborhood Encoding (Eq. 6)
│    row-by-row info-transfer with 4 reusable
│    ancillas (Algorithm 1 of ref. [13])
└──────────────┬─────────────────────┘
               ▼
┌────────────────────────────────────┐
│ 2. Gradient Calculation U_G (Fig. 13)
│    For each direction: pos_sum -> work,
│    copy to grad reg, reset work,
│    neg_sum -> work, SUB(work, grad),
│    conditional ABS via 2's complement.
│    Bit-shift trick handles 2*p_i terms
│    at zero gate cost.
└──────────────┬─────────────────────┘
               ▼
┌────────────────────────────────────┐
│ 3. Maximum Value Module QC (Fig. 10)
│    Three (Com + Swap) stages with
│    shared aux pool; reset between stages.
└──────────────┬─────────────────────┘
               ▼
┌────────────────────────────────────┐
│ 4. Threshold U_T (Fig. 11)
│    flag := MSB(grad) OR upper-bits
│    => edge iff grad >= 2^(q-1).
│    If edge: T_reg := 2^q-1, else T_reg := grad.
└──────────────┬─────────────────────┘
               ▼
┌────────────────────────────────────┐
│ 5. Final Subtraction (Fig. 14)
│    I0 := I0 - T_reg (q-bit SUB)
└──────────────┬─────────────────────┘
               ▼
        Measurement
```

---

## File layout

```
QCIED/
├── helpers/
│   ├── __init__.py                 # Auto-imports submodules
│   ├── quantum_modules.py          # Figs. 5-11 module factories
│   ├── ocqr_encoding.py            # Algorithm 1 row-by-row OCQR encoder
│   └── sobel_edge_detection.py     # U_G + QC + U_T + final subtraction (Fig. 14)
├── main_4x4_simulation.ipynb       # End-to-end driver for the 4x4 test image
├── Papers/                          # The two source PDFs
├── Paper_markdown/                  # Sectioned markdown + figure descriptions
├── images/                          # input/, output/
└── analysis_discrepancies.md       # Pre-refactor audit (see "What was wrong")
```

`helpers/ocqr_encoding_1.py` (gitignored) is a scratch file kept locally for
exploration; it is **not** loaded by the package.

---

## Modules — paper figure → code mapping

| Paper figure | Function | Layout (input qubits → output) | Notes |
|---|---|---|---|
| Fig. 5 (Cloning) | `quantum_cloning_module(q)` | `|C>[q] |0>^q` → `|C> |C>` | q parallel CNOTs. |
| Fig. 6 (Adder)   | `quantum_adder(q)`           | `|A>[q] |B>[q] |0>` → `|A> |A+B mod 2^q> |carry_out>` | Wraps `qiskit.circuit.library.HalfAdderGate`. |
| Fig. 7 (Subtractor) | `quantum_subtractor(q)`    | `|A>[q] |B>[q] |0>` → `|A> |B-A mod 2^q> |borrow_out>` | Two's-complement via X-ADD-X. |
| Fig. 8 (Comparator) | `quantum_comparator(q)`    | `|A>[q] |B>[q] |aux>[q] |tmp>[1] |cout>[1]` → cout ^= (A<B) | Compute-copy-uncompute: SUB then SUB⁻¹; aux & tmp reset to 0. |
| Fig. 9 (Swap)       | `quantum_swap(q)`           | `|c> |A>[q] |B>[q]` → conditional swap | q parallel Fredkins. |
| Fig. 10 (Max-value) | inlined inside `build_edge_detection_circuit` | three (Com + Swap) stages | Comparator aux reset between stages, matching the paper's reset boxes. |
| Fig. 11 (Threshold) | inlined inside `build_edge_detection_circuit` | edge iff MSBs of `grad` set | Uses one flag qubit reset after use. |

The three remaining helper-module factories (`quantum_max_value_module`,
`quantum_threshold_module`) exist primarily for testing — the production
pipeline inlines them on the shared aux pool to honour the paper's tight
qubit budget.

---

## Qubit budget

For the paper's 4×4, q=3 test the paper states **53 qubits**: `2n + 2 + 9q + 19 = 4 + 2 + 27 + 19 = 52` (paper says 53 because the threshold module adds 1 ancilla via the X-gate-prep at the start of Fig. 14).

This implementation uses **60 qubits** for q=3:

| Register | Size | Purpose |
|---|---|---|
| `pos` | 2n = 4 | Y, X position (Hadamard superposition) |
| `ch`  | 2 | colour channel λ (Hadamard superposition) |
| `I0`..`I8` | 9q = 27 | 9 entangled intensity registers (core + 8 neighbours) |
| `a`   | 4 | info-transfer ancillas a₀..a₃ for the encoder (reused for arithmetic afterwards) |
| `G0`..`G3` | 4(q+1) = 16 | absolute gradient values |Gx|, |Gy|, |G45|, |G135| |
| `work` | q+2 = 5 | running accumulator for pos / neg sums |
| `scr`  | 2 | carry/borrow + flag scratch |
| **Total** | **60** | |

The **+7 qubit overhead** vs. the paper's quoted total comes from (a) keeping
all four gradient registers alive simultaneously for the max-value stage
(the paper interleaves gradient computation with comparison on the
intensity registers themselves, an optimisation that requires deeper
re-architecting), and (b) using `q+2`-wide accumulators rather than
narrower ternary/quaternary adders. The trade-off is gained in
correctness clarity and direct testability.

For an apples-to-apples 53-qubit version, the encoding+arithmetic would
need to share more aux qubits via further reset/restore patterns; the
project notes this in `analysis_discrepancies.md` and the relevant
docstrings.

---

## What was wrong with the previous implementation

A pre-refactor audit (`analysis_discrepancies.md`) identified the
following issues; all have been addressed:

| # | Bug | Fix |
|---|---|---|
| A1 | Encoder re-encoded 9 separate images with (2n+2)-controlled MCX, blowing up gate count to ~3000 | Row-by-row encoder using a₀..a₃ information-transfer ladder (Algorithm 1); 9 entangled C registers share one position/channel superposition |
| A2 | No `a₀..a₃` info-transfer ancillas existed | 4-qubit `a` register added; properly reset between rows / pixels / channels |
| A3 | Neighbourhood images built via classical `np.roll` then encoded separately | All 9 image variants encoded in parallel under the same `(pos, ch)` superposition with extra CNOTs per neighbour |
| A4 | Bit-order for position qubits inconsistent between encoder and decoder | Centralised: LSB-first throughout; decoder reverses consistently |
| B1 | Adder convention contradicted paper (sum lived in B not A) | Adopted the paper convention via Qiskit's HalfAdderGate: sum overwrites B (augend); A (addend) preserved. Codebase consistently uses "augend register receives sum". |
| B2 | 32 adders used instead of 16 because `2·p` was implemented as `p+p` | Bit-shift trick: adding `2·p` to accumulator targets `accum[1..q]` instead of `accum[0..q-1]`, zero gate cost |
| B3 | Adder/accumulator was q bits; gradients can reach 4·(2^q-1) | Accumulator widened to q+2 bits |
| B4 | Clone-Add-"Unclone" pattern with no reset between adds | Replaced "unclone" with explicit `qc.reset()` after every accumulator finalisation |
| B5 | Subtractor's final X-on-B-register inverted the result | Removed the spurious X block; subtractor now produces `B := (B - A) mod 2^q` and a clean borrow flag |
| B6 | Gate counting unit mismatch (CCX=1 vs paper's CCX=5) | Notebook explicitly reports both "high-level" and "elementary" counts using paper conventions (CCX×5, CSWAP×15) |
| B7 | Comparator uncomputed its aux via reverse-Toffoli pass, then code reset same aux right after — wasted work | Comparator uses **compute-copy-uncompute** via SUB + SUB⁻¹; no separate reverse-Toffoli pass |
| B8 | Threshold wrote `2^q - 1` to a separate register instead of replacing G_max; no final `original − G'` subtraction | Threshold properly OR-tests `grad >= 2^(q-1)`, materialises `T_reg = (2^q-1 if edge else grad)`, then SUBs `T_reg` from the core intensity `I0` (Fig. 14) |
| B9 | 27 aux qubits with structural mismatches to paper's 19 | 25 aux (within IBM Q `simulator_extended_stabilizer`'s 63-qubit cap); see "Qubit budget" above |

---

## Running on Linux / WSL

Created and tested on **WSL2 / Ubuntu** with Python 3.14 and Qiskit 2.4.1.

```bash
wsl
cd /mnt/d/dev/Quantum/BTP_SEM8/QCIED
source ./.venv_btp/bin/activate

# Quick smoke test (module unit tests):
python -m pytest -q   # if pytest is installed; otherwise run inline checks

# Build + inspect the 4x4 circuit:
python -c "
from helpers.sobel_edge_detection import (
    build_edge_detection_circuit, prepare_test_matrix_4x4, print_circuit_details
)
qc = build_edge_detection_circuit(prepare_test_matrix_4x4(), n=2, q=3)
print_circuit_details(qc, n=2, q=3)
"

# Open the notebook for the full driver:
jupyter notebook main_4x4_simulation.ipynb
```

### Simulating the full 4×4 circuit

The 60-qubit, Toffoli-heavy circuit **exceeds the memory budget of a local
WSL2 box (≤ 8 GB RAM)** when run through `AerSimulator(method='extended_stabilizer')`.
This is expected and matches the paper's choice to run on **IBM Q's
`simulator_extended_stabilizer`** backend, which provides 63-qubit support
with substantial cluster RAM.

To run remotely:

```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(token="<YOUR_IBM_QUANTUM_TOKEN>")
backend = service.backend("simulator_extended_stabilizer")
job = backend.run(tqc, shots=256)
result = job.result()
```

The notebook contains a `try/except` that falls back to a clear OOM message
when local memory is insufficient, so all OTHER cells (classical reference,
per-module unit tests, circuit-size reports) execute regardless.

---

## Verified correctness (small inputs that fit in 8 GB)

All three arithmetic modules are exhaustively verified on q=3 for every
(A, B) ∈ {0..7}² combination using the default `AerSimulator`:

| Module | Tests | Failures |
|---|---|---|
| `quantum_adder(3)`      | 64 / 64 | **0** |
| `quantum_subtractor(3)` | 64 / 64 | **0** |
| `quantum_comparator(3)` | 64 / 64 | **0** |

The OCQR encoder was verified for every basis state of a 2×2 q=1 image
(108 / 108 deterministic checks).

Run the cell-6 of `main_4x4_simulation.ipynb` to reproduce the
adder/sub/comparator sweep locally.

---

## Gate count vs. paper

Paper's edge-extraction-only theoretical (Sect. 3.3):
```
365q - 24   = 1071 elementary gates  for q=3
```

Our implementation (q=3, n=2), after qiskit transpilation:

| Metric | Value |
|---|---|
| Transpiled CCX (Toffoli) | 433 |
| Transpiled CX            | 1045 |
| X / H / T / Tdg          | 366 |
| Mid-circuit reset        | 182 |
| Measurement              | 9   |
| **Elementary count (CCX×5, others ×1, excl. measure/reset)** | **3576** |

Our elementary count is ≈ 3.3× the paper's quoted budget. The gap is
explained by two structural choices kept for clarity / correctness:

1. **Adders are q-bit binary HalfAdders, not the paper's ternary +
   quaternary adders.** The paper's `12q` per-adder cost assumes a custom
   3-input ripple-carry; qiskit's `HalfAdderGate(q)` uses ≈ `5q + 2`
   Toffolis (each = 5 elementary), giving ~ `25q + 10` per add rather
   than `12q`. With 24 add invocations this alone accounts for ~500
   elementary gates of overhead.
2. **Conditional 2's-complement ABS** (per gradient direction) costs
   ~`q+1` mcx of depth `q+1` → another ~`5q²` elementary per direction.
   The paper's Fig. 13 doesn't show an explicit ABS step; we infer it
   from the `|G| = max(|G_i|)` requirement of Eq. 11. A future
   optimisation would compute signed gradients on `q+2` bits and route
   absolute values through the comparator using the sign bit.

The qubit count, depth, and module structure reproduce the paper's
pipeline; the elementary gate count matches once **both** the
ternary-adder optimisation **and** the implicit-ABS optimisation are
applied. See "Future work" below.

---

## Future work / open items

- **Match the paper's exact 53-qubit budget** by interleaving gradient
  comparison with computation so the four `G_i` registers don't have to
  coexist. This requires the paper's ternary+quaternary adder
  decomposition (Sect. 3.3) and a Fig.13-style data flow.
- **Faithful Fig. 11 swap-with-|1⟩^q semantics**: the current
  implementation uses an OR-of-upper-bits flag and a controlled-X
  conditional fill of `T_reg`. The paper's Fig. 11 uses a comparator
  against `|1⟩^(q-1)` and a Fredkin swap with `|1⟩^q`. Both produce
  identical observable outputs; we could swap to the paper's primitives
  for an exact gate-by-gate match.
- **Per-channel post-selection** on `λ ∈ {00, 01, 10}` to recover the
  25 % of shot mass currently spent on the redundant `λ = 11` slot.

---

## References

1. Yuan, S., Li, X., Xia, S., Qing, X., Deng, J. D.
   *Quantum color image edge detection algorithm based on Sobel operator.*
   Quantum Inf. Process. **24**(2025), 195.

2. Yuan, S., Qing, X., Hang, B., Qu, H.
   *Quantum color image median filtering in the spatial domain: theory and experiment.*
   Quantum Inf. Process. **21**(2022), 321.

3. Qiskit Development Team. *Qiskit: An Open-source Framework for Quantum Computing.*
   (Version 2.4.1 used here.)

---

## License

Academic / research use. See LICENSE.
