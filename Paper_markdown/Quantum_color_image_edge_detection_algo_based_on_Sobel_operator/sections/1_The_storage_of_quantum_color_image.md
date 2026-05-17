# 2 The storage of quantum color image

In this paper, the OCQR model was chosen to represent the color image. This model can conveniently handle the intensity information of each color channel and accurately recover the quantum image from the classical image through a finite number of quantum measurements. For a color image with intensity range of $[0,2^{q}-1]$ and a size of $2^{n}\times2^{n}$, the OCQR model can be represented as [6]:

$$|I\rangle=\frac{1}{\sqrt{2^{2n+1}}}\sum_{\lambda=0}^{3}\sum_{Y=0}^{2^{n}-1}\sum_{X=0}^{2^{n}-1}\otimes_{i=0}^{q-1}|C_{YX}^{i}\rangle|\lambda\rangle|YX\rangle \quad (1)$$

where $\lambda$ represents the color channel information, $\lambda\in\{00,01,10,11\}$, $|00\rangle$ represents the 'R' color channel, $|01\rangle$ represents the 'G' channel, $|10\rangle$ represents the 'B' color channel, and $|11\rangle$ is the redundant qubits; $n$ qubits represent the position information along the X-axis, and another $n$ qubits represent the position information along the Y-axis, where $C_{YX}^{i}\in\{0,1\}$, $i=0,1,...,q-1$, which encodes the intensity information of the corresponding color channel for the image. Figure 1 illustrates an example of a $4\times4$ color image, where every (R, G, B) channel ranges in [0, 7] utilizing the OCQR model.

[Image Description: A 4x4 grid of colored pixels showing R, G, B values for each coordinate from (00,00) to (11,11). Next to it is a large equation explicitly defining the quantum superposition state corresponding to this specific image based on the OCQR formulation.]
*Fig. 1: A 4x4 color image represented with the OCQR model*

As edge detection requires neighboring pixels to perform computations, we need to obtain the eight-neighborhood image of Fig. 1, as shown in Fig. 2. In this paper, we use the row-by-row image preparation method proposed in our previous work [13], which can prepare nine images simultaneously with the lowest complexity.

[Image Description: A diagram showing the central 4x4 color image surrounded by eight identical copies of the image shifted by one pixel in each of the 8 directions (up, down, left, right, and diagonals). This illustrates the pixel and its 8-neighborhood configuration.]
*Fig. 2: A 4x4 color image and its eight neighborhood images*

Figure 3 shows the preparation process of a pixel at position '0000' in Fig. 1, and Fig. 4 is the quantum circuit diagram of the nine quantum color images corresponding to the position information '0000' and color channel 'R' in Fig. 2. For detailed preparation procedures, please refer to reference [13].

[Image Description: A quantum circuit diagram for preparing the '0000' pixel in the RGB channels. It uses H gates on position ($Y_0, Y_1, X_0, X_1$) and color channel ($\lambda_0, \lambda_1$) qubits, followed by a sequence of Toffoli and CNOT gates interacting with auxiliary qubits ($a_0, a_1, a_2, a_3$) to encode intensity values on $C_0, C_1, C_2$. The circuit is split into three "Information transform module" blocks for the R, G, and B channels respectively.]
*Fig. 3: Pixel preparation of the '0000' position in Fig. 1*

[Image Description: A large quantum circuit diagram for preparing nine quantum color images for position '0000' and the 'R' channel. It applies H gates to position and color channel qubits, followed by a dense network of CNOT and Toffoli gates acting on a wide array of intensity qubits (representing $C^i_{Y+y,X+x}$) and auxiliary qubits, setting up the necessary neighborhood states.]
*Fig. 4: Preparation of nine quantum color images corresponding to position information "0000" and color channel 'R' in Fig. 2*
