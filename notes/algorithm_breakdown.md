# Algorithm Breakdown — Quantum Color Image Edge Detection (Sobel)

Sources (all citations below refer to these):

- **[MAIN]** *Quantum color image edge detection algorithm based on Sobel operator* — Yuan, Li, Xia, Qing, Deng. Paper_markdown/Quantum_color_image_edge_detection_algo_based_on_Sobel_operator/.
- **[MF]** *Quantum color image median filtering in the spatial domain* — used for §2 encoding detail. Paper_markdown/Quantum_color_image_median_filtering_in_the_spatial_domain/.
- **[OCQR]** *An optimized quantum representation for color digital images* — Liu, Zhang, Lu, Wang, Wang (2018). Paper_markdown/OCQR_Encoding/.

Conventions:

- `q` = bits per color channel (intensity is in `[0, 2^q − 1]`).
- `n` = bits per coordinate axis (image is `2^n × 2^n`).
- All register names match the papers verbatim (`C_YX`, `λ`, `Y`, `X`, `G_x`, `G_y`, `G_45`, `G_135`, `G_max`, `G'`, `a_i`).
- "Reset" = the explicit reset operation introduced in [MF §2] (a box around `|0⟩`); it forcibly returns the qubit to `|0⟩` mid-circuit so it can be reused.

---

## 1. Quantum Encoding Scheme (how classical data maps to qubits)

### 1.1 OCQR representation [OCQR §3.1, MAIN Eq. 1, MF Eq. 1]

A color image of size `2^n × 2^n` with intensities `[0, 2^q − 1]` is stored as:

```latex
|I⟩ = (1 / √(2^(2n+1))) · Σ_{λ=0..3} Σ_{Y=0..2^n−1} Σ_{X=0..2^n−1}
        ( ⊗_{i=0..q−1} |C_YX^i⟩ ) |λ⟩ |YX⟩            (MAIN Eq. 1)
```

Registers and qubit counts:

| Register | Width | Role |
|---|---|---|
| `C` = `C_YX^{q−1} … C_YX^0` | `q` | Intensity of one color channel at position `(Y,X)`. One physical `q`-qubit register is shared across all `(λ,Y,X)` via entanglement. |
| `λ` = `λ_1 λ_0` | `2` | Channel index. `|00⟩ = R`, `|01⟩ = G`, `|10⟩ = B`, `|11⟩` = spare (unused; [OCQR §3.1]). |
| `Y` = `Y_{n−1}…Y_0` | `n` | Row coordinate. |
| `X` = `X_{n−1}…X_0` | `n` | Column coordinate. |

Total qubits to *store* a single OCQR image: `q + 2 + 2n` [OCQR §3.1, "the total number of qubits used in OCQR model is 2·n + q + 2"].

The intensity register is per *position+channel* slot of the superposition, not per pixel — the same `q`-qubit register holds different binary strings on different branches of the `|λ⟩|YX⟩` superposition.

### 1.2 Nine-image neighborhood representation [MF §2.2, MF Eq. 6]

Edge detection at `(Y,X)` requires the 3×3 neighborhood. The paper jointly encodes nine OCQR images that share the position `|YX⟩` and channel `|λ⟩` qubits:

```
|I⟩ = (1 / √(2^(2n+1))) · Σ_{λ} Σ_{Y} Σ_{X}
        |C_{Y,X}⟩ ⊗ |C_{Y−1,X}⟩ ⊗ |C_{Y−1,X+1}⟩ ⊗ |C_{Y,X+1}⟩
        ⊗ |C_{Y+1,X+1}⟩ ⊗ |C_{Y+1,X}⟩ ⊗ |C_{Y+1,X−1}⟩
        ⊗ |C_{Y,X−1}⟩ ⊗ |C_{Y−1,X−1}⟩
        ⊗ |λ⟩ |YX⟩                                   (MF Eq. 6)
```

Each of the nine `|C_{Y+dy,X+dx}⟩` is a `q`-qubit register → **9·q intensity qubits** for the nine-image bundle.

Each neighborhood image is a *circular shift* of the central image; out-of-bounds wrap around [MF §2.2 first paragraph]. The eight directions `(dy,dx) ∈ {−1,0,+1}^2 \ {(0,0)}` are obtained by shifting the central image by `(−dy, −dx)` (e.g. the "above" neighbor image is the central image shifted *down*).

### 1.3 Auxiliary qubits used only during preparation [MF §2.1, MAIN §3.2 last paragraph]

Four auxiliary qubits `a_0, a_1, a_2, a_3` are used during preparation (the "information transfer module") and **fully reset** before the gradient stage. They are then reused as the operational ancillas for adders/comparators downstream [MAIN §3.2 last paragraph: "After the image preparation, the auxiliary qubits are set to zero using a reset gate, and these four auxiliary qubits can be repeatedly utilized later"].

