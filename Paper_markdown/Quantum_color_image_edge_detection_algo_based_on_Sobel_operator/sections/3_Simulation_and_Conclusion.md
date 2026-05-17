# 4 The simulation of the proposed algorithm on IBM Q platform

This section simulates the proposed algorithm on the IBM Q platform. IBM has several real quantum devices and simulators available for users through the cloud. These devices are accessible and can be used through Qiskit, an open-source quantum software development kit, and IBM Q Experience, which offers a virtual interface for coding a quantum computer. In addition, researchers can use a local simulator through Qiskit. In the Qiskit framework, the quantum devices, quantum simulator, and local simulator are all called backends. As of May 2022, 5,000 qubits can be achieved through the backend ('Simulator_stabilizer'). The corresponding quantum circuit for median filtering of a quantum color image can be simulated on the IBM Q platform, and the overall quantum circuit can be verified by the output data reflected by the probability histogram of the quantum circuit. For further details on the IBM Q platform, the reader is referred to our previous work [7].

As the IBM Q platform can provide up to 5000 qubits, it can simulate large-sized color images. Considering the large size of the output probability histogram, this paper first simulated an edge detection algorithm for a color image with intensity values ranging from 0 to 7 and a size of $4\times4$. As shown in Fig. 14, four qubits are needed to represent position information, two qubits are needed to represent color channel information, and 27 qubits are required to encode the intensity values of the image and its neighborhood. An additional 20 auxiliary qubits are needed to ensure the success of the quantum adder and other modules, resulting in a total of 53 qubits needed. Therefore, the IBM Q backend selected for this chapter is "simulator_extended_stabilizer", which provides 63 qubits. The designed quantum circuit is transmitted to the quantum simulation backend, and the measurement count is set to 256 to obtain all the information about intensity $|med\rangle$, color channel $\lambda$, and position $|YX\rangle$. The program runs for a total time of 188.38 s. Figure 15a shows the original image, Fig. 15b shows the filtered image, and Fig. 16 shows the probability histogram of the edge detection for a $4\times4$ image color image.

[Image Description: Two 4x4 grids. (a) shows the initial 4x4 color image with a range of color intensities. (b) shows the result of the quantum color image edge detection algorithm applied to the same 4x4 grid, highlighting detected edges with strong intensities against a background of 0s.]
*Fig. 15: a A 4x4 color image; b The result of measuring the quantum color image edge detection algorithm*

[Image Description: A bar chart displaying the measurement results of the quantum color image edge detection circuit. The x-axis lists binary strings representing different quantum states, and the y-axis shows the respective probabilities (e.g., 0.017, 0.024) corresponding to edge pixels.]
*Fig. 16: The probability histogram of a 4x4 color image after edge detection*

The strings in the x-axis of Fig. 16 represent the quantum state output of the quantum measurement. For example, the first string '000000111' indicates that the first four qubits represent the position information of the color image from right to left, the fifth and sixth qubits represent the color channel information, and the last three qubits represent the intensity information. The y-axis represents the probability of the quantum state under quantum measurement. Although the verification confirms that the designed circuit is correct, the image obtained in the figure does not reflect the edge detection result. Therefore, in the following, three standard test color images, such as Peppers and Baboon, with a size of $512\times512$, are selected as the input of the color image edge detection circuit.

The quantum backend "simulator_stabilizer" is chosen for this experiment, and each color image is measured 3.2 million times. However, the maximum number of measurements on IBM Q is 20,000 times. Therefore, the entire circuit is repeated 16 times to obtain all the information and restore the classical filtered image information. The final result of the whole circuit is 1,048,576 strings, so the probability histogram cannot be displayed. Due to the large size of the image and the long queue time of the IBM Q backend, it took 3.5 h to complete the edge detection of the image.

As shown in Fig. 17, it can be seen that the edge detection results of the classical color image are the same as those of the quantum edge detection algorithm in this paper, and the algorithm complexity $O(q)$ is much lower than that of the classical color image edge detection algorithm $O(2^{2n})$.

[Image Description: A grid of 10 sample images featuring 'Peppers' and 'Baboon'. Column 1 (a, f) shows the original color images. Column 2 (b, g) shows the edge detection on the R channel. Column 3 (c, h) shows the edge detection on the G channel. Column 4 (d, i) shows the edge detection on the B channel. Column 5 (e, j) shows the integrated full-color edge detection results where edges form bright, multi-colored outlines against a dark background.]
*Fig. 17: a, f the original image; b, g edge detection results of the "R" channel; c, h Results after edge detection of the "G" channel. d, i edge detection results of the "B" channel; e, j The result of integrated edge detection*

