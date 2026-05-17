# 2 The storage of quantum color image

This paper adopts the OCQR [8] model. In this model, the intensity information per color channel can be easily processed, and the quantum image can be accurately restored to the classic image through quantum measurements. However, the image is prepared separately for each pixel, and therefore, it is necessary to use multi-bit-controlled NOT gates to prepare the color information throughout the entire image [8], imposing an excessive time complexity. To overcome this, we prepare the image in rows and use the information transfer module and the reset operation to convert the multi-bit-controlled NOT gates to Toffoli gates, dramatically reducing time complexity. Given that the auxiliary qubits in the information transfer module can be reused in the following image processing process, the auxiliary qubits are not added to the total qubits required in the entire algorithm. Furthermore, the reset operation can set a qubit state to zero [16]. In the following quantum circuits, the symbol (0) with a square outside represents the reset operation.

## 2.1 The improvement of quantum color image preparation module

This subsection improves the color image preparation module based on the OCQR model, which encode the classic color image into the quantum superposition states described in Eq. 1. Let the size of a color image be $2^{n}\times2^{n}$ and every channel (R,G,B) ranges in $[0,2^{q}-1]$. For the OCQR model, the color image can be written as:

$$|I\rangle=\frac{1}{\sqrt{2^{2n+1}}}\sum_{\lambda=0}^{1}\sum_{Y=0}^{2^n-1}\sum_{X=0}^{2^n-1}\otimes_{i=0}^{q-1}|C_{YX}^{i}\rangle|\lambda\rangle|YX\rangle \quad (1)$$

where $C_{YX}^{i}\in\{0,1\}$, $i=0,1,...,q-1$, which encodes the image's intensity information of the corresponding color channel, $\lambda$ encodes the color channel, $n$ qubits encode the position information on the X axis, and another $n$ qubits encode the position information on the Y axis.

[Image Description: A 4x4 grid of colored squares with their corresponding RGB values and binary coordinates. Beside it is a long mathematical equation representing the quantum state of this 4x4 color image utilizing the OCQR model.]
*Fig. 1: A 4x4 color image represented with the OCQR model*

Figure 1 illustrates an example of a $4\times4$ color image, where every (R,G,B) channel ranges in [0, 7] utilizing the OCQR model. One pixel at position '0000' in Fig. 1 is selected as an example to explain the optimization process. The quantum circuit to encode the pixel to the quantum state is as illustrated in Fig. 2, and the role of each qubit is described next.

[Image Description: A quantum circuit diagram for pixel preparation at position '0000'. It shows horizontal lines for qubits (C0, C1, C2 for intensity, lambda0, lambda1 for color channel, Y0, Y1, X0, X1 for position, and a0-a3 as auxiliary qubits). It includes H gates, Toffoli gates, and CNOT gates grouped into three 'Information transform module' blocks for R, G, and B channels.]
*Fig. 2: Pixel preparation of the '0000' position in Fig. 1*

**Intensity information.** In Fig. 2, from top to bottom, the first three qubits $C_{0}$ to $C_{2}$ represent the intensity information, i.e., the outputs of $C_{0}$ to $C_{2}$ are the first three qubits of binary strings 001000000, 010010000 and 001100000. The results indicate that the intensity of the RGB channel is 1, 2, and 1 in decimal, respectively.
**Color channel information.** The qubits $\lambda_{0}$ and $\lambda_{1}$ represent the corresponding RGB color channel, hence $|00\rangle$, $|01\rangle$, and $|10\rangle$ indicate the 'R', 'G', and 'B' channel, respectively. The outputs of $\lambda_{0}$ and $\lambda_{1}$ are the fourth and fifth qubits of the binary strings 001000000, 010010000, and 001100000.
**Position information.** The qubits $Y_{0}$ and $X_{0}$ represent the position information at the Y and X axis, corresponding to the last two qubits of the binary strings 0010011, 0100111, and 1111011 in Fig. 2.
**Auxiliary qubits.** The qubits $a_{0}$ to $a_{3}$ are four auxiliary qubits that reduce time complexity and prepare the color image processed in rows.

Next, we introduce how the color image per row is prepared using the auxiliary qubits.
The X, Y, and $\lambda$ evolve into the quantum superposition state after H gates, which encode the position and color channel information. Step 1, the Y coordinate information of the first row in the image is transmitted to the auxiliary qubit $a_{3}$ through the quantum gates. Step 2, the position encoding of the first pixel is implemented using Toffoli gates connecting the $a_{3}$ and X coordinate information, which is transmitted to the auxiliary qubit $a_{2}$. Step 3, the location information of $a_{2}$ and the color channel information 'R' are encoded together and transmitted to the auxiliary qubit $a_{1}$. Step 4, the process adds the CNOT gate to $a_{1}$ and the intensity information C so that the position, color channel, and intensity information are in a one-by-one correspondence.

