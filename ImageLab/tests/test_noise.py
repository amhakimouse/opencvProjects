import numpy as np

from app.tools.noise import run

KINDS = ["gaussian", "salt & pepper", "speckle"]


def flat(v=128):
    return np.full((100, 100, 3), v, np.uint8)


def test_zero_amount_is_identity():
    img = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
    for k in KINDS:
        assert np.array_equal(run(img, k, 0, 1), img)


def test_same_seed_same_noise():
    for k in KINDS:
        assert np.array_equal(run(flat(), k, 30, 7), run(flat(), k, 30, 7))
        assert not np.array_equal(run(flat(), k, 30, 7), run(flat(), k, 30, 8))


def test_gaussian_std_matches_sigma():
    out = run(flat(), "gaussian", 10, 1).astype(float)
    assert 9 < out.std() < 11


def test_salt_pepper_only_extremes():
    out = run(flat(), "salt & pepper", 20, 1)
    changed = out != 128
    assert set(np.unique(out[changed])) <= {0, 255}
    assert 0.15 < changed.mean() < 0.25


def test_speckle_stronger_on_bright_areas():
    assert run(flat(40), "speckle", 30, 1).std() < run(flat(200), "speckle", 30, 1).std()