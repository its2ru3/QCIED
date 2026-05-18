"""Phase 2 sanity tests — U_G, QC, U_T composition.

We don't drive the full pipeline through a simulator here (it's too large
for the 4×4 case before any Phase 3 register sharing). Instead we:

  * build each composition block and verify it composes without error,
  * print ``circuit.draw('text')`` for the standalone pieces,
  * count qubits / gates,
  * build the top-level ``build_edge_detection_v2`` and report its
    metrics (qubit budget, op counts) for the Phase 3 register-sharing
    discussion in ``notes/todo.md`` §0.5.

Run:  wsl .venv_btp/bin/python3 -m tests.test_phase2
"""

from qiskit import QuantumCircuit, QuantumRegister

from helpers.ocqr_encoding_new import prepare_test_matrix_4x4
from helpers.sobel_v2 import (
    GRAD_DEFS,
    append_QC,
    append_U_G_one_direction,
    append_U_T,
    build_edge_detection_v2,
)


def _alloc(width, name):
    return QuantumRegister(width, name)


def test_U_G_one_direction_builds(q=3):
    """Build U_G for one direction (Gx) and report metrics."""
    width = q + 2
    intensity = [_alloc(q, f"I{i}") for i in range(9)]
    g_x = _alloc(width, "Gx")
    pos_w = _alloc(width, "pos_w")
    neg_w = _alloc(width, "neg_w")
    work = _alloc(4, "work")  # z, pad, com_internal, flag
    qc = QuantumCircuit(*intensity, g_x, pos_w, neg_w, work)
    append_U_G_one_direction(
        qc, intensity, "Gx", g_x,
        pos_w, neg_w, work[0], work[1], work[2], work[3], q,
    )

    print(f"\n--- U_G (one direction: Gx, q={q}) ---")
    print(f"  qubits: {qc.num_qubits}")
    print(f"  depth: {qc.depth()}")
    ops = qc.count_ops()
    print(f"  ops: {dict(ops)}")
    print(f"  total gates: {sum(ops.values())}")
    assert qc.num_qubits == 9 * q + 3 * width + 4
    assert sum(ops.values()) > 0
    print("test_U_G_one_direction_builds: OK")


def test_QC_builds(q=3):
    width = q + 2
    g_x = _alloc(width, "Gx")
    g_y = _alloc(width, "Gy")
    g_45 = _alloc(width, "G45")
    g_135 = _alloc(width, "G135")
    z = _alloc(1, "z")
    ib = _alloc(1, "ib")
    flag = _alloc(1, "flag")
    qc = QuantumCircuit(g_x, g_y, g_45, g_135, z, ib, flag)
    append_QC(qc, g_x, g_y, g_45, g_135, z[0], ib[0], flag[0], width)

    print(f"\n--- QC (max-of-four, width={width}) ---")
    # Drawing this is big; fold it tighter.
    print(qc.draw("text", fold=180))
    print(f"  qubits: {qc.num_qubits} (expected {4 * width + 3})")
    print(f"  depth: {qc.depth()}")
    ops = qc.count_ops()
    print(f"  ops: {dict(ops)}")
    print(f"  total gates: {sum(ops.values())}")
    assert qc.num_qubits == 4 * width + 3
    # Three Com+Swap+Com triples → 3 × (2·Sub + 1·CNOT + 1·Swap) flow.
    assert ops.get("cswap", 0) == 3 * width, \
        f"expected {3*width} CSWAPs (3 swaps × width); got {ops.get('cswap', 0)}"
    print("test_QC_builds: OK")


def test_U_T_builds(q=3):
    width = q + 2
    g_max = _alloc(width, "Gmax")
    output = _alloc(q, "G_out")
    qc = QuantumCircuit(g_max, output)
    append_U_T(qc, g_max, output, q)

    print(f"\n--- U_T (threshold via MSB-CNOT, q={q}) ---")
    print(qc.draw("text", fold=120))
    print(f"  qubits: {qc.num_qubits} (expected {width + q})")
    ops = qc.count_ops()
    print(f"  ops: {dict(ops)}")
    assert qc.num_qubits == width + q
    # q CNOTs, no other gates.
    assert ops.get("cx", 0) == q
    assert sum(ops.values()) == q
    print("test_U_T_builds: OK")


def test_gradient_definitions():
    """The four GRAD_DEFS entries each cover the expected image indices."""
    expected = {
        "Gx":   {2, 3, 4, 8, 7, 6},
        "Gy":   {6, 5, 4, 8, 1, 2},
        "G45":  {1, 2, 3, 7, 6, 5},
        "G135": {3, 4, 5, 1, 8, 7},
    }
    for name, spec in GRAD_DEFS.items():
        seen = set(spec["pos"]) | set(spec["neg"])
        assert seen == expected[name], f"{name}: indices {seen} != expected {expected[name]}"
        assert spec["doubled_pos"] in spec["pos"]
        assert spec["doubled_neg"] in spec["neg"]
    print("test_gradient_definitions: OK")


def test_full_pipeline_builds():
    """Top-level builder: report the qubit budget at (n=2, q=3)."""
    rgb = prepare_test_matrix_4x4()
    qc = build_edge_detection_v2(rgb, n=2, q=3)
    print(f"\n--- Full pipeline build_edge_detection_v2(n=2, q=3) ---")
    print(f"  qubits: {qc.num_qubits}")
    print(f"  classical bits: {qc.num_clbits}")
    print(f"  depth: {qc.depth()}")
    ops = qc.count_ops()
    print(f"  ops: {dict(ops)}")
    print(f"  total gates: {sum(ops.values())}")
    # See notes/todo.md §0.5: 16q + 4n + 22 = 78 at (n=2, q=3). Exceeds the
    # 63-qubit extended_stabilizer cap by 11-15 — Phase 3 work to share
    # registers / unwind accumulators / re-architect for the budget.
    print(f"  --- budget note ---")
    print(f"  extended_stabilizer cap: 63 qubits")
    print(f"  current overage: {qc.num_qubits - 63} qubits (Phase 3 work)")
    assert qc.num_qubits > 0
    print("test_full_pipeline_builds: OK")


def main():
    print("=" * 64)
    print("Phase 2 tests — U_G, QC, U_T composition")
    print("=" * 64)
    test_gradient_definitions()
    test_U_G_one_direction_builds(3)
    test_QC_builds(3)
    test_U_T_builds(3)
    test_full_pipeline_builds()
    print()
    print("All Phase 2 tests passed.")


if __name__ == "__main__":
    main()
