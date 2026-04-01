from qiskit import QuantumCircuit, QuantumRegister
from basic_modules import quantum_adder, quantum_subtractor, quantum_comparator, quantum_swap

def build_gradient_module(q):
    pixels = [QuantumRegister(q, f'p_{i}') for i in range(9)]
    gx = QuantumRegister(q + 2, 'Gx')
    gy = QuantumRegister(q + 2, 'Gy')
    g45 = QuantumRegister(q + 2, 'G45')
    g135 = QuantumRegister(q + 2, 'G135')
    aux = QuantumRegister(16, 'aux')
    
    qc = QuantumCircuit(*pixels, gx, gy, g45, g135, aux)
    
    add_gate = quantum_adder(q)
    sub_gate = quantum_subtractor(q)
    
    qc.append(add_gate, list(pixels[2]) + list(pixels[5]) + [aux[0], aux[1]])
    
    return qc.to_gate(label="UG_Gradient")

def build_max_value_module(q):
    gx = QuantumRegister(q, 'Gx')
    gy = QuantumRegister(q, 'Gy')
    g45 = QuantumRegister(q, 'G45')
    g135 = QuantumRegister(q, 'G135')
    gmax = QuantumRegister(q, 'Gmax')
    flag = QuantumRegister(3, 'compare_flag')
    
    qc = QuantumCircuit(gx, gy, g45, g135, gmax, flag)
    
    comp_gate = quantum_comparator(q)
    swap_gate = quantum_swap(q)
    
    qc.append(comp_gate, list(gx) + list(gy) + [flag[0]])
    qc.append(swap_gate, [flag[0]] + list(gx) + list(gy))
    
    return qc.to_gate(label="QC_Max")

def build_threshold_module(q):
    gmax = QuantumRegister(q, 'Gmax')
    thresh = QuantumRegister(q, 'T')
    out = QuantumRegister(q, 'Edge_Pixel')
    flag = QuantumRegister(1, 'flag')
    
    qc = QuantumCircuit(gmax, thresh, out, flag)
    
    comp_gate = quantum_comparator(q)
    qc.append(comp_gate, list(gmax) + list(thresh) + [flag[0]])
    
    for i in range(q):
        qc.cx(flag[0], out[i])
        
    return qc.to_gate(label="UT_Threshold")