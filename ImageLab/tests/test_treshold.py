import numpy as np

from app.tools.threshold import run


def two_levels():
    img = np.full((40, 40, 3), 50, np.uint8)
    img[:, 20:] = 200
    return img


def call(img, method="otsu", **kw):
    args = dict(threshold=127, blur=1, block_size=31, c=5, invert=False)
    args.update(kw)
    return run(img, method, **args)


def test_otsu_separates_two_levels():
    out = call(two_levels())
    assert out[:, :20].max() == 0 and out[:, 20:].min() == 255


def test_manual_threshold():
    out = call(two_levels(), "manual", threshold=100)
    assert out[:, :20].max() == 0 and out[:, 20:].min() == 255


def test_invert_flips_result():
    a = call(two_levels())
    b = call(two_levels(), invert=True)
    assert np.array_equal(a, 255 - b)


def test_output_is_binary_2d():
    img = np.random.randint(0, 256, (30, 30, 3), dtype=np.uint8)
    for m in ["manual", "otsu", "triangle", "adaptive mean", "adaptive gaussian"]:
        out = call(img, m)
        assert out.ndim == 2 and set(np.unique(out)) <= {0, 255}