# Fig. 6: Two-Digit Quantum Adder
**Context:** Circuit to calculate the sum of two 2-qubit registers.
**Description:** - Inputs are two 2-qubit values $C_{YX}$ and $C_{Y'X'}$, plus ancilla $|0\rangle$ qubits.
**Gate Sequence:**
1.  **Half/Full Adders:** The circuit uses two cascading sub-modules (red dashed boxes).
2.  **Gates:** Uses CNOT and Toffoli gates.
3.  The first box computes intermediate sum and carry logic into the ancilla lines.
4.  The second box finalizes the operation, outputting a 3-qubit sum ($s_0, s_1, s_2$) while leaving the input registers conceptually intact (or entangled with the result). 
5.  Simplified as an 'ADD' block.
