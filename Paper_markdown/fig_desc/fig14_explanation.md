# Fig. 14: Color Image Edge Detection Algorithm
**Context:** The macroscopic, high-level quantum circuit integrating all sub-modules to perform the complete edge detection algorithm.
**Description:** - Shows the entire data pipeline from initial states to the final edge map $|G\rangle$.
**Gate Sequence:**
1.  **Neighborhood Preparation:** Generates the central pixel and its 8 neighborhood pixels simultaneously.
2.  **Gradient Calculation ($U_G$):** Takes the 9 pixel values and outputs the four directional gradients ($G_x$, $G_y$, $G_{45}$, $G_{135}$).
3.  **Maximum Value Calculation (QC):** Takes the four gradients and outputs the absolute maximum gradient $G_{max}$.
4.  An intermediate X-gate (NOT gate) prepares an ancilla.
5.  **Thresholding ($U_T$):** Compares $G_{max}$ against the threshold to generate the final binary edge state $|G\rangle$.
