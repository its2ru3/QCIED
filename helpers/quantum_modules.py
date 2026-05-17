"""Quantum modules for color-image edge detection (Yuan et al. 2025).

Implements Figs. 5-11 with paper-faithful contracts. Built for qiskit >= 2.

Modules
-------
* `quantum_cloning_module(q)` (Fig. 5): U_c |C> |0>^q -> |C> |C>.  q CNOTs.
* `quantum_adder(q)` (Fig. 6): wraps qiskit's HalfAdderGate.
    Inputs: |A>[q] |B>[q] |0>      Output: |A>[q] |B+A>[q] |carry_out>
    That is, B is overwritten with (A+B) mod 2^q on its q wires, and the
    carry-out is written into a single auxiliary qubit.
    NOTE: The paper draws sum overwriting *A* and preserving *B*; qiskit's
    library does the opposite (sum overwrites *B*, A preserved). Behaviour is
    symmetric so we pick whichever matches the rest of the pipeline. We
    consistently use "augend register receives sum" throughout this codebase.
* `quantum_subtractor(q)` (Fig. 7): wraps a subtractor built from
    SUB(A, B) := X-on-B, ADD, X-on-B  (yields B := (B - A) mod 2^q with
    carry-out on the borrow qubit). Combined with proper handling, computes
    A - B into a wider register.
* `quantum_comparator(q)` (Fig. 8): writes |A < B> into cout. Uses (q-1)+1
    auxiliary qubits internally, all reset to |0> by the module.
* `quantum_swap(q)` (Fig. 9): q parallel Fredkin gates with shared control.
* `quantum_threshold_module(q)` (Fig. 11): factory; main pipeline inlines.
* `quantum_max_value_module(q)` (Fig. 10): factory; main pipeline inlines.

Qubit budgets follow the paper. Auxiliary registers are reset to |0> at the
end of every module call; callers may share a single ancilla pool across
sequential calls.
"""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.library import HalfAdderGate


# ---------------------------------------------------------------------------
# Fig. 5
# ---------------------------------------------------------------------------
def quantum_cloning_module(q):
    """Fig. 5. U_c |C>|0>^q = |C>|C>. Returns a Gate with 2q qubits."""
    src = QuantumRegister(q, "src")
    tgt = QuantumRegister(q, "tgt")
    qc = QuantumCircuit(src, tgt, name=f"U_c({q})")
    for i in range(q):
        qc.cx(src[i], tgt[i])
    return qc.to_gate(label="U_c")


# ---------------------------------------------------------------------------
# Fig. 6
# ---------------------------------------------------------------------------
def quantum_adder(q):
    """Fig. 6.  Returns a Gate that does:

        |A>[q] |B>[q] |c_out>[1]  ->  |A>[q] |(A+B) mod 2^q>[q] |c_out XOR (carry)>[1]

    where c_out is the carry-out qubit (auxiliary). When the caller starts
    with c_out = |0>, this yields the exact (q+1)-bit sum spread across
    B and c_out: low q bits in B, high bit in c_out.
    """
    a = QuantumRegister(q, "a")
    b = QuantumRegister(q, "b")
    c = QuantumRegister(1, "c_out")
    qc = QuantumCircuit(a, b, c, name=f"ADD({q})")
    # qiskit HalfAdderGate(q) acts on 2q+1 qubits: [a_0..a_{q-1}, b_0..b_{q-1}, c_out]
    # Output: a unchanged; b := (a+b) mod 2^q; c_out := c_out XOR carry.
    qc.append(HalfAdderGate(q), list(a) + list(b) + list(c))
    return qc.to_gate(label="ADD")


# ---------------------------------------------------------------------------
# Fig. 7
# ---------------------------------------------------------------------------
def quantum_subtractor(q):
    """Fig. 7.  Returns a Gate that does:

        |A>[q] |B>[q] |b_out>[1]  ->  |A>[q] |(B - A) mod 2^q>[q] |b_out XOR (borrow)>[1]

    Built from the half adder by complementing B, adding, complementing back:
        B - A == NOT(NOT B + A)   (two's complement identity, mod 2^q)
    The borrow-out is captured on b_out.
    """
    a = QuantumRegister(q, "a")
    b = QuantumRegister(q, "b")
    borrow = QuantumRegister(1, "b_out")
    qc = QuantumCircuit(a, b, borrow, name=f"SUB({q})")
    # NOT B
    for i in range(q):
        qc.x(b[i])
    # b := (a + b) mod 2^q, borrow := (a + b) carry-out
    qc.append(HalfAdderGate(q), list(a) + list(b) + list(borrow))
    # NOT B again -> b holds (B - A) mod 2^q.
    # The carry-out of (NOT B + A) is exactly the borrow flag (carry=1 iff
    # A > B, i.e. iff B - A underflows), so we don't flip `borrow`.
    for i in range(q):
        qc.x(b[i])
    return qc.to_gate(label="SUB")


