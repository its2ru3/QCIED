# 3 Edge detection algorithm of quantum color image

This section presents a quantum edge detection algorithm based on the Sobel operator for color images. Firstly, several necessary quantum image processing modules are introduced, such as the quantum cloning module, the quantum adder module [9], the quantum subtractor module [36], the quantum comparator module, and so on. Then, these modules are adopted to design the quantum circuit of the overall algorithm.

## 3.1 Necessary quantum image processing modules
In this subsection, several necessary quantum image processing modules are introduced.

### 3.1.1 Quantum cloning module
Equation 2 defines the quantum cloning module, which is composed of multiple CNOT gates and can copy the information of a qubit sequence $|C_{YX}\rangle=|C_{YX}^{n-1}\cdot\cdot\cdot C_{YX}^{0}\rangle$ to another qubit sequence $|0\rangle^{\otimes n}$. The quantum circuit of the quantum cloning operation module is shown in Fig. 5.

$$U_{c}(|C\rangle|0\rangle^{\otimes n})=|C\rangle|C\rangle \quad (2)$$

[Image Description: A quantum cloning module circuit. It uses a sequence of CNOT gates where a set of original qubits $|C_{i}\rangle$ act as control bits to flip a set of target qubits initially at $|0\rangle$, effectively duplicating the state to $|C\rangle|C\rangle$. A simplified block diagram labeled "$U_c$" is shown next to it.]
*Fig. 5: Quantum circuit and simplified diagram of quantum replication module*

### 3.1.2 Quantum adder module
According to [9], given a composite system composed of two n-qubit quantum states $|C_{YX}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle$ as addend and augend, the purpose of the quantum adder is to recursively calculate each pair of $|C_{YX}^{i}\rangle$ and $|C_{Y^{\prime}X^{\prime}}^{i}\rangle$ in the two quantum states $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$. The overall quantum circuit diagram is shown in Fig. 6, where $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$ represent two addends, $|a_{0}\rangle$ and $|a_{1}\rangle$ are two auxiliary qubits with an initial value of $|0\rangle$ used as carry bits throughout the adder. $|s\rangle=|s_{0}s_{n}...s_{1}\rangle$ represents the result obtained after addition. The output of the quantum adder is $|b\rangle=|C_{YX}+C_{Y^{\prime}X^{\prime}}\rangle\otimes|C_{Y^{\prime}X^{\prime}}\rangle$, and the corresponding unitary evolution is shown in Equation 3.

$$U_{add}|C_{YX}^{n-1}\cdot\cdot\cdot C_{YX}^{0}\rangle\otimes|C_{Y^{\prime}X^{\prime}}^{n-1}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle=|s_{0}s_{n}...s_{1}\rangle\otimes|C_{Y^{\prime}X^{\prime}}^{n-1}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle \quad (3)$$

[Image Description: A two-digit quantum adder circuit. It takes two sets of 2-qubit inputs ($C^0_{YX}, C^1_{YX}$ and $C^0_{Y'X'}, C^1_{Y'X'}$) and auxiliary qubits initialized to $|0\rangle$. It uses Toffoli and CNOT gates to perform binary addition, outputting the 3-qubit sum $s_0, s_1, s_2$. A simplified block labeled "ADD" is also shown.]
*Fig. 6: Quantum circuit and simplified diagram of two-digit quantum adder*

### 3.1.3 Quantum subtractor module
According to reference [36], given a composite system consisting of two n-qubit quantum states $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$ as input, the purpose of the quantum subtractor is to recursively compute each pair of $|C_{YX}^{i}\rangle$ and $|C_{Y^{\prime}X^{\prime}}^{i}\rangle$ from the two quantum states $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$. The overall quantum circuit is shown in Fig. 7, similar to the quantum adder described above, where $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ represents the minuend, $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$ represents the subtrahend, $|s\rangle=|s_{0}s_{n}...s_{1}\rangle$ represents the subtracted result, $|a_{0}\rangle$ and $|a_{1}\rangle$ are two auxiliary qubits initialized to $|0\rangle$, and are alternately set to $|0\rangle$ throughout the subtractor circuit as borrow bits. The output of the quantum subtractor is $|s\rangle=|C_{YX}-C_{Y^{\prime}X^{\prime}}\rangle\otimes|C_{Y^{\prime}X^{\prime}}\rangle$, and the corresponding unitary evolution is shown in Equation 4.

