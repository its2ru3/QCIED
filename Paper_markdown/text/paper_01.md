# Quantum color image edge detection algorithm based on Sobel operator

Suzhen Yuan$^{\text{1,2,3}}$, Xianli Li$^{\text{1}}$, Shuyin Xia$^{\text{3,4}}$, Xianrong Qing$^{\text{1}}$, Jermiah D. Deng$^{\text{2}}$

Received: 11 October 2024 / Accepted: 12 June 2025 / Published online: 24 June 2025
© The Author(s), under exclusive licence to Springer Science+Business Media, LLC, part of Springer Nature 2025

## Abstract

Edge detection is a preprocessing step in image processing that directly affects the effectiveness of subsequent image processing. However, real-time image preprocessing is challenging to achieve with the increased number and quality of images. Therefore, this paper studies a quantum color image spatial edge detection algorithm and uses the International Business Machines Quantum (IBM Q) quantum simulation platform to simulate and verify the designed quantum circuit. First, the quantum adder, quantum subtractor, quantum maximum value calculation module, and quantum threshold operation module are optimized. Then, based on these modules, a new quantum edge detection algorithm is designed. Finally, the analysis shows that compared with existing related work, the algorithm in this paper has lower circuit complexity and fewer qubits, reducing the circuit complexity from $O(n^2 + q^3)$ to $O(q)$. Finally, the proposed algorithm is simulated on the IBM Q quantum simulator, which can effectively detect the edge information of quantum color images.

**Keywords** Quantum color image processing · Image edge detection algorithm · Quantum image simulation

# 1 Introduction

Digital image processing is a process of processing, analyzing, and changing digital images using computer technology. With the sharp increase in image data volume, the real-time problem of image processing algorithms has become a limitation of the current technical level. Since state-of-the-art algorithms often have overwhelming computational complexity, finding better ways to store and process digital images with high precision and high real-time performance is necessary. Quantum image processing has essential advantages such as parallelism and superposition and can perform more calculations simultaneously, effectively solving the above problems.
