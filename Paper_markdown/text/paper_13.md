**Fig. 14** Quantum circuit of color image edge detection algorithm

a three-qubit adder. In the maximum value calculation module, one auxiliary qubit is needed as the result bit to control the subsequent swap module. Basic quantum operation modules such as quantum adders, quantum subtractors, and quantum comparators still require one auxiliary qubit to complete the operation.

## 3.3 Circuit complexity analysis

In quantum information processing, the complexity of the circuit depends on the number of quantum gates used. When performing edge detection on a color image of size $2^n \times 2^n$ with an intensity range of $[0, 2^{q-1}]$, the complexity analysis of a series of quantum algorithms used in the quantum circuit shown in Fig. 14 is as follows.

The edge extraction module includes the quantum edge gradient calculation, maximum value calculation, and threshold calculation modules. The edge gradient calculation module uses 16 quantum adders, four quantum subtractors, and two quantum copying modules. According to [36], the complexity of a $q$-bit quantum adder is $12q$, the complexity of a $q$-bit quantum subtractor is $14q$, and the complexity of a quantum copying module is $q$. Therefore, the complexity of the edge gradient calculation module is $(12q \times 16 + 14q \times 4 = 248q)$. The maximum value calculation module includes three comparators and three controlled exchange gates, and its complexity is $(87q - 18)$. The threshold calculation module consists of a comparator, $q$ X gates, and a controlled exchange gate, resulting in a $(14q - 6 + q + 15q = 30q - 6)$ complexity. Therefore, the complexity of this part is $(248q + 87q - 18 + 30q - 6 = 365q - 24)$.

In general, image preparation is not included when calculating the circuit complexity of quantum image processing algorithms. Therefore, this paper compares the edge extraction module with other literature, as shown in Table 1.

From Table 1, it can be seen that when large-sized images are used as input for quantum algorithms, the algorithm designed in this paper has a significant advantage
