import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from PIL import Image

def encode_ocqr(image_path, n=1, q=3):
    """
    Encodes a classical image into the OCQR quantum representation.
    n: power for 2^n x 2^n image size (default 1 means 2x2 image)
    q: color depth (default 3 means 0-7 RGB values)
    """
    # 1. Load and resize image
    img = Image.open(image_path).convert('RGB')
    img = img.resize((2**n, 2**n))
    pixel_data = np.array(img)
    print("Image matrix is: ")
    print(pixel_data)

    # 2. Allocate Qubits: Position (2n), Channel Index (2), Color Value (q)
    pos_qubits = QuantumRegister(2*n, 'pos')
    ch_qubits = QuantumRegister(2, 'ch')
    color_qubits = QuantumRegister(q, 'color')
    qc = QuantumCircuit(pos_qubits, ch_qubits, color_qubits)

    # 3. Step 1: Initialize superposition for position and channel (Eq 7)
    qc.h(pos_qubits)
    qc.h(ch_qubits)

    # 4. Step 2: Set color values for each pixel and channel (Eq 8-10)
    controls = list(pos_qubits) + list(ch_qubits)
    
    for y in range(2**n):
        for x in range(2**n):
            for ch in range(3): # 0=R, 1=G, 2=B
                val = pixel_data[y, x, ch]
                if val == 0: 
                    continue
                
                # Convert coordinates and channel to binary
                bin_y = format(y, f'0{n}b')
                bin_x = format(x, f'0{n}b')
                bin_pos = bin_y + bin_x 
                bin_ch = format(ch, '02b') 
                
                # Convert pixel intensity to binary (reversed for LSB matching)
                bin_val = format(val, f'0{q}b')[::-1]

                # Apply X gates to condition the multi-controlled gates on '0' states
                for idx, bit in enumerate(reversed(bin_pos)):
                    if bit == '0': qc.x(pos_qubits[idx])
                for idx, bit in enumerate(reversed(bin_ch)):
                    if bit == '0': qc.x(ch_qubits[idx])

                # Apply MCX (Multi-Controlled X) to set the intensity bits
                for idx, bit in enumerate(bin_val):
                    if bit == '1':
                        qc.mcx(controls, color_qubits[idx])

                # Uncompute X gates to restore control state
                for idx, bit in enumerate(reversed(bin_pos)):
                    if bit == '0': qc.x(pos_qubits[idx])
                for idx, bit in enumerate(reversed(bin_ch)):
                    if bit == '0': qc.x(ch_qubits[idx])

    return qc

# Example usage:
# qc = encode_ocqr("my_image.jpg", n=1, q=8)
# print(f"Total qubits: {qc.num_qubits}")
# print(f"Circuit depth: {qc.depth()}")