"""
Quantum Modules for Color Image Edge Detection
Based on the paper: Quantum color image edge detection algorithm based on Sobel operator

This module implements all the basic quantum operations needed for the edge detection algorithm:
1. Quantum Cloning Module (Fig. 5)
2. Quantum Adder Module (Fig. 6) 
3. Quantum Subtractor Module (Fig. 7)
4. Quantum Comparator Module (Fig. 8)
5. Quantum Swap Module (Fig. 9)
6. Maximum Value Calculation Module (Fig. 10)
7. Quantum Threshold Module (Fig. 11)
"""

from qiskit import QuantumCircuit, QuantumRegister
import numpy as np


# ---------------------------------------------------------------------------
# Fig. 5: Quantum Cloning Module
# ---------------------------------------------------------------------------
def quantum_cloning_module(q):
    """
    Quantum Cloning Module (Fig. 5)
    Copies qubit sequence |C> to another qubit sequence |0>^q
    U_c(|C> |0>^q) = |C> |C>
    
    Implementation: q parallel CNOT gates from source[i] -> target[i]
    Total qubits: 2q
    """
    source = QuantumRegister(q, 'source')
    target = QuantumRegister(q, 'target')
    qc = QuantumCircuit(source, target)
    for i in range(q):
        qc.cx(source[i], target[i])
    return qc.to_gate(label="CLONE")


# ---------------------------------------------------------------------------
# Fig. 6: Quantum Adder Module
# ---------------------------------------------------------------------------
def quantum_adder(q):
    """
    Quantum Adder Module (Fig. 6)
    Ripple-carry adder for two q-bit numbers.
    
    Input layout: |A>[q] |B>[q] |carry>[2]  (total: 2q+2 qubits)
    Result: sum stored in B register + carry bits; A register preserved
    
    Per paper Fig. 6: cascading half/full adder modules using CNOT and Toffoli gates.
    """
    a = QuantumRegister(q, 'a')
    b = QuantumRegister(q, 'b')
    carry = QuantumRegister(2, 'carry')
    qc = QuantumCircuit(a, b, carry)
    
    # Bit 0: half adder
    qc.ccx(a[0], b[0], carry[0])
    qc.cx(a[0], b[0])
    
    # Bits 1..q-1: full adder with alternating carry qubits
    for i in range(1, q):
        c_in = carry[(i - 1) % 2]
        c_out = carry[i % 2]
        qc.ccx(a[i], b[i], c_out)
        qc.cx(a[i], b[i])
        qc.ccx(c_in, b[i], c_out)
        qc.cx(c_in, b[i])
    
    return qc.to_gate(label="ADD")


# ---------------------------------------------------------------------------
# Fig. 7: Quantum Subtractor Module
# ---------------------------------------------------------------------------
def quantum_subtractor(q):
    """
    Quantum Subtractor Module (Fig. 7)
    Computes A - B using two's complement: A - B = A + (~B + 1)
    
    Input layout: |A>[q] |B>[q] |borrow>[2]  (total: 2q+2 qubits)
    Result: difference stored in B register; A register preserved; B restored
    
    Per paper Fig. 7: NOT gates invert B, adder computes A + ~B + 1, then NOT gates restore B.
    """
    a = QuantumRegister(q, 'a')
    b = QuantumRegister(q, 'b')
    borrow = QuantumRegister(2, 'borrow')
    qc = QuantumCircuit(a, b, borrow)
    
    # Complement B for two's complement
    for i in range(q):
        qc.x(b[i])
    
    # Set initial carry = 1 (for +1 in two's complement)
    qc.x(borrow[0])
    
    # Bit 0: half adder with carry-in = 1
    qc.ccx(a[0], b[0], borrow[1])
    qc.cx(a[0], b[0])
    qc.ccx(borrow[0], b[0], borrow[1])
    qc.cx(borrow[0], b[0])
    
    # Bits 1..q-1: full adder
    for i in range(1, q):
        c_in_idx = 1 if i == 1 else (i - 1) % 2
        c_out_idx = 0 if i == 1 else i % 2
        qc.ccx(a[i], b[i], borrow[c_out_idx])
        qc.cx(a[i], b[i])
        qc.ccx(borrow[c_in_idx], b[i], borrow[c_out_idx])
        qc.cx(borrow[c_in_idx], b[i])
    
    # Restore B
    for i in range(q):
        qc.x(b[i])
    
    return qc.to_gate(label="SUB")


