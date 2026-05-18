"""Phase 0 sanity tests — classical reference + circular-shift helper.

These verify the Python building blocks that the quantum pipeline is
compared against. No quantum circuits here.

Run:  wsl .venv_btp/bin/python3 -m tests.test_phase0
"""

import numpy as np

from helpers.circular_shift import SHIFTS, prepare_neighborhood_images
from helpers.classical_reference import (
    SOBEL_MASKS,
    classical_edge_detection,
    classical_sobel_gradients,
)
from helpers.ocqr_encoding_new import prepare_test_matrix_4x4


def test_circular_shift_basic():
    """A pixel placed at (1, 1) appears in each neighbor image at the right offset."""
    h = w = 4
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[1, 1] = [7, 0, 0]  # red marker at (1, 1)

    images = prepare_neighborhood_images(rgb)
    assert len(images) == 9, f"expected 9 neighborhood images, got {len(images)}"

    # The shifted image i should place the marker at (1 - dy, 1 - dx) mod (h, w)
    # because shifted[y, x] = rgb[(y + dy) % h, (x + dx) % w]; we want
    # (y + dy) % h == 1 and (x + dx) % w == 1.
    for i, (dy, dx) in enumerate(SHIFTS):
        expected_y = (1 - dy) % h
        expected_x = (1 - dx) % w
        got = images[i][expected_y, expected_x, 0]
        assert got == 7, (
            f"shift {i} ({dy}, {dx}): expected marker at "
            f"({expected_y}, {expected_x}) but got intensity {got}"
        )
    print("test_circular_shift_basic: OK")


def test_circular_shift_wraps():
    """A pixel at (0, 0) wraps to (h-1, w-1) under the NW shift, etc."""
    h = w = 4
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    rgb[0, 0] = [5, 0, 0]

    images = prepare_neighborhood_images(rgb)
    # Find the image with shift (-1, -1) — that's index 8 (NW).
    nw_image = images[SHIFTS.index((-1, -1))]
    # nw_image[y, x] = rgb[(y - 1) % h, (x - 1) % w]. So at (y, x) = (1, 1)
    # we get rgb[0, 0] = 5. And at (y, x) = (0, 0) we get rgb[-1, -1] = rgb[3, 3] = 0.
    assert nw_image[1, 1, 0] == 5, f"expected NW image[1,1]=5, got {nw_image[1, 1, 0]}"
    assert nw_image[0, 0, 0] == 0, f"expected NW image[0,0]=0, got {nw_image[0, 0, 0]}"
    print("test_circular_shift_wraps: OK")


def test_classical_gradient_known_corner_case():
    """Uniform image → all gradients = 0, all directions, all channels."""
    rgb = np.full((4, 4, 3), 5, dtype=np.uint8)
    grads = classical_sobel_gradients(rgb)
    for name, arr in grads.items():
        assert (arr == 0).all(), f"{name}: expected all zeros for uniform image"
    print("test_classical_gradient_known_corner_case: OK")


def test_classical_gradient_step_edge():
    """Vertical step edge gives a non-zero G_x (vertical mask) somewhere."""
    rgb = np.zeros((4, 4, 3), dtype=np.uint8)
    rgb[:, 2:, 0] = 7  # left half = 0, right half = 7, in R channel
    grads = classical_sobel_gradients(rgb)
    # The vertical-mask (G_x in our table) should pick this up.
    gx = grads["Gx"][..., 0]  # R channel
    assert (np.abs(gx) > 0).any(), "Gx should detect the vertical step edge"
    print("test_classical_gradient_step_edge: OK")
    print(f"  Gx (R channel):\n{gx}")


def test_classical_edge_detection_signature():
    """End-to-end signature: returns (g_prime, g_max, threshold) shapes."""
    rgb = prepare_test_matrix_4x4()
    g_prime, g_max, threshold = classical_edge_detection(rgb, q=3)
    assert g_prime.shape == rgb.shape, f"g_prime shape: {g_prime.shape} vs {rgb.shape}"
    assert g_max.shape == rgb.shape, f"g_max shape: {g_max.shape} vs {rgb.shape}"
    assert threshold == 2 ** (3 - 1), f"default threshold should be 2^(q-1)=4, got {threshold}"
    # All edges should be either 0 or 2^q-1.
    edge_value = 2 ** 3 - 1
    assert ((g_prime == 0) | (g_prime == edge_value)).all(), \
        "g_prime values should be exactly 0 or 2^q-1"
    print("test_classical_edge_detection_signature: OK")
    print(f"  threshold={threshold}, edge_value={edge_value}")
    print(f"  edge counts per channel:")
    for c, name in enumerate("RGB"):
        n_edge = int((g_prime[..., c] == edge_value).sum())
        print(f"    {name}: {n_edge} edge pixels / {g_prime[..., c].size}")


def main():
    print("=" * 64)
    print("Phase 0 tests")
    print("=" * 64)
    print(f"Defined Sobel masks: {list(SOBEL_MASKS)}")
    print()
    test_circular_shift_basic()
    test_circular_shift_wraps()
    test_classical_gradient_known_corner_case()
    test_classical_gradient_step_edge()
    test_classical_edge_detection_signature()
    print()
    print("All Phase 0 tests passed.")


if __name__ == "__main__":
    main()
