# Fig. 8: Three-Digit Quantum Comparator
**Context:** Circuit to compare two 3-qubit values to determine which is larger.
**Description:** - Inputs are two 3-qubit registers $C_{YX}$ and $C_{Y'X'}$, and ancilla qubits.
**Gate Sequence:**
1.  A symmetrical, parallelized structure of CNOT and Toffoli gates.
2.  The circuit evaluates the bits from Most Significant Bit (MSB) to Least Significant Bit (LSB).
3.  The boolean result of the comparison ($C_{YX} > C_{Y'X'}$) is written to a final ancilla output qubit labeled $C_{out}$.
4.  Simplified as a 'Com' block.
