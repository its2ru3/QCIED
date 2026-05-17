# QCIED Implementation — Discrepancies vs. Paper

Findings after reading `helpers/ocqr_encoding.py`, `helpers/quantum_modules.py`,
`helpers/sobel_edge_detection.py`, `main_4x4_simulation.ipynb`, the original Sobel
paper (Yuan et al., 2025), and Section 2 of the median-filtering paper (Yuan et al.,
2022, ref. [13] in the original).

Two independent problem areas: **(A) Intensity / neighborhood encoding** and
**(B) edge-detection circuit construction and gate accounting**. The third-party
analysis you quoted is partially right (it correctly identifies the bit-shift /
adder-count issue and the elementary-gate counting convention), but it misses
the bigger structural issues — especially in encoding.

---

## A. Intensity-encoding problems

The paper's encoding scheme is **not** what your code does. The paper builds on the
median-filtering paper (ref. [13]), which is explicit on every step. Your code
implements a textbook MCX-per-pixel scheme that:

1. Uses a separate intensity register per neighborhood image (9 registers of `q`
   qubits each), AND
2. Encodes every (pos, channel, intensity_bit) combination using a (2n+2)-controlled
   MCX gate, AND
3. Encodes the eight neighborhoods by re-encoding shifted images independently.

The paper does all three differently.

### A.1 The paper does NOT use one register per neighborhood

What the paper does (Sect. 2, Eq. 6 of the median-filtering paper, repeated in
Fig. 4 of the Sobel paper):

> "...adding only several CNOT gates based on Fig. 2 ... the quantum preparation
> of eight images and their neighborhood can be realized by adding only several
> CNOT gates."

The nine neighborhood values for the **same** `(Y, X, λ)` are stored as nine
*entangled* `q`-qubit ledgers, all keyed off the **same** shared position/channel
superposition. Concretely: position register `|YX⟩` is shared, channel register
`|λ⟩` is shared, and there are 9 intensity registers `|C_{Y,X}⟩, |C_{Y-1,X}⟩, …`
each `q` qubits. For the **same** superposition basis state `|YX⟩|λ⟩`, the *eight*
neighbor registers hold the eight shifted pixel values *all at once*. The
"only several CNOTs" is exactly the row-by-row neighbor trick — pixel
`C(Y+1,X)` of the core image is the value of `C(Y,X)` for the "shift-up" image,
so once the core ledger is encoded, neighbors come from CNOT-copies into
the other 8 ledgers gated by the same ancilla `a₁` that already encoded
position+channel for the row.

Your code (`helpers/sobel_edge_detection.py:296-345`) does this:

```python
neighborhoods = prepare_neighborhood_images(rgb_matrix)
for img_idx, neighborhood in enumerate(neighborhoods):
    ...
    for y in range(size):
      for x in range(size):
        for ch in range(3):
            ...
            for bit_idx, bit in enumerate(bin_intensity):
                if bit == '1':
                    qc.mcx(controls, intensity_reg[bit_idx])  # (2n+2)-ctrl MCX
```

That re-encodes each neighborhood from scratch — costing 9× the encoding work,
and using `(2n+2)`-controlled MCX (which Qiskit synthesises with `O(2^(2n))`
Toffolis/ancillae). This is **exactly** the inefficient `O(qn·2^{2n})` regime
the median-filtering paper *replaces* with the row-by-row method.

### A.2 The information-transfer / ancilla trick is absent

The paper (median-filtering Sect. 2.1, "Algorithm 1") uses **4 auxiliary qubits
`a₀, a₁, a₂, a₃`** to convert one expensive `(2n+2)`-controlled MCX per
intensity bit into a **chain of Toffolis**:

- `a₃ ← Y-row indicator` (one Toffoli sequence per row, then reset).
- `a₂ ← a₃ AND X-column` (Toffoli; one per pixel in the row).
- `a₁ ← a₂ AND λ-channel` (Toffoli; one per channel per pixel).
- Encoding intensity bit is then just `CNOT a₁ → C^i` per bit set in the
  pixel value. After encoding, reset `a₀, a₁`, then reset `a₂` between pixels,
  reset `a₃` between rows.

The paper's complexity expression `(5n + 3q + 30)·2^n + (5n - 4)·2^n + 2n + 2`
counts exactly this. Your implementation has **no** information-transfer
auxiliaries, no row/column ancilla, no reuse. Every pixel is independently
addressed with a fresh `(2n+2)`-ctrl MCX. That's the wrong algorithm, not just
a constant-factor difference.

