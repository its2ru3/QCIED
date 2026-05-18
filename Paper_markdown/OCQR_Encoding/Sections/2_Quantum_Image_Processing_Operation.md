# 4 Quantum Image Processing Operation Based on OCQR

In this section, some fundamental operations on OCQR model will be discussed. Because of the particular properties of this model, these operations can be performed flexibly and efficiently.

## 4.1 Channel Swapping Operation
The Channel Swapping Operation (CS) can be divided into three types $CS_{RG}$, $CS_{RB}$ and $CS_{GB}$, which achieve the swap of value in channel R and G, R and B, G and B respectively. If we have a quantum image represented by (3), the specific implementation processes of channel swapping operations are described as follows.

$$CS_{RG}(|I\rangle)=\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|01\rangle+|g_{yx}\rangle\otimes|00\rangle+ |b_{yx}\rangle\otimes|10\rangle+|S_{yx}\rangle\otimes|11\rangle )|yx\rangle) \quad (13)$$
$$CS_{RB}(|I\rangle)=\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|10\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|00\rangle+|S_{yx}\rangle\otimes|11\rangle )|yx\rangle) \quad (14)$$
$$CS_{GB}(|I\rangle)=\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|10\rangle+ |b_{yx}\rangle\otimes|01\rangle+|S_{yx}\rangle\otimes|11\rangle )|yx\rangle) \quad (15)$$

From the equations above, it can be seen that only channel index qubits are transformed. The examples of three CS operations are shown in Fig. 4. We can conclude from the examples that only simple quantum operations is needed to complete the this operation. Therefore the computation complexity of every channel swapping operation is $O(1)$.

[Image Description: A four-part diagram showing channel swapping operations. (a) A 2x2 grid image (top-left Red, top-right Green, bottom-left Blue, bottom-right White). (b) Output image for $CS_{RG}$, swapping the red and green channels. (c) Output image for $CS_{RB}$, swapping the red and blue channels. (d) A simple quantum circuit representing the channel swapping implementation, showing input state $|c(y,x)\rangle$, a set of 2 position qubits $|y\rangle$ and $|x\rangle$, and 2 channel index qubits $|ch\_index_0\rangle, |ch\_index_1\rangle$. A SWAP gate (connected X symbols) acts between the two channel index qubits $|ch\_index_0\rangle$ and $|ch\_index_1\rangle$ to execute the swap.]
*Fig. 4: The examples of channel swapping operation and methods to realize in quantum circuit. a The original image. b-d The output images and realization methods about $CS_{RG}$, $CS_{RB}$ and $CS_{GB}$ Operations*

## 4.2 One Channel Operation
One Channel Changing Operation (OC) can also be divided into three types $OC_{r}$, $OC_{g}$ and $OC_{b}$, which achieve the change of value in channel R, G and B respectively. The specific implementation processes of them are described as (16-18).

$$OC_{R}(|I\rangle)=OC_{R}\left(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle\right)$$
$$=\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}(( |r'_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle) \quad (16)$$
$$|r'_{yx}\rangle=|r_{yx}^{\prime q-1}\cdot\cdot\cdot r_{yx}^{\prime 0}\rangle$$

$$OC_{G}(|I\rangle)=OC_{G}\left(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle\right)$$
$$=\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|00\rangle+|g'_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle) \quad (17)$$
$$|g'_{yx}\rangle=|g_{yx}^{\prime q-1}\cdot\cdot\cdot g_{yx}^{\prime 0}\rangle$$

$$OC_{B}(|I\rangle)=OC_{B}\left(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle\right)$$
$$=\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b'_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle) \quad (18)$$
$$|b'_{yx}\rangle=|b_{yx}^{\prime q-1}\cdot\cdot\cdot b_{yx}^{\prime 0}\rangle$$

For every OC operation, some $(2n+2)-Cnot$ gates (this quantum gate can be decomposed to $O(2n+2)$ Toffoli gates at most [23]) are utilized to change the information of every channel. In the most complex case, every qubit used to represent color value will be changed. Therefore the complexity of one channel operation is no more than $O(q(2n+2))$. Because of the unique coding method for color information, the operations that simultaneously changing the value of three channels can be realized in OCQR model with low computation complexity. Figure 5 shows an example of color reversal operation. After applying the quantum NOT gate in every qubit presenting the channel value, the original image (a) is transformed to image (b). And (c) is the quantum circuit about realizing this operation. It can be seen that the complexity of color reversal operation is O(q).

[Image Description: A three-part diagram showing the color reversal operation. (a) The original 2x2 grid image (top-left Red, top-right Green, bottom-left Blue, bottom-right White). (b) The color-reversed output image (top-left Cyan, top-right Magenta, bottom-left Yellow, bottom-right Black). (c) The quantum circuit for realizing this operation, which applies a series of NOT (X/$\oplus$) gates directly to all the channel value qubits $|c(y,x)^0\rangle$ through $|c(y,x)^7\rangle$. Position and channel index qubits remain untouched.]
*Fig. 5: The examples of color reversal operation. a The original image. b The output image after applying this operation. c the realization method about this operation*

## 4.3 Geometric and Color Transformation on OCQR Quantum Image
Similar to the NEQR model, OCQR image also uses an entangled qubit sequence to represent the position information of all the pixels. Therefore some geometric transformations on NEQR model are also advisable in OCQR image, such as cycle shift operation and so on. The cycle shift operation based on OCQR can be designed using the same method described in [24] and the complexity of this operation on OCQR is also $O(n^{2})$.

On the other hand, since OCQR utilizes a qubit sequence to encode color information instead of angles like MCRQI, most color transformations such as addition operation, subtraction operation and halving operation are applicable in OCQR image. Because q qubits are used to represent the color value in OCQR, the specific implementation processes of these color transformation can follow the way designed in NEQR model [24]. For addition operation, subtraction operation and halving operation in OCQR model, the complexity of them is same which is $O(q)$.