Thus, the position and the color channel information can be shared, which we call an information transfer system (Fig. 2). When the intensity information of a pixel's 'R' channel is available, the auxiliary qubits $a_{1}$ and $a_{2}$ will be set to zero using the reset operation. Then, we repeat steps 3 and 4, and the position information $a_{2}$ and the color channel information 'G' and 'B' are encoded. So, the corresponding intensity information is prepared, and the position information is shared. When a pixel is prepared, $a_{2}$ is set to zero, and steps 2 to 4 are repeated to operate the first line of the other pixel values to share the Y position information. When the first row of pixels is ready, $a_{3}$ is set to zero, and the process repeats steps 1-4 to start preparing the next row of pixels. Reusing the auxiliary qubits requires only four auxiliary qubits for the entire preparation process, which do not increase as the color image size increases. The algorithm is presented in Algorithm 1.

**Algorithm 1: Preparation of the quantum color image**
Input: Classical color image
Output: Quantum color image
1. for Input classic color image information do
2.   for Detect the image information of each row of the first pixel do
3.     Y coordinate information is transmitted to the auxiliary qubit $a_{3}$
4.     for Pixels in the same row do
5.       $a_{3}$ and X coordinate information preparation on $a_{2}$;
6.       for Same pixel do
7.         $a_{2}$ and color channel $\lambda$ refer to the preparation of $a_{1}$;
8.         Add the CNOT gate to $a_{1}$ and intensity information C;
9.         Reset $a_{0}$ and $a_{1}$;
10.      end
11.    end
12.    Reset $a_{2}$;
13.  end
14.  Reset $a_{3}$;
15. end

Figure 2 highlights that the information transfer module can transmit the position and the color channel information to the auxiliary qubit through nine Toffoli gates and one CNOT gate. Then, the intensity information can be obtained through some CNOT gates instead of 4-bit control NOT gates. Although four auxiliary qubits are added for this process, these can be efficiently reused for subsequent filtering.

Let the size of a color image be $2^{n}\times2^{n}$ and every (R,G,B) channel ranges in $[0,2^{q}-1]$. The time complexity of the storage for the color image can be calculated as follows. It requires $2n+2$ H gates to create the position and color channel information at a quantum superposition state, and the preparation of the first-pixel value of each row in the image requires an information transmission module and $3q$ CNOT gates. An information transmission module includes $2n+5$ Toffoli gates and a CNOT gate. $n+6$ Toffoli gates and $3q$ CNOT gates are required to prepare each pixel from the second pixel to the end of the first row. According to [34], the time complexity of an H gate, NOT gate, and CNOT gate is one, respectively, and the time complexity of a Toffoli gate is five. Therefore, the complexity of preparing a row is as follows:

$$(2n+5)\times5+3q+1+[(n+6)\times5+3q](2^{n}-1)+2n+2 = (5n+3q+30)\cdot2^{n}+7n-2 \quad (2)$$

The total time complexity is as follows:

$$[(5n+3q+30)\cdot2^{n}+5n-4]\cdot2^{n}+2n+2 = (5n+30+3q)\cdot2^{2n}+(5n-4)\cdot2^{n}+2n+2 = O((n+q)2^{2n}) \quad (3)$$

According to [35], an n-bit control NOT gate can be constructed by two $(n-1)$-bit control NOT gates and two Toffoli gates, which can be constructed through $(3\times2^{n-2}-2)$ Toffoli gates without an auxiliary qubit. In [8], the OCQR model uses $(2n+2)$-bit control NOT gates, and the number of the multi-bit control NOT gate is $3q2^{2n}$. Hence, the complexity is as follows:

$$5\times3q\times(3\times2^{2n}-2)\times2^{2n}+q+2n+2 = 45q\times2^{4n}-30q\times2^{2n}+2n+q+2 = O(q2^{4n}) \quad (4)$$

Based on [34], an n-bit control NOT gate is equivalent to $2(n-1)$ Toffoli gates and a CNOT gate, which uses $n-1$ auxiliary qubits. If the color image encoding process of [8] adopts this strategy, the complexity reduces to:

$$(2(2n+1)\times5+1)\times3q\cdot2^{2n}+2n+q+2 = 60nq\cdot2^{2n}+33q\cdot2^{2n}+2n+q+2 = O(qn2^{2n}) \quad (5)$$

Nevertheless, it uses $3q\cdot2^{2n}\cdot(2n+1)$ auxiliary qubits. Table 1 reports the comparison results considering time complexity and the number of auxiliary qubits for the color image storage process.

**Table 1: Image preparation compared against the original OCQR model considering auxiliary qubits and time complexity**

| Preparation method | Time complexity | Auxiliary qubits |
| :--- | :--- | :--- |
| [8] without auxiliary qubit | $O(q2^{4n})$ | 0 |
| [8] uses auxiliary qubits | $O(qn2^{2n})$ | $O(qn2^{2n})$ |
| Our | $O((q+n)2^{2n})$ | 4 |


