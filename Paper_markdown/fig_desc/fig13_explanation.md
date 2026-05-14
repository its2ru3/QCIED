# Fig. 13: Edge Gradient Calculation Module
**Context:** Quantum circuit to calculate the four directional edge gradients for a given pixel using its 3x3 neighborhood.
**Description:** - Inputs are the 9 quantum states representing the central pixel and its 8 neighbors ($C_{Y,X}$, $C_{Y+1,X+1}$, etc.). Outputs are the four directional gradients $G_x$, $G_y$, $G_{45}$, $G_{135}$.
**Gate Sequence:**
1.  **Replication:** 'Uc' (Quantum Replication) modules duplicate required pixel states.
2.  **Weighted Summation:** A massive cascading network of 'Add' (Quantum Adder) modules computes the weighted sums of the neighborhood pixels corresponding to the positive and negative weights of the Sobel masks from Fig. 12.
3.  **Difference:** 'Sub' (Quantum Subtractor) modules calculate the final differences between the summed regions to output the exact gradients for each of the four directions.
4.  Simplified as a '$U_G$' block.
