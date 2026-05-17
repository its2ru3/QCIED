# 3 Median filtering algorithm of quantum color image

This section designs the median filtering algorithm for quantum color imagery. First, we introduce the comparator [36], controlled switch [33], and sorting [31] modules. Then, we design the median filtering algorithm for the quantum color images utilizing these modules.

## 3.1 Comparator module

Suppose there are two numbers $a$ and $b$. Although current comparators [30, 31] can distinguish three states, i.e., $a>b$, $a<b$, and $a=b$, this paper adopts the quantum comparator of [36], which can distinguish only two states $a>b$ and $a\le b$, but affords a lower time complexity. Suppose a composite system comprises two n-qubits quantum states $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$. The quantum comparator compares the qubit strings $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$. $|C_{out}\rangle$ is the output qubit of the quantum comparator. When $|C_{YX}\rangle\ge|C_{Y^{\prime}X^{\prime}}\rangle$, $|C_{out}\rangle=|0\rangle$. It is worth noting that the auxiliary qubits do not increase as the numbers involved in the comparison increase. Compared with [30, 31], the time complexity of the proposed quantum comparator decreases from an exponential level to a polynomial level. The corresponding quantum circuit diagram is illustrated in Fig. 5.

[Image Description: A quantum circuit diagram for a three-digit quantum comparator, alongside its simplified block diagram equivalent (labeled 'Com'). The circuit uses CNOT, Toffoli, and X gates to compare two 3-qubit inputs, outputting the result on an auxiliary qubit $C_{out}$.]
*Fig. 5: Three-digit quantum comparator*

## 3.2 Swap module

A quantum swap module aims to realize the exchange of two pixels [33], with Fig. 6 presenting the quantum circuit of a swap module. The latter figure reveals that the swap module comprises some controlled swap gates and the control bit is the result qubit $|C_{out}\rangle$ of the comparator. For example, given a two n-bit composite system $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$, among them, $|C_{YX}\rangle=|C_{YX}^{n-1}C_{YX}^{n-2}\cdot\cdot\cdot C_{YX}^{0}\rangle$ and $|C_{Y^{\prime}X^{\prime}}\rangle=|C_{Y^{\prime}X^{\prime}}^{n-1}C_{Y^{\prime}X^{\prime}}^{n-2}\cdot\cdot\cdot C_{Y^{\prime}X^{\prime}}^{0}\rangle$. When $C_{out}=1$, $|C_{YX}\rangle|C_{Y^{\prime}X^{\prime}}\rangle$ transforms into $|C_{Y^{\prime}X^{\prime}}\rangle|C_{YX}\rangle$ after passing through the quantum swap module. When $C_{out}=0$ no transformation occurs. Compared with [30, 31], the output qubit of the swap module is reduced to one qubit, which will significantly reduce time complexity.

[Image Description: A quantum circuit diagram showing a controlled swap module and its block diagram representation (labeled 'Swap'). The control bit $C_{out}$ determines whether the two q-bit inputs are swapped using multiple Fredkin (controlled-SWAP) gates.]
*Fig. 6: Quantum controlled swap module*

## 3.3 Sort module

The sorting module comprises three comparison modules and three controlled swap modules and is designed to sort three pixels in ascending order. This module sorts three intensity values to calculate the maximum, intermediate, and minimum. Unlike [31], in this paper, the output qubit of the comparator module is reused by the reset operation. Thus, the total number of qubits required in the sort module is reduced. As shown in Fig. 7, when three pixel values $|C_{Y,X}\rangle=|C_{Y,X}^{q-1}C_{Y,X}^{q-2}\cdot\cdot\cdot C_{Y,X}^{0}\rangle$, $|C_{Y+1,X}\rangle=|C_{Y+1,X}^{q-1}C_{Y+1,X}^{q-2}\cdot\cdot\cdot C_{Y+1,X}^{0}\rangle$, and $|C_{Y+1,X+1}\rangle=|C_{Y+1,X+1}^{q-1}C_{Y+1,X+1}^{q-2}\cdot\cdot\cdot C_{Y+1,X+1}^{0}\rangle$ are inputs, the outputs are $|C_{Y,X}^{\prime}\rangle=Max$, $|C_{Y+1,X}^{\prime}\rangle=Med$, and $|C_{Y+1,X+1}^{\prime}\rangle=Min$. Thus, this sort module can realize the sort function, utilizing a single auxiliary qubit.