# ---------------------------------------------------------------------------
# Fig. 8
# ---------------------------------------------------------------------------
def quantum_comparator(q):
    """Fig. 8. Writes (A < B) into cout; A, B, and all aux qubits preserved/restored.

    Layout (gate qubit order):
      a[0..q-1]   : A register, preserved at end.
      b[0..q-1]   : B register, preserved at end.
      aux[0..q-1] : q work qubits (A clone), reset to |0>.
      tmp[0]      : 1 working borrow flag, reset to |0>.
      cout[0]     : output flag; XOR-ed with (A < B).

    Total: 3q + 2 qubits.

    Construction (compute-copy-uncompute):
      1. aux := A           (q CNOTs)
      2. SUB(B, aux)        => aux := (A - B) mod 2^q, tmp := (A < B)
      3. CNOT tmp -> cout
      4. SUB^{-1}(B, aux)    => aux back to A, tmp back to 0
      5. aux := 0           (q CNOTs)

    Cost: 2q CNOTs + 2 SUB invocations + 1 CNOT.
    """
    if q < 1:
        raise ValueError("q must be >= 1")
    a = QuantumRegister(q, "a")
    b = QuantumRegister(q, "b")
    aux = QuantumRegister(q, "aux")
    tmp = QuantumRegister(1, "tmp")
    cout = QuantumRegister(1, "cout")
    qc = QuantumCircuit(a, b, aux, tmp, cout, name=f"CMP({q})")
    sub = quantum_subtractor(q)
    for i in range(q):
        qc.cx(a[i], aux[i])
    qc.append(sub, list(b) + list(aux) + [tmp[0]])
    qc.cx(tmp[0], cout[0])
    qc.append(sub.inverse(), list(b) + list(aux) + [tmp[0]])
    for i in range(q):
        qc.cx(a[i], aux[i])
    return qc.to_gate(label="CMP")


# ---------------------------------------------------------------------------
# Fig. 9
# ---------------------------------------------------------------------------
def quantum_swap(q):
    """Fig. 9. Conditionally swap A<->B based on a single control qubit."""
    ctrl = QuantumRegister(1, "ctrl")
    a = QuantumRegister(q, "a")
    b = QuantumRegister(q, "b")
    qc = QuantumCircuit(ctrl, a, b, name=f"SWAP({q})")
    for i in range(q):
        qc.cswap(ctrl[0], a[i], b[i])
    return qc.to_gate(label="SWAP")


# ---------------------------------------------------------------------------
# Fig. 10 (factory; main pipeline inlines)
# ---------------------------------------------------------------------------
def quantum_max_value_module(q):
    """Reference factory for MAX(Gx, Gy, G45, G135) — NOT USED by the pipeline.

    The main pipeline inlines three (Com + Swap) stages on a shared auxiliary
    pool with `reset` between stages (honouring the paper's 19-qubit budget).
    This factory uses fresh flag + comparator-aux qubits per stage and is kept
    only for testing.

    Layout per stage uses comparator with (q + 1) aux qubits (q for clone, 1
    for tmp).
    """
    gx = QuantumRegister(q, "Gx")
    gy = QuantumRegister(q, "Gy")
    g45 = QuantumRegister(q, "G45")
    g135 = QuantumRegister(q, "G135")
    flags = QuantumRegister(3, "flags")
    caux_a = QuantumRegister(q + 1, "cmp_aux_a")
    caux_b = QuantumRegister(q + 1, "cmp_aux_b")
    caux_c = QuantumRegister(q + 1, "cmp_aux_c")
    qc = QuantumCircuit(gx, gy, g45, g135, flags, caux_a, caux_b, caux_c,
                        name=f"MAX({q})")
    cmp_g = quantum_comparator(q)
    swp_g = quantum_swap(q)

    def cmp_swap(hi, lo, fl, ca):
        # cmp expects: [a..q-1, b..q-1, aux..q-1, tmp, cout]
        qc.append(cmp_g, list(hi) + list(lo) + list(ca[:q]) + [ca[q]] + [fl])
        qc.append(swp_g, [fl] + list(hi) + list(lo))

    cmp_swap(gx, gy, flags[0], caux_a)
    cmp_swap(g45, g135, flags[1], caux_b)
    cmp_swap(gx, g45, flags[2], caux_c)
    return qc.to_gate(label="MAX")


# ---------------------------------------------------------------------------
# Fig. 11 (factory; main pipeline inlines)
# ---------------------------------------------------------------------------
def quantum_threshold_module(q):
    """Build U_T as a self-contained gate.

    Fig. 11 contract:
        Inputs: |1>^q (constant), |G_max>, |1>^(q-1) (constant), aux.
        Effect: if G_max >= 2^(q-1), swap G_max <-> |1>^q (so the G_max wire
                becomes 2^q-1, marking 'edge'); else G_max unchanged.

    Because T = 2^(q-1) has only the MSB set, "G_max >= T" reduces to
    "MSB(G_max) == 1". We use that simplification: flag := MSB(G_max), then
    conditionally swap, then uncompute flag.
    """
    ones_q = QuantumRegister(q, "ones_q")
    gmax = QuantumRegister(q, "gmax")
    flag = QuantumRegister(1, "flag")
    qc = QuantumCircuit(ones_q, gmax, flag, name=f"U_T({q})")
    qc.cx(gmax[q - 1], flag[0])
    qc.append(quantum_swap(q), [flag[0]] + list(gmax) + list(ones_q))
    # After the swap, MSB(gmax) is still 1 if the swap fired (gmax now = 2^q-1)
    # or unchanged otherwise. Either way, MSB(gmax)==1 IFF flag==1, so we can
    # uncompute with the same CNOT.
    qc.cx(gmax[q - 1], flag[0])
    return qc.to_gate(label="U_T")


__all__ = [
    "quantum_cloning_module",
    "quantum_adder",
    "quantum_subtractor",
    "quantum_comparator",
    "quantum_swap",
    "quantum_max_value_module",
    "quantum_threshold_module",
]
