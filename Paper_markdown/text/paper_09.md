**Fig. 8** Quantum circuit and simplified diagram of three-digit quantum comparator

**Fig. 9** Quantum circuit and simplified diagram of quantum-controlled swap module

### 3.1.6 Maximum value calculation module

This paper will involve finding the maximum value from four numbers. Thus, the maximum value calculation module consists of three comparison modules and three controlled switch modules, as shown in Fig. 10. The input numbers are $|G_1\rangle, |G_2\rangle, |G_3\rangle,$ and $|G_4\rangle$; the maximum value calculation module outputs is the maximum value $|G_{max}\rangle$.

### 3.1.7 Quantum threshold module

The design of the quantum threshold module is as follows: Assume that the range of pixel values is $[0, 2^q - 1]$, and the threshold is $2^{q-1}$. As shown in Fig. 11, from top to bottom, the first $q$ qubits encode the value $2^q - 1$, the second $q$ qubits encode $G_{max}$, which is the maximum value obtained from the previous stage, and the last $q-1$ qubits encode the threshold $2^{q-1}$. $G_{max}$ will be compared with $2^{q-1}$, when $G_{max}$ is larger, it is set to $2^q - 1$, otherwise, it is set to zero. The purpose of this module is to obtain the edge pixels.
