import cv2

from app.registry import Param, Tool, register


def run(img, method, clip_limit, tile_size):
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y = ycrcb[:, :, 0]
    if method == "clahe":
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
        ycrcb[:, :, 0] = clahe.apply(y)
    else:
        ycrcb[:, :, 0] = cv2.equalizeHist(y)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)


register(Tool(
    id="histogram",
    name="Histogram Equalization",
    description="Boost contrast by spreading intensities (global or adaptive CLAHE).",
    params=[
        Param("method", "Method", "select", "global", options=["global", "clahe"]),
        Param("clip_limit", "CLAHE clip limit", "float", 2.0, min=1, max=10, step=0.5),
        Param("tile_size", "CLAHE tile size", "int", 8, min=2, max=16, step=1),
    ],
    func=run,
))