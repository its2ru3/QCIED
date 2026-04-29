"""
OCQR Image Encoding Module
Based on the paper: Quantum color image edge detection algorithm based on Sobel operator

This module implements the Optimized Quantum Representation for color digital images (OCQR)
as described in Equation (1) of the paper:

|I> = 1/sqrt(2^(2n+1)) * sum_{lambda=0}^3 sum_{Y=0}^{2^n-1} sum_{X=0}^{2^n-1} 
       tensor_{i=0}^{q-1} |C_{YX}^i> |lambda> |YX>

where:
- lambda: color channel (00=R, 01=G, 10=B, 11=redundant)
- n: number of qubits for X and Y position each
- q: number of qubits for color intensity (range [0, 2^q - 1])
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from PIL import Image


def encode_ocqr_from_matrix(rgb_matrix, n=2, q=3):
    """
    Encodes a classical RGB matrix into the OCQR quantum representation.
    
    Args:
        rgb_matrix: 3D numpy array of shape (2^n, 2^n, 3) with RGB values
        n: power for 2^n x 2^n image size (default 2 means 4x4 image)
        q: color depth in bits (default 3 means 0-7 RGB values)
        
    Returns:
        QuantumCircuit: OCQR encoded quantum circuit
    """
    # Validate input matrix dimensions
    expected_size = 2**n
    if rgb_matrix.shape != (expected_size, expected_size, 3):
        raise ValueError(f"Matrix must be shape ({expected_size}, {expected_size}, 3)")
    
    print(f"Encoding {expected_size}x{expected_size} RGB matrix with {q}-bit color depth")
    print("Input matrix:")
    print("R channel:")
    print(rgb_matrix[:, :, 0])
    print("G channel:")
    print(rgb_matrix[:, :, 1])
    print("B channel:")
    print(rgb_matrix[:, :, 2])
    
    # Allocate quantum registers
    # Position information: n qubits for Y, n qubits for X
    pos_qubits = QuantumRegister(2*n, 'pos')
    
    # Color channel: 2 qubits (00=R, 01=G, 10=B, 11=redundant)
    channel_qubits = QuantumRegister(2, 'channel')
    
    # Color intensity: q qubits for each channel
    color_qubits = QuantumRegister(q, 'color')
    
    # Create quantum circuit
    qc = QuantumCircuit(pos_qubits, channel_qubits, color_qubits)
    
    # Step 1: Initialize superposition for position and channel
    # This creates uniform superposition over all positions and color channels
    qc.h(pos_qubits)
    qc.h(channel_qubits)
    
    # Step 2: Encode color values using multi-controlled X gates
    # For each pixel position and color channel, set the corresponding intensity
    
    for y in range(expected_size):
        for x in range(expected_size):
            for ch in range(3):  # R, G, B channels (skip redundant channel 11)
                val = rgb_matrix[y, x, ch]
                
                # Skip if pixel value is 0 (already in |0> state)
                if val == 0:
                    continue
                
                # Convert position to binary
                bin_y = format(y, f'0{n}b')  # Y position
                bin_x = format(x, f'0{n}b')  # X position
                bin_pos = bin_y + bin_x      # Combined position
                
                # Convert channel to binary
                bin_channel = format(ch, '02b')  # 00, 01, or 10
                
                # Convert intensity value to binary (LSB first for quantum encoding)
                bin_intensity = format(val, f'0{q}b')[::-1]  # Reverse for LSB first
                
                # Control qubits for multi-controlled operations
                controls = list(pos_qubits) + list(channel_qubits)
                
                # Prepare control states for multi-controlled X gates
                # Apply X gates to convert |0> control states to |1> for MCX operations
                for idx, bit in enumerate(reversed(bin_pos)):
                    if bit == '0':
                        qc.x(pos_qubits[idx])
                
                for idx, bit in enumerate(reversed(bin_channel)):
                    if bit == '0':
                        qc.x(channel_qubits[idx])
                
                # Apply multi-controlled X gates to set intensity bits
                for bit_idx, bit in enumerate(bin_intensity):
                    if bit == '1':
                        qc.mcx(controls, color_qubits[bit_idx])
                
                # Uncompute the X gates to restore control qubits
                for idx, bit in enumerate(reversed(bin_pos)):
                    if bit == '0':
                        qc.x(pos_qubits[idx])
                
                for idx, bit in enumerate(reversed(bin_channel)):
                    if bit == '0':
                        qc.x(channel_qubits[idx])
    
    print(f"Created OCQR circuit with {qc.num_qubits} qubits")
    print(f"Position qubits: {2*n}, Channel qubits: 2, Color qubits: {q}")
    print(f"Circuit depth: {qc.depth()}")
    
    return qc


def encode_ocqr_from_image(image_path, n=2, q=3):
    """
    Encode a classical image file into OCQR quantum representation.
    
    Args:
        image_path (str): Path to the image file (e.g., './images/input/peppers.jpg')
        n (int): Number of position qubits (log2 of image dimension)
        q (int): Number of color qubits (bits per color channel)
        
    Returns:
        tuple: (QuantumCircuit, numpy.ndarray) - OCQR circuit and image data
    """
    # Load and preprocess image
    img = Image.open(image_path).convert('RGB')
    
    # Resize to 2^n x 2^n
    target_size = 2**n
    img = img.resize((target_size, target_size))
    
    # Convert to numpy array and scale to appropriate range
    pixel_data = np.array(img, dtype=np.uint8)
    
    # Scale to [0, 2^q - 1] range if necessary
    max_val = 2**q - 1
    if pixel_data.max() > max_val:
        pixel_data = (pixel_data * max_val / 255).astype(np.uint8)
    
    return encode_ocqr_from_matrix(pixel_data, n, q)


def prepare_test_matrix_4x4():
    """
    Creates the 4x4 test matrix from Figure 1 and Figure 15 of the paper.
    
    Matrix values:
    R: [[1,2,2,0], [3,3,2,3], [4,2,7,3], [3,3,0,0]]
    G: [[2,3,6,7], [5,4,4,7], [7,6,7,5], [7,5,7,2]]  
    B: [[1,2,0,2], [0,1,2,5], [4,1,7,5], [5,0,2,0]]
    
    Returns:
        numpy.ndarray: 4x4x3 RGB matrix with values in range [0, 7]
    """
    rgb_matrix = np.array([
        [[1, 2, 1], [2, 3, 2], [2, 6, 0], [0, 7, 2]],  # Row 0
        [[3, 5, 0], [3, 4, 1], [2, 4, 2], [3, 7, 5]],  # Row 1
        [[4, 7, 4], [2, 6, 1], [7, 7, 7], [6, 6, 6]],  # Row 2
        [[3, 7, 5], [3, 5, 0], [0, 7, 2], [0, 2, 0]]   # Row 3
    ], dtype=np.uint8)
    
    return rgb_matrix


def prepare_neighborhood_images(rgb_matrix):
    """
    Prepares the eight-neighborhood images as shown in Figure 2 of the paper.
    For edge detection, we need the original image plus its 8 shifted versions.
    
    Args:
        rgb_matrix: Original 4x4 RGB matrix
        
    Returns:
        list: List of 9 RGB matrices (original + 8 neighborhoods)
    """
    h, w = rgb_matrix.shape[:2]
    neighborhoods = []
    
    # Original image
    neighborhoods.append(rgb_matrix.copy())
    
    # Define 8 neighborhood shifts
    shifts = [
        (-1, -1), (-1, 0), (-1, 1),  # Top row
        (0, -1),          (0, 1),    # Middle row (skip 0,0 as it's original)
        (1, -1),  (1, 0), (1, 1)    # Bottom row
    ]
    
    for dy, dx in shifts:
        shifted = np.zeros_like(rgb_matrix)
        for y in range(h):
            for x in range(w):
                # Calculate source position with boundary conditions
                src_y = y + dy
                src_x = x + dx
                
                # Handle boundaries (pad with zeros)
                if 0 <= src_y < h and 0 <= src_x < w:
                    shifted[y, x] = rgb_matrix[src_y, src_x]
                else:
                    shifted[y, x] = [0, 0, 0]  # Boundary padding
                    
        neighborhoods.append(shifted)
    
    return neighborhoods


def encode_ocqr_with_neighborhoods(rgb_matrix, n=2, q=3):
    """
    Encodes the original image and its 8 neighborhoods for edge detection.
    This implements the row-by-row image preparation method mentioned in the paper.
    
    Args:
        rgb_matrix: Original RGB matrix
        n: position qubits per dimension
        q: color depth bits
        
    Returns:
        QuantumCircuit: Complete circuit with original + 8 neighborhood images
    """
    # Get all neighborhood images
    neighborhoods = prepare_neighborhood_images(rgb_matrix)
    
    print(f"Preparing {len(neighborhoods)} images (original + 8 neighborhoods)")
    
    # Create registers for all images
    circuits = []
    
    for i, neighborhood in enumerate(neighborhoods):
        print(f"Encoding image {i+1}/9")
        qc = encode_ocqr_from_matrix(neighborhood, n, q)
        circuits.append(qc)
    
    # Combine circuits (this is a simplified approach)
    # In practice, the paper uses a more sophisticated method to prepare all images simultaneously
    # For now, we'll return the list of individual circuits
    
    return circuits


def decode_ocqr_to_classical(counts, n=2, q=3):
    """
    Decodes quantum measurement results back to classical image format.
    
    Args:
        counts: Measurement results from quantum circuit execution
        n: position qubits per dimension
        q: color depth bits
        
    Returns:
        numpy.ndarray: Reconstructed RGB matrix
    """
    size = 2**n
    rgb_matrix = np.zeros((size, size, 3), dtype=np.uint8)
    
    # Parse measurement results
    for state_str, count in counts.items():
        # Extract position, channel, and color information from state string
        # Format: |YX> |channel> |color>
        # Total bits: 2n (position) + 2 (channel) + q (color)
        
        if len(state_str) != (2*n + 2 + q):
            continue
            
        # Extract components (assuming little-endian bit order)
        color_bits = state_str[:q]  # First q bits are color
        channel_bits = state_str[q:q+2]  # Next 2 bits are channel
        pos_bits = state_str[q+2:]  # Last 2n bits are position
        
        # Convert binary strings to integers
        color_val = int(color_bits[::-1], 2)  # Reverse for MSB first
        channel_val = int(channel_bits[::-1], 2)
        pos_val = int(pos_bits[::-1], 2)
        
        # Convert position to (y, x) coordinates
        x = pos_val % size
        y = pos_val // size
        
        # Map channel to RGB
        if channel_val == 0:  # 00 = R
            rgb_matrix[y, x, 0] = color_val
        elif channel_val == 1:  # 01 = G
            rgb_matrix[y, x, 1] = color_val
        elif channel_val == 2:  # 10 = B
            rgb_matrix[y, x, 2] = color_val
        # channel_val == 3 is redundant, ignore
    
    return rgb_matrix


def visualize_ocqr_encoding_example():
    """
    Demonstrates the OCQR encoding process with the 4x4 test matrix.
    """
    print("=== OCQR Encoding Example ===")
    
    # Create test matrix from paper
    test_matrix = prepare_test_matrix_4x4()
    
    # Encode to quantum circuit
    qc = encode_ocqr_from_matrix(test_matrix, n=2, q=3)
    
    print(f"\nQuantum circuit created with {qc.num_qubits} qubits")
    print(f"Circuit depth: {qc.depth()}")
    
    return qc, test_matrix


if __name__ == "__main__":
    # Test the encoding with the paper's example matrix
    qc, matrix = visualize_ocqr_encoding_example()
    
    # Optional: Save circuit diagram
    try:
        qc.draw('mpl', filename='ocqr_circuit.png')
        print("Circuit diagram saved as 'ocqr_circuit.png'")
    except:
        print("Could not save circuit diagram (matplotlib not available)")