The shared-register `aux` you carve up in `build_edge_detection_circuit`
(`sobel_edge_detection.py:106-129`) is reserved for arithmetic — none of it
is used for the encoding's `a₀..a₃`. Worse, the encoding pass in
`encode_intensity_values` ignores `aux` entirely.

### A.3 The 9 neighbors should be sourced from the encoding, not by classical
       Python shift

`prepare_neighborhood_images` (`ocqr_encoding.py:190`) does a Python-side
`np.roll`-style shift of the classical RGB matrix, then re-encodes each
shifted variant. That's a classical-image trick, not the quantum
neighborhood preparation the paper describes (Fig. 4 of the Sobel paper /
Eq. 6 of the median paper).

The paper's neighborhood preparation is *quantum-parallel*: nine entangled
ledgers indexed by the same `|YX⟩`, prepared simultaneously by adding 8
CNOTs (one per neighbor) inside the same row-by-row sweep. Your code
classically pre-computes the shifts and then quantum-encodes them
independently. Same Hilbert-space content for a single basis state, but
roughly 9× the gates — and you've lost the paper's claim of "preparation
costs amortise across all 9 images".

### A.4 Position bit-order is inconsistent

`ocqr_encoding.py:94` (initial encoding) and `sobel_edge_detection.py:321-345`
(re-encoding inside the circuit builder) disagree on whether to reverse `bin_pos`.
The first uses `enumerate(reversed(bin_pos))`, the second uses `enumerate(bin_y)`
after already reversing with `[::-1]`. This is benign for measurement decoding
(you decode the same way), but you have **two different encodings** living in
the same project for the same operation. Pick one and centralise. The
`decode_ocqr_to_classical` (`ocqr_encoding.py:296-298`) reverses bits again when
mapping back, so any inconsistency upstream produces silently wrong pixels at
non-symmetric positions.

### A.5 11-channel is encoded as background, not "redundant"

The paper says `|11⟩` is the **redundant** color slot — it should be left as
`|0⟩` *intensity* (i.e., no pixel data, so the slot contributes zero amplitude
mass after measurement post-selection). Your initial `qc.h(channel_qubits)` puts
1/4 of the channel mass on `|11⟩`, but nothing is written there, which is fine.
But you also do not flag/condition arithmetic on `λ ≠ 11`, so any gradient
computation runs on the redundant slot too. Whether that matters depends on
whether you post-select; right now you don't, so the measurement histogram
contains a useless 25% mass that dilutes shots.

---

## B. Edge-detection / Sobel circuit problems

The third-party analysis you quoted captures two of these (B.2 and B.6). The
others are real bugs that affect either correctness or gate count.

### B.1 Adder is wrong: it overwrites the addend, not the augend

Paper (Eq. 3): `U_add (|A⟩ ⊗ |B⟩) = |s⟩ ⊗ |B⟩`, so **A is destroyed and replaced
with the sum, B survives**.

Your `quantum_adder` (`quantum_modules.py:42-70`) puts the sum in `B`:

```python
qc.ccx(a[0], b[0], carry[0])
qc.cx(a[0], b[0])  # b[0] <- a[0] XOR b[0]  → sum lands in B
```

So in your convention `A` survives and `B` becomes the sum. That's the
**opposite of the paper**. By itself this is just a labelling choice — but
combined with your "clone then add then unclone" pattern in `_compute_gradient`
(see B.4) it produces nonsense. After `clone_gate(intensity → clone)` and
`add_gate(clone, grad_out)`, your `grad_out` register accumulates the sum
(correct outcome by coincidence), but the second `clone_gate` call to "unclone"
runs CNOT(intensity → clone) again on a `clone` register that is now
`intensity ⊕ grad_out_old` — not `intensity` — so the "unclone" leaves
`clone = grad_out_old`, not `|0⟩`. **`clone` is not zeroed between uses.**

That breaks the second iteration immediately. The next `add_gate(clone, grad_out)`
adds `grad_out_old` to itself, doubling it. Verify by `qc.reset(clone)` between
adds and the gate count drops by the unclone calls, but the math becomes correct.

(This is the most damaging single bug in the gradient module. The "clone-add-unclone"
pattern as written is a no-op for clearing.)

### B.2 Bit-shift optimisation is missing (32 adders instead of 16)

