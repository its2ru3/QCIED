# Fig. 5: Quantum Replication Module
**Context:** Circuit to duplicate a $q$-qubit quantum state $|C\rangle$ into an initialized zero register.
**Description:** - The circuit consists of two $q$-qubit registers: a source $|C\rangle$ and a target $|0\rangle^{\otimes q}$.
**Gate Sequence:**
1.  A parallel array of $q$ **CNOT gates**.
2.  Each qubit $C_i$ in the source register acts as the control for a CNOT gate targeting the corresponding $|0\rangle$ qubit in the target register.
3.  This acts as a quantum bitwise copy operation. It is simplified as a block denoted $U_c$.
