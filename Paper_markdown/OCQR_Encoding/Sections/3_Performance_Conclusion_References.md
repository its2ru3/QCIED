# 5 Performance Comparison with Latest Models

In this section, the performance comparison is discussed among the models (OCQR and NCQI).
Firstly, as shown in Table 1, the entangled qubits used in NCQI model is more than that used in OCQR model. NCQI utilized 3q qubits to represent the color information, but the OCQR only makes use of $q+2$ qubits which apply nearly one-third times the qubits to store the pixel value. As we all know, qubits are very valuable computing resources. Therefore, OCQR has higher storage efficiency compared with the NCQI model.

**Table 1: The comparison of qubit number used in two quantum representation models**

| Model | The number of qubits |
| :--- | :--- |
| NCQI | $2n+3q$ |
| OCQR | $2n+q+2$ |

On the other hand, since both NCQI and OCQR use the basis state of a qubit sequence to represent the pixel information, any image transformations performed on an NCQI model can also be implemented on OCQR model. Table 2 shows the complexity comparison about some image processing methods. It can be seen that OCQR is more efficient to conduct some quantum image color transformations.

**Table 2: Complexity comparison about some image processing methods among OCQR and NCQI model**

| Methods | OCQR | NCQI |
| :--- | :--- | :--- |
| Halving operation | $O(q)$ | $O(3q)$ |
| Addition operation | $O(q)$ | $O(3q)$ |
| Subtraction operation | $O(q)$ | $O(3q)$ |
| Color reversal operation | $O(q)$ | $O(3q)$ |
| Channel swapping operation | $O(1)$ | $O(q)$ |
| Cycle shift operation | $O(n^{2})$ | $O(n^{2})$ |

# 6 Conclusion and Future Work
In this paper, an optimized quantum representation for color digital images is proposed based on the quantum superposition and entanglement properties. The OCQR model uses a three-dimensional quantum sequences to represent the channel value, the channel index, and position information respectively. Compared with the latest model NCQI, OCQR not only uses less qubits to save computing resources but is more efficiency to conduct some color transformations. Hence, OCQR is more suitable to store and process the quantum color image.

The storage of image is the basic part of the quantum image processing. In the future, we will try our best to design some quantum image processing methods based on OCQR model.

**Acknowledgements:** The authors appreciate the kind comments and professional criticisms of the anonymous reviewer. This has greatly enhanced the overall quality of the manuscript and opened numerous perspectives geared toward improving the work. This work is supported in part by National High-tech R&D Program of China (863 Program) under Grants 2012AA01A301, 2012AA010901, 2012AA010303, and 2015AA01A301. And it is partially supported by the laboratory pre-research fund (9140C810106150C81001), and by the open project of State Key Laboratory of High-end Server & Storage Technology (2014HSSA01). Moreover, it is a part of program for New Century Excellent Talents in University and National Science Foundation (NSF) China 61272142, 61402492, 61402486, 61379146, 61272483.

## References
1. Shor, P.W.: Algorithms for quantum computation: discrete logarithms and factoring[C]. In: 1994 Proceedings of the 35th Annual Symposium on Foundations of Computer Science, pp. 124-134. IEEE (1994)
2. Grover, L.K.: A fast quantum mechanical algorithm for database search[C]. In: Proceedings of the Twenty-Eighth Annual ACM Symposium on Theory of Computing, pp 212-219. ACM (1996)
3. Venegas-Andraca, S.E., Bose, S.: Storing, processing, and retrieving an image using quantum mechanics[C]. In: AeroSense 2003, pp. 137-147. International Society for Optics and Photonics (2003)
4. Venegas-Andraca, S.E., Ball, J.L.: Processing images in entangled quantum systems[J]. Quantum Inf. Process 9(1), 1-11 (2010)
5. Latorre, J.I.: Image compression and entanglement[J]. arXiv:quant-ph/0510031 (2005)
6. Le, P.Q., Dong, F., Hirota, K.: A flexible representation of quantum images for polynomial preparation, image compression, and processing operations[J]. Quantum Inf. Process 10(1), 63-84 (2011)
7. Sang, J., Wang, S., Shi, X., et al.: Quantum realization of arnold scrambling for IFRQI[J]. Int. J. Theor. Phys., 1-16 (2016)
8. Sun, B., Iliyasu, A.M., Yan, F., et al.: An RGB multi-channel representation for images on quantum computers[J]. J. Adv. Comput. Intell. Intell. Inf. 17(3), 404-417 (2013)
9. Zhang, Y., Lu, K., Gao, Y., et al.: NEQR: A novel enhanced quantum representation of digital images[J]. Quantum Inf. Process. 12(8), 2833-2860 (2013)
10. Jiang, N., Wang, J., Mu, Y.: Quantum image scaling up based on nearest-neighbor interpolation with integer scaling ratio[J]. Quantum Inf. Process 14(11), 1-26 (2015)
11. Sang, J., Wang, S., Li, Q.: A novel quantum representation of color digital images[J]. Quantum Inf. Process 16(2), 42 (2017)
12. Liu, K., Zhang, Y., Lu, K., et al.: Restoration for noise removal in quantum images[J]. Int. J. Theor. Phys., 1-20 (2017)
13. Li, P., Liu, X., Xiao, H.: Quantum image median filtering in the spatial domain[J]. Quantum Inf. Process 17(3), 49 (2018)
14. Yuan, S., Mao, X., Zhou, J., et al.: Quantum image filtering in the spatial domain [J]. Int. J. Theor. Phys., 1-17 (2017)
15. Zhou, R.G., Hu, W., Fan, P.: Quantum watermarking scheme through Arnold scrambling and LSB steganography [J]. Quantum Inf. Process 16(9), 212 (2017)
16. Li, P., Zhao, Y., Xiao, H., et al.: An improved quantum watermarking scheme using small-scale quantum circuits and color scrambling[J]. Quantum Inf. Process 16(5), 127 (2017)
17. Miyake, S., Nakamae, K.: A quantum watermarking scheme using simple and small-scale quantum circuits[J]. Quantum Inf. Process 15(5), 1-16 (2016)
18. Jiang, N., Dang, Y., Wang, J.: Quantum image matching[J]. Quantum Inf. Process 15(9), 1-30 (2016)
19. Yang, Y.G., Zhao, Q.Q., Sun, S.J.: Novel quantum gray-scale image matching[J]. Optik 126(22), 3340-3343 (2015)
20. Dang, Y., Jiang, N., Hu, H., et al.: Analysis and improvement of the quantum image matching[J]. Quantum Inf. Process 16(11), 269 (2017)
21. Zhou, R.-G., Tan, C., Ian, H.: Global and Local Translation Designs of Quantum Image Based on FRQI. Int. J. Theor. Phys. 56(4), 1382-1398 (2017)
22. Zhou, R.-G., Liu, X.A., Zhu, C., Wei, L., Zhang, X., Ian, H.: Similarity analysis between quantum images. Quantum Inf. Process 17, 121 (2018)
23. Yang, G., Song, X., Hung, W.N.N., et al.: Group theory based synthesis of binary reversible circuits[C]. In: International Conference on Theory and Applications of MODELS of Computation, pp. 365-374. Springer (2006)
24. Zhang, Y., Lu, K., Xu, K., et al.: Local feature point extraction for quantum images[J]. Quantum Inf. Process 14(5), 1573-1588 (2015)
