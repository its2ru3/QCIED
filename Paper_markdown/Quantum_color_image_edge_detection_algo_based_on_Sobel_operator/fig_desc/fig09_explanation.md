# Fig. 9: Quantum-Controlled Swap Module
**Context:** Circuit that swaps the contents of two quantum registers based on a single control qubit.
**Description:** - Inputs are a control qubit $C_{out}$ and two $q$-qubit registers $C_{YX}$ and $C_{Y'X'}$.
**Gate Sequence:**
1.  Consists entirely of $q$ parallel **Fredkin gates** (Controlled-SWAP gates).
2.  The $C_{out}$ qubit controls all $q$ Fredkin gates.
3.  If $C_{out} = 1$, the states of the $i$-th qubit in $C_{YX}$ and $C_{Y'X'}$ are swapped. If $0$, they remain unchanged. 
4.  Simplified as a 'Swap' block.