# 5 Conclusion

This paper proposes a quantum color image edge detection algorithm based on the OCQR representation pattern and simulates it on the IBM Q platform. The specific work is as follows: first, various modules that make up the overall circuit, such as quantum adders, quantum subtractors, quantum maximum value calculation modules, and quantum threshold operation modules, are optimized using the reset gate. Based on these basic functional modules, a new edge detection algorithm based on an improved Sobel operator is designed. Through analysis, compared with the existing related work, it has lower circuit complexity and uses fewer qubits. The circuit complexity is reduced from $O(n^{2}+q^{3})$ to $O(q)$, and it can also process quantum color images. Therefore, the proposed quantum circuit helps simulate the proposed algorithm on the IBM Q simulator, and the experiment shows that the algorithm can effectively detect details in quantum color images. 
The quantum color image edge detection algorithm proposed in this paper can be used for quantum machine learning to process large amounts of image data. Further practical applications of quantum image processing still need to be explored; therefore, the ideas discussed in this paper will provide effective solutions for many problems in related fields.

**Acknowledgements:** The authors would like to acknowledge the financial support of the China University Industry-University-Research Innovation Fund Project (2021BCA02004), the National Natural Science Foundations of China (62222601, 61801061, 62176033, 62221005, 61936001), the Natural Science Foundation of Chongqing (cstc2019jcyj-msxmX0124), the China Scholarship Council's Young Key Teachers Overseas Training Program (202107845003) and the key cooperation project of Chongqing Municipal Education Commission (HZ2021008). The first author would also like to acknowledge the assistance she received from the China Scholarship Council and the University of Otago during her visit to New Zealand.

**Data availability:** No datasets were generated or analyzed during the current study.

