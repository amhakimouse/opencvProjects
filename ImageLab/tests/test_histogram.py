import numpy as np

from app.tools.histogram import run


def low_contrast():
    row = np.linspace(100, 140, 64).astype(np.uint8)
    return np.dstack([np.tile(row, (64, 1))] * 3)


def test_global_increases_contrast():
    img = low_contrast()
    out = run(img, "global", 2.0, 8)
    assert out.std() > img.std()


def test_clahe_keeps_shape_and_dtype():
    img = low_contrast()
    out = run(img, "clahe", 2.0, 8)
    assert out.shape == img.shape and out.dtype == np.uint8