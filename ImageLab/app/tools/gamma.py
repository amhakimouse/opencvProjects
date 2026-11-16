import cv2
import numpy as np

from app.registry import Param, Tool, register


def run(img, gamma, apply_to):
    lut = np.round(255 * (np.arange(256) / 255) ** (1 / gamma)).astype(np.uint8)  #lookup table: Im2 = 255 · (Im1 / 255)^(1/γ)
    if apply_to == "luminance":
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        ycrcb[:, :, 0] = cv2.LUT(ycrcb[:, :, 0], lut)
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    return cv2.LUT(img, lut)


register(Tool(
    id="gamma",
    name="Gamma Correction",
    description="Non-linear brightness: lift shadows (gamma > 1) or darken (gamma < 1).",
    params=[
        Param("gamma", "Gamma", "float", 1.0, min=0.2, max=5.0, step=0.1),
        Param("apply_to", "Apply to", "select", "all channels", options=["all channels", "luminance"]),
    ],
    func=run,
))