$$U_{sub}|C_{YX}^{n-1}\cdot\cdot\cdot C_{YX}^{0}\rangle\otimes|C_{Y^{\prime}X^{\prime}}^{n-1}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle=|s_{n-1}...s_{0}\rangle\otimes|C_{Y^{\prime}X^{\prime}}^{n-1}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle \quad (4)$$

[Image Description: A two-digit quantum subtractor circuit. It takes two 2-qubit inputs (minuend and subtrahend) and uses auxiliary borrow qubits ($a_0, a_1$). It employs a combination of CNOT, X, and Toffoli gates to compute the difference $s_0, s_1$. A simplified block labeled "SUB" is also provided.]
*Fig. 7: Quantum circuit and simplified diagram of two-digit quantum subtractor*

### 3.1.4 Quantum comparator module
Since this paper needs to calculate the maximum value of $|G_{x}\rangle$, $|G_{y}\rangle$, $|G_{45}\rangle$ and $|G_{135}\rangle$, the relationship between them needs to be compared. This paper adopts the quantum comparator proposed in reference [37]. Although this method can only distinguish between two states, its overall quantum circuit complexity is relatively low, which is advantageous for reducing the overall design complexity. For example, the input consists of two-qubit sequences denoted as $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$, respectively. When $|C_{YX}\rangle<|C_{Y^{\prime}X^{\prime}}\rangle$, $|C_{out}\rangle=|1\rangle$. When $|C_{YX}\rangle\ge|C_{Y^{\prime}X^{\prime}}\rangle$, $|C_{out}\rangle=|0\rangle$. The overall quantum circuit is shown in Fig. 8.

[Image Description: A three-digit quantum comparator circuit. It takes two 3-qubit inputs ($C_{YX}$ and $C_{Y'X'}$) and uses an arrangement of CNOT, X, and Toffoli gates to output a single flag qubit $C_{out}$. A simplified block labeled "Com" is also shown.]
*Fig. 8: Quantum circuit and simplified diagram of three-digit quantum comparator*

### 3.1.5 Quantum swap module
The quantum swap module is composed of several quantum-controlled gates, and its purpose is to use the result of the quantum comparator as the control bit to ensure that the larger value is in the first qubits, as shown in Fig. 9. For example, given a two n-bit composite system $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$, where $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$. When $C_{out}=1$, the state $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$ is transformed into $|C_{Y^{\prime}X^{\prime}}\rangle|C_{YX}\rangle$ after passing through the quantum swap module. When $C_{out}=0$ no transformation occurs.

[Image Description: A quantum-controlled swap module circuit. It uses a control qubit $C_{out}$ connected to multiple Fredkin (controlled-SWAP) gates to conditionally swap corresponding pairs of qubits between two q-bit registers, $C_{YX}$ and $C_{Y'X'}$. A simplified block labeled "Swap" is also displayed.]
*Fig. 9: Quantum circuit and simplified diagram of quantum-controlled swap module*

### 3.1.6 Maximum value calculation module
This paper will involve finding the maximum value from four numbers. Thus, the maximum value calculation module consists of three comparison modules and three controlled switch modules, as shown in Fig. 10. The input numbers are $|G_{1}\rangle$, $|G_{2}\rangle$, $|G_{3}\rangle$, and $|G_{4}\rangle$; the maximum value calculation module outputs is the maximum value $|G_{max}\rangle$.

[Image Description: A quantum circuit for calculating the maximum of four inputs ($G_x, G_y, G_{45}, G_{135}$). It chains three Comparator (Com) modules and three Swap modules. It compares pairs, swaps the larger to the top, and repeats until the overall maximum $G_{max}$ is isolated on the top register. A simplified "QC" block summarizes the module.]
*Fig. 10: Quantum circuit and simplified diagram of maximum value calculation module*

### 3.1.7 Quantum threshold module
The design of the quantum threshold module is as follows: Assume that the range of pixel values is [0, $2^{q}-1$], and the threshold is $2^{q-1}$. As shown in Fig. 11, from top to bottom, the first q qubits encode the value $2^{q}-1$, the second q qubits encode $G_{max}$, which is the maximum value obtained from the previous stage, and the last $q-1$ qubits encode the threshold $2^{q-1}$. $G_{max}$ will be compared with $2^{q-1}$, when $G_{max}$ is larger, it is set to $2^{q}-1$, otherwise, it is set to zero. The purpose of this module is to obtain the edge pixels.