### 1.4 Encoding algorithm (Algorithm 1, [MF §2.1])

Pseudocode literally as in [MF Algorithm 1]:

```
for each row of the classical image:
    Step 1: transmit Y-coordinate information to a_3 (Toffoli/CNOT chain)
    for each pixel in that row:
        Step 2: a_3 and X coordinate → a_2 (Toffoli)
        for each channel λ ∈ {R, G, B}:
            Step 3: a_2 and λ → a_1 (Toffoli)
            Step 4: CNOT(a_1, C_i) for each intensity bit C_i that should be 1
            Reset a_0, a_1
        Reset a_2
    Reset a_3
```

Initial H gates: `H^⊗(2n+2)` on `Y, X, λ` to put position and channel in uniform superposition (preceding step 1) [MF Fig. 2, paragraph after Algorithm 1].

Preparation time complexity: `O((q+n)·2^{2n})` with 4 auxiliary qubits [MF Eq. 3, Table 1].

For the 9-image bundle: after step 4 sets the central pixel's intensity bits, additional CNOT gates copy/encode each neighbor's pixel value into the corresponding `C_{Y+dy,X+dx}^i` register from the same `a_1` control line, with the classical bit values determining which CNOTs are present [MF §2.2 last paragraph, MAIN Fig. 4].

---

## 2. Sub-circuits

For each sub-circuit below: **purpose, input qubits, output qubits, gates, ancilla usage**.

### 2.1 Quantum cloning module `U_c` [MAIN §3.1.1, Eq. 2, Fig. 5]

- **Purpose:** Copy a `q`-qubit register `|C⟩ = |C_{q−1}…C_0⟩` into a target register initialized to `|0⟩^⊗q`.
  ```
  U_c (|C⟩ |0⟩^⊗q) = |C⟩ |C⟩         (Eq. 2)
  ```
  (Bitwise computational-basis copy; not universal cloning.)
- **Inputs:** source `|C⟩` (`q` qubits), target `|0⟩^⊗q` (`q` qubits).
- **Outputs:** source unchanged, target = `|C⟩`.
- **Gates:** `q` CNOTs in parallel — `CNOT(C_i → target_i)` for `i = 0..q−1`.
- **Ancilla:** none.

### 2.2 Quantum adder module `ADD` [MAIN §3.1.2, Eq. 3, Fig. 6]

- **Purpose:** Ripple-carry add of two `q`-qubit values, producing a `(q+1)`-bit sum (top bit is the final carry).
  ```
  U_add |C_YX⟩ ⊗ |C_Y'X'⟩  =  |s_0 s_q … s_1⟩ ⊗ |C_Y'X'⟩     (Eq. 3)
  ```
  Output is stored back into the `C_YX` register's qubits **plus the carry ancilla bit**; the augend `C_Y'X'` is preserved.
