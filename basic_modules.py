from qiskit import QuantumCircuit
from qiskit.circuit.library import CDKMRippleCarryAdder

def quantum_adder(q):
    return CDKMRippleCarryAdder(num_state_qubits=q).to_gate(label="ADD")

def quantum_subtractor(q):
    qc = QuantumCircuit(2 * q + 2)
    qc.append(CDKMRippleCarryAdder(num_state_qubits=q).inverse(), range(2 * q + 2))
    return qc.to_gate(label="SUB")

def quantum_comparator(q):
    qc = QuantumCircuit(2 * q + 1)
    return qc.to_gate(label="COMP")

def quantum_swap(q):
    qc = QuantumCircuit(2 * q + 1)
    for i in range(q):
        qc.cswap(0, i + 1, q + i + 1)
    return qc.to_gate(label="CSWAP")