[Image Description: A quantum threshold module circuit. It inputs a constant $|1\rangle^{\otimes q}$ (representing $2^q-1$), a $q$-bit value $G_{max}$, and a $q-1$-bit threshold $|1\rangle^{\otimes (q-1)}$. It uses a Comparator (Com) and controlled-X (CNOT) gates to conditionally output either the maximum pixel value ($2^q-1$) or $0$ based on the comparison result $G'$. The module is summarized as block $U_T$.]
*Fig. 11: Quantum circuit and simplified diagram of quantum threshold module*

## 3.2 Quantum edge detection algorithm for color images

Edge detection is detecting the edges of the image, and the Sobel operator [30] is one of the most widely used algorithms for edge extraction. The filter window is shown in Fig. 12a, which is a $3\times3$ window and is relevant to the center pixel and its neighborhood pixels. The approximate values of the pixel intensity gradients are calculated using the Sobel operator and the filter window. The classical Sobel operator consists of two masks, as shown in Fig. 12b, c, for calculating the approximate values of the intensity gradient in the horizontal and vertical directions, respectively.

However, the classical Sobel operator can only detect edges in the vertical and horizontal directions, but detecting edges in the diagonal direction is difficult. Thus, this paper improves the Sobel operator by adding two auxiliary positions to enable diagonal edge detection. Figure 12d, e shows the $+45^{\circ}$, and $+135^{\circ}$ masks.

The approximate values of the gradients in four directions can be calculated using the convolution operation in Equation 5 and Equation 6.

$$G_{x}=[\begin{matrix}-1&-2&-1\\ 0&0&0\\ 1&2&1\end{matrix}]*p, \quad G_{y}=[\begin{matrix}-1&0&1\\ -2&0&2\\ -1&0&1\end{matrix}]*p \quad (5)$$

$$G_{45}=[\begin{matrix}0&1&2\\ -1&0&1\\ -2&-1&0\end{matrix}]*p, \quad G_{135}=[\begin{matrix}-2&-1&0\\ -1&0&1\\ 0&1&2\end{matrix}]*p \quad (6)$$

where $*$ is the convolution operation, $G_{x}$, $G_{y}$, $G_{45}$, and $G_{135}$ represent the pixel gradient values detected by the vertical, horizontal, $+45^{\circ}$, and $+135^{\circ}$ edge detection masks, respectively, and p represents the original image. As for the pixel in position $(Y,X)$, Equation 5 and Equation 6 can be transformed into Equation 7, Equation 8, Equation 9, and Equation 10.

$$G_{x}=p(Y-1,X+1)+2p(Y,X+1)+p(Y+1,X+1)-p(Y-1,X-1)-2p(Y,X-1)-p(Y+1,X-1) \quad (7)$$

$$G_{y}=-p(Y-1,X-1)-2p(Y,X-1)-p(Y+1,X-1)+p(Y-1,X+1)+2p(Y,X+1)+p(Y+1,X+1) \quad (8)$$

$$G_{45}=-p(Y,X-1)-2p(Y+1,X-1)-p(Y+1,X)+p(Y-1,X)+2p(Y-1,X+1)+p(Y,X-1) \quad (9)$$

$$G_{135}=-p(Y-1,X)-2p(Y-1,X-1)-p(Y,X-1)+p(Y+1,X)+2p(Y+1,X+1)+p(Y+1,X+1) \quad (10)$$

[Image Description: Five grid illustrations. (a) A 3x3 pixel filter window labeled p(Y-1, X-1) to p(Y+1, X+1). (b) Classical Sobel vertical mask. (c) Classical Sobel horizontal mask. (d) Improved +45 degree mask. (e) Improved +135 degree mask.]
*Fig. 12: The filter window and masks of edge detection. a A filter window. b-e are masks of four directions of improved Sobel operator*

After calculating the gradients in different directions, the gradient value of each pixel is the maximum absolute value of the four gradient values, as shown in Equation 11.

$$G=max\{|G_{x}|,|G_{y}|,|G_{45}|,|G_{135}|\} \quad (11)$$

Based on quantum image processing modules in the previous subsection, the quantum circuit of the edge detection algorithm for color images is designed based on the improved Sobel operator. Firstly, the quantum circuit to obtain four gradients is designed as shown in Fig. 13. The inputs are the color image and neighborhoods prepared in Section 2, and the outputs are the gradient values in four directions. Due to quantum parallelism, the gradients of other pixels are also calculated when calculating the gradient of one pixel.

[Image Description: A large quantum circuit for edge gradient calculation. It takes 9 pixel values from the neighborhood as input and routes them through a complex network of Adder (Add) and Subtractor (Sub) modules, alongside cloning gates ($U_c$), to compute the four directional gradients $|G_x\rangle, |G_y\rangle, |G_{45}\rangle, |G_{135}\rangle$. It corresponds to the block $U_G$.]
*Fig. 13: Quantum circuit and simplified diagram of edge gradient calculation*

Secondly, the gradient values obtained in each direction are used for bubble sorting to calculate the maximum value G of the four directions. The maximum value can be obtained through the maximum value calculation module as shown in Fig. 10. Finally, edge pixel information can be obtained by comparing G with the threshold $T=2^{q-1}$. All pixel gradient values less than T are preserved, and those exceeding T are replaced with T, as shown in Fig. 11. Combining these steps can obtain the quantum circuit for the Sobel operator-based edge gradient calculation. The overall quantum circuit for color image edge detection can be achieved by subtracting the edge gradient from the prepared original image, as shown in Fig. 14.

[Image Description: The complete quantum circuit for color image edge detection. It sequentially connects the 'Preparation of Quantum Color Images and their Neighborhood' block, the 'Quantum Gradient Calculation Module ($U_G$)', the 'Maximum Value Calculation Module (QC)', an X gate for a specific auxiliary qubit, and the 'Quantum Thresholding Operation Module ($U_T$)' to output the final edge image state $|G\rangle$.]
*Fig. 14: Quantum circuit of color image edge detection algorithm*

Figure 14 shows that 19 auxiliary qubits are used. During the image preparation process, four auxiliary qubits are needed. After the image preparation, the auxiliary qubits are set to zero using a reset gate, and these four auxiliary qubits can be repeatedly utilized later. In the subsequent gradient calculation process, eight auxiliary qubits are needed to encode eight quantum ternary adders. Another eight auxiliary qubits are required to encode eight quantum quaternary adders. In the second copy module, an additional auxiliary qubit is necessary to encode the copy bit to replicate the output of a three-qubit adder. In the maximum value calculation module, one auxiliary qubit is needed as the result bit to control the subsequent swap module. Basic quantum operation modules such as quantum adders, quantum subtractors, and quantum comparators still require one auxiliary qubit to complete the operation.

## 3.3 Circuit complexity analysis

In quantum information processing, the complexity of the circuit depends on the number of quantum gates used. When performing edge detection on a color image of size $2^{n}\times2^{n}$ with an intensity range of $[0,2^{q-1}]$, the complexity analysis of a series of quantum algorithms used in the quantum circuit shown in Fig. 14 is as follows. 

The edge extraction module includes the quantum edge gradient calculation, maximum value calculation, and threshold calculation modules. The edge gradient calculation module uses 16 quantum adders, four quantum subtractors, and two quantum copying modules. According to [36], the complexity of a q-bit quantum adder is 12q, the complexity of a q-bit quantum subtractor is 14q, and the complexity of a quantum copying module is q. Therefore, the complexity of the edge gradient calculation module is $(12q\times16+14q\times4=248q)$. 
The maximum value calculation module includes three comparators and three controlled exchange gates, and its complexity is $(87q-18)$. 
The threshold calculation module consists of a comparator, q X gates, and a controlled exchange gate, resulting in a $(14q-6+q+15q=30q-6)$ complexity. Therefore, the complexity of this part is $(248q+87q-18+30q-6=365q-24)$.

In general, image preparation is not included when calculating the circuit complexity of quantum image processing algorithms. Therefore, this paper compares the edge extraction module with other literature, as shown in Table 1.

**Table 1: Comparison of the quantum circuit for quantum colored image edge detection with other methods in terms of circuit complexity and other aspects**

| Method | Circuit complexity | Whether it is a colored image | Simulation |
| :--- | :--- | :--- | :--- |
| [24] | $O(n^{2}+2^{q+4}+q^{2})$ | No | No |
| [26] | $O(n^{2}+2^{q+5}+q^{2})$ | No | No |
| [27] | $O(n^{2}+q^{3})$ | No | Yes |
| Our | $O(q)$ | Yes | Yes |

From Table 1, it can be seen that when large-sized images are used as input for quantum algorithms, the algorithm designed in this paper has a significant advantage in terms of circuit complexity. Additionally, it can process quantum color images, while references [24, 26] and [27] can only process grayscale images. Moreover, this paper presents, for the first time, a simulation of a quantum edge detection algorithm for color images based on the Sobel operator using a quantum simulator. In contrast, references [24, 26] and [27] only performed simple simulations using MATLAB software, which further demonstrates the applicability of the algorithm designed in this paper to quantum color images.
