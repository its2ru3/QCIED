# Fig. 10: Maximum Value Calculation Module
**Context:** Circuit to find the absolute maximum value among four $q$-qubit input registers.
**Description:** - Inputs are four registers ($G_x, G_y, G_{45}, G_{135}$), corresponding to gradient values in different directions.
**Gate Sequence:**
1.  This is a macroscopic circuit utilizing the defined 'Com' (Comparator) and 'Swap' modules.
2.  **Stage 1:** A 'Com' block compares $G_x$ and $G_{45}$. A 'Swap' block then routes the larger value to the top wire.
3.  **Stage 2:** In parallel, a 'Com' and 'Swap' block compare $G_y$ and $G_{135}$, routing the larger to its local top wire.
4.  **Stage 3:** A final 'Com' and 'Swap' block compare the two winners from Stage 1 & 2. The absolute maximum is routed to the final output register $G_{max}$.
5.  Simplified as a single 'QC' block.