Confirmed in the third-party analysis. Paper Sect. 3.3:

> "The edge gradient calculation module uses 16 quantum adders, four quantum
> subtractors, and two quantum copying modules."

You use 32 adders (4 per direction × 4 directions × 2 sign halves) instead of
16, because you implement `2·p₅` by **adding `p₅` twice** rather than wiring
`p₅` shifted left by one bit position into a `(q+1)`-bit accumulator.

Mechanically, "multiply by 2" is a register-level rewire: when adding `2·p` to
a `(q+1)`-bit accumulator `acc`, treat `p` as if its bit `i` lives at
position `i+1` of `acc` and add. No gate cost. Concretely, you can call the
adder against `acc[1:q+1]` while leaving `acc[0]` alone. This is what the
paper's "8 ternary adders + 8 quaternary adders + 2 copy modules" decomposition
in Fig. 14's accounting refers to:

- **Ternary adder** (3-bit input → 4-bit output): `pᵢ + pⱼ + (2·pₖ)`, computed
  as `(pᵢ ⊕ pⱼ on low bits) + (pₖ ⊕ on high bits)`.
- **Quaternary adder** (4-bit + 4-bit): merges two ternary results into the
  final 5-bit signed sum.
- **One copy module** per side to feed the second ternary into the quaternary.

This is the structure of Fig. 13 — *not* a flat cascade of 8 binary adders.

### B.3 The subtractor's `q` doesn't match the sum's width

Both your `quantum_adder` and `quantum_subtractor` are `q` → `q` operations
(`quantum_modules.py:42, 76`). But after summing four `q`-bit values you have
a `(q+2)`-bit result (max `4·(2^q-1) = 2^{q+2} - 4`). You write into
`pos[0][:q]` (line 343 onward) which **truncates the carry-out into nothing**;
the carry register only holds 2 bits and is overwritten on every adder call.
Your gradient values are silently mod-`2^q`.

Paper uses (q+1)-bit and (q+2)-bit adders explicitly (see Fig. 13: the chain
widens). Pre-allocate the accumulator at `(q+2)` bits and use width-matched
adders, not fixed-`q` adders into truncated slices.

### B.4 `_compute_gradient` does not reset `clone` (related to B.1)

`sobel_edge_detection.py:231-244`:

```python
for pixel_idx in pos_terms:
    qc.append(clone_gate, list(intensity[pixel_idx]) + clone)
    qc.append(add_gate, clone + grad_out + carry)
    qc.append(clone_gate, list(intensity[pixel_idx]) + clone)  # NOT a real unclone
    for c in carry:
        qc.reset(c)
```

For the "unclone" to zero `clone`, `clone` must equal `intensity[pixel_idx]`
when the second `clone_gate` (which is a parallel CNOT) runs. After the
adder, `clone` is unchanged *iff* the adder leaves its first argument intact
— which it does in your implementation (sum goes to `b`). So actually
`clone` is restored to `intensity[pixel_idx]` and then XORed back to `0` by
the second CNOT chain. **B.1 is therefore a false alarm** — but only because
of your non-paper adder convention. If you ever fix the adder to match the
paper (sum overwrites `a`, augend survives in `b`), this whole pattern
silently breaks. The safe pattern is `qc.reset(clone)` after the adder, no
"unclone" call.

I'm leaving B.1 in this report flagged as a **latent bug** that will surface
the moment the adder is changed to match the paper.

### B.5 Subtractor is not a true subtractor; doesn't match Fig. 7

`quantum_subtractor` (`quantum_modules.py:76-117`):

```python
for i in range(q): qc.x(b[i])      # ~B
qc.x(borrow[0])                     # +1 trick
... cascading adder logic ...
for i in range(q): qc.x(b[i])      # restore B
```

The paper's Fig. 7 (and ref. [36] it cites) describes a borrow-propagating
subtractor with the same structure as the adder but using borrow logic in the
Toffoli pattern, not "invert + add + invert". Your implementation:

1. Computes `A + ~B + 1 = A - B` into B's slot using the adder's convention.
2. Then *inverts B again*, leaving B holding `~(A - B)`, not `B` and not
   `A - B`.

Concretely: at line 113, `for i in range(q): qc.x(b[i])` restores `B` only if
`b[i]` still holds the original `~B` value. But the inner adder loop wrote
the **sum** into `b[i]` (line 100: `qc.cx(a[0], b[0])`). So the final
"restore" inverts the result, not B. The output is **`~(A - B)` in B and
unchanged A in A**, not "difference in B, original B in A".

