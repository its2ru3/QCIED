# Fig. 11: Quantum Threshold Module
**Context:** Quantum circuit for comparing a calculated maximum gradient against a threshold to determine if a pixel is an edge.
**Description:** - Inputs are the maximum calculated gradient $G_{max}$, a predefined threshold value $|1\rangle^{\otimes q}$ (or similar threshold state), and ancilla qubits.
**Gate Sequence:**
1.  **Comparison:** A 'Com' (Comparator) module evaluates if $G_{max}$ exceeds the threshold.
2.  **State Flip:** The output of the comparator acts as a control for a series of NOT gates (represented by 'X' symbols with vertical control lines) targeting an initialized $|0\rangle$ ancilla.
3.  **Threshold Output:** A final controlled operation (with a hollow circle indicating it triggers on state $|0\rangle$) sets the final thresholded output $G'$.
4.  Simplified as a '$U_T$' block.
