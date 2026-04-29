**Fig. 12** The filter window and masks of edge detection. **a** A filter window. **b**–**e** are masks of four directions of improved Sobel operator

$$G_{45} = \begin{bmatrix} 0 & 1 & 2 \\ -1 & 0 & 1 \\ -2 & -1 & 0 \end{bmatrix} * p, G_{135} = \begin{bmatrix} -2 & -1 & 0 \\ -1 & 0 & 1 \\ 0 & 1 & 2 \end{bmatrix} * p \quad (6)$$

where $*$ is the convolution operation, $G_x$, $G_y$, $G_{45}$, and $G_{135}$ represent the pixel gradient values detected by the vertical, horizontal, $+45^{\circ}$, and $+135^{\circ}$ edge detection masks, respectively, and $p$ represents the original image. As for the pixel in position $(Y, X)$, Equation 5 and Equation 6 can be transformed into Equation 7, Equation 8, Equation 9, and Equation 10.

$$G_x = p(Y-1, X+1) + 2p(Y, X+1) + p(Y+1, X+1) - p(Y-1, X-1) - 2p(Y, X-1) - p(Y+1, X-1) \quad (7)$$

$$G_y = -p(Y-1, X-1) - 2p(Y, X-1) - p(Y+1, X-1) + p(Y-1, X+1) + 2p(Y, X+1) + p(Y+1, X+1) \quad (8)$$

$$G_{45} = -p(Y, X-1) - 2p(Y+1, X-1) - p(Y+1, X) + p(Y-1, X) + 2p(Y-1, X+1) + p(Y, X-1) \quad (9)$$

$$G_{135} = -p(Y-1, X) - 2p(Y-1, X-1) - p(Y, X-1) + p(Y+1, X) + 2p(Y+1, X+1) + p(Y+1, X+1) \quad (10)$$

After calculating the gradients in different directions, the gradient value of each pixel is the maximum absolute value of the four gradient values, as shown in Equation 11.

$$G = \max \{|G_x|, |G_y|, |G_{45}|, |G_{135}|\} \quad (11)$$

Based on quantum image processing modules in the previous subsection, the quantum circuit of the edge detection algorithm for color images is designed based on the improved Sobel operator.

Firstly, the quantum circuit to obtain four gradients is designed as shown in Fig. 13. The inputs are the color image and neighborhoods prepared in Section 2, and the outputs are the gradient values in four directions. Due to quantum parallelism, the gradients of other pixels are also calculated when calculating the gradient of one pixel.
