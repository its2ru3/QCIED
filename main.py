from qiskit import transpile
from qiskit_aer import AerSimulator
from image_prep import encode_ocqr
from edge_detection import build_gradient_module, build_max_value_module, build_threshold_module

def main():
    q = 3
    n = 2
    
    main_qc = encode_ocqr("input.jpg", n=n, q=q)
    
    grad_gate = build_gradient_module(q)
    max_gate = build_max_value_module(q)
    thresh_gate = build_threshold_module(q)
    
    main_qc.measure_all()
    
    simulator = AerSimulator(method='extended_stabilizer')
    compiled_circuit = transpile(main_qc, simulator)
    
    job = simulator.run(compiled_circuit, shots=256)
    result = job.result()
    
    print(result.get_counts())

if __name__ == "__main__":
    main()