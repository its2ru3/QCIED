"""Phase 1 sanity tests — paper-faithful modules in ``helpers.modules_v2``.

For each module: build with a sample width, print ``circuit.draw('text')``,
verify qubit count + gate count + arithmetic correctness on small cases.

Run:  wsl .venv_btp/bin/python3 -m tests.test_phase1
"""

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from helpers.modules_v2 import (
    append_adder,
    append_comparator,
    append_subtractor,
    quantum_adder,
    quantum_cloning_module,
    quantum_comparator,
    quantum_subtractor,
    quantum_swap,
)


def _set_int(qc, reg, value, width):
    """Initialise a register to a classical integer (LSB at reg[0])."""
    for i in range(width):
        if (value >> i) & 1:
            qc.x(reg[i])


def _measure_register(sv, qubit_range):
    """Extract the integer encoded in the given qubit range from a deterministic statevector."""
    top = max(sv.to_dict().items(), key=lambda kv: abs(kv[1]) ** 2)
    bits = top[0][::-1]  # qiskit prints MSB-first; reverse to qubit-0-first
    selected = bits[qubit_range[0]:qubit_range[1]]
    return int(selected[::-1], 2) if selected else 0


def test_cloning_module(width=3):
    gate_circ = quantum_cloning_module(width)
    print(f"\n--- Cloning U_c(width={width}) ---")
    print(gate_circ.draw("text", fold=120))
    print(f"  qubits: {gate_circ.num_qubits} (expected {2 * width})")
    ops = gate_circ.count_ops()
    print(f"  ops: {dict(ops)}")
    assert gate_circ.num_qubits == 2 * width
    assert ops.get("cx", 0) == width, f"expected {width} CNOTs, got {ops.get('cx', 0)}"
    print("test_cloning_module: OK")


def test_adder_correctness(width=3):
    """Exhaustively verify b := (a + b) mod 2^w; carry-out on c_out; z, c restored."""
    gate_circ = quantum_adder(width)
    print(f"\n--- Adder ADD(width={width}) ---")
    print(gate_circ.draw("text", fold=120))
    print(f"  qubits: {gate_circ.num_qubits} (expected {2 * width + 2})")
    assert gate_circ.num_qubits == 2 * width + 2

    fails = 0
    for a_val in range(2 ** width):
        for b_val in range(2 ** width):
            a = QuantumRegister(width, "a")
            b = QuantumRegister(width, "b")
            z = QuantumRegister(1, "z")
            c = QuantumRegister(1, "c")
            qc = QuantumCircuit(a, b, z, c)
            _set_int(qc, a, a_val, width)
            _set_int(qc, b, b_val, width)
            append_adder(qc, a, b, z[0], c[0], width)
            sv = Statevector(qc)
            a_out = _measure_register(sv, (0, width))
            b_out = _measure_register(sv, (width, 2 * width))
            z_bit = _measure_register(sv, (2 * width, 2 * width + 1))
            c_bit = _measure_register(sv, (2 * width + 1, 2 * width + 2))
            expected_full = a_val + b_val
            expected_b = expected_full % (2 ** width)
            expected_c = (expected_full >> width) & 1
            if not (a_out == a_val and b_out == expected_b
                    and z_bit == 0 and c_bit == expected_c):
                fails += 1
    print(f"  exhaustive arithmetic check: {fails} failures over {4 ** width} cases")
    assert fails == 0
    print("test_adder_correctness: OK")


def test_subtractor_correctness(width=3):
    """Exhaustively verify b := (b - a) mod 2^w; bo = 1 iff b < a; z restored."""
    gate_circ = quantum_subtractor(width)
    print(f"\n--- Subtractor SUB(width={width}) ---")
    print(gate_circ.draw("text", fold=120))
    print(f"  qubits: {gate_circ.num_qubits} (expected {2 * width + 2})")
    assert gate_circ.num_qubits == 2 * width + 2

    fails = 0
    for a_val in range(2 ** width):
        for b_val in range(2 ** width):
            a = QuantumRegister(width, "a")
            b = QuantumRegister(width, "b")
            z = QuantumRegister(1, "z")
            bo = QuantumRegister(1, "bo")
            qc = QuantumCircuit(a, b, z, bo)
            _set_int(qc, a, a_val, width)
            _set_int(qc, b, b_val, width)
            append_subtractor(qc, a, b, z[0], bo[0], width)
            sv = Statevector(qc)
            a_out = _measure_register(sv, (0, width))
            b_out = _measure_register(sv, (width, 2 * width))
            z_bit = _measure_register(sv, (2 * width, 2 * width + 1))
            bo_bit = _measure_register(sv, (2 * width + 1, 2 * width + 2))
            expected_b = (b_val - a_val) % (2 ** width)
            expected_bo = 1 if b_val < a_val else 0
            if not (a_out == a_val and b_out == expected_b
                    and z_bit == 0 and bo_bit == expected_bo):
                fails += 1
    print(f"  exhaustive arithmetic check: {fails} failures over {4 ** width} cases")
    assert fails == 0
    print("test_subtractor_correctness: OK")


def test_comparator_correctness(width=3):
    """Exhaustively verify cout = [a < b]; a, b preserved; z & ib restored."""
    gate_circ = quantum_comparator(width)
    print(f"\n--- Comparator CMP(width={width}) ---")
    print(gate_circ.draw("text", fold=120))
    print(f"  qubits: {gate_circ.num_qubits} (expected {2 * width + 3})")
    assert gate_circ.num_qubits == 2 * width + 3

    fails = 0
    for a_val in range(2 ** width):
        for b_val in range(2 ** width):
            a = QuantumRegister(width, "a")
            b = QuantumRegister(width, "b")
            z = QuantumRegister(1, "z")
            ib = QuantumRegister(1, "ib")
            cout = QuantumRegister(1, "cout")
            qc = QuantumCircuit(a, b, z, ib, cout)
            _set_int(qc, a, a_val, width)
            _set_int(qc, b, b_val, width)
            append_comparator(qc, a, b, z[0], ib[0], cout[0], width)
            sv = Statevector(qc)
            a_out = _measure_register(sv, (0, width))
            b_out = _measure_register(sv, (width, 2 * width))
            z_bit = _measure_register(sv, (2 * width, 2 * width + 1))
            ib_bit = _measure_register(sv, (2 * width + 1, 2 * width + 2))
            cout_bit = _measure_register(sv, (2 * width + 2, 2 * width + 3))
            expected_cout = 1 if a_val < b_val else 0
            if not (a_out == a_val and b_out == b_val
                    and z_bit == 0 and ib_bit == 0 and cout_bit == expected_cout):
                fails += 1
    print(f"  exhaustive arithmetic check: {fails} failures over {4 ** width} cases")
    assert fails == 0
    print("test_comparator_correctness: OK")


def test_swap_module(width=3):
    gate_circ = quantum_swap(width)
    print(f"\n--- Swap(width={width}) ---")
    print(gate_circ.draw("text", fold=120))
    print(f"  qubits: {gate_circ.num_qubits} (expected {2 * width + 1})")
    ops = gate_circ.count_ops()
    print(f"  ops: {dict(ops)}")
    assert gate_circ.num_qubits == 2 * width + 1
    assert ops.get("cswap", 0) == width
    print("test_swap_module: OK")


def main():
    print("=" * 64)
    print("Phase 1 tests — paper-faithful modules")
    print("=" * 64)
    test_cloning_module(3)
    test_adder_correctness(3)
    test_subtractor_correctness(3)
    test_comparator_correctness(3)
    test_swap_module(3)
    print()
    print("All Phase 1 tests passed.")


if __name__ == "__main__":
    main()
