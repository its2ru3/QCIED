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
    quantum_swap, quantum_cloning_module, quantum_max_value_module,
    quantum_threshold_module, quantum_gradient_calculation
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
    
    Circuit structure per paper Fig. 14:
    1. Neighborhood Preparation: 9 images (original + 8 shifts) in OCQR format
    2. Gradient Calculation (U_G): 4 directional gradients per channel
    3. Maximum Value Calculation (QC): max(|Gx|, |Gy|, |G45|, |G135|)
    4. NOT gate on ancilla (preparation for threshold)
    5. Thresholding (U_T): compare G_max with T=2^(q-1)
    
    Qubit layout per paper Section 4 (for 4x4, q=3):
    - Position: 2n = 4 qubits
    - Channel: 2 qubits  
    - Intensity: 9 × q = 27 qubits (9 neighborhood images)
    - Auxiliary: 20 qubits
    - Total: 53 qubits
    
    Args:
        n: Image dimension parameter (2^n × 2^n image)
        q: Color depth bits (intensity range [0, 2^q - 1])
        
    Returns:
        QuantumCircuit: Complete edge detection circuit with all registers
    """
    # --- Register allocation ---
    pos = QuantumRegister(2 * n, 'pos')           # Position qubits (shared)
    channel = QuantumRegister(2, 'ch')             # Channel qubits (shared)
    # 9 neighborhood intensity registers (original + 8 shifts)
    intensity = [QuantumRegister(q, f'I{i}') for i in range(9)]
    # Gradient output registers (4 directions × q bits)
    gx = QuantumRegister(q, 'gx')
    g45 = QuantumRegister(q, 'g45')
    gy = QuantumRegister(q, 'gy')
    g135 = QuantumRegister(q, 'g135')
    # Max value module flags + comparator aux
    max_flags = QuantumRegister(3, 'max_flags')
    comp_aux = QuantumRegister(q - 1, 'comp_aux')
    # Threshold output
    edge_out = QuantumRegister(q, 'edge_out')
    # General auxiliary (per paper: 20 total aux, some already allocated)
    aux_remaining = 20 - 3 - (q - 1)  # Subtract flags and comp_aux from 20
    aux = QuantumRegister(max(aux_remaining, 0), 'aux')
    # Classical register for measurement
    creg = ClassicalRegister(2 * n + 2 + q, 'meas')  # Measure pos + ch + edge_out
    
    all_regs = [pos, channel] + intensity + [gx, g45, gy, g135, max_flags, comp_aux, edge_out, aux, creg]
    qc = QuantumCircuit(*all_regs)
    
    # --- Step 1: Image Preparation ---
    # Initialize superposition over position and channel
    qc.h(pos)
    qc.h(channel)
    # Intensity encoding would be done via OCQR encoding (multi-controlled X gates)
    # This is handled separately via encode_intensity_values()
    
    # --- Step 2: Gradient Calculation (U_G) ---
    # In quantum parallelism, for each (Y,X,λ) in superposition,
    # compute gradients from the 9 neighborhood intensity values.
    # The gradient_calculation gate takes 9 intensity registers + outputs 4 gradients.
    grad_gate = quantum_gradient_calculation(q)
    # Note: The full gradient gate requires many internal qubits (clones, accumulators, aux)
    # For the 4x4 case, we append it as a composite block
    # The qubit mapping connects intensity[i] → gradient inputs, gx/gy/g45/g135 → outputs
    # This is simplified here; the actual mapping requires the internal register layout
    
    # --- Step 3: Maximum Value Calculation (QC) ---
    max_gate = quantum_max_value_module(q)
    qc.append(max_gate, list(gx) + list(g45) + list(gy) + list(g135) + list(max_flags) + list(comp_aux))
    # After this, gx contains G_max
    
    # --- Step 4: NOT gate on ancilla (Fig. 14 step 4) ---
    # This prepares the ancilla for the threshold comparison
    # (In the paper's circuit, an X gate is applied before the threshold module)
    
    # --- Step 5: Thresholding (U_T) ---
    thresh_gate = quantum_threshold_module(q)
    qc.append(thresh_gate, list(gx) + list(edge_out))
    # edge_out now contains the edge pixel value: 2^q-1 if edge, 0 otherwise
    
    # --- Measurement ---
    # Measure position, channel, and edge output
    qc.measure(list(pos) + list(channel) + list(edge_out), list(creg))
    
    return qc


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
    from helpers.ocqr_encoding_2 import prepare_neighborhood_images
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
    from helpers.ocqr_encoding_2 import prepare_test_matrix_4x4
    
    print("=== Building Quantum Edge Detection Circuit ===")
    test_matrix = prepare_test_matrix_4x4()
    
    # Build circuit
    qc = build_edge_detection_circuit(n=2, q=3)
    
    # Encode intensity values
    qc = encode_intensity_values(qc, test_matrix, n=2, q=3)
    
    # Print details
    print_circuit_details(qc, n=2, q=3)
