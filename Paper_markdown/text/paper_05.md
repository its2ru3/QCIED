**Fig. 3** Pixel preparation of the '0000' position in Fig. 1

quantum subtractor module [36], the quantum comparator module, and so on. Then, these modules are adopted to design the quantum circuit of the overall algorithm.

## 3.1 Necessary quantum image processing modules

In this subsection, several necessary quantum image processing modules are introduced.

### 3.1.1 Quantum cloning module

Equation 2 defines the quantum cloning module, which is composed of multiple CNOT gates and can copy the information of a qubit sequence $|C_{YX}\rangle = |C_{YX}^{n-1} \dots C_{YX}^0\rangle$ to another qubit sequence $|0\rangle^{\otimes n}$. The quantum circuit of the quantum cloning operation module is shown in Fig. 5.

$$U_c(|C\rangle |0\rangle^{\otimes n}) = |C\rangle |C\rangle \quad (2)$$

### 3.1.2 Quantum adder module

According to [9], given a composite system composed of two $n$-qubit quantum states $|C_{YX}\rangle$ and $|C_{Y'X'}\rangle$ as addend and augend, the purpose of the quantum adder is to recursively calculate each pair of $|C_{YX}^i\rangle$ and $|C_{Y'X'}^i\rangle$ in the two quantum states $|C_{YX}\rangle = |C_{YX}^{n-1}C_{YX}^{n-2} \dots C_{YX}^0\rangle$ and $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1}C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$. The overall quantum
