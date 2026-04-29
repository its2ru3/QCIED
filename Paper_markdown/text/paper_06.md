**Fig. 4** Preparation of nine quantum color images corresponding to position information "0000" and color channel 'R' in Fig. 2

circuit diagram is shown in Fig. 6, where $|C_{YX}\rangle = |C_{YX}^{n-1}C_{YX}^{n-2} \dots C_{YX}^0\rangle$ and $|C_{Y'X'}\rangle = |C_{Y'X'}^{n-1}C_{Y'X'}^{n-2} \dots C_{Y'X'}^0\rangle$ represent two addends, $|a_0\rangle$ and $|a_1\rangle$ are two auxiliary qubits with an initial value of $|0\rangle$ used as carry bits throughout the adder. $|s\rangle = |s_0s_n \dots s_1\rangle$ represents the result obtained after addition. The output of the quantum adder is $|s\rangle \otimes |b\rangle = |C_{YX} + C_{Y'X'}\rangle \otimes |C_{Y'X'}\rangle$, and the corresponding unitary evolution is shown in Equation 3.

$$U_{add} \left| C_{YX}^{n-1} \dots C_{YX}^0 \right\rangle \otimes \left| C_{Y'X'}^{n-1} \dots C_{Y'X'}^0 \right\rangle = \left| s_0s_n \dots s_1 \right\rangle \otimes \left| C_{Y'X'}^{n-1} \dots C_{Y'X'}^0 \right\rangle \quad (3)$$