- **Inputs:** addend `|C_YX⟩` (`q` qubits), augend `|C_Y'X'⟩` (`q` qubits), two carry ancillas `a_0, a_1` initialised to `|0⟩`.
- **Outputs:** sum register `|s⟩ = |s_0 s_q … s_1⟩` (uses the addend's `q` qubits plus the high carry bit; `(q+1)` bits total), augend preserved, the **other** carry ancilla reset to `|0⟩` (Fig. 6 shows a square-`|0⟩` reset on the bottom `a_1` line at the end).
- **Gates per bit position:** alternating Toffoli + CNOT pattern. From Fig. 6 for the 2-bit case: the two red dashed boxes are the "half-adder + full-adder" pair; gates are CNOT and Toffoli (CCX) only. Each bit position uses 2 Toffolis and 2 CNOTs in [MAIN] (complexity `12q` [MAIN §3.3] = 2 Toffoli + 2 CNOT ≈ 12 NCV gates per bit when a Toffoli is counted at NCV cost 5 plus one CNOT cost 1, but the exact decomposition is unspecified — see implementation note below).
- **Ancilla:** **2 qubits total** (`a_0`, `a_1`), **alternating carry** — each bit position uses one of them and resets the other; both end the gate clean at `|0⟩`. This is the property that lets the same 2-qubit `a_0/a_1` pair serve adders of arbitrary `q`. [MAIN §3.1.2: "`|a_0⟩` and `|a_1⟩` are two auxiliary qubits with an initial value of `|0⟩` used as carry bits throughout the adder"].

*Implementation note.* The 2-bit pattern in Fig. 6 must be generalised to `q` bits before implementation; the paper does **not** give an explicit `q`-bit circuit diagram. Standard Qiskit `HalfAdderGate` is **not** a substitute because it needs `~q−1` carry ancillas; the paper's design recycles exactly 2 carries [auxiliary-budget memory]. This is flagged for a separate design step.

### 2.3 Quantum subtractor module `SUB` [MAIN §3.1.3, Eq. 4, Fig. 7]

- **Purpose:** Two's-complement difference of two `q`-qubit values.
  ```
  U_sub |C_YX⟩ ⊗ |C_Y'X'⟩  =  |s_{n−1}…s_0⟩ ⊗ |C_Y'X'⟩       (Eq. 4)
  ```
  Output replaces the minuend register; subtrahend preserved.
- **Inputs:** minuend `|C_YX⟩` (`q`), subtrahend `|C_Y'X'⟩` (`q`), two borrow ancillas `a_0, a_1` (`|0⟩`).
- **Outputs:** difference in the minuend register (`q` qubits, with top bit acting as a sign/borrow indicator), subtrahend preserved, both ancillas reset to `|0⟩` (Fig. 7 shows two square-`|0⟩` reset boxes at the end of `a_0` and `a_1`).
- **Gates:** X (NOT) gates flip bits to form two's complement, plus CNOT and Toffoli — see Fig. 7. Two red dashed-box stages mirror the adder structure.
- **Ancilla:** **2 qubits total**, alternating borrow (same trick as ADD).

The paper does not address negative results explicitly; gradients are accumulated as `(sum of positives) − (sum of negatives)`, both non-negative `(q+2)`-bit numbers, so the SUB output is the magnitude of `G_dir` *only when* positives ≥ negatives. The max module (§2.6) then operates on these magnitudes. The threshold step (§2.7) compares this magnitude to `2^(q−1)`. (The paper is silent on the negative case; the simulation results in MAIN §4 suggest the algorithm treats it as the magnitude implicitly via the comparator's ordering. Flag for implementation review.)

### 2.4 Quantum comparator module `Com` [MAIN §3.1.4, Fig. 8, ref. 37 (Xia et al. 2019)]

- **Purpose:** Compare two `q`-qubit values; set a single flag qubit.
  ```
  Com(|C_YX⟩, |C_Y'X'⟩) → |C_out⟩
      C_out = 1  if  C_YX < C_Y'X'
      C_out = 0  if  C_YX ≥ C_Y'X'
  ```
  Both input registers are preserved (Fig. 8 shows them unchanged on the output side).
- **Inputs:** `|C_YX⟩` (`q`), `|C_Y'X'⟩` (`q`), one ancilla `|0⟩` for an intermediate signal, and one ancilla `|0⟩` for `C_out`.
- **Outputs:** `C_out` (1 qubit), both inputs unchanged, intermediate ancilla returned to `|0⟩` (Fig. 8 shows the third line — initially `|0⟩` — emerging again as `|0⟩`).
- **Gates:** From Fig. 8 (3-bit example): a symmetric MSB-to-LSB structure of CNOTs and Toffolis, with two CNOTs flanking each bit position to convert inputs, and Toffolis with open and filled controls cascading toward `C_out`. Inputs `C^i_YX` are bracketed by CNOTs that flip them and undo the flip (preserving inputs); the inner Toffolis write into the intermediate ancilla and then `C_out`. Open circles (negative controls) appear at the `C^1_YX`/`C^1_Y'X'` row — these are MSB ordering controls.
- **Ancilla:** **2 qubits** within the comparator (`C_out` plus one intermediate); the intermediate is uncomputed inside the module.

### 2.5 Quantum controlled swap module `Swap` [MAIN §3.1.5, Fig. 9]

- **Purpose:** Conditional swap of two `q`-qubit registers controlled by `C_out`.
  ```
  if C_out = 1: |C_YX⟩|C_Y'X'⟩ → |C_Y'X'⟩|C_YX⟩
  if C_out = 0: unchanged
  ```
- **Inputs:** `C_out` (1), `|C_YX⟩` (`q`), `|C_Y'X'⟩` (`q`).
- **Outputs:** possibly swapped registers; `C_out` unchanged.
- **Gates:** `q` Fredkin (CSWAP) gates in parallel, all sharing `C_out` as control. Fig. 9 shows `CSWAP(C_out; C^i_YX, C^i_Y'X')` for `i = q−1 … 0`.
- **Ancilla:** none.

### 2.6 Maximum value calculation module `QC` [MAIN §3.1.6, Fig. 10]

- **Purpose:** Place `max(G_x, G_y, G_45, G_135)` on the top wire.
- **Inputs:** four `q`-qubit gradient registers `|G_x⟩, |G_y⟩, |G_45⟩, |G_135⟩`, one shared ancilla `|0⟩`.
- **Outputs:** top register = `|G_max⟩`; the other three wires hold the remaining values in unspecified order (they are not used downstream).
- **Sequential structure** (read off Fig. 10, top-to-bottom inputs `G_x, G_y, G_45, G_135`, shared single-bit ancilla at the bottom):
  1. `Com(G_x, G_45)` → writes flag to ancilla.
  2. `Swap` controlled by ancilla on `(G_x, G_45)`; reset ancilla.
  3. `Com(G_x, G_y)` → flag.
  4. `Swap` on `(G_x, G_y)`; reset ancilla.
  5. `Com(G_x, G_135)` → flag.
  6. `Swap` on `(G_x, G_135)`; reset ancilla.

  After step 6 the top wire (`G_x` slot) holds the maximum of the four; the other three slots retain the remaining values.

  *Note.* Fig. 10 indeed shows three `Com`+`Swap` pairs separated by `|0⟩` reset boxes on a single ancilla wire — i.e. it's a serial linear-scan max, not a tournament tree. The figure-description markdown's "tournament" wording is incorrect.
- **Ancilla:** **1 qubit**, reused across all three comparisons via reset.

### 2.7 Quantum threshold module `U_T` [MAIN §3.1.7, Fig. 11]

- **Purpose:** Produce the binary edge value `G'`: `2^q − 1` if `G_max ≥ 2^(q−1)`, else `0`. (Paper: "when `G_max` is larger, it is set to `2^q − 1`, otherwise, it is set to zero".)
- **Inputs (top-to-bottom in Fig. 11):**
  - `|1⟩^⊗q` — constant `2^q − 1` (the "all-ones" output value)
  - `|G_max⟩` — `q` qubits, output of QC
  - `|1⟩^⊗(q−1)` — constant `2^(q−1)` (the threshold encoded as the top bit `1` followed by `q−1` zeros; the figure labels this `q−1` qubits at `|1⟩` but the operational meaning per text is "encode the threshold `2^(q−1)`"; see implementation note below).
  - One ancilla `|0⟩` for `C_out` (becomes input control of the swap).
- **Sequence:**
  1. `Com(|G_max⟩, threshold)` writes `C_out` (= 1 iff `G_max < threshold`).
  2. Reset `C_out`'s intermediate ancilla per the comparator's internal cleanup.
  3. Controlled-SWAP between the `|1⟩^⊗q` top register and `|G_max⟩` middle register, controlled on the **comparator outcome**. Per the paper text: when `G_max ≥ threshold`, swap so that the middle wire (the `G'` output) gets `2^q − 1`; when `G_max < threshold`, instead drive the middle wire to `0`. Fig. 11 shows the swap with a hollow (negative) control marker — i.e. the swap fires when the comparator result indicates `G_max ≥ threshold` (`C_out = 0`).
- **Output:** `G'` on the middle wire — `|2^q − 1⟩` for edge pixels, `|0⟩` otherwise.
- **Ancilla:** the comparator's `C_out` (1 qubit) plus its internal one; the constant registers (`|1⟩^⊗q` and `|1⟩^⊗(q−1)`) are not ancillas — they are *initialized* constants. After the swap they may end in different states (Fig. 11 shows the top wire output as the swapped value), which is fine because they are not used afterward.

*Implementation note.* Fig. 11 labels the bottom register as `|1⟩^(q−1)` — `(q−1)` qubits set to `|1⟩` means the value `2^(q−1) − 1`, not `2^(q−1)`. The text says the threshold is `2^(q−1)`, which is `1` followed by `q−1` zeros (a single `|1⟩` MSB and `q−1` `|0⟩`s). This is a notational ambiguity in the paper. The most defensible reading from the text is "threshold value `2^(q−1)`"; the comparator should be sized to `q` bits with both inputs zero-padded consistently. Flag for verification at implementation time.

---

## 3. Connecting the Sub-circuits

### 3.1 Gradient calculation module `U_G` [MAIN §3.2, Fig. 13]

Inputs: the nine neighborhood registers from §1.2 — `|C_{Y,X}⟩, |C_{Y−1,X−1}⟩, |C_{Y−1,X}⟩, |C_{Y−1,X+1}⟩, |C_{Y,X−1}⟩, |C_{Y,X+1}⟩, |C_{Y+1,X−1}⟩, |C_{Y+1,X}⟩, |C_{Y+1,X+1}⟩`.

Outputs: four `q`-qubit (actually `(q+2)`-bit; see below) registers `|G_x⟩, |G_y⟩, |G_45⟩, |G_135⟩`.

Gradient definitions [MAIN Eqs. 7–10]:

```
G_x   = p(Y−1,X+1) + 2·p(Y,X+1) + p(Y+1,X+1)
       − p(Y−1,X−1) − 2·p(Y,X−1) − p(Y+1,X−1)             (Eq. 7)
G_y   = − p(Y−1,X−1) − 2·p(Y,X−1) − p(Y+1,X−1)
       + p(Y−1,X+1) + 2·p(Y,X+1) + p(Y+1,X+1)             (Eq. 8)
G_45  = − p(Y,X−1) − 2·p(Y+1,X−1) − p(Y+1,X)
       + p(Y−1,X) + 2·p(Y−1,X+1) + p(Y,X−1)               (Eq. 9; sic — both ±p(Y,X−1) appear in source)
G_135 = − p(Y−1,X) − 2·p(Y−1,X−1) − p(Y,X−1)
       + p(Y+1,X) + 2·p(Y+1,X+1) + p(Y+1,X+1)             (Eq. 10; sic — duplicate p(Y+1,X+1))
final: G = max(|G_x|, |G_y|, |G_45|, |G_135|)             (Eq. 11)
```

`G_x` and `G_y` in the paper are duplicates by sign — Eq. 7 and Eq. 8 share the same six neighbours `(Y−1,X±1), (Y,X±1), (Y+1,X±1)` and the same coefficients with signs swapped, so `G_y = −G_x` as written. This is a transcription anomaly in the source; the canonical Sobel operator has `G_y` use the top vs bottom rows. **Treat Eqs. 7–10 as authoritative for this implementation per the paper, but flag this anomaly** — the *masks in Fig. 12* (cited in the same section) are the conventional ones and would give the canonical `G_y` over rows. The implementation should follow Fig. 12 masks, with Eq. 7–10 used as cross-check.

The "weighted" coefficients `2·p` are realised as `p + p` — i.e. each `2·p` term is two adder calls with the same operand. The cloning module `U_c` duplicates `p` so it can be added to two partial sums simultaneously (see Fig. 13's two `U_c` blocks at the input).

Per [MAIN §3.3], `U_G` uses:
- 16 adders (`Add`),
- 4 subtractors (`Sub`),
- 2 cloning modules (`U_c`).

Block-level data flow (read off Fig. 13):
1. Replicate `|C_{Y,X+1}⟩` and `|C_{Y,X−1}⟩` (the "centre-column" rows used in two gradient computations each) with two `U_c` modules.
2. Run a cascade of `Add`s building up the **positive partial sum** for each gradient (e.g., for `G_x`: `p(Y−1,X+1) + p(Y,X+1) + p(Y,X+1) + p(Y+1,X+1)` — note `2·p` realised by adding the *clone* of `p(Y,X+1)`).
3. Run another cascade of `Add`s building the **negative partial sum**.
4. `Sub`tract the negative sum from the positive sum → `G_dir`.
5. One intermediate result is reset (square-`|0⟩` box in Fig. 13) before the second copy-and-add pass for the next gradient.

Bit-width growth: each `Add` of `q`-bit values yields a `(q+1)`-bit result; six pixels accumulated produces at most `6·(2^q − 1) < 2^(q+3)`, so the gradient register width is `q + 3` in the worst case. The paper labels its gradient registers `q`-wide in Fig. 10 and elsewhere — this is another transcription simplification. In implementation, allocate `(q + ⌈log2 8⌉) = q + 3` bits for each gradient register; the maximum-of-four and threshold modules then operate at width `q + 3` (with the threshold value `2^(q−1)` also padded). Flag.

### 3.2 Overall edge-detection circuit (Fig. 14)

Top-to-bottom register layout in Fig. 14 (left side of figure, the `|0⟩` block of input wires):

| Register block | Width | Initial state |
|---|---|---|
| Nine intensity registers `C_{Y−1,X−1}, …, C_{Y+1,X+1}` | `9q` | `|0⟩^⊗9q` |
| `λ` | `2` | `|0⟩^⊗2` then H |
| `Y` | `n` | `|0⟩^⊗n` then H |
| `X` | `n` | `|0⟩^⊗n` then H |
| `a` (working ancilla pool) | the paper labels this **19** | `|0⟩^⊗19` |

Pipeline (sequential blocks in Fig. 14):

```
[ Preparation of Quantum Color Images and their Neighborhood ]
        ↓ (nine |C_{Y+dy,X+dx}⟩ registers prepared; |λ⟩,|YX⟩ in superposition)
[ Quantum Gradient Calculation Module  U_G ]   (§3.1 here)
        ↓ (outputs |G_x⟩, |G_y⟩, |G_45⟩, |G_135⟩)
[ Maximum Value Calculation Module  QC ]      (§2.6 here)
        ↓ (outputs |G_max⟩ on top wire)
[ X gate on one ancilla qubit ]                (sets the threshold-comparator's `|0⟩` ancilla to `|1⟩`, used as part of the |1⟩^q / |1⟩^(q−1) constants entering U_T)
        ↓
[ Quantum Thresholding Module  U_T ]           (§2.7 here)
        ↓
|G⟩  — the binary edge map
```

Final measurement: measure `Y`, `X`, `λ`, and the `G'` output register (Fig. 14 labels the final output `|G⟩`). Pixel `(Y,X)` of channel `λ` is an edge iff the measured `G'` string equals `2^q − 1` [MAIN §3.2 last paragraph].

### 3.3 Output → input register wiring through the pipeline

| Producer | Output register | Consumer | Consumer input slot |
|---|---|---|---|
| Preparation | `\|C_{Y+dy,X+dx}⟩` × 9 | `U_G` | nine pixel inputs |
| `U_G` | `\|G_x⟩, \|G_y⟩, \|G_45⟩, \|G_135⟩` | `QC` | four gradient inputs |
| `QC` | top wire = `\|G_max⟩` | `U_T` | middle wire (`G_max` input) |
| Constants `\|1⟩^q`, `\|1⟩^(q−1)` | initialized inside `U_T` | `U_T` | top and bottom wires |
| `U_T` | middle wire = `\|G'⟩` | measurement | — |

Within `U_G`:
- `U_c#1`: copies `|C_{Y,X+1}⟩` (or `|C_{Y−1,X+1}⟩` per the symmetry of Fig. 13) so the same pixel can be summed twice (`2·p` weight).
- `U_c#2`: same purpose for the negative-sum side.
- All `Add`s and the final `Sub` are pipelined per gradient: positive accumulator → negative accumulator → `Sub` → gradient register.
- One intermediate qubit is **reset** between the four gradient computations (Fig. 13 shows a `|0⟩` box in the middle of the circuit) so its qubit can be reused.

---

## 4. Ancilla Inventory (the `a` register, width 19 per Fig. 14, or 20 per MAIN §4)

Per [MAIN §3.2 last paragraph], during the **gradient stage** (after preparation has released its 4 ancillas):

| Use | Count | Notes |
|---|---|---|
| Carry/borrow ancillas for the 16 `Add`s and 4 `Sub`s | 8 + 8 = 16? | "eight auxiliary qubits are needed to encode eight quantum ternary adders. Another eight auxiliary qubits are required to encode eight quantum quaternary adders." — this counts ancillas as needed at each adder size step; in practice 2 ancillas per adder suffice if alternating (see §2.2), so the 16 figure in MAIN §3.2 is **the worst-case live-set across the pipeline**, not the per-adder requirement. |
| Extra ancilla for second `U_c` copy module | 1 | "an additional auxiliary qubit is necessary to encode the copy bit to replicate the output of a three-qubit adder." |
| `QC` shared flag qubit | 1 | "In the maximum value calculation module, one auxiliary qubit is needed as the result bit to control the subsequent swap module." Reused 3× via reset. |
| Per-module ancilla for adder/sub/comparator basic operation | 1 | "Basic quantum operation modules such as quantum adders, quantum subtractors, and quantum comparators still require one auxiliary qubit to complete the operation." (Already covered by the carry/borrow pair above.) |
| Threshold `C_out` ancilla | 1 | The `\|0⟩` line in Fig. 11 (and the X gate before `U_T` initialises one of the constant lines). |

[MAIN §4] states the actual 4×4 simulation uses **20 ancillas** in total (the `(6q+2)` budget at `q=3` = 20). Fig. 14 labels the ancilla bus width "19" — discrepancy noted; treat **20** as the authoritative number ([MAIN §4] is the simulation-grounded source).

For the 4×4 case [MAIN §4]:
- position `2n = 4`
- channel `λ = 2`
- 9 intensity registers × `q=3` = 27
- ancillas = 20
- **total = 53 qubits**, simulated on `simulator_extended_stabilizer` (63-qubit cap).

For general `q`, the **`6q + 2`** ancilla budget [auxiliary-budget memory; consistent with `(2 per adder) × 2 alternating + (q · 4)` accumulator slots and a 2-bit shared carry] is the design target:
- `4q` qubits — accumulators for `G_x, G_y, G_45, G_135` (locked from when each is written until the QC step consumes it);
- `q` qubits — `clone` workspace;
- `q` qubits — `neg_accum` workspace;
- `2` qubits — alternating carry/borrow pair.

**Uncomputation points** in the pipeline:
1. After preparation: reset `a_0..a_3` (the four preparation ancillas) so they become part of the working pool.
2. Inside `U_G`: one `|0⟩` reset box mid-circuit (Fig. 13) — the intermediate sum's carry qubit returns to `|0⟩` before the next gradient's adds start.
3. Inside `QC`: after each `Com`+`Swap` pair, reset the shared flag ancilla (`|0⟩` boxes in Fig. 10, three times).
4. Inside `ADD`/`SUB`: the alternating-carry trick keeps both carry ancillas at `|0⟩` at the end of each `q`-bit operation.
5. Inside `Com`: the intermediate signal ancilla is uncomputed by symmetric CNOT/Toffoli pairs (Fig. 8 — same controls appearing on both sides of the central Toffolis).
6. Inside `U_T`: the comparator's internal ancilla is uncomputed within `Com`; `C_out` itself remains entangled with the swap outcome and is *not* uncomputed — but the threshold module is the last operation before measurement, so this is fine.

---

## 5. Step-by-step Algorithm (numbered, top-level)

For an input classical color image of size `2^n × 2^n` with channels in `[0, 2^q − 1]`:

1. **Allocate registers.** Nine intensity registers `C_{Y+dy,X+dx}` of width `q` each (total `9q`), channel `λ` (2), coordinates `Y` (`n`) and `X` (`n`), ancilla pool `a` of width `6q + 2` (per design target; the paper-stated 19 / measured 20 are special cases). Initialise all to `|0⟩`.
2. **Hadamard the addressing qubits.** Apply `H` to every qubit of `λ`, `Y`, `X` — creating uniform superposition over `(λ, Y, X)`.
3. **Encode the central image** following [MF Algorithm 1] (`Algorithm 1`, §1.4 above): for each row, transfer Y to `a_3`; for each pixel, transfer Y+X to `a_2`; for each channel `λ`, transfer Y+X+λ to `a_1`, then CNOT(`a_1`, `C_i`) for each intensity bit `C_i` that should be 1. Reset `a_0..a_3` as per the algorithm's reset points.
4. **Encode the eight neighborhood images.** After each pixel's central-image encoding within Step 3, append the additional CNOTs from `a_1` to each `C_{Y+dy,X+dx}^i` matching the classical bit value at the *shifted* pixel position (the row-shift implements the circular shift of [MF §2.2]).
5. **Reset preparation ancillas.** After the full image is prepared, reset `a_0..a_3` — they re-enter the ancilla pool as the working carry/borrow pair.
6. **Compute `U_G` (gradient calculation), Fig. 13:**
   - 6a. `U_c #1`: clone `|C_{Y,X+1}⟩` into a workspace register.
   - 6b. Build positive partial sum for `G_x` via `Add` cascade: `p(Y−1,X+1) + p(Y,X+1) + clone(p(Y,X+1)) + p(Y+1,X+1)` → accumulator register `pos`.
   - 6c. Build negative partial sum for `G_x` via `Add` cascade: `p(Y−1,X−1) + p(Y,X−1) + clone(p(Y,X−1)) + p(Y+1,X−1)` → accumulator register `neg` (requires the second `U_c` for `p(Y,X−1)`).
   - 6d. `Sub`: `pos − neg` → write into the `G_x` output register; reset the carry/borrow ancillas.
   - 6e. Reset the intermediate carry qubit (`|0⟩` box in Fig. 13).
   - 6f. Repeat 6a–6e for `G_y`, `G_45`, `G_135` (per Eqs. 7–10 / Fig. 12 masks). Each accumulator register `pos` and `neg` is the same physical `q`-bit pool reused; the four output `G_dir` registers are *not* reused — they remain occupied through the rest of the algorithm.
7. **Compute `QC` (max of four), Fig. 10:**
   - 7a. `Com(G_x, G_45)` → flag ancilla.
   - 7b. `Swap(G_x, G_45)` controlled on flag; reset flag.
   - 7c. `Com(G_x, G_y)` → flag.
   - 7d. `Swap(G_x, G_y)` controlled on flag; reset flag.
   - 7e. `Com(G_x, G_135)` → flag.
   - 7f. `Swap(G_x, G_135)` controlled on flag; reset flag.
   - After 7f, register that started as `G_x` holds `G_max`.
8. **Prepare threshold-module constants.** Apply X gates to qubits that should be `|1⟩` (Fig. 14 shows one X gate inline between QC and `U_T`; this initialises the `|1⟩^⊗q` "all-ones" register and the `|1⟩` MSB of the threshold register).
9. **Apply `U_T` (threshold), Fig. 11:**
   - 9a. `Com(G_max, 2^(q−1))` → `C_out`.
   - 9b. Controlled-swap between the `|1⟩^⊗q` register and `G_max` register, controlled on `C_out` per the polarity in Fig. 11. The middle wire (`G_max` slot) becomes `G'` = `2^q − 1` for edges, `0` otherwise.
10. **Measure.** Measure `Y`, `X`, `λ`, and the `G'` register. A measurement outcome `(y, x, λ, 2^q − 1)` indicates pixel `(y, x)` of channel `λ` is an edge; outcome `(y, x, λ, 0)` indicates non-edge.

---

## 6. Key Equation Index

| Equation | Source | What it defines |
|---|---|---|
| Eq. 1 | MAIN §2 | OCQR state `|I⟩` |
| Eq. 2 | MAIN §3.1.1 | Cloning `U_c (|C⟩|0⟩) = |C⟩|C⟩` |
| Eq. 3 | MAIN §3.1.2 | Adder unitary `U_add` |
| Eq. 4 | MAIN §3.1.3 | Subtractor unitary `U_sub` |
| Eq. 5 | MAIN §3.2 | Classical Sobel masks `G_x, G_y` |
| Eq. 6 | MAIN §3.2 (also MF §2.2) | Diagonal masks `G_45, G_135` (MAIN) / 9-image joint state (MF) |
| Eq. 7 | MAIN §3.2 | `G_x` from pixel positions |
| Eq. 8 | MAIN §3.2 | `G_y` from pixel positions |
| Eq. 9 | MAIN §3.2 | `G_45` from pixel positions |
| Eq. 10 | MAIN §3.2 | `G_135` from pixel positions |
| Eq. 11 | MAIN §3.2 | `G = max(|G_x|, |G_y|, |G_45|, |G_135|)` |
| MF Eq. 1 | MF §2.1 | OCQR (median-filtering paper's restatement) |
| MF Eq. 6 | MF §2.2 | Nine-image joint state |
| OCQR Eq. 3 | OCQR §3.1 | OCQR full state with all four `λ` channels and intensities |
| OCQR Eq. 6 | OCQR §3.2 | Preparation operator step 1 `U_1 = I^⊗(q+2) ⊗ H^⊗(2n)` |
| OCQR Eq. 11 | OCQR §3.2 | Preparation operator step 2 `U_2 = Π_{y,x} U_{yx}` |

| Figure | Source | Subject |
|---|---|---|
| Fig. 1 | MAIN | 4×4 example image |
| Fig. 2 | MAIN | Eight neighbourhood images |
| Fig. 3 | MAIN | Pixel preparation circuit (one position) |
| Fig. 4 | MAIN | Nine-image preparation circuit (one position) |
| Fig. 5 | MAIN | `U_c` cloning |
| Fig. 6 | MAIN | 2-bit `ADD` |
| Fig. 7 | MAIN | 2-bit `SUB` |
| Fig. 8 | MAIN | 3-bit `Com` |
| Fig. 9 | MAIN | `Swap` |
| Fig. 10 | MAIN | `QC` (max of four) |
| Fig. 11 | MAIN | `U_T` (threshold) |
| Fig. 12 | MAIN | Sobel masks (4 directions) |
| Fig. 13 | MAIN | `U_G` (gradient) |
| Fig. 14 | MAIN | Overall edge-detection circuit |
| Fig. 15 | MAIN | 4×4 input/output visual |
| MF Fig. 2 | MF | OCQR preparation circuit detail |
| MF Fig. 3 | MF | Nine neighbourhood images (circular shift) |
| MF Fig. 4 | MF | Nine-image preparation circuit |

---

## 7. Flagged Ambiguities / Anomalies (for implementation decisions)

These are things the source text underspecifies or appears to contain transcription errors in:

1. **Eqs. 7 & 8** as transcribed make `G_y = −G_x`. The conventional Sobel `G_y` uses the top/bottom rows. Follow the **masks of Fig. 12** rather than the textual Eqs. 7–10 if they conflict.
2. **Eq. 9 has `±p(Y,X−1)` twice** (transcription).
3. **Eq. 10 has `p(Y+1,X+1)` twice** (transcription).
4. **Adder gate count vs Fig. 6.** Fig. 6 shows only the 2-bit case. The generalisation to `q` bits is implied but not drawn; the paper's `12q` complexity bound and the 2-ancilla alternating-carry property are the constraints to satisfy.
5. **Subtractor sign**. The paper does not say how negative intermediate results are handled. Since `max(|G_x|,...)` is the final quantity, the subtractor's output likely needs to be the absolute difference — but the paper's `Sub` is signed. The most consistent reading: each `G_dir` register stores the *signed* sum and the comparator's behaviour on these signed values yields the correct max-magnitude *only by accident* of the operand ordering. **This must be verified by simulation against a classical reference** before relying on it.
6. **Threshold register width** in Fig. 11 is labelled `(q−1)` qubits all `|1⟩`, which encodes `2^(q−1) − 1`, not `2^(q−1)`. The text says the threshold is `2^(q−1)`. Resolve by encoding the threshold as a `q`-bit register: `|1⟩|0⟩^⊗(q−1)` (MSB only), and matching `G_max` width.
7. **Ancilla width in Fig. 14 is 19, in MAIN §4 it is 20.** Use 20 (the simulation-grounded number) and the `6q+2` general formula.
8. **Gradient register width.** Six pixels of `q`-bit values sum to ≤ `8·(2^q − 1)` → needs `q + 3` bits, not `q`. Allocate accordingly.
9. **QC structure** in Fig. 10 is *serial* (three `Com`+`Swap` pairs sharing a single reset ancilla), not parallel/tournament. The fig-description markdown's "tournament" wording does not match Fig. 10.
