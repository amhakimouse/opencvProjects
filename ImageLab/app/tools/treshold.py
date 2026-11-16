import cv2

from app.registry import Param, Tool, register


def run(img, method, threshold, blur, block_size, c, invert):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur |= 1                                   # kernel size must be odd
    if blur > 1:
        gray = cv2.GaussianBlur(gray, (blur, blur), 0)
    kind = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY

    if method == "manual":
        _, out = cv2.threshold(gray, threshold, 255, kind)
    elif method == "otsu":
        _, out = cv2.threshold(gray, 0, 255, kind + cv2.THRESH_OTSU)
    elif method == "triangle":
        _, out = cv2.threshold(gray, 0, 255, kind + cv2.THRESH_TRIANGLE)
    else:
        mode = cv2.ADAPTIVE_THRESH_MEAN_C if method == "adaptive mean" else cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        out = cv2.adaptiveThreshold(gray, 255, mode, kind, block_size | 1, c)
    return out


register(Tool(
    id="threshold",
    name="Auto Thresholding",
    description="Binarize an image: manual, Otsu, triangle, or adaptive for uneven lighting.",
    params=[
        Param("method", "Method", "select", "otsu",
              options=["manual", "otsu", "triangle", "adaptive mean", "adaptive gaussian"]),
        Param("threshold", "Threshold (manual)", "int", 127, min=0, max=255, step=1),
        Param("blur", "Pre-blur", "int", 5, min=1, max=15, step=2),
        Param("block_size", "Block size (adaptive)", "int", 31, min=3, max=99, step=2),
        Param("c", "C (adaptive)", "int", 5, min=-20, max=20, step=1),
        Param("invert", "Invert", "bool", False),
    ],
    func=run,
))