# ---------------------------------------------------------------------------
# Fig. 8: Quantum Comparator Module
# ---------------------------------------------------------------------------
def quantum_comparator(q):
    """
    Quantum Comparator Module (Fig. 8)
    Compares two q-bit numbers from MSB to LSB.
    
    Input: |A>[q] |B>[q] |aux>[q-1] |C_out>[1]  (total: 3q qubits)
    Output: |A> |B> |aux=0> |C_out> where C_out = 1 if A < B, else C_out = 0
    
    Per paper Fig. 8: symmetrical structure of CNOT and Toffoli gates,
    evaluates bits from MSB to LSB. Uses q-1 auxiliary qubits for intermediate results.
    Aux qubits are returned to |0> after computation.
    """
    a = QuantumRegister(q, 'a')
    b = QuantumRegister(q, 'b')
    aux = QuantumRegister(q - 1, 'aux')
    cout = QuantumRegister(1, 'cout')
    qc = QuantumCircuit(a, b, aux, cout)
    
    # Forward pass: compute from MSB to LSB
    # aux[i] stores whether A < B determined by bits q-1 down to i+1
    # We use aux[q-2] for MSB result, then propagate down
    
    # MSB (bit q-1): if a[q-1]=0 and b[q-1]=1 → A < B at MSB
    qc.x(a[q-1])
    qc.ccx(a[q-1], b[q-1], aux[q-2])
    qc.x(a[q-1])
    
    # Bits q-2 down to 1: propagate comparison
    for i in range(q-2, 0, -1):
        # a[i]=0 and b[i]=1 → A < B at this bit position
        qc.x(a[i])
        qc.ccx(a[i], b[i], aux[i-1])
        qc.x(a[i])
        # OR with higher-bit result: if already A < B from above, propagate
        qc.cx(aux[i], aux[i-1])
    
    # LSB (bit 0): combine into cout
    qc.x(a[0])
    qc.ccx(a[0], b[0], cout[0])
    qc.x(a[0])
    qc.cx(aux[0], cout[0])
    
    # Reverse pass: uncompute auxiliary qubits (restore to |0>)
    # Forward was: for i in range(q-2, 0, -1): Toffoli→aux[i-1], CNOT aux[i]→aux[i-1]
    # Reverse: for i in range(1, q-1): undo CNOT, undo Toffoli
    for i in range(1, q-1):
        # Reverse the CNOT (aux[i] → aux[i-1])
        qc.cx(aux[i], aux[i-1])
        # Reverse the Toffoli (a[i], b[i] → aux[i-1])
        qc.x(a[i])
        qc.ccx(a[i], b[i], aux[i-1])
        qc.x(a[i])
    
    # Uncompute MSB auxiliary
    qc.x(a[q-1])
    qc.ccx(a[q-1], b[q-1], aux[q-2])
    qc.x(a[q-1])
    
    return qc.to_gate(label="COMP")


# ---------------------------------------------------------------------------
# Fig. 9: Quantum Controlled Swap Module
# ---------------------------------------------------------------------------
def quantum_swap(q):
    """
    Quantum-Controlled Swap Module (Fig. 9)
    Conditionally swaps two q-bit registers based on control bit.
    
    Input: |C_out>[1] |A>[q] |B>[q]  (total: 2q+1 qubits)
    If C_out=1: swaps A and B (so max goes to A, min to B)
    
    Per paper Fig. 9: q parallel Fredkin (controlled-SWAP) gates.
    """
    control = QuantumRegister(1, 'control')
    a = QuantumRegister(q, 'a')
    b = QuantumRegister(q, 'b')
    qc = QuantumCircuit(control, a, b)
    for i in range(q):
        qc.cswap(control[0], a[i], b[i])
    return qc.to_gate(label="CSWAP")


