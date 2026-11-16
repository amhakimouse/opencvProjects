import numpy as np

from app.tools.gamma import run


def flat(v):
    return np.full((10, 10, 3), v, np.uint8)


def test_gamma_one_is_identity():
    img = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
    assert np.array_equal(run(img, 1.0, "all channels"), img)


def test_gamma_above_one_brightens():
    assert run(flat(100), 2.0, "all channels").mean() == 160


def test_gamma_below_one_darkens():
    assert run(flat(100), 0.5, "all channels").mean() < 100


def test_black_and_white_are_fixed():
    assert run(flat(0), 3.0, "all channels").mean() == 0
    assert run(flat(255), 3.0, "all channels").mean() == 255