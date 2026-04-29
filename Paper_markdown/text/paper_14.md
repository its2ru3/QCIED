**Table 1** Comparison of the quantum circuit for quantum colored image edge detection with other methods in terms of circuit complexity and other aspects

| Method | Circuit complexity | Whether it is a colored image | Simulation |
| :--- | :--- | :--- | :--- |
| [24] | $O(n^2 + 2^{q+4} + q^2)$ | No | No |
| [26] | $O(n^2 + 2^{q+5} + q^2)$ | No | No |
| [27] | $O(n^2 + q^3)$ | No | Yes |
| Our | $O(q)$ | Yes | Yes |

in terms of circuit complexity. Additionally, it can process quantum color images, while references [24, 26] and [27] can only process grayscale images. Moreover, this paper presents, for the first time, a simulation of a quantum edge detection algorithm for color images based on the Sobel operator using a quantum simulator. In contrast, references [24, 26] and [27] only performed simple simulations using MATLAB software, which further demonstrates the applicability of the algorithm designed in this paper to quantum color images.

## 4 The simulation of the proposed algorithm on IBM Q platform

This section simulates the proposed algorithm on the IBM Q platform. IBM has several real quantum devices and simulators available for users through the cloud. These devices are accessible and can be used through Qiskit, an open-source quantum software development kit, and IBM Q Experience, which offers a virtual interface for coding a quantum computer. In addition, researchers can use a local simulator through Qiskit. In the Qiskit framework, the quantum devices, quantum simulator, and local simulator are all called backends. As of May 2022, 5,000 qubits can be achieved through the backend ('Simulator_stabilizer'). The corresponding quantum circuit for median filtering of a quantum color image can be simulated on the IBM Q platform, and the overall quantum circuit can be verified by the output data reflected by the probability histogram of the quantum circuit. For further details on the IBM Q platform, the reader is referred to our previous work [7].

As the IBM Q platform can provide up to 5000 qubits, it can simulate large-sized color images. Considering the large size of the output probability histogram, this paper first simulated an edge detection algorithm for a color image with intensity values ranging from $0$ to $7$ and a size of $4 \times 4$. As shown in Fig. 14, four qubits are needed to represent position information, two qubits are needed to represent color channel information, and 27 qubits are required to encode the intensity values of the image and its neighborhood. An additional 20 auxiliary qubits are needed to ensure the success of the quantum adder and other modules, resulting in a total of 53 qubits needed. Therefore, the IBM Q backend selected for this chapter is "simulator_extended_stabilizer", which provides 63 qubits. The designed quantum circuit is transmitted to the quantum simulation backend, and the measurement count is set to 256 to obtain all the information about intensity $|med\rangle$, color channel $\lambda$, and position $|YX\rangle$. The program runs