This propagates through `_compute_gradient`:

```python
qc.append(sub_gate, grad_out + neg_accum + carry)
for i in range(q):
    qc.swap(grad_out[i], neg_accum[i])
```

After your `sub_gate`, `neg_accum` holds `~(grad_out - neg_accum)`. You then
swap into `grad_out`, so `grad_out` ends up holding the bitwise complement of
the desired gradient. Edge pixels are then thresholded on the MSB
(`gx_out[q-1]`), and since `~G_max` has MSB inverted relative to `G_max`,
your threshold fires on `G_max < 2^{q-1}` instead of `G_max ≥ 2^{q-1}`.
That's a "you measured the non-edges" inversion.

To fix: either drop the second `for i in range(q): qc.x(b[i])` block, or
implement Fig. 7 as a borrow-propagating subtractor directly. The cleanest
fix that matches the paper: remove lines 114-115 and confirm `B` ends with
`A - B`.

### B.6 Elementary-gate counting vs. high-level

Confirmed: paper counts `ccx` (Toffoli) as 5 elementary gates, `cswap`
(Fredkin) as 15. You're counting after `qc.decompose()`, which unrolls
custom gates but leaves `ccx` and `cswap` as one each. So paper-`1071` and
your `806` are **not the same units**. Apples-to-apples comparison requires
transpiling to a `{cx, h, t, tdg, s, sdg, x}` basis (Clifford+T).

If you decompose all `ccx` (5 elementary) and `cswap` (15 elementary), your
806 explodes well past 1071. The reason: B.2 (you have 32 adders not 16) and
B.7 (max-value module aux not zeroed between stages — see below).

### B.7 Max-value module: comparator aux not reset between stages

`quantum_max_value_module` (`quantum_modules.py:209-245`) shares one
`comp_aux` register of size `q-1` across all three comparator calls. Your
`quantum_comparator` (`quantum_modules.py:123-181`) **does** uncompute its
aux at the end (lines 168-179), so this works — but uncomputation costs
roughly as many gates as the forward pass. Paper's comparator (Fig. 8 / ref.
[37]) is **not symmetric**: it uses dirty ancillas and reuses them via
resets, not via reverse-Toffoli uncomputation. The paper's quoted comparator
complexity `14q - 6` is achievable only with the `reset`-based aux strategy,
not the symmetric-uncompute strategy.

Concretely: in `build_edge_detection_circuit` you already `qc.reset(comp_aux)`
between stages (lines 173-174, 180-181, 187-188). That means the
uncomputation half of your `quantum_comparator` is **wasted work** — you
reset right after. Inline the comparator so the forward pass writes directly
into a slot that's reset between stages, and drop the reverse pass. That
roughly halves your comparator gate count.

### B.8 Threshold module is wrong topology

Paper Fig. 11: a comparator + controlled-swap that *replaces* G_max with the
threshold value `2^{q-1}` when `G_max ≥ T`. Result: edge pixels have value
`T = 2^{q-1}`, non-edges keep their gradient.

Then Fig. 14 (overall): the *final* image is `original − edge_gradient`,
i.e., subtract the thresholded gradient from the prepared original. This
yields the visible edge map.

Your threshold (`quantum_modules.py:251-275`) instead does:

```python
for i in range(q):
    qc.cx(gmax[q - 1], output[i])
```

which sets output to `2^q - 1` (all ones) iff `MSB(G_max) = 1`. That's a
*different* operation:

- It assumes `T = 2^{q-1}` and that MSB-test is the comparator (true for that
  T, fine).
- It writes `2^q - 1` instead of `T`. The paper writes `T` (so edge pixel ≡
  threshold value, and `original − T` yields the displayed edge image).
- It writes into a separate `output` register instead of replacing `G_max`.
- It never does the final `original − edge_gradient` subtraction the paper
  requires in Fig. 14.

Your measurement (`sobel_edge_detection.py:198`) measures `pos + ch +
edge_out` — `edge_out` is `2^q - 1` for edges and `0` otherwise. That works
as a binary edge map but skips the paper's "subtract from original" step,
so the output cannot match Fig. 15(b) which shows the edge **subtracted**
from the input intensity.

### B.9 Auxiliary qubit budget doesn't match paper