# ---------------------------------------------------------------------------
# Fig. 10: Maximum Value Calculation Module
# ---------------------------------------------------------------------------
def quantum_max_value_module(q):
    """
    Maximum Value Calculation Module (Fig. 10)
    Finds maximum value among four q-bit gradient values.
    
    Input: |Gx>[q] |G45>[q] |Gy>[q] |G135>[q] |flags>[3]  (total: 4q+3 qubits)
    Output: |G_max> in Gx register
    
    Per paper Fig. 10:
    - Stage 1: Compare Gx and G45, swap so larger is in Gx
    - Stage 2: Compare Gy and G135, swap so larger is in Gy
    - Stage 3: Compare winners (Gx, Gy), swap so max is in Gx
    """
    gx = QuantumRegister(q, 'gx')
    g45 = QuantumRegister(q, 'g45')
    gy = QuantumRegister(q, 'gy')
    g135 = QuantumRegister(q, 'g135')
    flags = QuantumRegister(3, 'flags')
    comp_aux = QuantumRegister(q - 1, 'comp_aux')  # Reusable aux for comparator
    qc = QuantumCircuit(gx, g45, gy, g135, flags, comp_aux)
    
    comp_gate = quantum_comparator(q)
    swap_gate = quantum_swap(q)
    
    # Stage 1: Compare Gx and G45 (per Fig. 10)
    qc.append(comp_gate, list(gx) + list(g45) + list(comp_aux) + [flags[0]])
    qc.append(swap_gate, [flags[0]] + list(gx) + list(g45))
    
    # Stage 2: Compare Gy and G135 (per Fig. 10)
    qc.append(comp_gate, list(gy) + list(g135) + list(comp_aux) + [flags[1]])
    qc.append(swap_gate, [flags[1]] + list(gy) + list(g135))
    
    # Stage 3: Compare winners
    qc.append(comp_gate, list(gx) + list(gy) + list(comp_aux) + [flags[2]])
    qc.append(swap_gate, [flags[2]] + list(gx) + list(gy))
    
    return qc.to_gate(label="MAX_CALC")


# ---------------------------------------------------------------------------
# Fig. 11: Quantum Threshold Module
# ---------------------------------------------------------------------------
def quantum_threshold_module(q):
    """
    Quantum Threshold Module (Fig. 11)
    Applies threshold T = 2^(q-1) to determine edge pixels.
    
    Input: |G_max>[q] |output>[q]  (total: 2q qubits)
    Output: |G_max> |edge_pixel> where edge_pixel = 2^q-1 if G_max >= T, else 0
    
    Per paper Fig. 11:
    1. Compare G_max with threshold T=2^(q-1)
    2. If G_max >= T: set output to 2^q-1 (all 1s) via controlled-X gates
    3. If G_max < T: output stays |0>
    
    Since T = 2^(q-1) = 100...0 in binary, checking the MSB of G_max
    is sufficient: MSB=1 means G_max >= T.
    """
    gmax = QuantumRegister(q, 'gmax')
    output = QuantumRegister(q, 'output')
    qc = QuantumCircuit(gmax, output)
    
    # If MSB of G_max is 1 (G_max >= 2^(q-1)), set all output bits to 1
    for i in range(q):
        qc.cx(gmax[q - 1], output[i])
    
    return qc.to_gate(label="THRESHOLD")


