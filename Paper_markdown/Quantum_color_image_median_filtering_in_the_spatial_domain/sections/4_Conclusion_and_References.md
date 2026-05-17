# 5 Conclusion

This paper designs a novel and efficient spatial median filtering algorithm for quantum color images based on the OCQR representation mode, simulated on the IBM Q platform. Specifically, this work first presents a novel method of preparing quantum images based on the OCQR model. The images are encoded in rows, and the information transfer module is designed to convert the multi-bit-controlled NOT gates to Toffoli gates, which dramatically reduces time complexity. Second, we develop a novel method to obtain the neighborhood pixels. Eight color images are used to store neighborhood information, and their position and color channel qubits are shared with the core image, fully exploiting quantum parallelism and thus improving the performance of the subsequent process. Third, we suggest a spatial median filtering algorithm for quantum color imagery based on basic modules. The advantages of the suggested median filtering algorithm are lower time complexity and fewer auxiliary qubits. Compared with current algorithms, the proposed median filtering algorithm affords a reduced time complexity from $O(q^{2})$ to $O(q)$, and the number of auxiliary qubits reduces from $O(q)$ to $O(1)$. The quantum median filtering algorithm provides exponential speed-up compared with its classic counterpart. In addition, the proposed algorithm is simulated in the IBM Q quantum simulator through the Qiskit framework, demonstrating the feasibility of the proposed algorithm. 

The multiple image encoding and processing methods are applicable for image neighborhoods in single image processing schemes and can be applied to quantum machine learning that needs to process large amounts of image data. Nevertheless, more interesting practical applications involving quantum image processing and machine learning should be explored. Overall, the idea discussed in this paper shall provide an efficient solution for many problems in the big data era.

