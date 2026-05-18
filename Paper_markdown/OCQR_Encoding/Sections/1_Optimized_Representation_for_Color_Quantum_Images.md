# 3 Optimized Representation for Color Quantum Images

Suppose the value range of each channel (R, G, B) is $[0,2^{q}-1]$ in the quantum image with size $2^{n}*2^{n}$, the NCQI model can be indicated as the following equation, where $C(x,y)$ represents the pixel value of RGB channels. And the number of qubits employed in this model is $2*n+3q$.

$$|I\rangle=\frac{1}{2^{n}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}|C(x,y)\rangle\otimes|yx\rangle$$
$$|C(x,y)\rangle=|\underbrace{R_{q-1}\cdot\cdot\cdot R_{0}}_{Red}\underbrace{G_{q-1}\cdot\cdot\cdot G_{0}}_{Green}\underbrace{B_{q-1}\cdot\cdot\cdot B_{0}}_{Blue}\rangle \quad (2)$$

For a $2\times2$ color image example with every channel R, G, B ranged $[0,2^{8}-1]$ as shown in Fig. 1, two qubits are used to store the coordinate information and 24 qubits are utilized to store the color information. Therefore, if fewer qubits are used to represent the color information for every pixel, more computing resources will be saved.

[Image Description: A diagram showing a 2x2 grid of pixels representing a color image. The top-left pixel at coordinate Y=1, X=0 is red. The top-right pixel at coordinate Y=1, X=1 is green. The bottom-left pixel at coordinate Y=0, X=0 is blue. The bottom-right pixel at coordinate Y=0, X=1 is white. Beside the grid is a complex quantum state equation for $|I\rangle$ representing this image using the NCQI model, explicitly showing 24-bit strings per pixel concatenating the 8-bit values for the R, G, and B color channels respectively alongside the 2-bit position states.]
*Fig. 1: A 2*2 color image example represented by NCQI model*

In this section, an optimized quantum representation for color digital images will be proposed to improve the performance of storage. And the preparation procedures of OCQR model will also be introduced in details.

## 3.1 Quantum Image Representation Model-OCQR
Based on the model NCQI, we proposed an optimized quantum representation for color digital images. This model uses a three-dimensional quantum sequences to store the color quantum image, one represents the channel value, another indicates the channel index, and the other introduces the position information. Equation (3) shows the details of this model.

$$|I\rangle=\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}|c(x,y)\rangle|ch\_index\rangle|yx\rangle \quad (3)$$
$$= \frac{1}{2^{n+1}} \sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1} \left( |r_{yx}\rangle \otimes |00\rangle + |g_{yx}\rangle \otimes |01\rangle + |b_{yx}\rangle \otimes |10\rangle + |s_{yx}\rangle \otimes |11\rangle \right) |yx\rangle$$
$$\begin{cases} |r_{yx}\rangle=|r_{yx}^{q-1}\cdot\cdot\cdot r_{yx}^{0}\rangle, |g_{yx}\rangle=|g_{yx}^{q-1}\cdot\cdot\cdot g_{yx}^{0}\rangle, \\ |b_{yx}\rangle=|b_{yx}^{q-1}\cdot\cdot\cdot b_{yx}^{0}\rangle, |s_{yx}\rangle=|0^{q-1}\cdot\cdot\cdot 0^{0}\rangle \end{cases}$$

The $|ch\_index\rangle$ indicates the index of channel. It is usually encoded by the two qubits for RGB channel index, where $|00\rangle$ is red channel index, $|01\rangle$ stands for green channel index, $|10\rangle$ means blue while $|11\rangle$ represents a spare channel index. Although the spare channel will not be used in this article, it can be utilized to store other pixel information such as transparency discussed in [8].

For a $2^{n}*2^{n}$ color image with every channel ranged between 0 and $2^{q}-1$, $q$ qubits are used to represent the channel value, 2 qubits to indicate the channel index, and the other $2*n$ qubits to store the coordinate information. Therefore the total number of qubits used in OCQR model is $2*n+q+2$. Compared with the NCQI model that need $2n+3q$ qubits to store the same size image, new representation OCQR can save the resource of storage through applying nearly one-third times the qubits to store the pixel value.

Figure 2 shows a $2*2$ color image and its representative expression in OCQR model. Because three channels ranged $[0, 2^{8}-1]$, eight qubits are needed to represent the channel value. As a result, OCQR model totally utilizes 12 qubits to store this image which is much smaller than the number of qubits required in NCQI model.

