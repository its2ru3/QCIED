# TODO — Audit of `helpers/*_new.py` vs `notes/algorithm_breakdown.md`

Source of truth: `notes/algorithm_breakdown.md` **plus the resolutions in §0 below** — when the two disagree, §0 wins. Files audited (read-only): `helpers/ocqr_encoding_new.py`, `helpers/quantum_modules_new.py`, `helpers/sobel_edge_detection_new.py`.

Severity legend: **[BLOCKER]** = wrong output guaranteed; **[BUG]** = wrong in some inputs / nontrivially off-spec; **[DEVIATION]** = differs from paper but might still produce correct numbers; **[CLEANUP]** = dead code / sloppy structure; **[HALFADDER]** = location of `HalfAdderGate` use (replacement site).

---

## 0. Decisions on the breakdown's flagged anomalies

These pin the open questions in `notes/algorithm_breakdown.md` §7 to concrete implementation rules. **The implementation MUST follow these decisions verbatim.** Paper section refs are kept so every rule remains traceable.

### 0.1 Gradients — follow Fig. 12 masks; disregard Eqs. 7–10 textual transcription

The textual Eqs. 7–10 in [MAIN §3.2] are buggy (transcription errors per breakdown Flags #1–#3). **Authority: Fig. 12 masks [MAIN §3.2].** Concrete `GRAD_EQS` per the image-index map of `prepare_neighborhood_images` (after the §1.1 circular-shift fix):

| Direction | Mask source | Positive terms | Negative terms |
|---|---|---|---|
| `G_x` | Fig. 12b (vertical) | `p(Y−1,X+1) + 2·p(Y,X+1) + p(Y+1,X+1)` | `p(Y−1,X−1) + 2·p(Y,X−1) + p(Y+1,X−1)` |
| `G_y` | Fig. 12c (horizontal) | `p(Y+1,X−1) + 2·p(Y+1,X) + p(Y+1,X+1)` | `p(Y−1,X−1) + 2·p(Y−1,X) + p(Y−1,X+1)` |
| `G_45` | Fig. 12d (+45°) | `p(Y−1,X) + 2·p(Y−1,X+1) + p(Y,X+1)` | `p(Y,X−1) + 2·p(Y+1,X−1) + p(Y+1,X)` |
| `G_135` | Fig. 12e (+135°) | `p(Y,X+1) + 2·p(Y+1,X+1) + p(Y+1,X)` | `p(Y−1,X) + 2·p(Y−1,X−1) + p(Y,X−1)` |

Confirmed: the existing `GRAD_EQS` table in `sobel_edge_detection_new.py:92–97` already matches these masks exactly (verified by re-deriving index tuples against `prepare_neighborhood_images`'s shift list). **Carry that table over to the new implementation unchanged.**

### 0.2 Adder — alternating-carry ripple, exactly 2 recycled ancillas

Per breakdown §2.2 and [MAIN §3.1.2]: implement the `q`-bit adder as a ripple-carry chain whose two ancillas (`a_0`, `a_1`) are used in alternation across bit positions and both end at `|0⟩`. This is the only construction that hits the `12q` complexity target and respects the `6q + 2` ancilla bound for general `q`.

- Provisional `HalfAdderGate` is acceptable **only** for Phase 1 prototyping while the rest of the pipeline is being verified — tag every site `# CUSTOM_ADDER_SITE` for Phase 4 replacement.
- The custom adder must support `.inverse()` for uncomputation use cases.

### 0.3 Absolute value via Com + Swap before Sub (paper modules only)

Per breakdown §7 Flag #5 (open question on sign handling): **resolve by comparing the two accumulator registers first, swapping the larger to the minuend slot, then subtracting.** This uses only modules already in the paper (`Com` Fig. 8, `Swap` Fig. 9, `Sub` Fig. 7) and guarantees a non-negative result, so no sign bit, no two's-complement, no MSB-reset hack.

Concrete per-direction sequence inside `U_G`:

```
pos_sum  ← cascade of Adds over the three positive-term pixels (with cloning for 2·p)
neg_sum  ← cascade of Adds over the three negative-term pixels (with cloning for 2·p)
flag     ← Com(pos_sum, neg_sum)          # flag = 1 iff pos_sum < neg_sum
Swap controlled on flag: (pos_sum, neg_sum) — after this, the top slot holds max(pos_sum, neg_sum) and the bottom holds min
|G_dir|  ← Sub(top, bottom)                # top - bottom, guaranteed ≥ 0
reset flag
```

Subtracting `min` from `max` is always non-negative, so the SUB's result is `|pos_sum − neg_sum|` = `|G_dir|`. No sign bit needed in any downstream register.

### 0.4 Threshold — no threshold register at all; MSB-controlled CNOT

Per breakdown §7 Flag #6 (threshold register ambiguity): **resolve by not allocating a threshold register.** Because `T = 2^(q+2−1) = 2^(q+1)` for the `(q+2)`-bit accumulator (or `2^(q−1)` for the paper's `q`-bit framing), the threshold test reduces to **a single MSB check**: `|G_max| ≥ T  ⇔  MSB(|G_max|) = 1`.

Concrete `U_T` (replaces breakdown §2.7 and Fig. 11):

```
for each bit i in the output register (initially |0⟩^q):
    CNOT(MSB(G_max), output[i])
```

So the output register is `|0⟩^q` if `MSB = 0` (non-edge) or `|1⟩^q = 2^q − 1` if `MSB = 1` (edge). No `Com`, no constant register, no swap inside `U_T`. **One ancilla saved (the `Com`'s `C_out`), `q` qubits saved (no threshold constant register).**

Width detail: with `(q+2)`-bit gradient registers per §0.8, the threshold `T = 2^(q+1)` corresponds to bit index `q+1` (the top bit). The MSB-CNOT therefore controls on bit `q+1` of the `G_max` register.

**Output register choice:** the simplest realisation re-uses `G_max`'s low `q` bits as the output — overwrite them via the MSB-controlled CNOTs, then measure. But that destroys `G_max`'s value (fine, we don't need it again).

### 0.5 Ancilla budget — exactly `6q + 2`

Per breakdown §4 + §7 Flag #7: **the ancilla pool is `6q + 2` qubits, end of discussion.** For `q = 3` this is exactly 20 (matches [MAIN §4]); for `q = 8` it scales to 50.

Layout (the design target from `[[project-custom-adder]]`):

| Slot | Width | Use |
|---|---|---|
| `G_x_accum` | `q + 2` | locked from end of `G_x` computation through `QC` |
| `G_y_accum` | `q + 2` | likewise |
| `G_45_accum` | `q + 2` | likewise |
| `G_135_accum` | `q + 2` | likewise |
| `pos_work` | `q + 2` | accumulator workspace for positive sum (reused across directions) |
| `neg_work` | `q + 2` | accumulator workspace for negative sum (reused across directions) |
| `clone_work` | `q` | cloning workspace for the `2·p` middle term |
| `carry_a0`, `carry_a1` | 2 | alternating-carry pair for ADD/SUB |
| `qc_flag` | 1 | shared comparison flag for `QC` (3-stage cascade) — also reused inside `U_G` for the §0.3 abs-value Com |

Hold on — `4·(q+2) + 2·(q+2) + q + 2 + 1 = 7q + 11`, which exceeds `6q + 2` for any `q ≥ 0`. So this naïve layout overflows the budget. The breakdown's `6q + 2` partition assumes the accumulators are `q` bits, not `q + 2`. With `(q + 2)`-bit accumulators per §0.8 we will *exceed* `6q + 2` and need to either:
- (a) accept a higher ancilla budget than the paper claims (something like `7q + 11`), or
- (b) compress somewhere — e.g. share `pos_work` / `neg_work` with two of the `G_dir_accum` slots by interleaving the QC max-cascade with the gradient computation.

Phase 2 implementation must surface the actual qubit count and choose between (a) and (b) explicitly. Document the deviation from `6q + 2` if (a) wins. **Provisional rule: try (a) first** — extra ancillas are acceptable per `[[project-simulator-qubits]]` so long as they earn their keep, and `7q + 11 = 32` at `q = 3` plus `9q + 2 + 2n = 31` payload = **63 qubits total**, exactly the `extended_stabilizer` cap. Tight but feasible.

### 0.6 Gradient register width — `q + 2` bits

Per breakdown §7 Flag #8: each Sobel mask has coefficients summing in absolute value to `1 + 2 + 1 = 4` on each side. Max accumulator value = `4 · (2^q − 1) < 2^(q+2)`. **Allocate exactly `q + 2` bits** per accumulator (and per gradient register).

(Note: my breakdown previously said `q + 3` based on summing all 8 surrounding pixels naïvely; the user's stricter analysis using actual mask weights gives `q + 2`. Use `q + 2`.)

### 0.7 QC structure — serial cascade with shared flag reset

Per breakdown §7 Flag #9 (and breakdown §2.6): three `Com` + `Swap` pairs executed sequentially, all sharing one flag ancilla that is `reset` after each swap. Match Fig. 10 exactly:

```
Com(G_x_accum,  G_45_accum)  → flag
Swap(flag; G_x_accum, G_45_accum)
reset flag

Com(G_x_accum,  G_y_accum)   → flag
Swap(flag; G_x_accum, G_y_accum)
reset flag

Com(G_x_accum,  G_135_accum) → flag
Swap(flag; G_x_accum, G_135_accum)
reset flag
```

After the third reset, `G_x_accum` holds `G_max`.

### 0.8 Summary of all eight overrides on the breakdown

| Breakdown Flag # | Decision | Section |
|---|---|---|
| 1 (Eqs. 7 & 8) | Use Fig. 12b/c masks (table in §0.1). | §0.1 |
| 2 (Eq. 9 typo) | Use Fig. 12d mask (table in §0.1). | §0.1 |
| 3 (Eq. 10 typo) | Use Fig. 12e mask (table in §0.1). | §0.1 |
| 4 (Adder generalisation) | Alternating-carry, 2 recycled ancillas. | §0.2 |
| 5 (Subtractor sign) | Pre-sort with `Com` + `Swap` so `Sub` always gets `max − min ≥ 0`. | §0.3 |
| 6 (Threshold width) | Drop threshold register; MSB-controlled CNOT on a fresh `|0⟩^q` output. | §0.4 |
| 7 (Ancilla width 19 vs 20) | Use `6q + 2`; allow `7q + 11` if §0.5 sub-budget overflows. | §0.5 |
| 8 (Gradient register width) | `q + 2` bits per accumulator (not `q + 3`). | §0.6 |
| 9 (QC structure) | Serial 3-stage Com+Swap with shared reset-able flag. | §0.7 |

---

---

## File 1: `helpers/ocqr_encoding_new.py`

### 1.1 [BUG] `prepare_neighborhood_images` uses zero-padding, not circular shift

- **Where:** lines 51–72, especially line 69 `if 0 <= sy < h and 0 <= sx < w:` (else `shifted[y,x] = 0`).
- **Says:** out-of-bounds neighbors → 0 (zero padding).
- **Should:** breakdown §1.2 — "Each neighborhood image is a **circular shift** of the central image; out-of-bounds wrap around [MF §2.2 first paragraph]." Use modulo indexing: `sy = (y + dy) % h`, `sx = (x + dx) % w`.
- **Impact:** edge-pixel gradients are wrong (boundary handling differs from paper). For interior pixels of the 4×4 test image (i.e. only the 4 interior cells of a 4×4), no impact. For all boundary pixels, gradients differ.
- **Action:** in the new (corrected) encoder, replace `if 0 <= …` with modular indexing.

### 1.2 [BUG] Neighborhood image ordering does not match the breakdown's MF Eq. 6 ordering

- **Where:** lines 59–62 — order is `[(0,0), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1)]` (core, N, NE, E, SE, S, SW, W, NW).
- **Says (docstring at line 54–57):** claims it follows MF Eq. 6 ordering of `C_{Y,X}, C_{Y-1,X}, C_{Y-1,X+1}, C_{Y,X+1}, C_{Y+1,X+1}, C_{Y+1,X}, C_{Y+1,X-1}, C_{Y,X-1}, C_{Y-1,X-1}`.
- **Reality:** the ordering in the *code* matches the docstring exactly. So the ordering is fine — but the **`shifted[y,x] = rgb_matrix[sy, sx]`** mapping has a semantic question: with `shift = (dy, dx) = (-1, 0)`, `shifted[y,x] = rgb[y-1, x]`. In the joint state at quantum address `|YX⟩`, register `C_{Y-1,X}` should hold the pixel value at `(Y-1, X)`. So `shifted[y,x] = rgb[y-1, x]` means "at quantum address `(y, x)`, the `C_{Y-1,X}` register holds `rgb[y-1, x]`" — that is the value of the pixel north of `(y,x)`. ✓ Consistent.
- **No action**; flagged because the docstring claim and ordering match.

### 1.3 [BUG] `encode_ocqr_neighborhoods` MCX-control logic for the X-mask is brittle

- **Where:** lines 102–115 (`_apply_x_mask`) and its call sites lines 223, 233, 241.
- **Says:** flip qubits whose bit is `0` so that a positive-control MCX/Toffoli fires on the desired pattern.
- **Should:** the breakdown's §1.4 (MF Algorithm 1) does the equivalent step via the "information transfer module" — Toffolis that test the `(Y, X, λ)` pattern. The sandwich-flip approach is a standard, correct realisation; this works.
- **Subtle bug:** `_apply_x_mask` is called twice (sandwich), but **after the second call the qubits are restored only if `_multi_controlled_and` preserved them**. For controls = `[a3] + Y_qubits`, the X-flips are on `Y_qubits` only — and the MCX writes only to `a3` (the target), leaving the Y controls intact. ✓ Correct.
- **No action.**

### 1.4 [BUG] Encoder writes to **all 9 intensity registers in superposition simultaneously** instead of using the address-conditioned approach

- **Where:** lines 247–255. Inside `for img_idx in range(9)`, for each image's classical pixel value `val` at `(y, x, ch_idx)`, the code emits `CNOT(a1, target_reg[bit_pos])` for each `1` bit. This is conditioned only on `a1 = (Y==y AND X==x AND λ==ch_idx)`.
- **Says (breakdown §1.4 step 4):** "CNOT(a_1, C_i) for each intensity bit `C_i` that should be 1" — i.e. for the **central image**. Then breakdown §1.4 last paragraph: "After step 4 sets the central pixel's intensity bits, additional CNOT gates copy/encode each neighbor's pixel value into the corresponding `C_{Y+dy,X+dx}^i` register from the same `a_1` control line".
- **Reality:** the code *does* write to all 9 registers from the same `a_1` control line, but uses `neighborhoods[img_idx][y, x, ch_idx]` (which is the pre-shifted value at `(y, x)`) as the classical lookup. That is correct: the `(Y, X)` address that activates `a_1 = 1` is the *current* address, and the value placed into `C_{Y+dy,X+dx}` register at that address is the value of the *shifted* image at `(y, x)` — which equals `rgb[y+dy, x+dx]` (or 0 with the current zero-padding bug from §1.1). ✓ Semantically correct apart from §1.1.
- **No action** beyond §1.1.

### 1.5 [CLEANUP] `a_0` ancilla is referenced but never written

- **Where:** line 208 unpacks `a0, a1, a2, a3`; line 234, 242 pass `a0` as scratch to `_multi_controlled_and`; lines 259 resets `a0`.
- **Says:** breakdown §1.3 — 4 ancillas `a_0..a_3`. The paper's circuit (MF Fig. 2) uses `a_0` as part of the cascade.
- **Reality:** `a_0` is only used as a scratch ancilla for 3-control MCX uncomputation inside `_multi_controlled_and`, not as a signal carrier. Functionally OK; the comment at lines 209–211 admits the divergence.
- **Action:** in the new implementation, decide whether to match MF Fig. 2 exactly (active `a_0`) or document the substitution explicitly with paper section ref. Either is defensible; prefer matching the figure for paper-name register fidelity per `[[feedback-coding-conventions]]`.

### 1.6 [BUG] `encode_ocqr_from_matrix` is broken

- **Where:** lines 272–295. Allocates `intensity = QuantumRegister(q, "I0")` and `aux = QuantumRegister(4, "a")` on `qc`. Then calls `encode_ocqr_neighborhoods(qc, …, [intensity] + [QuantumRegister(q, f"_dummy{i}") for i in range(8)], …)`. The 8 dummy registers are **not added to `qc`** (see line 290's missing `qc.add_register(…)`).
- **Reality:** any CNOTs emitted onto the dummy registers will fail at execution because those qubits don't belong to `qc`.
- **Action:** delete or rewrite this helper. It's a "convenience for tests" that is currently non-functional.

### 1.7 [CLEANUP] `_multi_controlled_and_inv` exists but is identical to `_multi_controlled_and` and is never called

- **Where:** lines 149–154.
- **Action:** delete in the new implementation, or keep only if uncomputation order ever differs.

### 1.8 [BUG] `decode_ocqr_to_classical` only handles `ch_val ∈ {0, 1, 2}`, dropping λ=11 outcomes

- **Where:** line 333 `if 0 <= ch_val <= 2:`.
- **Says:** breakdown §1.1 — `|11⟩` is the spare channel, *unused*. The OCQR formula gives equal amplitude to all 4 `λ` values.
- **Reality:** dropping λ=11 silently loses 25% of the probability mass. Decoded images will be off by a factor of 4/3 in shot counts and could mask bugs.
- **Action:** in the new decoder, either explicitly mark λ=11 as "discarded as designed" with a per-channel renormalisation, or post-select on λ ∈ {00, 01, 10} *before* dividing into bins so the reported counts reflect actual successful measurements.

---

## File 2: `helpers/quantum_modules_new.py`

### 2.1 [HALFADDER] `append_adder` is a thin wrapper around `HalfAdderGate(q)`

- **Where:** line 66 `qc.append(HalfAdderGate(q), list(a) + list(b) + [carry_out])`.
- **Replacement site #1.** Replace with custom paper-spec adder (Fig. 6 generalised to `q` bits, 2-ancilla alternating carry).
- The wrapper signature `(qc, a, b, carry_out, q)` provides only **1** carry qubit. The paper's adder needs **2** (`a_0, a_1`) for the alternating-carry trick. The new adder API must accept two ancillas.

### 2.2 [HALFADDER] `append_adder_inverse` uses `HalfAdderGate(q).inverse()`

- **Where:** line 81.
- **Replacement site #2.** Will go away once the custom adder has its own `.inverse()` (or an explicit subtractor variant).

### 2.3 [HALFADDER] `append_subtractor` calls `HalfAdderGate(q)` after X-flipping `b`

- **Where:** lines 97–101.
- **Replacement site #3.** This whole function is **dead code** anyway (see 2.4 below) but flagged for completeness.

### 2.4 [BLOCKER] `append_subtractor` is a broken half-implementation with `pass` at the end

- **Where:** lines 87–116. The function X-flips `b`, runs `HalfAdderGate`, X-flips `b` back, then has a long comment block, then `pass`. It writes incorrect arithmetic: the X-flip-around-`HalfAdderGate` trick computes `a + (NOT b)` *without* the `+1`, so the result is `a − b − 1` (assuming `HalfAdderGate` writes the sum into `a`), not `a − b`.
- **Says:** breakdown §2.3 — subtractor must produce `|s⟩ = |C_YX − C_Y'X'⟩` with both borrow ancillas reset.
- **Reality:** off-by-one across the whole subtractor whenever this function is called.
- **Mitigating fact:** `append_subtractor` is **never called** anywhere in `quantum_modules_new.py` or `sobel_edge_detection_new.py`. It is dead code. (`_append_ripple_subtractor` likewise — line 119–142 also ends in `pass`.) The actually-used subtractor is in `quantum_subtractor` (lines 145–168).
- **Action:** in the new implementation, delete `append_subtractor` and `_append_ripple_subtractor`. Implement the subtractor as the gate-faithful Fig. 7 circuit, returning a clean unitary.

### 2.5 [BUG] `quantum_subtractor` (the live one) uses an unverified identity

- **Where:** lines 145–168. Uses `A − B mod 2^q = NOT(B + NOT(A) mod 2^q)`. Wraps `HalfAdderGate(q)` with X-flips on `a`.
- **Says:** breakdown §2.3 — paper's Fig. 7 has its own gate sequence with **2 alternating borrow ancillas**, not 1.
- **Reality:** the identity is arithmetically correct only if `HalfAdderGate(q)` semantics are `(A_in, B_in, c) → (A_in, A_in+B_in, c⊕carry_out)`. **This needs simulation verification.** It also uses **1** borrow ancilla, not 2.
- The borrow-flag derivation in the docstring ("carry-out of (b + NOT(a)) = 1 iff b > a") is correct *under* the assumed adder semantics — but the comparator (§2.6 below) wires `bo[0] → cout[0]` via CNOT directly, treating this borrow as the comparator's flag. If the borrow polarity is inverted (1-iff-A<B vs 1-iff-A>B), the comparator silently outputs the opposite predicate.
- **Action:** in the new implementation, build the subtractor from Fig. 7's explicit gate sequence with 2 alternating-borrow ancillas; cross-verify by simulating on small `q` against a classical reference.

### 2.6 [BUG] `quantum_comparator` polarity may be inverted vs the breakdown

- **Where:** lines 174–190.
- **Says:** breakdown §2.4 — `C_out = 1` iff `C_YX < C_Y'X'`; `C_out = 0` iff `C_YX ≥ C_Y'X'`.
- **Reality:** the code copies `bo[0]` (the subtractor's borrow flag) into `cout[0]`. Whether that borrow is `1-iff-A<B` or `1-iff-A>B` depends on the unverified identity in §2.5. The docstring on line 167 claims "carry-out of (b + NOT(a)) = 1 iff b > a; that's exactly the borrow". With `A < B ⇔ b > a`, that's consistent with the paper's convention only if the substitution is correct.
- **Also:** the comparator uses **2** ancillas (`bo`, `cout`) — matching the breakdown's "2 qubits within the comparator". The intermediate `bo` is uncomputed by `sub.inverse()`. ✓
- **Action:** simulate `Com(A, B)` on small operand pairs `(A, B)` ∈ {(0,0), (0,1), (1,0), (3,3), (5,2), …} and verify `C_out` matches the breakdown's spec.

### 2.7 [DEVIATION] Comparator built from `sub + cx + sub^-1` is **structurally different from paper Fig. 8**

- **Where:** lines 186–189.
- **Says:** breakdown §2.4 — Fig. 8 is an MSB-to-LSB cascade of CNOTs and Toffolis directly comparing `C_YX^i` with `C_Y'X'^i`, with an intermediate signal ancilla uncomputed within the module. **Not** a subtractor sandwich.
- **Reality:** subtractor-based comparator is functionally equivalent (modulo §2.6) but has higher gate cost (2× subtractor instead of one comparator's worth of gates) and double the carry ancillas live.
- **Action:** in the new implementation, build the comparator from Fig. 8 directly so it can fit within the **2-ancilla** budget [breakdown §2.4 last sentence] and so its complexity matches the paper's `14q` figure used in [MAIN §3.3] complexity analysis. For the *interim* using qiskit's HalfAdder, this sandwich approach works but inflates ancilla usage — keep it as a temporary, but flag it.

### 2.8 [BUG] `quantum_max_value_module` and `quantum_threshold_module` are stubs returning `None`

- **Where:** lines 211–216.
- **Says:** breakdown §2.6, §2.7 — `QC` is three `Com`+`Swap` pairs with a shared 1-bit ancilla; `U_T` is `Com(G_max, 2^(q−1))` followed by a controlled-swap with `|1⟩^⊗q`.
- **Reality:** unimplemented in `quantum_modules_new.py`. `sobel_edge_detection_new.py` open-codes substitutes that **do not match the paper** (see §3.4, §3.5 below).
- **Action:** implement both in the new module file.

### 2.9 [HALFADDER] Indirect uses through `quantum_subtractor`

- **Where:** line 163 — `quantum_subtractor` calls `HalfAdderGate(q)`. Therefore `quantum_comparator` (line 187) and any module composed from these inherit a `HalfAdderGate` dependency.
- **Replacement site #4** (transitive).

---

## File 3: `helpers/sobel_edge_detection_new.py`

### 3.1 [BLOCKER] `_compute_one_gradient` does not produce `|G_dir|` — it resets the sign bit instead of doing a real absolute value

- **Where:** lines 263–308, especially line 303 `qc.reset(work_pos[qp2 - 1])`.
- **Says:** §0.3 — abs-value is obtained via `Com(pos, neg)` + controlled `Swap` to route the larger to the minuend slot, then a single `Sub`. No sign bit ever appears.
- **Reality:** the code resets the MSB to 0 after subtraction. This is **not** absolute value:
  - If `pos ≥ neg`: the MSB is already 0, reset is a no-op. ✓
  - If `pos < neg`: result is in two's complement (MSB = 1), and the *meaningful* magnitude bits live below. Resetting the MSB silently corrupts the value — it produces `(result mod 2^{q+1})`, not `|result|`.
- **Impact:** any pixel where the negative-direction gradient exceeds the positive-direction one produces a garbage `|G_dir|`.
- **Action:** rewrite `U_G` per §0.3 exactly. Pseudocode:
  ```
  pos_work ← Add cascade for positive terms
  neg_work ← Add cascade for negative terms
  flag    ← Com(pos_work, neg_work)            # 1 iff pos < neg
  Swap(flag; pos_work, neg_work)                # now pos_work ≥ neg_work
  G_dir   ← Sub(pos_work, neg_work)             # ≥ 0, written into the G_dir accumulator
  reset flag, neg_work, pos_work
  ```

### 3.2 [BLOCKER] `_max_into_running` collapses `U_G` and `QC` into one folded loop, departing from Fig. 13 + Fig. 10

- **Where:** lines 310–355.
- **Says:** breakdown §3.2 — pipeline is `U_G → QC → U_T`, with `U_G` producing **four** gradient registers held simultaneously, then `QC` computes max-of-four via three `Com`+`Swap` pairs sharing one ancilla, then `U_T` thresholds.
- **Reality:** the new code maintains a running max during gradient computation. After each gradient is computed in `work_pos`, it compares to `running_max` and conditionally swaps. The four gradient registers are never simultaneously materialised.
- **Impact:** functionally this can produce the same result IF the comparator on `(|G_new|, running_max)` is correct (it isn't — see §3.3) AND `|G_new|` is correct (it isn't — see §3.1). But it **departs from the paper's circuit** and breaks any one-to-one mapping with Fig. 14.
- **Action:** in the new implementation, restore the paper's pipeline:
  1. Compute all four `|G_dir|` (or signed `G_dir` per chosen handling from §3.1) into four dedicated registers.
  2. Run the QC module (three serial `Com`+`Swap` pairs with one shared reset ancilla, per breakdown §2.6).
  3. Run `U_T` per breakdown §2.7.

### 3.3 [BUG] In-place comparator inside `_max_into_running` uses an ad-hoc carry-test, not `Com`

- **Where:** lines 322–344.
- **Says:** breakdown §2.4 — comparator returns `C_out = 1` iff `A < B`, both inputs preserved, intermediate uncomputed.
- **Reality:** the new code clones `running_max` into `work_neg`, X-flips `work_neg`, runs `HalfAdderGate(q+1)` to compute `work_pos + ~work_neg`, copies the carry into `flag`, then resets `work_neg` and `carry`. This is approximately a subtractor-based comparator, but:
  - It conditionally cswaps `running_max ↔ work_pos` on `flag` (line 343). After the swap, `running_max` may hold either the old running max or the new gradient. But `work_pos` is then **reset** (lines 348–349), discarding the old running max!
  - If the swap fired (`flag = 1`), the *new* gradient is now in `running_max` (correct) and the *old* running max is in `work_pos` and gets reset — fine, we don't need it.
  - If the swap did NOT fire, the new gradient is still in `work_pos` and gets reset — also fine.
  - So this part *might* be functionally right.
- **Real bug:** `qc.cx(carry, flag)` (line 337) — `flag` is reset later via `qc.reset(flag)` (line 345), but the line 337 step uses `carry` which is "the carry-out of HalfAdderGate". The HalfAdderGate's last argument (`+ [carry]`) is XORed with the carry-out, so `carry ⊕= carry_out`. Since `carry` was reset to 0 before this op, after the gate `carry == carry_out`. Then `cx(carry, flag)` writes `flag = carry_out`. ✓
- **Subtle issue:** after line 337, `carry` is reset (line 341). This **loses information**, but since the comparator's contract requires uncomputation anyway, and the only side effect we wanted (`flag = predicate`) is captured, this is acceptable.
- **Real real bug:** the cswap on line 343 doesn't preserve `flag` uncomputation. After the cswap, `flag` is still set; line 345 resets it. Functionally fine.
- **Action:** rewrite as a clean Fig. 8 comparator + Fig. 9 swap, sharing one ancilla per breakdown §2.6. Keep this code only as a stepping-stone test.

### 3.4 [BLOCKER] `U_T` (threshold) replaced with a bit-OR test that is not the paper's circuit

- **Where:** lines 360–373.
- **Says:** §0.4 — `U_T` is **a single MSB-controlled CNOT cascade** onto a fresh `|0⟩^q` output register. No `Com`, no threshold register, no swap.
- **Reality:** the new code:
  1. Sets `flag = OR(running_max[q-1], running_max[q])` via three gates (`cx`, `cx`, `ccx` — which is wrong, see below).
  2. Conditionally NOTs all low bits of `running_max` based on `flag`.
  3. The result on `running_max[0..q-1]` is supposed to be `2^q − 1` if flag, else original.
- **Bugs in this code path:**
  - **OR is computed correctly** (as it happens) but is the wrong predicate — §0.4 needs a single MSB check, not an OR over multiple bits.
  - **Conditional-NOT semantics are wrong.** `cx(flag, running_max[i])` **XORs** flag into each bit; it does not *force* the bit to 1. So for an edge pixel whose `running_max[i]` was already 1, the XOR flips it to 0 — the output is not `2^q − 1`.
  - For non-edges (`flag = 0`), nothing happens — but the spec says non-edges should be `0`, not the original `running_max`.
  - **Net:** this output bears no relationship to the "edges = `2^q − 1`, non-edges = `0`" contract.
- **Action:** rewrite per §0.4 exactly:
  ```
  output ← |0⟩^q        # already zero on allocation
  for i in 0..q-1:
      CNOT(G_max[q+1], output[i])   # MSB of the (q+2)-bit G_max
  ```
  Then measure `output` (along with `Y`, `X`, `λ`). Drop the threshold constant register, drop the `Com` call, drop the swap.

### 3.5 [BLOCKER] Final SUB step `I_0 := I_0 − running_max[:q]` is not in the paper's algorithm

- **Where:** lines 377–383.
- **Says:** breakdown §3.2 — final block is `U_T`, then measurement directly on `G'` (and `Y, X, λ`). The paper subtracts the edge gradient from the original *only in the visual rendering of the output image* [MAIN §3.2 last sentence], not in the quantum circuit's pre-measurement state.
- **Reality:** the new code emits a `HalfAdderGate`-based subtractor that mutates `I_0` (the central intensity register). This:
  - Changes the measurement target from "G' for edge classification" to "I_0 − G' for output-image rendering".
  - Uses **another `HalfAdderGate`**, adding another `HalfAdder` replacement site.
- **Action:** decide which output is wanted (binary edge map per breakdown §3.2 step 10, OR rendered image per MAIN §3.2 last sentence). For paper-fidelity, go with the breakdown's binary edge map — drop this SUB. If rendered image is desired later, do it classically after measurement.

### 3.6 [BUG] `encode_ocqr_neighborhoods` is called twice

- **Where:** line 163 inside `build_edge_detection_circuit`, and the comment at line 260 says "we don't repeat" — but line 163 is the only call. So actually **not called twice**, despite the misleading comment. The line 164 `QuantumRegister(0, "_") if False else aux[:4]` is also a head-scratcher: the ternary always evaluates `aux[:4]`. The dead `if False` branch should be removed.
- **Action:** in the new implementation, single clean call: `encode_ocqr_neighborhoods(qc, pos, ch, intensity, aux[:4], rgb_matrix, n, q)`. Drop the comment block at lines 256–260 about "we don't repeat."

### 3.7 [DEVIATION] Gradient computation uses bit-shifted adds for `2·p`, not the paper's `U_c` + double-`Add`

- **Where:** lines 271–275, 281–285 (use `_apply_add(qc, …, shift=1, …)` for the weighted-2 terms).
- **Says:** breakdown §3.1 — "The 'weighted' coefficients `2·p` are realised as `p + p` — i.e. each `2·p` term is two adder calls with the same operand. The cloning module `U_c` duplicates `p` so it can be added to two partial sums simultaneously."
- **Reality:** bit-shift adds are *arithmetically equivalent* and use *fewer adders*. They also dodge the need for the cloning workspace. But they don't match Fig. 13's structure.
- **Impact:** circuit complexity numbers won't match [MAIN §3.3] (`16 Add + 4 Sub + 2 U_c`). Functional output should be identical.
- **Action:** in the new implementation, *prefer* the paper-spec construction (cloning + double-add) for traceability per `[[feedback-coding-conventions]]`, unless that pushes ancilla count past the `6q + 2` budget. The bit-shift trick saves 4 adders and 2 cloning modules, which is large — keep it as a **documented deviation** with a code comment citing the optimisation and confirming arithmetic equivalence.

### 3.8 [BUG] `GRAD_EQS` for `Gy` follows Fig. 12 (canonical) not Eq. 8 (transcribed)

- **Where:** line 94 `"Gy": {"pos": [(6, 0), (5, 1), (4, 0)], "neg": [(8, 0), (1, 1), (2, 0)]}`.
- **Says:** breakdown §3.1 (and Flag #1 of §7) — paper's Eq. 8 is broken (gives `G_y = −G_x`). Use Fig. 12 masks as authoritative.
- **Reality:** code uses bottom-row − top-row, which is the Fig. 12 canonical `G_y`. ✓
- **No action**; flagged because it's correct *despite* contradicting Eq. 8.

### 3.9 [CLEANUP] Massive dead comment block analysing the alias-slot problem

- **Where:** lines 184–256.
- These walk through several abandoned designs ("Workaround … PRAGMATIC FIX … FINAL FIX"). They're useful context for understanding the running-max decision but make the file hard to read. Delete in the new implementation; preserve the FINAL FIX rationale as one short comment.

### 3.10 [HALFADDER] All `HalfAdderGate` uses in this file

| Line | Context | Args | Width |
|---|---|---|---|
| 105 | `_apply_add` (helper used for positive-sum accumulation) | `src + dst[shift:shift+q] + [dst_carry]` | `q` |
| 293 | `_compute_one_gradient` — subtractor (`work_pos := work_pos − work_neg`) via X-invert trick | `work_neg + work_pos + [carry]` | `q+2` |
| 328 | `_max_into_running` — comparator-by-subtraction | `work_pos[:q+1] + work_neg[:q+1] + [carry]` | `q+1` |
| 381 | Final image-rendering subtract `I_0 := I_0 − running_max[:q]` | `running_max[:q] + intensity[0] + [carry]` | `q` |

Plus all uses inherited via `quantum_modules_new.py`:
- `append_adder` (line 66) — 1 site
- `append_adder_inverse` (line 81) — 1 site
- `append_subtractor` (line 98, dead code) — 1 site
- `quantum_subtractor` (line 163) — used by `quantum_comparator`

**Total `HalfAdderGate` instantiation sites: 8** (4 in `sobel_edge_detection_new.py` + 4 in `quantum_modules_new.py`).

---

## Estimated ancilla savings from a custom adder

(For interpretation of the breakdown's `6q + 2` budget.)

**Today (using `HalfAdderGate`):**
- `HalfAdderGate(q)` writes the carry-out to its `(2q+1)`-th argument. That argument is always **1 dedicated carry qubit per adder call** in the current code.
- `quantum_subtractor` instantiates `HalfAdderGate(q)` with `bo[0]` as that carry qubit → 1 ancilla per subtractor.
- `quantum_comparator` runs subtractor twice but on the same `bo[0]` — `1` ancilla effective.
- In `sobel_edge_detection_new.py`, the *adder calls inside `_compute_one_gradient`* use **bits of `work_pos` itself** as the carry destination (lines 272, 275, 282, 285) — i.e. the result register absorbs the carry, no extra ancilla. So 0 extra ancillas for those.
- The big subtractor inside `_compute_one_gradient` (line 293) uses `carry` (aux[18]) — 1 ancilla.
- The comparator-by-subtraction at line 328 also uses `carry` — same 1 ancilla.
- The final image subtract at line 381 — same 1 ancilla.

So in the current code, the *carry/borrow* live-set is **1 qubit at a time**. The "savings" from a custom 2-carry adder would actually **increase** ancilla count from 1 to 2 for *each call site*, BUT only if you preserved the `HalfAdderGate`'s "carry-target is part of the result register" trick. The paper's design is *not* about saving ancillas at the per-adder level vs `HalfAdderGate` — it's about **not blowing past 2 ancillas for ADD when the result must NOT widen** (i.e. you don't have the spare bit in the result register).

**For the actual paper pipeline (where result register width is exactly `q`, no widening allowed):**
- Qiskit `HalfAdderGate(q)` writes the carry into a separate qubit → needs **1 carry ancilla** per add.
- Cuccaro / paper's alternating-carry adder also needs **2 carry ancillas** for a `q`-bit add and recycles them.
- For a 4×4 image (`q = 3`), this is `1` vs `2` ancillas per adder — no benefit.

**For an `n`-bit RGB image (`q = 8`):**
- Qiskit `HalfAdderGate(q=8)` still needs only 1 carry qubit (it's not the typical "ripple of q ancillas" — it's a different design that widens the output).
- *However*, if you actually want a *non-widening* adder (overflow truncated), `HalfAdderGate` is the wrong tool — it always outputs `q+1` bits. To truncate, you'd need to discard or reset the carry, but then your adder is fragile to overflow.

**The real reason to write a custom adder** (per the breakdown's §2.2 implementation note and `[[project-custom-adder]]`):
- The paper claims `q`-bit gradient registers but actually needs `q+3` bits (breakdown Flag #8). If you stick to the paper's `q`-bit registers, you need an adder that handles overflow without growing the result register — *and* fits 2 carry ancillas inside the strict `6q+2` budget.
- For `q = 8` the paper-style alternating-carry adder uses 2 ancillas; qiskit `HalfAdderGate(q=8)` produces a 9-bit result, which forces you to grow the gradient register to 9 (or 10, 11, …) bits as gradients accumulate — which the breakdown already accommodates (`q + 3` bits) but at a qubit cost.

**Concrete estimate for `q = 3` (4×4 test image):**
- Current 4 adder calls (positive + negative accumulators per gradient × 4 gradients) widen each accumulator. The new code already uses `q + 2 = 5` bits per accumulator → 10 qubits for `work_pos + work_neg` instead of 6.
- A custom non-widening adder + signed handling would reduce this to `q = 3` bits per accumulator + 2 carry ancillas + a sign-tracking ancilla → **9 qubits** vs the current **10**. Net **saving: 1 qubit**.

**Concrete estimate for `q = 8` (full RGB):**
- Current widening adders would push each accumulator to `q + 3 = 11` bits → 22 qubits for both, plus per-add carries.
- Custom non-widening adder → `q = 8` bits + 2 carries reused → **18 qubits**. Net **saving: 4 qubits per direction × 4 directions = 16 qubits across the algorithm**, or roughly **20%** of the `6q + 2 = 50` ancilla budget.
- This matters because the total `q = 8`, `n = 9` qubit count is `9q (intensity) + 2 (λ) + 2n (pos) + ancillas = 72 + 2 + 18 + (50 or more) = 142+`. The `extended_stabilizer` cap is 63 — **`q = 8` won't fit regardless** of adder choice. For `q = 8` we'd need a different simulator. The custom adder is *necessary but not sufficient* to lift the qubit constraint.

**Conclusion:** the custom adder buys ~1 qubit at `q = 3` and ~16 qubits at `q = 8`. **At `q = 3` we can fit either way; at `q = 8` neither fits on `extended_stabilizer`.** The reason to build the custom adder is **paper fidelity** and to make `q = 4, 5, 6` (intermediate sizes) tractable on the 63-qubit simulator.

---

## Prioritized implementation plan (build in **new files**, do NOT edit `*_new.py`)

Suggested file names — final naming is your call, but using `_v2.py` or `_paper.py` keeps the diff scope obvious. The implementation order is what matters.

### Phase 0 — scaffolding (no quantum yet)

**P0.1.** Create `helpers/classical_reference.py` — port `classical_sobel_gradients` and `classical_edge_detection` from `sobel_edge_detection_new.py:53–86`. **Fix** the boundary handling: per breakdown §1.2 (circular shift), use modular indexing for the kernel reads. Add unit tests verifying interior + boundary pixels against a hand-computed reference. This is the oracle for everything else.

**P0.2.** Create `helpers/circular_shift.py` — replacement for `prepare_neighborhood_images` with circular indexing (`%`).

### Phase 1 — quantum modules (matching paper figures, using `HalfAdderGate` provisionally)

**P1.1.** `helpers/modules_v2.py` containing:
- `quantum_cloning(qc, src, tgt, q)` — paper Fig. 5, identical to existing `append_cloning`. Trivial.
- `quantum_adder_provisional(qc, a, b, c_ancilla, q)` — wraps `HalfAdderGate(q)`. **[HALFADDER]** Mark with comment `# TODO custom adder per breakdown §2.2` plus a unique tag like `# CUSTOM_ADDER_SITE` so all sites are greppable.
- `quantum_subtractor_v2(qc, a, b, bo, q)` — implement from paper Fig. 7 directly (X-flips + Toffoli/CNOT cascade with 2 alternating-borrow ancillas). Cross-verify against `a − b mod 2^q` with statevector simulation on `q ∈ {2, 3, 4}` and operand pairs covering positive, negative, equal, and overflow cases.
- `quantum_comparator_v2(qc, a, b, intermediate, c_out, q)` — implement from paper Fig. 8 directly. Verify polarity (`C_out = 1 iff a < b`) on the same operand pairs.
- `quantum_swap_v2(qc, ctrl, a, b, q)` — `q` parallel CSWAPs, identical to existing `append_swap`. Trivial.

**P1.2.** Unit-test each module in `tests/test_modules_v2.py` against the classical reference on `q = 2..5`. Tests must verify the unitary, ancilla cleanup (post-state at the ancillas is `|0⟩`), and input preservation.

### Phase 2 — gradient + max + threshold composition

**P2.1.** `helpers/sobel_v2.py` with:
- `build_U_G(qc, intensity_regs, gradient_regs, ancillas, n, q)` — paper Fig. 13 augmented per §0.3 (abs-value via `Com` + `Swap` before `Sub`). Gradient registers are **`q + 2` bits** per §0.6.
- `build_QC(qc, g_regs, flag_ancilla, n, q)` — paper Fig. 10 (3 `Com`+`Swap` pairs serial, shared flag reset between each) per §0.7.
- `build_U_T(qc, g_max, output_reg, q)` — **MSB-controlled CNOT cascade** per §0.4. No `Com`, no constant register, no swap. The `output_reg` is a fresh `q`-qubit `|0⟩^q` register reused as the measurement target.
- `build_edge_detection_v2(rgb_matrix, n, q)` — top-level builder using the `6q + 2` budget (or `7q + 11` if §0.5 (a) is needed).

**P2.2.** Implement the §0.3 abs-value sequence inside `build_U_G`. Per direction:
  1. Add cascade into `pos_work` (with cloning for `2·p` term per §0.1).
  2. Add cascade into `neg_work`.
  3. `Com(pos_work, neg_work)` → `flag`.
  4. `Swap(flag; pos_work, neg_work)` so `pos_work ≥ neg_work`.
  5. `Sub(pos_work, neg_work)` → `G_dir_accum`.
  6. Reset `flag`, `pos_work`, `neg_work`.
Verify `G_dir_accum ≥ 0` post-condition by simulation on the 4×4 test matrix.

**P2.3.** Unit-test `U_G`, `QC`, `U_T` individually against the classical reference on the 4×4 test matrix.

### Phase 3 — full pipeline + simulation

**P3.1.** Build a new top-level notebook (mirroring `main_4x4_simulation_old.ipynb`'s minimalist style per `[[project-file-layout]]`) that wires everything together and measures.

**P3.2.** Simulate on `extended_stabilizer`, count qubits, verify the 4×4 result matches the classical reference within statistical tolerance.

**P3.3.** Note the qubit count as a function of `q ∈ {2, 3, 4}` with the provisional `HalfAdderGate`-based adder. Document the curve.

### Phase 4 — custom adder

**P4.1.** Design the alternating-carry `q`-bit adder per Fig. 6 and the breakdown §2.2 implementation note. Provide:
- `quantum_adder_v2(qc, a, b, a0, a1, q)` — 2 carry ancillas, alternating.
- `quantum_adder_v2_inverse(...)` for uncomputation.
- Unit tests verifying correctness, input preservation, and **ancilla cleanup** (both ancillas end at `|0⟩`).

**P4.2.** Swap out the `quantum_adder_provisional` calls in `modules_v2.py` and `sobel_v2.py` (greppable via the `CUSTOM_ADDER_SITE` tag).

**P4.3.** Re-measure qubit count for `q ∈ {2..8}`; verify the savings hit the `6q + 2` budget target.

---

## Quick-reference checklist (every actionable item in one place)

- [ ] **P0.1** classical reference with circular boundary (fixes audit §1.1)
- [ ] **P0.2** circular-shift neighborhood helper
- [ ] **P1.1** Fig. 5 cloning, Fig. 6 adder (provisional w/ `HalfAdderGate`), Fig. 7 subtractor, Fig. 8 comparator, Fig. 9 swap
- [ ] **P1.2** unit tests for §2.1, §2.5 (subtractor verify), §2.6 (comparator polarity)
- [ ] **P2.1** `U_G`, `QC`, `U_T` per §0.3, §0.7, §0.4; gradient regs at **`q + 2`** bits per §0.6
- [ ] **P2.2** abs-value gradient via §0.3 (Com + Swap before Sub) — fixes audit §3.1
- [ ] **P2.3** end-to-end tests against the classical oracle
- [ ] **P3.1** new top-level notebook (style of `main_4x4_simulation_old.ipynb`)
- [ ] **P3.2** verify on `extended_stabilizer`; confirm total ≤ 63 qubits at `q = 3`
- [ ] **P3.3** record qubit-count curves vs `q`; flag the budget breakpoint
- [ ] **P4.1** custom 2-ancilla alternating-carry adder + its inverse per §0.2
- [ ] **P4.2** replace every `CUSTOM_ADDER_SITE`
- [ ] **P4.3** re-measure budget; confirm `6q + 2` (or document the `7q + 11` deviation per §0.5)

### HalfAdderGate replacement sites — every location to swap out

| File | Line(s) | What | Width |
|---|---|---|---|
| `quantum_modules_new.py` | 66 | `append_adder` | `q` |
| `quantum_modules_new.py` | 81 | `append_adder_inverse` | `q` |
| `quantum_modules_new.py` | 98 | `append_subtractor` (dead) | `q` |
| `quantum_modules_new.py` | 163 | `quantum_subtractor` (live, used by comparator) | `q` |
| `sobel_edge_detection_new.py` | 105 | `_apply_add` helper (gradient accumulation) | `q` |
| `sobel_edge_detection_new.py` | 293 | gradient subtractor (`work_pos − work_neg`) | `q+2` |
| `sobel_edge_detection_new.py` | 328 | comparator-by-subtraction in `_max_into_running` | `q+1` |
| `sobel_edge_detection_new.py` | 381 | final image subtract | `q` |

All eight to be replaced in Phase 4. Mark each with `# CUSTOM_ADDER_SITE` in the new files so they're greppable.