# ---------------------------------------------------------------------------
# Fig. 13: Edge Gradient Calculation Module (single pixel, single channel)
# ---------------------------------------------------------------------------
def quantum_gradient_calculation(q):
    """
    Edge Gradient Calculation Module (Fig. 13) for a single pixel and channel.
    
    Calculates all 4 gradients for a single color channel using the
    improved Sobel operator masks (Fig. 12 / Eqs. 7-10).
    
    Neighborhood pixel index mapping (3x3 window):
        0=(Y-1,X-1)  1=(Y-1,X)  2=(Y-1,X+1)
        3=(Y,X-1)    4=(Y,X)    5=(Y,X+1)
        6=(Y+1,X-1)  7=(Y+1,X)  8=(Y+1,X+1)
    
    Gradient equations from paper:
        Gx   = p2 + 2*p5 + p8 - p0 - 2*p3 - p6              (Eq. 7)
        Gy   = p6 + 2*p7 + p8 - p0 - 2*p1 - p2              (Eq. 8)
        G45  = p1 + 2*p2 + p5 - p3 - 2*p6 - p7              (Eq. 9)
        G135 = p5 + 2*p8 + p7 - p1 - 2*p0 - p3              (Eq. 10)
    
    Note: Eq. 9 has a typo in the paper (p(Y,X-1) appears with both + and - sign).
    The correct G45 from the mask is: -p3 - 2*p6 - p7 + p1 + 2*p2 + p5
    
    Input: 9 pixel registers [q each] + aux
    Output: 4 gradient registers [q+1 each] (extra bit for sign/overflow)
    
    Total qubits: 9*q + 9*q (clones) + 4*(q+1) (gradients) + 8*(q+2) (accum) + aux
    """
    # 9 neighborhood pixel intensity registers
    pixels = [QuantumRegister(q, f'p{i}') for i in range(9)]
    # Cloned copies (each pixel used in multiple gradient calculations)
    clones = [QuantumRegister(q, f'c{i}') for i in range(9)]
    # Gradient output registers (q+1 bits for sign handling)
    gx   = QuantumRegister(q + 1, 'gx')
    gy   = QuantumRegister(q + 1, 'gy')
    g45  = QuantumRegister(q + 1, 'g45')
    g135 = QuantumRegister(q + 1, 'g135')
    # Accumulation registers for positive and negative Sobel terms
    pos  = [QuantumRegister(q + 1, f'pos_g{i}') for i in range(4)]  # 4 gradients
    neg  = [QuantumRegister(q + 1, f'neg_g{i}') for i in range(4)]
    # Auxiliary qubits for adder/subtractor carry/borrow (2 per arithmetic op)
    # 4 gradients × (8 add + 1 sub) = 36 ops × 2 = 72, round up to 80
    aux = QuantumRegister(80, 'aux')
    
    all_regs = (pixels + clones + [gx, gy, g45, g135] + pos + neg + [aux])
    qc = QuantumCircuit(*all_regs)
    
    clone_gate = quantum_cloning_module(q)
    add_gate = quantum_adder(q)
    sub_gate = quantum_subtractor(q)
    
    # Step 1: Clone all 9 pixel values
    for i in range(9):
        qc.append(clone_gate, list(pixels[i]) + list(clones[i]))
    
    # Helper: weighted sum using adder
    # add_gate layout: |A>[q] |B>[q] |carry>[2] → sum in B
    # To compute A + B: put A in reg_a, B in reg_b, carry=|00>
    # To compute A + 2*B: add B twice to A
    
    aux_idx = 0  # Track auxiliary qubit usage
    
    # --- Gx = p2 + 2*p5 + p8 - p0 - 2*p3 - p6 (Eq. 7) ---
    # Positive: p2 + p5 + p5 + p8 → pos[0]
    qc.append(add_gate, list(clones[2]) + list(pos[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[5]) + list(pos[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[5]) + list(pos[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[8]) + list(pos[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Negative: p0 + p3 + p3 + p6 → neg[0]
    qc.append(add_gate, list(clones[0]) + list(neg[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[3]) + list(neg[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[3]) + list(neg[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[6]) + list(neg[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Gx = pos[0] - neg[0]
    qc.append(sub_gate, list(pos[0][:q]) + list(neg[0][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    for i in range(q + 1):
        qc.cx(pos[0][i], gx[i])
    
    # --- Gy = p6 + 2*p7 + p8 - p0 - 2*p1 - p2 (Eq. 8) ---
    # Positive: p6 + p7 + p7 + p8 → pos[1]
    qc.append(add_gate, list(clones[6]) + list(pos[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[7]) + list(pos[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[7]) + list(pos[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[8]) + list(pos[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Negative: p0 + p1 + p1 + p2 → neg[1]
    qc.append(add_gate, list(clones[0]) + list(neg[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[1]) + list(neg[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[1]) + list(neg[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[2]) + list(neg[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Gy = pos[1] - neg[1]
    qc.append(sub_gate, list(pos[1][:q]) + list(neg[1][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    for i in range(q + 1):
        qc.cx(pos[1][i], gy[i])
    
    # --- G45 = p1 + 2*p2 + p5 - p3 - 2*p6 - p7 (Eq. 9) ---
    # Positive: p1 + p2 + p2 + p5 → pos[2]
    qc.append(add_gate, list(clones[1]) + list(pos[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[2]) + list(pos[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[2]) + list(pos[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[5]) + list(pos[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Negative: p3 + p6 + p6 + p7 → neg[2]
    qc.append(add_gate, list(clones[3]) + list(neg[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[6]) + list(neg[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[6]) + list(neg[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[7]) + list(neg[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # G45 = pos[2] - neg[2]
    qc.append(sub_gate, list(pos[2][:q]) + list(neg[2][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    for i in range(q + 1):
        qc.cx(pos[2][i], g45[i])
    
    # --- G135 = p5 + 2*p8 + p7 - p1 - 2*p0 - p3 (Eq. 10) ---
    # Positive: p5 + p8 + p8 + p7 → pos[3]
    qc.append(add_gate, list(clones[5]) + list(pos[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[8]) + list(pos[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[8]) + list(pos[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[7]) + list(pos[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # Negative: p1 + p0 + p0 + p3 → neg[3]
    qc.append(add_gate, list(clones[1]) + list(neg[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[0]) + list(neg[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[0]) + list(neg[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    qc.append(add_gate, list(clones[3]) + list(neg[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    # G135 = pos[3] - neg[3]
    qc.append(sub_gate, list(pos[3][:q]) + list(neg[3][:q]) + [aux[aux_idx], aux[aux_idx+1]])
    aux_idx += 2
    for i in range(q + 1):
        qc.cx(pos[3][i], g135[i])
    
    return qc.to_gate(label="GRADIENT_CALC")