**Acknowledgements:** The authors would like to acknowledge the financial support of the China University Industry-University-Research Innovation Fund Project(2021BCA02004), the National Natural Science Foundation of China (61801061,62176033,61936001), the Natural Science Foundation of Chongqing(cstc2019jcyj-msxmX0124), the expert linguistic services provided from EditSprings (https://www.editsprings.cn) and the valuable inputs of the reviewers.

**Data Availability Statement:** No datasets were generated or analyzed during the current study.

## References
1. Venegas-Andraca, S.E., Bose, S.: Quantum computation and image processing: new trends in artificial intelligence. In: IJCAI, p. 1563 (2003)
2. Le, P.Q., Dong, F., Hirota, K.: A flexible representation of quantum images for polynomial preparation, image compression, and processing operations. Quantum Inf. Process. 10(1), 63-84 (2011)
3. Zhang, Y., Lu, K., Gao, Y., Wang, M.: Neqr: a novel enhanced quantum representation of digital images. Quantum Inf. Process. 12(8), 2833-2860 (2013)
4. Li, H.S., Zhu, Q., Li, M.-C., Ian, H., et al.: Multidimensional color image storage, retrieval, and compression based on quantum amplitudes and phases. Inf. Sci. 273, 212-232 (2014)
5. Jiang, N., Wang, L.: Quantum image scaling using nearest neighbor interpolation. Quantum Inf. Process. 14(5), 1559-1571 (2015)
6. Jiang, N., Wang, J., Mu, Y.: Quantum image scaling up based on nearest-neighbor interpolation with integer scaling ratio. Quantum Inf. Process. 14(11), 4001-4026 (2015)
7. Sang, J., Wang, S., Li, Q.: A novel quantum representation of color digital images. Quantum Inf. Process. 16(2), 1-14 (2017)
8. Liu, K., Zhang, Y., Lu, K., Wang, X., Wang, X.: An optimized quantum representation for color digital images. Int. J. Theor. Phys. 57(10), 2938-2948 (2018)
9. Yan, F., Li, N., Hirota, K.: Qhsl: a quantum hue, saturation, and lightness color model. Inf. Sci. 577, 196-213 (2021)
10. Le, P.Q., Iliyasu, A.M., Dong, F., Hirota, K.: Strategies for designing geometric transformations on quantum images. Theoret. Comput. Sci. 412(15), 1406-1418 (2011)
11. Fan, P., Zhou, R.G., Jing, N., Li, H.S.: Geometric transformations of multidimensional color images based on nass. Inf. Sci. 340, 191-208 (2016)
12. Zhou, R.G., Tan, C., Ian, H.: Global and local translation designs of quantum image based on frqi. Int. J. Theor. Phys. 56(4), 1382-1398 (2017)
13. Zhou, R.G., Liu, X., Luo, J.: Quantum circuit realization of the bilinear interpolation method for gqir. Int. J. Theor. Phys. 56(9), 2966-2980 (2017)
14. Yuan, S., Mao, X., Chen, L., Wang, X.: Improved quantum dilation and erosion operations. Int. J. Quantum Inf. 14(07), 1650036 (2016)
15. Fan, P., Zhou, R.G., Hu, W., Jing, N.: Quantum circuit realization of morphological gradient for quantum grayscale image. Int. J. Theor. Phys. 58(2), 415-435 (2019)
16. Yuan, S., Wen, C., Hang, B., Gong. Y.: The dual-threshold quantum image segmentation algorithm and its simulation. Quantum Inf. Process. 19(12), 1-21 (2020)
17. Li, P., Shi, T., Zhao, Y., Lu, A.: Design of threshold segmentation method for quantum image. Int. J. Theor. Phys. 59(2), 514-538 (2020)
18. Yang, Y.G., Tian, J., Lei, H., Zhou, Y.H., Shi, W.M.: Novel quantum image encryption using one-dimensional quantum cellular automata. Inf. Sci. 345, 257-270 (2016)
19. Wang, J., Geng, Y.C., Han, L., Liu, J.Q.: Quantum image encryption algorithm based on quantum key image. Int. J. Theor. Phys. 58(1), 308-322 (2019)
20. Liu, X., Xiao, D., Liu, C.: Three-level quantum image encryption based on Arnold transform and logistic map. Quantum Inf. Process. 20(1), 1-22 (2021)
21. Wang, L., Ran, Q., Ma, J.: Double quantum color images encryption scheme based on dqrci. Multimed. Tools Appl. 79(9), 6661-6687 (2020)
22. Jiang, N., Wang, L.: Analysis and improvement of the quantum arnold image scrambling. Quantum Inf. Process. 13(7), 1545-1551 (2014)
23. Iliyasu, A.M., Le, P.Q., Dong, F., Hirota, K.: Watermarking and authentication of quantum images based on restricted geometric transformations. Inf. Sci. 186(1), 126-149 (2012)
24. Pang, C.Y., Zhou, R.G., Hu, B.Q., Hu, W., El-Rafei, A.: Signal and image compression using quantum discrete cosine transform. Inf. Sci. 473, 121-141 (2019)
25. Caraiman, S., Manta, V.I.: Quantum image filtering in the frequency domain. Adv. Electr. Comput. Eng. 13(3), 77-85 (2013)
26. Li, P., Xiao, H.: An improved filtering method for quantum color image in frequency domain. Int. J. Theor. Phys. 57(1), 258-278 (2018)
27. Yuan, S., Mao, X., Zhou, J., Wang, X.: Quantum image filtering in the spatial domain. Int. J. Theor. Phys. 56(8), 2495-2511 (2017)
28. Yuan, S., Lu, Y., Mao, X., Luo, Y., Yuan, J.: Improved quantum image filtering in the spatial domain. Int. J. Theor. Phys. 57(3), 804-813 (2018)
29. Li, P., Liu, X., Xiao, H.: Quantum image weighted average filtering in spatial domain. Int. J. Theor. Phys. 56(11), 3690-3716 (2017)
30. Li, P., Liu, X., Xiao, H.: Quantum image median filtering in the spatial domain. Quantum Inf. Process. 17(3), 1-25 (2018)
31. Jiang, S., Zhou, R.G., Hu, W., Li, Y.: Improved quantum image median filtering in the spatial domain. Int. J. Theor. Phys. 58(7), 2115-2133 (2019)
32. Xia, H., Xiao, Y., Song, S., Li, H.: Quantum circuit design of approximate median filtering with noise tolerance threshold. Quantum Inf. Process. 19, 1-23 (2020)
33. Ali, A.E., Abdel-Galil, H., Mohamed, S.: Quantum image mid-point filter. Quantum Inf. Process. 19(8), 1-23 (2020)
34. Nielsen, M.A., Chuang, I.: Quantum Computation and Quantum Information. American Association of Physics Teachers, College Park (2002)
35. Yang, G., Song, X., Hung, W.N., Xie, F., Perkowski, M.A.: Group theory based synthesis of binary reversible circuits. In: International Conference on Theory and Applications of Models of Computation, pp. 365-374 (2006)
36. Xia, H., Li, H., Zhang, H., Liang, Y., Xin, J.: Novel multi-bit quantum comparators and their application in image binarization. Quantum Inf. Process. 18(7), 1-17 (2019)
