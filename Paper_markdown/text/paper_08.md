**Fig. 7** Quantum circuit and simplified diagram of two-digit quantum subtractor

is shown in Equation 4.

$$U_{sub} \left| C_{YX}^{n-1} \dots C_{YX}^0 \right\rangle \otimes \left| C_{Y'X'}^{n-1} \dots C_{Y'X'}^0 \right\rangle = \left| s_{n-1} \dots s_0 \right\rangle \otimes \left| C_{Y'X'}^{n-1} \dots C_{Y'X'}^0 \right\rangle \quad (4)$$

### 3.1.4 Quantum comparator module

Since this paper needs to calculate the maximum value of $|G_x\rangle, |G_y\rangle, |G_{45}\rangle$ and $|G_{135}\rangle$, the relationship between them needs to be compared. This paper adopts the quantum comparator proposed in reference [37]. Although this method can only distinguish between two states, its overall quantum circuit complexity is relatively low, which is advantageous for reducing the overall design complexity. For example, the input consists of two-qubit sequences denoted as $|C_{YX}\rangle = |C_{YX}^{n-1} C_{YX}^{n-2} \dots C_{YX}^0\rangle$ and $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1} C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$, respectively. When $|C_{YX}\rangle < |C_{Y'X'}\rangle, |C_{out}\rangle = |1\rangle$. When $|C_{YX}\rangle \ge |C_{Y'X'}\rangle, |C_{out}\rangle = |0\rangle$. The overall quantum circuit is shown in Fig. 8.

### 3.1.5 Quantum swap module

The quantum swap module is composed of several quantum-controlled gates, and its purpose is to use the result of the quantum comparator as the control bit to ensure that the larger value is in the first qubits, as shown in Fig. 9. For example, given a two $n$-bit composite system $|C_{YX}\rangle |C_{Y'X'}\rangle$, where $|C_{YX}\rangle = |C_{YX}^{n-1} C_{YX}^{n-2} \dots C_{YX}^0\rangle$ and $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1} C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$. When $C_{out} = 1$, the state $|C_{YX}\rangle |C_{Y'X'}\rangle$ is transformed into $|C_{Y'X'}\rangle |C_{YX}\rangle$ after passing through the quantum swap module. When $C_{out} = 0$, no transformation occurs.