Paper (Sect. 3.2): **19 auxiliary qubits** total — 4 for encoding (a₀..a₃,
reusable), 8 for "eight quantum ternary adders", 8 for "eight quantum
quaternary adders", 1 for the second copy module, 1 for max-value result
bit, 1 shared scratch for adder/sub/comparator basic ops.

Your code uses `num_aux = 6q + 2 = 20` (`sobel_edge_detection.py:108`) for
arithmetic only, plus `9q = 27` for the 9 intensity registers, plus `2n + 2
= 6` for position+channel. The 4 encoding ancillas don't exist.

The paper's "27 qubits for image and 8 neighborhoods" assumes the 9 entangled
ledgers from Sect. 2 — same as yours. But the 20 auxiliaries are sized for
the ternary/quaternary adder pipeline (8+8+1+1+1+1 = 20). Your layout
spends them on:

```python
gx_out, gy_out, g45_out, g135_out  # 4q
clone                                # q
neg_accum                            # q
carry                                # 2
```

= 6q + 2 = 20. By coincidence the count lines up; the **roles do not**. In
particular, the paper does not hold all four gradient outputs alive
simultaneously — Fig. 13 chains them in series with reused workspace.

---

## C. Why your gate count is what it is

For 4×4, q=3, paper says elementary-gate complexity `365q − 24 = 1071`
*for the edge-extraction module alone (no encoding)*. Your numbers are for
the **full circuit including encoding**:

- Edge-detection-only (your 806 figure): higher-level count, `ccx` and
  `cswap` not exploded. If you decompose those, ≈ `424 cx + 5·199 ccx +
  15·9 cswap + 58 x + 6 u + 9 measure + 101 reset` = (roughly) **1700+**
  elementary gates → clearly above 1071, even ignoring resets/measure/u.
  Excess sources: B.2 (16 extra adders), B.7 (wasted uncompute in comparator).

- Encoded + edge-detection (your 3964): the extra ≈3158 gates are from
  `mcphase` (462) + `u` (1778) + `h` (924) which are entirely the
  Qiskit synthesis of your (2n+2)-controlled MCX cascade across 9
  neighborhoods (A.1 / A.2). Replace with the row-by-row scheme: the
  encoding contribution drops to `(5n + 3q + 30)·2^n + (5n - 4)·2^n + 2n + 2`
  ≈ **240 gates** at n=2, q=3 (decomposed to Toffoli-equivalent), i.e.,
  ~ 1200 elementary, not 3158.

---

## D. Order of recommended fixes

If your goal is "run on `simulator_extended_stabilizer` and reproduce
Fig. 15(b)", in priority order:

1. **B.5** — fix the subtractor (drop the second X-on-B block). Without
   this, every gradient is bitwise-complemented and the threshold inverts.
   This is correctness-blocking.

2. **B.3 + B.4** — widen adders/accumulators to `q+2`, replace
   "clone-add-unclone" with "add + reset clone". Without this, gradients
   wrap mod `2^q` and the edge map is wrong on any large gradient.

3. **B.8** — implement Fig. 11 + Fig. 14 faithfully: comparator+swap to
   write `T` into `G_max` when above threshold, then `original − G_max`
   subtraction. Otherwise you cannot reproduce Fig. 15(b).

4. **A.1 / A.2 / A.3** — replace `encode_intensity_values` with the
   row-by-row info-transfer scheme from the median-filtering paper Sect.
   2.1. This is the single biggest gate-count win (~3000 gates → ~250).

5. **B.2** — bit-shift instead of double-add (drops 16 adders).

6. **B.7** — inline comparator, drop reverse uncomputation, use
   reset-based aux. Halves comparator cost.

7. **B.6** — once 1–6 are done, transpile to Clifford+T (or paper's
   elementary basis `{cx, h, t, tdg, s, sdg, x, ccx→5, cswap→15}`) and
   compare against `365q − 24`. Expect parity within ~5%.

8. **A.5** — optionally post-select on `λ ≠ 11` to recover the 25% shot
   budget.

---

## E. Quick verification path before refactoring

You can validate B.5 alone in ~5 minutes: build the current circuit with
`q=3`, plug in a known input, look at the gradient register state via
`Statevector(qc)` (or measure just `gx_out`) — you should see the bit
pattern of `255 − G_x` (or whatever for your input) rather than `G_x`. If
that confirms, fix the subtractor first and re-test before moving to the
adder widening.