[Image Description: A diagram displaying the same 2x2 grid of pixels as in Fig 1: top-left (red), top-right (green), bottom-left (blue), and bottom-right (white). Beside the grid is the mathematical equation for $|I\rangle$ using the OCQR model. Instead of a single 24-bit string per pixel, it shows a superposition of four terms per pixel, representing the 8-bit intensity value entangled with a 2-bit channel index (00 for R, 01 for G, 10 for B, 11 for Spare), dramatically shortening the necessary qubit sequence length per basis state.]
*Fig. 2: A 2*2 color image example represented by OCQR model*

## 3.2 Quantum Image Preparation
To apply the quantum mechanics to image processing, the image information should be stored in a quantum superposition state at first. In this subsection, the preparation procedures for OCQR model will be discussed.

At the beginning, $2n+q+2$ qubits are initialized for a $2^{n}*2^{n}$ color image with each channel ranged $[0, 2^{q}-1]$. The initial state can be shown in the (4).

$$|I\rangle_{0}=|0\rangle^{\otimes q+2+2n} \quad (4)$$

Figure 3 depicts workflow of preparation about the new quantum image model. In this figure, the whole procedure can be divided into two steps.

[Image Description: A flowchart detailing the preparation process of the OCQR model. It consists of three boxes connected by large block arrows. Box 1 ("Initial state") contains the formula $|I\rangle_0 = |0\rangle^{\otimes q+2+2n}$. An arrow labeled "Step 1" leads to Box 2 ("Middle state") containing the superposition formula $|I\rangle_1 = \frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(|0\rangle^{q}\otimes(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|yx\rangle)$. Another arrow labeled "Step 2" leads to Box 3 ("OCQR model") containing the final formula $|I\rangle = \frac{1}{2^{n+1}} \sum_{y=0}^{2^n-1}\sum_{x=0}^{2^n-1}((R_{yx}\otimes|00\rangle + G_{yx}\otimes|01\rangle + B_{yx}\otimes|10\rangle + S_{yx}\otimes|11\rangle)\otimes|yx\rangle)$.]
*Fig. 3: The workflow of preparation process for OCQR model*

Step 1: an empty quantum image is constructed through transforming the initial state $|I\rangle_{0}$ to the middle state $|I\rangle_{1}$.
In this step, the common single quantum gate I and H are used to construct the whole quantum operation as in (6)

$$I=[\begin{matrix}1&0\\ 0&1\end{matrix}] \quad H=\frac{1}{\sqrt{2}}[\begin{matrix}1&1\\ 1&-1\end{matrix}] \quad (5)$$
$$U_{1} = I^{\otimes q+2} \otimes H^{\otimes 2n} \quad (6)$$

Equation (7) interprets the quantum transformation from the initial state $|I\rangle_{0}$ to the intermediate state $|I\rangle_{1}$. After this step, the position information of each pixel is stored in the OCQR quantum model and the color value is set 0 for every pixel.

$$|I\rangle_{1}=U_{1}(|I\rangle_{0})$$
$$=I^{\otimes q}\otimes H^{\otimes 2n+2}(|0\rangle^{q+2+2n})$$
$$=\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(|0\rangle^{q}\otimes(|00\rangle+|01\rangle+|11\rangle)\otimes|yx\rangle) \quad (7)$$

Step 2: To prepare the quantum image, we should set the color value of every pixel in the middle state $|I\rangle_{1}$. Because the color image resolution is $2^{n}*2^{n}$ this step must be divided into $2^{2n}$ sub-operations. For pixel (x, y), the quantum sub-operation for color value setting is shown as (8). It consists of three parts that are $R_{yx}$, $G_{yx}$, $B_{yx}$. These three operations contain q quantum oracles respectively. Taking $R_{yx}$ as example, every qubit in the red channel quantum sequence is processed according to the binary code of the channel value. For $r_{i}=1$, a controlled gate $2n+2$-CNOT is needed. Otherwise, nothing will be done on the quantum state.

$$\Omega_{yx}=\bigoplus_{i=1}^{3}\Omega_{yx}^{i}$$
$$\Omega_{yx}^{1}=R_{yx}, \quad \Omega_{yx}^{2}=G_{yx}, \quad \Omega_{yx}^{3}=B_{yx}$$
$$R_{yx}=\bigoplus_{i=1}^{q}R_{yx}^{i}, \quad G_{yx}=\bigoplus_{i=1}^{q}G_{yx}^{i}, \quad B_{yx}=\bigoplus_{i=1}^{q}B_{yx}^{i}$$
$$R_{yx}^{i}:|0\rangle\rightarrow|0\oplus r_{yx}^{i}\rangle, \quad G_{yx}^{i}:|0\rangle\rightarrow|0\oplus g_{yx}^{i}\rangle, \quad B_{yx}^{i}:|0\rangle\rightarrow|0\oplus b_{yx}^{i}\rangle \quad (8)$$

It is obvious that every sub-operation $\Omega_{yx}$ only set the color value of its corresponding pixel. Therefore, we can use $U_{yx}$ to express the unitary operation for every sub-operation as (9)

$$U_{yx}=(I^{q+2}\otimes\sum_{j=0}^{2^{n}-1}\sum_{i=0,ji\ne yx}^{2^{n}-1}|ji\rangle\langle ji|)+\Omega_{yx}\otimes|yx\rangle\langle yx| \quad (9)$$

After applying sub-operation $U_{yx}$, the middle state $|I_{1}\rangle$ is transformed as in (10)

$$U_{yx}(|I\rangle_{1})=[(I^{q+2}\otimes\sum_{j=0}^{2^{n}-1}\sum_{i=0,ji\ne yx}^{2^{n}-1}|ji\rangle\langle ji|)+\Omega_{yx}\otimes|yx\rangle\langle yx|] \times \left(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0}^{2^{n}-1}(|0\rangle^{q}\otimes(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|ji\rangle)\right)$$
$$=(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0,ji\ne yx}^{2^{n}-1}(|0\rangle^{q}\otimes(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|ji\rangle)) +\frac{1}{2^{n+1}}\Omega_{yx}\otimes|yx\rangle$$
$$=(\frac{1}{2^{n+1}}\sum_{j=0}^{2^{n}-1}\sum_{i=0,ji\ne yx}^{2^{n}-1}(|0\rangle^{q}\otimes(|00\rangle+|01\rangle+|10\rangle+|11\rangle)\otimes|ji\rangle)) + \frac{1}{2^{n+1}} ( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle \quad (10)$$

Through the operation introduced in (10), the color value of relevant pixel is stored. For the sake of setting the color value for every pixel, the operation $U_{2}$ is performed according to the following equation as in (11)

$$U_{2}=\prod_{y=0}^{2^{n}-1}\prod_{x=0}^{2^{n}-1}U_{yx} \quad (11)$$

$$U_{2}(|I\rangle_{1})=\prod_{y=0}^{2^{n}-1}\prod_{x=0}^{2^{n}-1}U_{yx}(|I\rangle_{1})$$
$$=(\frac{1}{2^{n+1}}\sum_{y=0}^{2^{n}-1}\sum_{x=0}^{2^{n}-1}(( |r_{yx}\rangle\otimes|00\rangle+|g_{yx}\rangle\otimes|01\rangle+ |b_{yx}\rangle\otimes|10\rangle+|s_{yx}\rangle\otimes|11\rangle )\otimes|yx\rangle))$$
$$=|I\rangle \quad (12)$$

After the above two steps, the quantum image stored in OCQR model has been prepared. Then we will show the validity of OCQR model through discussing the time complexity of preparation procedures.

**Theorem 1** The whole preparation of OCQR model will cost no more than $O(q+2+2n+ 3q(2n+2)2^{2n})$ for a color image with size $2^{n}*2^{n}$ and every channel (R, G, B) ranged $[0,2^{q}-1]$.
**Proof** The whole preparation consists of two steps. The time complexities of every step will be discussed as follows.

Firstly, there are $q+2+2n$ single quantum gates in the quantum operator $U_{1}$. Therefore, step1 will cost $O(q+2+2n)$.
Secondly, the function of step2 is to set the color value for every pixel in the quantum image. The whole operation is consisted of $2^{2n}$ sub-operations as shown in (11). Every sub-operation $U_{yx}$ contains three quantum operations to set color value of the relevant channel. For every channel, q qubits are applied by a controlled quantum gate in the most complex situation. It is known that all the controlled quantum gates are $(2n+2)$ -CNOT which can be decomposed into at most $O(2n+2)$ single quantum gate at most according to the discussion in [9]. Therefore the time complexity of the operation $U_{yx}$ is $O(3q(2n+2))$. And the whole time complexity of step2 is no more than $O(3q(2n+2)2^{2n})$.

Based on the above analyses, for a color image with size $2^{n}*2^{n}$ and each channel ranged $[0,2^{q}-1]$, the time complexity of preparing OCQR model is no more than $O(q+2+2n+ 3q(2n+2)2^{2n})$, which is approximately linear to the resolution of image.
