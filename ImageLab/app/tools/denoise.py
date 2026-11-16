import cv2

from app.registry import Param, Tool, register


def run(img, method, ksize, strength):
    ksize |= 1                                   # must be odd
    if method == "mean":
        return cv2.blur(img, (ksize, ksize))
    if method == "gaussian":
        return cv2.GaussianBlur(img, (ksize, ksize), 0)
    if method == "median":
        return cv2.medianBlur(img, ksize)
    if method == "bilateral":
        sigma = strength * 5
        return cv2.bilateralFilter(img, ksize, sigma, sigma)
    return cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)


register(Tool(
    id="denoise",
    name="Advanced Denoising",
    description="Remove noise with mean, Gaussian, median, bilateral or non-local means.",
    params=[
        Param("method", "Method", "select", "median",
              options=["mean", "gaussian", "median", "bilateral", "non-local means"]),
        Param("ksize", "Neighborhood size", "int", 5, min=3, max=15, step=2),
        Param("strength", "Strength (bilateral, NLM)", "float", 10, min=1, max=50, step=1),
    ],
    func=run,
))