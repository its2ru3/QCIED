# Fig. 7: Two-Digit Quantum Subtractor
**Context:** Circuit to calculate the difference between two 2-qubit registers.
**Description:** - Inputs match the adder (two 2-qubit values $C_{YX}$ and $C_{Y'X'}$, plus ancillas).
**Gate Sequence:**
1.  Structured in two cascading modules (red dashed boxes) similar to the adder.
2.  **Gates:** Uses NOT (X) gates, CNOTs, and Toffoli gates.
3.  The NOT gates invert specific input bits to facilitate a two's complement subtraction logic.
4.  Outputs a 3-qubit difference ($s_0, s_1, s_2$). Simplified as a 'SUB' block.
