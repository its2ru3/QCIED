**Fig. 5** Quantum circuit and simplified diagram of quantum replication module

**Fig. 6** Quantum circuit and simplified diagram of two-digit quantum adder

### 3.1.3 Quantum subtractor module

According to reference [36], given a composite system consisting of two $n$-qubit quantum states $|C_{YX}\rangle |C_{Y'X'}\rangle$ as input, the purpose of the quantum subtractor is to recursively compute each pair of $|C_{YX}^i\rangle$ from $|C_{Y'X'}^i\rangle$ from the two quantum states $|C_{YX}\rangle = |C_{YX}^{n-1}C_{YX}^{n-2} \dots C_{YX}^0\rangle$ and $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1}C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$. The overall quantum circuit is shown in Fig. 7, similar to the quantum adder described above, where $|C_{YX}\rangle = |C_{YX}^{n-1}C_{YX}^{n-2} \dots C_{YX}^0\rangle$ represents the minuend, $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1}C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$ represents the subtrahend, $|s\rangle = |s_0s_n \dots s_1\rangle$ represents the subtracted result, $|a_0\rangle$ and $|a_1\rangle$ are two auxiliary qubits initialized to $|0\rangle$, and are alternately set to $|0\rangle$ throughout the subtractor circuit as borrow bits. The output of the quantum subtractor is $|s\rangle = |C_{YX} - C_{Y'X'}\rangle \otimes |C_{Y'X'}\rangle$, and the corresponding unitary evolution
