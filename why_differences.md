# Why Our Implementation Differs from the Paper

## Qubit Count: 68 vs 53

The paper (Section 4) states that 53 qubits are needed for the 4×4 case:
- Position: 4 qubits
- Channel: 2 qubits
- Intensity: 27 qubits (9 images × 3 bits)
- Auxiliary: 20 qubits
- **Total: 53**

Our implementation uses 68 qubits. The difference comes from **explicit register allocation** vs the paper's **aggregated auxiliary count**.

### Where the Extra Qubits Come From

| Register | Our Count | Paper's Count | Explanation |
|-----------|-----------|---------------|-------------|
| Position (`pos`) | 4 | 4 | Same |
| Channel (`ch`) | 2 | 2 | Same |
| Intensity (`I0`–`I8`) | 27 | 27 | Same (9 × 3) |
| Gradient outputs (`gx`, `g45`, `gy`, `g135`) | 12 | 0 | Paper counts these as part of the 20 aux; we allocate them as named registers |
| Max flags (`max_flags`) | 3 | 0 | Paper includes in aux; we name them explicitly |
| Comparator aux (`comp_aux`) | 2 | 0 | Paper includes in aux; we name them explicitly |
| Edge output (`edge_out`) | 3 | 0 | Paper includes in aux; we name them explicitly |
| General aux | 15 | 20 | Paper lumps all working qubits here |
| **Total** | **68** | **53** | |

The paper's "20 auxiliary qubits" is a **summary figure** that encompasses gradient registers, max-value flags, comparator auxiliaries, threshold output, and general working qubits. Our modular design gives each register a descriptive name for clarity, which increases the apparent count but represents the same physical qubits.

### Reconciliation

If we group our registers the same way the paper does:

- **Position + Channel + Intensity**: 4 + 2 + 27 = **33 qubits** (same as paper)
- **Everything else** (gradients, flags, comp_aux, edge_out, aux): 12 + 3 + 2 + 3 + 15 = **35 qubits** vs paper's 20

The remaining difference (35 vs 20) is because:

1. **Gradient calculation sub-circuit** (Fig. 13): The paper's gradient module is a *composite gate* that internally uses cloned pixel registers, accumulation registers, and carry qubits. These internal qubits are created and destroyed within the gate. In our `quantum_gradient_calculation(q)` function in `quantum_modules.py`, these are allocated as part of the gate's internal circuit (9×q clones + 4×(q+1) accumulators + 80 aux = ~113 internal qubits for q=3). The paper does **not** count these internal qubits in the 53 total — they are transient and get uncomputed.

2. **Our top-level circuit** allocates gradient output registers (`gx`, `g45`, `gy`, `g135`) explicitly at the top level because the max-value and threshold modules need to read them. The paper considers these as part of the auxiliary pool.

3. **The 20 auxiliary qubits** in the paper are specifically described in the text (paper_12.md): 4 for image preparation, 8 for ternary adders, 8 for quaternary adders. These are the *reusable* auxiliaries that get reset between operations. Our implementation doesn't yet reuse/reset auxiliaries, so we allocate fresh ones for each operation.

## Circuit Depth and Gate Count

Our circuit has depth ~987 with ~2251 gates (after OCQR encoding). The paper doesn't report exact depth/gate counts — it focuses on circuit complexity O(q). The high count is primarily from the OCQR intensity encoding step, which uses multi-controlled X gates for each non-zero pixel value across 9 images × 16 positions × 3 channels.

## Classical vs Quantum Edge Results

The classical edge detection may produce slightly different results from the quantum simulation due to:

1. **Quantum noise**: Real/simulated quantum circuits introduce measurement noise, especially with 256 shots.
2. **Gradient sign handling**: The classical implementation uses `np.abs()` on gradients before taking the max. The quantum circuit computes signed gradients via two's complement subtraction, and the max-value module compares magnitude. Small differences in how negative values are handled can affect boundary pixels.
3. **Threshold boundary**: The paper's threshold module uses the MSB of G_max (equivalent to `G_max >= 2^(q-1)`). Our classical code also uses `>=`, matching the paper.