## 2.2 Preparation for neighborhood of pixels

For a filtering window of $3\times3$, the median filtering algorithm sorts all pixels within the window and their 8-neighborhoods and then selects the medians as outputs. The pixel and its 8-neighborhood preparation module will be proposed in this subsection, with the following steps comprising the neighborhood preparation module.

First, we obtain the 8-neighborhood images by performing a circular shift operation on the image to be processed before encoding them to a quantum state. As depicted in Fig. 3, the image in the center is the core image, and the surrounding eight images are the neighborhood images. For example, if we want to get the neighborhood above the central pixel, we should move all the pixels down by one pixel, as illustrated in the sub-figure of the first row and the second column in Fig. 3. It can be seen that pixels in the same position of the nine color images are the pixels to be processed and their 8-neighborhood pixels.

[Image Description: Nine 4x4 grids of colored squares showing a central core image (Y, X) and its eight-neighborhood images obtained by circular shift operations. The pixels in the same position across the nine images represent a pixel and its 8-neighborhood.]
*Fig. 3: 4x4 color image and its eight-neighborhood images*

Second, we design a quantum state to represent the nine color images. For a $2^{n}\times2^{n}$ color image and every (R,G,B) channel ranging in $[0,2^{q}-1]$, the position information of 2n qubits and the 2-qubits channel information are shared by the nine color images, defined as:

$$|I\rangle = \frac{1}{\sqrt{2^{2n+1}}}\sum_{\lambda=0}^{1}\sum_{Y=0}^{2^n-1}\sum_{X=0}^{2^n-1}|C_{Y,X}\rangle\otimes|C_{Y-1,X}\rangle\otimes|C_{Y-1,X+1}\rangle\otimes|C_{Y,X+1}\rangle \otimes |C_{Y+1,X+1}\rangle\otimes|C_{Y+1,X}\rangle\otimes|C_{Y+1,X-1}\rangle\otimes|C_{Y,X-1}\rangle\otimes|C_{Y-1,X-1}\rangle\otimes|\lambda\rangle|YX\rangle \quad (6)$$

where $C_{Y-1,X}, C_{Y-1,X+1}, C_{Y,X+1}, C_{Y+1,X+1}, C_{Y+1,X}, C_{Y+1,X-1}, C_{Y,X-1}, C_{Y-1,X-1}$ represent the grayscale value of eight-neighborhood pixels of $C_{Y,X}$.

Third, we design a quantum circuit that can encode the nine color images to a quantum state in Eq. 6. Since the complete quantum circuit diagram is too large, we only present the preparation of one channel information in one pixel to enhance readability.

[Image Description: A large quantum circuit diagram showing the preparation of nine quantum color images for position '0000' and color channel 'R'. The circuit uses a series of H gates and many CNOT gates to encode the pixel values into the respective quantum states of the neighborhood.]
*Fig. 4: Preparation of nine quantum color images corresponding to position information "0000" and color channel 'R' in Fig. 3*

Figure 4 illustrates the preparation process of the nine color images corresponding to position information '0000' and the color channel 'R' of the nine images in Fig. 3. Figure 4 reveals that the quantum preparation of eight images and their neighborhood can be realized by adding only several CNOT gates based on Fig. 2, which dramatically reduces the preparation complexity and the number of auxiliary qubits. The quantum circuit in the first half of Fig. 4 is part of Fig. 2, which encoding the position information '0000' and color channel 'R' of all images in Fig. 3. The subsequent CNOT gates encode the pixel values of the color channel 'R' at position '0000'. For example, the pixel value at position '0000' of the first picture in Fig. 3 (Position information is $Y+1,X-1$) is 0, and there is no need to add additional CNOT gates, as its default value is 0. The pixel value at position '0000' of the second image (Position information is $Y+1,X$) is 3; then, it needs to use CNOT gates to make the value of $C_{Y+1,X}^{1}$ and $C_{Y+1,X}^{2}$ equal to 1, and so on, we can complete the preparation of other images.

Table 2 reports the comparative results considering the time complexity for preparing a color image and its 8-neighborhood against [8, 30, 31].

**Table 2: Quantum color images and their eight-neighborhood preparation challenged against other methods in terms of auxiliary qubits and time complexity**

| Neighborhood representation | Time complexity | Auxiliary qubits | Quantum color image | Simulate |
| :--- | :--- | :--- | :--- | :--- |
| [30] | $O(qn2^{2n}+28n^{2})$ | $O(qn2^{2n})$ | No | No |
| [31] | $O(qn2^{2n}+10n^{2})$ | $O(qn2^{2n})$ | No | No |
| [8] | $O(qn2^{2n})$ | $O(qn2^{2n})$ | Yes | No |
| Our | $O((q+n)2^{2n})$ | 4 | Yes | Yes |