## References
1. Venegas-Andraca, S.E., Bose, S.: Quantum computation and image processing: new trends in artificial intelligence. In: IJCAI, p. 1563 (2003)
2. Le, P.Q., Dong, F., Hirota, K.: A flexible representation of quantum images for polynomial preparation, image compression, and processing operations. Quantum Inf. Process. 10(1), 63-84 (2011)
3. Zhang, Y., Lu, K., Gao, Y., Wang, M.: Neqr: a novel enhanced quantum representation of digital images. Quantum Inf. Process. 12(8), 2833-2860 (2013)
4. Jiang, N., Wang, J., Mu, Y.: Quantum image scaling up based on nearest-neighbor interpolation with integer scaling ratio. Quantum Inf. Process. 14(11), 4001-4026 (2015)
5. Sang, J., Wang, S., Li, Q.: A novel quantum representation of color digital images. Quantum Inf. Process. 16(2), 1-14 (2017)
6. Liu, K., Zhang, Y., Lu, K., Wang, X., Wang, X.: An optimized quantum representation for color digital images. Int. J. Theor. Phys. 57(10), 2938-2948 (2018)
7. Yuan, S., Wen, C., Hang, B., Gong, Y.: The dual-threshold quantum image segmentation algorithm and its simulation. Quantum Inf. Process. 19(12), 1-21 (2020)
8. Li, P., Shi, T., Zhao, Y., Lu, A.: Design of threshold segmentation method for quantum image. Int. J. Theor. Phys. 59(2), 514-538 (2020)
9. Yuan, S., Zhao, W., Gao, S., Xia, S.: An adaptive threshold-based quantum image segmentation algorithm and its simulation. Quantum Inf. Process. 21(10), 359 (2022)
10. Jiang, S., Zhou, R.G., Hu, W., Li, Y.: Improved quantum image median filtering in the spatial domain. Int. J. Theor. Phys. 58(7), 2115-2133 (2019)
11. Xia, H., Xiao, Y., Song, S., Li, H.: Quantum circuit design of approximate median filtering with noise tolerance threshold. Quantum Inf. Process. 19, 1-23 (2020)
12. Ali, A.E., Abdel-Galil, H., Mohamed, S.: Quantum image mid-point filter. Quantum Inf. Process. 19(8), 1-23 (2020)
13. Yuan, S., Qing, X., Hang, B.: Quantum color image median filtering in the spatial domain: theory and experiment. Quantum Inf. Process. 21(9), 321 (2022)
14. Jiang, N., Wang, L.: Analysis and improvement of the quantum Arnold image scrambling. Quantum Inf. Process. 13(7), 1545-1551 (2014)
15. Zhou, R.G., Sun, Y.J.: Quantum image Gray-code and bit-plane scrambling. Quantum Inf. Process. 14, 1717-1734 (2015)
16. Le, P.Q., Iliyasu, A.M., Dong, F., Hirota, K.: Strategies for designing geometric transformations on quantum images. Theoret. Comput. Sci. 412(15), 1406-1418 (2011)
17. Fan, P., Zhou, R.G., Jing, N., Li, H.S.: Geometric transformations of multidimensional color images based on nass. Inf. Sci. 340, 191-208 (2016)
18. Zhou, R.G., Tan, C., Ian, H.: Global and local translation designs of quantum image based on frqi. Int. J. Theor. Phys. 56(4), 1382-1398 (2017)
19. Zhou, N., Tong, L., Zou, W.: Multi-image encryption scheme with quaternion discrete fractional Tchebyshev moment transform and cross-coupling operation. Signal Process. 211, 109107 (2023)
20. Zhou, N., Hu, L., Huang, Z., Wang, M., Luo, G.: Novel multiple color images encryption and decryption scheme based on a bit-level extension algorithm. Expert Syst. Appl. 238 (2024)
21. Zhang, Y., Lu, K., Gao, Y.: QSobel: a novel quantum image edge extraction algorithm. Sci. China Inf. Sci. 58, 1-13 (2015)
22. Abdel-Khalek, S., Abdel-Azim, G.: New approach to image edge detection based on quantum entropy. J. Russ. Laser Res. 37, 141-154 (2016)
23. Yao, X.W., Wang, H., Liao, Z., Chen, M.C.: Quantum image processing and its application to edge detection: theory and experiment. Phys. Rev. X 7(3), 031041 (2017)
24. Fan, P., Zhou, R.G., Hu, W.: Quantum image edge extraction based on classical Sobel operator for NEQR. Quantum Inf. Process. 18(1), 24 (2019)
25. Fan, P., Zhou, R.G., Hu, W.W.: Quantum image edge extraction based on Laplacian operator and zero-cross method. Quantum Inf. Process. 18, 1-23 (2019)
26. Zhou, R.G., Liu, D.: Q: Quantum image edge extraction based on improved sobel operator. Int. J. Theor. Phys. 58, 2969-2985 (2019)
27. Chetia, R., Boruah, S.: Quantum image edge detection using improved Sobel mask based on NEQR. Quantum Inf. Process. 20, 1-25 (2021)
28. Xu, P., He, Z., Qiu, T.: Quantum image processing algorithm using edge extraction based on Kirsch operator. Opt. Express 28(9), 12508-12517 (2020)
29. Li, P., Shi, T., Lu, A.: Quantum implementation of classical Marr–Hildreth edge detection. Quantum Inf. Process. 19, 1-26 (2020)
30. Ma, Y., Ma, H., Chu, P.: Demonstration of quantum image edge extration enhancement through improved Sobel operator. IEEE Access 8, 210277-210285 (2020)
31. Liu, W., Wang, L.: Quantum image edge detection based on eight-direction Sobel operator for NEQR. Quantum Inf. Process. 21(5), 190 (2022)
32. Fan, P., Xiao, K.: Quantum image edge extraction based on difference of Gaussian operator. Quantum Inf. Process. 22(1), 46 (2023)
33. Chetia, R., Sahu, P.P.: Quantum image edge extraction algorithm for noisy image. IETE J. Res. 70(5), 5348-5363 (2024)
34. Yan, F., Venegas-Andraca, S.E.: Lessons from twenty years of quantum image processing. ACM Trans. Quantum Comput. 6(1), 1-29 (2025)
35. Yan, F., Li, N., Hirota, K.: QHSL: a quantum hue, saturation, and lightness color model. Inf. Sci. 577, 196-213 (2021)
36. Yuan, S., Gao, S., Wen, C.: A novel fault-tolerant quantum divider and its simulation. Quantum Inf. Process. 21(5), 182 (2022)
37. Xia, H., Li, H., Zhang, H., Liang, Y., Xin, J.: Novel multi-bit quantum comparators and their application in image binarization. Quantum Inf. Process. 18(7), 1-17 (2019)
