import numpy as np

from app.tools.denoise import run

METHODS = ["mean", "gaussian", "median", "bilateral", "non-local means"]


def flat(v=128):
    return np.full((64, 64, 3), v, np.uint8)


def test_median_removes_isolated_dots():
    img = flat()
    img[10, 10] = 255
    img[30, 40] = 0
    assert np.all(run(img, "median", 3, 10) == 128)


def test_mean_does_not_fully_remove_dots():
    img = flat()
    img[10, 10] = 255
    assert not np.all(run(img, "mean", 3, 10) == 128)


def test_all_methods_reduce_gaussian_noise():
    noise = np.random.default_rng(0).normal(0, 20, (64, 64, 3))
    img = np.clip(128 + noise, 0, 255).astype(np.uint8)
    for m in METHODS:
        assert run(img, m, 5, 10).astype(float).std() < img.astype(float).std()


def test_bilateral_keeps_edge_better_than_gaussian():
    img = flat(50)
    img[:, 32:] = 200
    gap = lambda o: int(o[5, 32, 0]) - int(o[5, 31, 0])
    assert gap(run(img, "bilateral", 9, 5)) >= 148
    assert gap(run(img, "gaussian", 9, 5)) < 100