[Image Description: A quantum circuit for a Sort module composed of three comparator modules (Com) and three swap modules (Swap) arranged sequentially. It takes three q-bit inputs and sorts them, shown alongside its simplified block representation.]
*Fig. 7: Sort module*

## 3.4 Median filtering algorithm of quantum color image

Next, we design the median filtering algorithm for a quantum color image. We adopt the method of [31] to obtain the median, involving the following steps. First, we sort the three elements of each column in the filter window (Fig. 8a), where B7, B8 and B9 are the maximum values of each column (Fig. 8b). Then, the three pixels of each row are sorted, and C3, C6, and C9 are the maximum values of each row (Fig. 8c). Finally, we sort the diagonal three pixels C3, C5, and C7, and the median value D2 (Fig. 8d) of the diagonal three pixels is the median value of the nine pixels in the filter window. For the detailed proof, the reader is referred to [31]. Due to quantum parallelism, when median filtering is performed on one pixel, it is also performed on the other pixels. Figure 9 illustrates the quantum circuit that realizes the median filtering algorithm for quantum color images. Table 3 reports the comparison results among existing median filtering algorithms of quantum grayscale images and the proposed algorithm, where $q$ represents a total of $2^{q}$ intensity levels.

[Image Description: A 4-step diagram showing the process of calculating a median from a 3x3 grid of pixels (A1 to A9). Step (a) shows the initial grid. Step (b) sorts columns resulting in B1-B9. Step (c) sorts rows resulting in C1-C9. Step (d) sorts the diagonal elements (C3, C5, C7) to find the median value D2.]
*Fig. 8: Median calculation [31]*

[Image Description: A block-level quantum circuit diagram for median calculation utilizing nine 'Sort' modules connected to process the 9 inputs (representing the 3x3 neighborhood). The equivalent combined block is labeled 'Median Calculation', outputting the 'Med' value.]
*Fig. 9: The quantum circuit of the median filtering algorithm*

The time complexity of a q-bit control NOT gate is $10(q-1)+1=10q-9$. It should be noted that [31] calculates only the time complexity of the swap gate and ignores the time complexity of the t-bit control swap gate. Furthermore, Jiang et al. [31] uses a 2-bit control swap gate, namely three 3-bit control NOT gates, so the time complexity of a 2-bit control swap gate is $21\times3q=63q$. Nevertheless, the proposed algorithm adopts the 1-bit control swap gate, which includes three Toffoli gates, and therefore, the time complexity of a 1-bit control swap gate is $5\times3q=15q$. 

In conclusion, the median filtering algorithm for quantum grayscale images [31] adopts 21 comparators (whose time complexity is $21q^{2}$) and 21 2-bit control swap gates, with a time complexity of $21q^{2}+63q\times21=21q^{2}+1323q$. The comparator used in this article has a time complexity of $14q-6$ and a total of 21 comparators (time complexity of $21\times(14q-6)=294q-126$) and 21 control swap gates (time complexity of $21\times15q=315q$). Thus, the total time complexity of the proposed quantum median filtering algorithm is $609q-126$. In addition, we use the reset operation to reuse qubits, and thus, the total number of auxiliary qubits during median calculation is constant.

**Table 3: Advantages and disadvantages of the existing median filtering algorithm in time complexity, auxiliary qubits, and simulation**

| Median filtering algorithms | Time complexity | Auxiliary qubit numbers | Simulation |
| :--- | :--- | :--- | :--- |
| [30] | $30q^{2}+1890q$ | $O(q)$ | No |
| [31] | $21q^{2}+1323q$ | $O(q)$ | No |
| Our | $609q-126$ | 2 | Yes |
