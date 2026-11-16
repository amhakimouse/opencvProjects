import numpy as np

from app.registry import Param, Tool, register


def run(img, kind, amount, seed):
    rng = np.random.default_rng(seed)
    f = img.astype(np.float32)

    if kind == "gaussian":
        out = f + rng.normal(0, amount, f.shape)
    elif kind == "speckle":
        out = f + f * rng.normal(0, amount / 100, f.shape)
    else:
        out = img.copy()
        mask = rng.random(img.shape[:2])
        p = amount / 200
        out[mask < p] = 0
        out[mask > 1 - p] = 255

    return np.clip(out, 0, 255).astype(np.uint8)


register(Tool(
    id="noise",
    name="Noise Simulator",
    description="Add Gaussian, salt and pepper, or speckle noise to test denoising.",
    params=[
        Param("kind", "Noise type", "select", "gaussian", options=["gaussian", "salt & pepper", "speckle"]),
        Param("amount", "Amount", "float", 25, min=0, max=100, step=1),
        Param("seed", "Seed", "int", 42, min=0, max=9999, step=1),
    ],
    func=run,
))