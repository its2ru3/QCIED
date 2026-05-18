"""Classical Sobel edge-detection oracle (paper Fig. 12 masks).

This is the ground truth against which the quantum pipeline is verified.
Per ``notes/todo.md`` §0.1 the gradient masks come from Fig. 12 of [MAIN],
not the textually-buggy Eqs. 7-10. Per ``notes/todo.md`` §1.1 the boundary
handling is **circular**, matching [MF §2.2] paragraph 1.

References
----------
[MAIN] Yuan et al., "Quantum color image edge detection algorithm based on
       Sobel operator", §3.2 Fig. 12, §3.2 Eq. 11.
[MF]   Yuan et al., "Quantum color image median filtering in the spatial
       domain", §2.2 (circular neighborhood).
"""

import numpy as np

# Fig. 12b-e masks of [MAIN §3.2]. Convention: kernel[dy+1, dx+1] is the
# weight applied to the pixel at offset (dy, dx) from the centre.
SOBEL_MASKS = {
    "Gx":   np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.int32),
    "Gy":   np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.int32),
    "G45":  np.array([[0, 1, 2], [-1, 0, 1], [-2, -1, 0]], dtype=np.int32),
    "G135": np.array([[-2, -1, 0], [-1, 0, 1], [0, 1, 2]], dtype=np.int32),
}


def classical_sobel_gradients(rgb_matrix):
    """Per-channel Sobel gradients in the 4 directions of Fig. 12.

    Circular boundary per [MF §2.2]: indices wrap with modulo ``h`` / ``w``.
    """
    h, w, channels = rgb_matrix.shape
    out = {name: np.zeros_like(rgb_matrix, dtype=np.int32)
           for name in SOBEL_MASKS}
    for c in range(channels):
        for name, kernel in SOBEL_MASKS.items():
            for y in range(h):
                for x in range(w):
                    acc = 0
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny = (y + dy) % h
                            nx = (x + dx) % w
                            acc += int(kernel[dy + 1, dx + 1]) * int(rgb_matrix[ny, nx, c])
                    out[name][y, x, c] = acc
    return out


def classical_edge_detection(rgb_matrix, q=None, threshold=None):
    """Reference quantum-algorithm output: 2^q-1 for edges, 0 for non-edges.

    Implements Eq. 11 of [MAIN §3.2] (max of |G_x|, |G_y|, |G_45|, |G_135|)
    plus the threshold step (paper Fig. 11) per ``notes/todo.md`` §0.4
    semantics: MSB of |G_max| at bit ``q+1`` of a (q+2)-bit register.

    Parameters
    ----------
    rgb_matrix : (H, W, C) uint8 array with values in [0, 2^q - 1].
    q : intensity bit-depth. Inferred from ``rgb_matrix.max()`` if not given.
    threshold : optional override; defaults to ``2**(q-1)`` per paper.
    """
    if q is None:
        max_val = int(rgb_matrix.max()) if rgb_matrix.size else 0
        q = max(1, int(np.ceil(np.log2(max_val + 1)))) if max_val > 0 else 1
    if threshold is None:
        threshold = 2 ** (q - 1)
    edge_value = 2 ** q - 1

    grads = classical_sobel_gradients(rgb_matrix)
    g_max = np.maximum.reduce([np.abs(grads[k]) for k in grads])
    g_prime = np.where(g_max >= threshold, edge_value, 0).astype(np.int32)
    return g_prime, g_max, threshold
