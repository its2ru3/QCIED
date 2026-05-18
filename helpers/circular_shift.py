"""Circular-shifted neighborhood images for the 9-image OCQR encoding.

Replaces ``ocqr_encoding_new.prepare_neighborhood_images`` which used
zero-padding. Per ``notes/todo.md`` §1.1 and [MF §2.2] the eight
neighborhood images are obtained by **circular shifts** of the central
image, so out-of-bounds indices wrap.

Image order matches MF Eq. 6 ([MF §2.2]):
    [core, N, NE, E, SE, S, SW, W, NW]
    = [(0,0), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1)]

This is the same shift-tuple list as in ``ocqr_encoding_new.py`` so the
downstream encoder semantics (which consume image index 0..8) are
unchanged.
"""

import numpy as np

SHIFTS = [
    (0, 0),    # 0  core         C_{Y,X}
    (-1, 0),   # 1  N            C_{Y-1,X}
    (-1, 1),   # 2  NE           C_{Y-1,X+1}
    (0, 1),    # 3  E            C_{Y,X+1}
    (1, 1),    # 4  SE           C_{Y+1,X+1}
    (1, 0),    # 5  S            C_{Y+1,X}
    (1, -1),   # 6  SW           C_{Y+1,X-1}
    (0, -1),   # 7  W            C_{Y,X-1}
    (-1, -1),  # 8  NW           C_{Y-1,X-1}
]


def prepare_neighborhood_images(rgb_matrix):
    """Return the 9 neighborhood matrices using circular indexing.

    At quantum address ``(y, x)`` register ``C_{Y+dy,X+dx}`` should hold the
    pixel value at ``rgb[(y+dy) % h, (x+dx) % w]``.  The shifted matrix
    ``out[i][y, x]`` is constructed so that this property holds.
    """
    h, w = rgb_matrix.shape[:2]
    out = []
    for dy, dx in SHIFTS:
        shifted = np.empty_like(rgb_matrix)
        for y in range(h):
            for x in range(w):
                sy = (y + dy) % h
                sx = (x + dx) % w
                shifted[y, x] = rgb_matrix[sy, sx]
        out.append(shifted)
    return out
