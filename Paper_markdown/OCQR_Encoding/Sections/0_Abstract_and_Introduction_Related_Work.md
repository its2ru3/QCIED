# An Optimized Quantum Representation for Color Digital Images

**Authors:** Kai Liu, Yi Zhang, Kai Lu, Xiaoping Wang, Xin Wang

## Abstract
With the continuous development of quantum computation, quantum mechanics has been widely exploited to meet the storage requirement of high definition image. In this paper, an optimized quantum representation for color digital images (OCQR) is proposed, which makes full use of quantum superposition characteristic to store the RGB value of every pixel. Compared with latest novel quantum representation of color digital images (NCQI), OCQR uses nearly one-third times the qubits to store the pixel value. Meanwhile, some image processing operations related to color information can be executed more simultaneously and conveniently based on OCQR. Therefore, the proposed OCQR model is better suited to represent the quantum color image.

**Keywords:** Quantum image, Image representation, Quantum algorithm

# 1 Introduction
Along with the continuous development of quantum computation, the power of quantum mechanics has attracted the interest of many researchers in recent years. Since Feynman presented the concept of quantum computations in 1982, many quantum algorithms have been proposed such as the quantum integer factoring algorithm [1] and Grover search algorithm [2]. 

At present, some researchers try to apply quantum computing to the field of image processing. There are many quantum methods concerning quantum image representation such as Qubit Lattice [3], Entangled Image [4], Real Ket [5], Flexible Representation of Quantum Images (FRQI) [6], Improved Flexible Representation of Quantum Images (IFRQI) [7], Multi-Channel Quantum Images (MCQI) [8], Novel Enhanced Quantum Representation of Digital Images (NEQR) [9], the Generalized Quantum Image Representation (GQIR) [10] and Novel Quantum Representation of Color Digital Images (NCQI) [11]. In these models, only MCQI and NCQI refer to quantum color image.

MCQI model is designed based on FRQI, which uses the probability amplitude to represent the channels information. Although channel swapping operation and one channel operation can be performed on MCQI model, the quantum image preparation of this model is too complicated, whose complexity is $O(4\times2^{4(n+1)}-6\times2^{2(n+1)}+2(n+1))$ for the image with size $2^{n}\times2^{n}$ according to the discussion in [11]. In order to resolve this problem, NCQI model is proposed to achieve a quadratic speedup in preparation procedure. Based on NCQI, some color image processing operations can be executed conveniently. However, it needs $2n+3q$ qubits to represent the RGB color image with size $2^{n}*2^{n}$ and every channel ranged $[0, 2^{q}-1]$, which does not make full use of quantum superposition to represent pixel values.

In this paper, an optimized quantum representation for color digital images is proposed to improve storage performance of NCQI model. The new representation model uses three-dimensional quantum sequence to store the channel index, channel information and position information of all pixels. Therefore, OCQR model only apply nearly one-third times the qubits to store the pixel value compared with NCQI. And these two models have almost the same complexity of preparation. On the other hand, any image operations performed on an NCQI model can be implemented on OCQR model and some operations based on OCQR can also be executed more conveniently.

The rest of this paper is organized as follows: Section 2 discusses the most relevant works in this field. Then Section 3 describes the newly storage model OCQR and introduces the process of model preparation. In Section 4, some basic operations based on OCQR are discussed. Next, the OCQR is compared with other models in Section 5. Finally, conclusion and prospects about the future work are presented in Section 6.

# 2 Related Work
In order to improve the flexible representation model (FRQI), a novel enhanced quantum representation (NEQR) is proposed which uses the basis state to store the gray-scale information of every pixel. In this model, one image is represented by a two-dimensional quantum sequence, one indicated the pixel position information, while the other described the pixel value. Since this model uses the basis state to store the pixel value for the first time, some quantum image processing algorithms can be implemented very conveniently such as image restoration algorithm [12-14], quantum watermarking algorithm [15-17], and other algorithms [18-22]. For an image with size $2^{n}*2^{n}$ and gray range $[0,2^{q}-1]$, the representative expression of NEQR model is defined as in (1) where $2*n+q$ qubits are needed.

$$|I\rangle = \frac{1}{2^n} \sum_{y=0}^{2^n-1}\sum_{x=0}^{2^n-1} |f(x,y)\rangle |yx\rangle, \quad f(x,y) \in [0, 2^q-1] \quad (1)$$

Inspired by the NEQR model, a novel quantum representation of color digital images (NCQI) is proposed to store and process quantum color image.
