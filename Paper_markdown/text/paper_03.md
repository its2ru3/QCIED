**Fig. 1** A $4 \times 4$ color image represented with the OCQR model

(3) The algorithm’s feasibility is verified through simulations on the IBM Quantum Experience (IBM Q) platform. Compared with other quantum edge detection algorithms, this algorithm has a lower circuit complexity and requires fewer ancillary qubits.

The remainder of this paper is organized as follows: Section 2 discusses storing a color image based on the OCQR model, and Sect. 3 builds the quantum edge detection circuit for color images. Section 4 performs the simulation experiment on the IBM Q platform, and finally, Sect. 5 concludes this work.

# 2 The storage of quantum color image

In this paper, the OCQR model was chosen to represent the color image. This model can conveniently handle the intensity information of each color channel and accurately recover the quantum image from the classical image through a finite number of quantum measurements. For a color image with intensity range of $[0, 2^q - 1]$ and a size of $d2^n \times 2^n$, the OCQR model can be represented as [6]:

$$|I\rangle = \frac{1}{\sqrt{2^{2n+1}}} \sum_{\lambda=0}^3 \sum_{Y=0}^{2^n-1} \sum_{X=0}^{2^n-1} \bigotimes_{i=0}^{q-1} |C_{YX}^i\rangle |\lambda\rangle |YX\rangle \quad (1)$$

where $\lambda$ represents the color channel information, $\lambda \in \{00, 01, 10, 11\}$, $|00\rangle$ represents the 'R' color channel, $|01\rangle$ represents the 'G' channel, $|10\rangle$ represents the 'B' color channel, and $|11\rangle$ is the redundant qubits; $n$ qubits represent the position information along the X-axis, and another $n$ qubits represent the position information along the Y-axis, where $C_{YX}^i \in \{0, 1\}$, $i = 0, 1, \dots, q-1$, which encodes the intensity information of the corresponding color channel for the image. Figure 1 illustrates an example of a $4 \times 4$ color image, where every (R, G, B) channel ranges in [0, 7] utilizing the OCQR model.

As edge detection requires neighboring pixels to perform computations, we need to obtain the eight-neighborhood image of Fig. 1, as shown in Fig. 2. In this paper, we use the row-by-row image preparation method proposed in our previous work [13],
