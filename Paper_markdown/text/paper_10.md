**Fig. 10** Quantum circuit and simplified diagram of maximum value calculation module

**Fig. 11** Quantum circuit and simplified diagram of quantum threshold module

## 3.2 Quantum edge detection algorithm for color images

Edge detection is detecting the edges of the image, and the Sobel operator [30] is one of the most widely used algorithms for edge extraction. The filter window is shown in Fig. 12a, which is a $3 \times 3$ window and is relevant to the center pixel and its neighborhood pixels. The approximate values of the pixel intensity gradients are calculated using the Sobel operator and the filter window. The classical Sobel operator consists of two masks, as shown in Fig. 12b, c, for calculating the approximate values of the intensity gradient in the horizontal and vertical directions, respectively.

However, the classical Sobel operator can only detect edges in the vertical and horizontal directions, but detecting edges in the diagonal direction is difficult. Thus, this paper improves the Sobel operator by adding two auxiliary positions to enable diagonal edge detection. Figure 12d, e shows the $+45^{\circ}$, and $+135^{\circ}$ masks.

The approximate values of the gradients in four directions can be calculated using the convolution operation in Equation 5 and Equation 6.

$$G_x = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} * p, G_y = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix} * p \quad (5)$$
