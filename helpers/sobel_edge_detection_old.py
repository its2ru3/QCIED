"""
Sobel Edge Detection for Quantum Color Images
Based on the paper: Quantum color image edge detection algorithm based on Sobel operator

This module implements the improved Sobel operator with 4-direction edge detection:
- Gx: Vertical gradient detection
- Gy: Horizontal gradient detection  
- G45: +45° diagonal gradient detection
- G135: +135° diagonal gradient detection

The improved Sobel operator uses the following masks (Fig. 12):

Gx = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
Gy = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
G45 = [[0, 1, 2], [-1, 0, 1], [-2, -1, 0]]
G135 = [[-2, -1, 0], [-1, 0, 1], [0, 1, 2]]

Final gradient: G = max(|Gx|, |Gy|, |G45|, |G135|)
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from .quantum_modules import (
    quantum_adder, quantum_subtractor, quantum_comparator,
    quantum_swap, quantum_cloning_module
)


def classical_sobel_gradients(rgb_matrix):
    """
    Classical implementation of the improved Sobel operator for verification.
    This helps validate the quantum implementation.
    
    Args:
        rgb_matrix: Input RGB matrix
        
    Returns:
        dict: Gradients in all 4 directions for each channel
    """
    h, w = rgb_matrix.shape[:2]
    gradients = {
        'Gx': np.zeros(rgb_matrix.shape, dtype=np.int16),
        'Gy': np.zeros(rgb_matrix.shape, dtype=np.int16), 
        'G45': np.zeros(rgb_matrix.shape, dtype=np.int16),
        'G135': np.zeros(rgb_matrix.shape, dtype=np.int16)
    }
    
    # Sobel kernels
    kernels = {
        'Gx': np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]),
        'Gy': np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]),
        'G45': np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]]),
        'G135': np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]])
    }
    
    # Apply convolution for each channel and gradient direction
    # Process ALL pixels including boundaries (zero-padding for out-of-bounds neighbors)
    for ch in range(3):  # R, G, B channels
        for grad_name, kernel in kernels.items():
            for y in range(h):
                for x in range(w):
                    # Build 3x3 neighborhood with zero-padding for boundaries
                    neighborhood = np.zeros((3, 3), dtype=rgb_matrix.dtype)
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < h and 0 <= nx < w:
                                neighborhood[dy + 1, dx + 1] = rgb_matrix[ny, nx, ch]
                    gradients[grad_name][y, x, ch] = np.sum(neighborhood * kernel)
    
    return gradients


def build_edge_detection_circuit(n=2, q=3):
    """
    Build the complete quantum edge detection circuit (Fig. 14) for a 2^n × 2^n image.

    Gradient calculation is inlined on the main circuit using a shared auxiliary
    register with reset gates for reuse, matching the paper's qubit layout.

    Circuit structure per paper Fig. 14:
    1. Neighborhood Preparation: 9 images (original + 8 shifts) in OCQR format
    2. Gradient Calculation (U_G): 4 directional gradients per channel (inline)
    3. Maximum Value Calculation (QC): max(|Gx|, |Gy|, |G45|, |G135|) (inline)
    4. Thresholding (U_T): compare G_max with T=2^(q-1) (inline)

    Qubit layout per paper Section 4 (for 4x4, q=3):
    - Position: 2n = 4 qubits
    - Channel: 2 qubits
    - Intensity: 9 × q = 27 qubits (9 neighborhood images)
    - Auxiliary: 6q + 2 qubits (20 for q=3)
    - Total: 2n + 2 + 15q + 2 = 53 qubits for n=2, q=3

    Args:
        n: Image dimension parameter (2^n × 2^n image)
        q: Color depth bits (intensity range [0, 2^q - 1])

    Returns:
        QuantumCircuit: Complete edge detection circuit with all registers
    """
    # --- Register allocation ---
    pos = QuantumRegister(2 * n, 'pos')
    ch = QuantumRegister(2, 'ch')
    intensity = [QuantumRegister(q, f'I{i}') for i in range(9)]

    # Shared auxiliary register: 6q + 2 qubits
    # For q=3: 20 qubits, matching paper
    num_aux = 6 * q + 2
    aux = QuantumRegister(num_aux, 'aux')

    creg = ClassicalRegister(2 * n + 2 + q, 'meas')

    all_regs = [pos, ch] + intensity + [aux, creg]
    qc = QuantumCircuit(*all_regs)

    # --- Aux sub-register layout ---
    gx_out = list(aux[0:q])
    gy_out = list(aux[q:2 * q])
    g45_out = list(aux[2 * q:3 * q])
    g135_out = list(aux[3 * q:4 * q])
    clone = list(aux[4 * q:5 * q])
    neg_accum = list(aux[5 * q:6 * q])
    carry = list(aux[6 * q:6 * q + 2])

    # Reusable workspace freed after gradient calculation
    flag = aux[4 * q]
    comp_aux_start = 4 * q + 1
    comp_aux = list(aux[comp_aux_start:comp_aux_start + q - 1])
    edge_out = list(aux[4 * q:5 * q])  # reuse clone space after gradients

    # --- Step 1: Image Preparation ---
    qc.h(pos)
    qc.h(ch)
    # Intensity encoding is applied separately via encode_intensity_values()

    # --- Step 2: Gradient Calculation (inline) ---
    add_gate = quantum_adder(q)
    sub_gate = quantum_subtractor(q)
    clone_gate = quantum_cloning_module(q)

    # Gx = p2 + 2*p5 + p8 - p0 - 2*p3 - p6  (Eq. 7)
    _compute_gradient(qc, q, add_gate, sub_gate, clone_gate,
                      intensity, gx_out, clone, neg_accum, carry,
                      pos_terms=[2, 5, 5, 8], neg_terms=[0, 3, 3, 6])

    # Gy = p6 + 2*p7 + p8 - p0 - 2*p1 - p2  (Eq. 8)
    _compute_gradient(qc, q, add_gate, sub_gate, clone_gate,
                      intensity, gy_out, clone, neg_accum, carry,
                      pos_terms=[6, 7, 7, 8], neg_terms=[0, 1, 1, 2])

    # G45 = p1 + 2*p2 + p5 - p3 - 2*p6 - p7  (Eq. 9)
    _compute_gradient(qc, q, add_gate, sub_gate, clone_gate,
                      intensity, g45_out, clone, neg_accum, carry,
                      pos_terms=[1, 2, 2, 5], neg_terms=[3, 6, 6, 7])

    # G135 = p5 + 2*p8 + p7 - p1 - 2*p0 - p3  (Eq. 10)
    _compute_gradient(qc, q, add_gate, sub_gate, clone_gate,
                      intensity, g135_out, clone, neg_accum, carry,
                      pos_terms=[5, 8, 8, 7], neg_terms=[1, 0, 0, 3])

    # Reset reusable workspace before max value calculation
    for qubit in clone + neg_accum + carry:
        qc.reset(qubit)

    # --- Step 3: Maximum Value Calculation (inline) ---
    comp_gate = quantum_comparator(q)
    swap_gate = quantum_swap(q)

    # Stage 1: Compare Gx and G45, swap so larger is in Gx
    qc.append(comp_gate, gx_out + g45_out + comp_aux + [flag])
    qc.append(swap_gate, [flag] + gx_out + g45_out)
    qc.reset(flag)
    for qubit in comp_aux:
        qc.reset(qubit)

    # Stage 2: Compare Gy and G135, swap so larger is in Gy
    qc.append(comp_gate, gy_out + g135_out + comp_aux + [flag])
    qc.append(swap_gate, [flag] + gy_out + g135_out)
    qc.reset(flag)
    for qubit in comp_aux:
        qc.reset(qubit)

    # Stage 3: Compare winners (Gx vs Gy), swap so max is in Gx
    qc.append(comp_gate, gx_out + gy_out + comp_aux + [flag])
    qc.append(swap_gate, [flag] + gx_out + gy_out)
    qc.reset(flag)
    for qubit in comp_aux:
        qc.reset(qubit)

    # Gx now holds G_max

    # --- Step 4: Thresholding (inline) ---
    # If MSB of Gx is 1 (G_max >= 2^(q-1)), set edge_out to 2^q - 1
    for i in range(q):
        qc.cx(gx_out[q - 1], edge_out[i])

    # --- Measurement ---
    qc.measure(list(pos) + list(ch) + edge_out, list(creg))

    return qc


def _compute_gradient(qc, q, add_gate, sub_gate, clone_gate,
                      intensity, grad_out, clone, neg_accum, carry,
                      pos_terms, neg_terms):
    """
    Compute one gradient direction inline on the main circuit.

    Flow:
      1. Accumulate positive Sobel terms into grad_out (via clone + add + unclone)
      2. Accumulate negative Sobel terms into neg_accum (via clone + add + unclone)
      3. Subtract: grad_out - neg_accum  (result lands in neg_accum)
      4. SWAP result back into grad_out
      5. Reset neg_accum and carry for reuse

    Args:
        qc: Main QuantumCircuit
        q: Bit depth
        add_gate: quantum_adder(q) gate
        sub_gate: quantum_subtractor(q) gate
        clone_gate: quantum_cloning_module(q) gate
        intensity: list of 9 intensity QuantumRegisters
        grad_out: list of q qubits for gradient output (accumulates positive sum)
        clone: list of q qubits for cloning workspace
        neg_accum: list of q qubits for negative sum accumulator
        carry: list of 2 qubits for adder/subtractor carry/borrow
        pos_terms: list of pixel indices for positive Sobel terms
        neg_terms: list of pixel indices for negative Sobel terms
    """
    # Positive terms: clone pixel, add to grad_out, unclone clone, reset carry
    for pixel_idx in pos_terms:
        qc.append(clone_gate, list(intensity[pixel_idx]) + clone)
        qc.append(add_gate, clone + grad_out + carry)
        qc.append(clone_gate, list(intensity[pixel_idx]) + clone)
        for c in carry:
            qc.reset(c)

    # Negative terms: clone pixel, add to neg_accum, unclone clone, reset carry
    for pixel_idx in neg_terms:
        qc.append(clone_gate, list(intensity[pixel_idx]) + clone)
        qc.append(add_gate, clone + neg_accum + carry)
        qc.append(clone_gate, list(intensity[pixel_idx]) + clone)
        for c in carry:
            qc.reset(c)

    # Subtract: grad_out - neg_accum  (result stored in neg_accum by sub_gate)
    qc.append(sub_gate, grad_out + neg_accum + carry)
    for c in carry:
        qc.reset(c)

    # Move result from neg_accum back to grad_out via SWAP
    for i in range(q):
        qc.swap(grad_out[i], neg_accum[i])

    # Reset neg_accum (now holds old grad_out positive sum)
    for a in neg_accum:
        qc.reset(a)


def encode_intensity_values(qc, rgb_matrix, n=2, q=3):
    """
    Encode pixel intensity values into the quantum circuit using OCQR encoding.
    Applies multi-controlled X gates to set intensity bits based on image data.
    
    This implements the image preparation step (Step 1) of Fig. 14.
    
    Args:
        qc: Quantum circuit with allocated registers
        rgb_matrix: 3D numpy array (2^n × 2^n × 3) with RGB values in [0, 2^q-1]
        n: Position qubits per dimension
        q: Color depth bits
        
    Returns:
        QuantumCircuit: Circuit with intensity encoding applied
    """
    size = 2 ** n
    
    # Get register references from the circuit
    # Assumes registers are named: pos, ch, I0..I8
    pos_reg = None
    ch_reg = None
    intensity_regs = []
    
    for reg in qc.qregs:
        if reg.name == 'pos':
            pos_reg = reg
        elif reg.name == 'ch':
            ch_reg = reg
        elif reg.name.startswith('I') and reg.name[1:].isdigit():
            intensity_regs.append(reg)
    
    if pos_reg is None or ch_reg is None:
        raise ValueError("Circuit must have 'pos' and 'ch' registers")
    
    # Encode the original image into I0 (central pixel)
    # For edge detection, we also need the 8 neighborhood images (I1-I8)
    from helpers.ocqr_encoding import prepare_neighborhood_images
    neighborhoods = prepare_neighborhood_images(rgb_matrix)
    
    for img_idx, neighborhood in enumerate(neighborhoods):
        if img_idx >= len(intensity_regs):
            break
        intensity_reg = intensity_regs[img_idx]
        
        for y in range(size):
            for x in range(size):
                for ch in range(3):  # R, G, B
                    val = neighborhood[y, x, ch]
                    if val == 0:
                        continue
                    
                    # Position binary (reversed for qubit indexing)
                    bin_y = format(y, f'0{n}b')[::-1]
                    bin_x = format(x, f'0{n}b')[::-1]
                    bin_channel = format(ch, '02b')[::-1]
                    bin_intensity = format(val, f'0{q}b')[::-1]
                    
                    controls = list(pos_reg) + list(ch_reg)
                    
                    # Apply X gates for |0> control states
                    for idx, bit in enumerate(bin_y):
                        if bit == '0':
                            qc.x(pos_reg[idx])
                    for idx, bit in enumerate(bin_x):
                        if bit == '0':
                            qc.x(pos_reg[n + idx])
                    for idx, bit in enumerate(bin_channel):
                        if bit == '0':
                            qc.x(ch_reg[idx])
                    
                    # Set intensity bits via multi-controlled X
                    for bit_idx, bit in enumerate(bin_intensity):
                        if bit == '1':
                            qc.mcx(controls, intensity_reg[bit_idx])
                    
                    # Uncompute X gates
                    for idx, bit in enumerate(bin_y):
                        if bit == '0':
                            qc.x(pos_reg[idx])
                    for idx, bit in enumerate(bin_x):
                        if bit == '0':
                            qc.x(pos_reg[n + idx])
                    for idx, bit in enumerate(bin_channel):
                        if bit == '0':
                            qc.x(ch_reg[idx])
    
    return qc


def print_circuit_details(qc, n=2, q=3):
    """
    Print detailed information about the edge detection circuit.
    
    Args:
        qc: Quantum circuit
        n: Image dimension parameter
        q: Color depth bits
    """
    print("=" * 60)
    print("QUANTUM EDGE DETECTION CIRCUIT DETAILS")
    print("=" * 60)
    print(f"Image size: {2**n} × {2**n}")
    print(f"Color depth: q = {q} bits (intensity range [0, {2**q - 1}])")
    print(f"Threshold: T = 2^(q-1) = {2**(q-1)}")
    print()
    
    print("Qubit breakdown:")
    total = 0
    for reg in qc.qregs:
        print(f"  {reg.name}: {len(reg)} qubits")
        total += len(reg)
    print(f"  TOTAL: {total} qubits")
    print()
    
    print(f"Circuit depth: {qc.depth()}")
    print(f"Total gates: {sum(qc.count_ops().values())}")
    print("Gate counts:")
    for gate, count in sorted(qc.count_ops().items(), key=lambda x: -x[1]):
        print(f"  {gate}: {count}")
    print()
    
    # Paper comparison
    paper_total = 2 * n + 2 + 9 * q + 20
    print(f"Paper's total qubit count (Section 4): {paper_total}")
    print(f"Our total qubit count: {total}")
    match = "✓" if total == paper_total else "✗"
    print(f"Match: {match}")


def classical_edge_detection(rgb_matrix, threshold=None):
    """
    Classical edge detection for comparison with quantum results.
    Based on paper: threshold T = 2^(q-1), edge pixels set to 2^q - 1 (max intensity)
    
    Args:
        rgb_matrix: Input RGB matrix with values in [0, 2^q - 1]
        threshold: Edge detection threshold (default: 2^(q-1) per paper)
        
    Returns:
        numpy.ndarray: Edge-detected image (edge pixels = max intensity, non-edge = 0)
    """
    # Calculate gradients using classical Sobel
    gradients = classical_sobel_gradients(rgb_matrix)
    
    # Calculate maximum gradient for each pixel and channel
    max_gradients = np.maximum.reduce([
        np.abs(gradients['Gx']), 
        np.abs(gradients['Gy']),
        np.abs(gradients['G45']), 
        np.abs(gradients['G135'])
    ])
    
    # Determine q from data range
    max_val = rgb_matrix.max()
    if max_val <= 7:
        q = 3  # [0, 7] range
    elif max_val <= 255:
        q = 8  # [0, 255] range
    else:
        q = int(np.ceil(np.log2(max_val + 1)))
    
    # Apply threshold per paper: T = 2^(q-1)
    if threshold is None:
        threshold = 2 ** (q - 1)
    
    # Max intensity value for edge pixels
    max_intensity = 2 ** q - 1
    
    # Create edge image: edge pixels = max_intensity, non-edge = 0
    # Paper threshold module (Fig. 11): G_max compared with 2^(q-1), larger → set to 2^q-1
    edge_image = np.where(max_gradients >= threshold, max_intensity, 0).astype(np.uint8)
    
    return edge_image, max_gradients, threshold


if __name__ == "__main__":
    # Build and test the quantum edge detection circuit for 4x4 image
    from helpers.ocqr_encoding import prepare_test_matrix_4x4
    
    print("=== Building Quantum Edge Detection Circuit ===")
    test_matrix = prepare_test_matrix_4x4()
    
    # Build circuit
    qc = build_edge_detection_circuit(n=2, q=3)
    
    # Encode intensity values
    qc = encode_intensity_values(qc, test_matrix, n=2, q=3)
    
    # Print details
    print_circuit_details(qc, n=2, q=3)
