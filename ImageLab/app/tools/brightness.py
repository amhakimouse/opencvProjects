import cv2

from app.registry import Param, Tool, register


def run(img, beta):
    return cv2.convertScaleAbs(img, alpha=1, beta=beta)


register(Tool(
    id="brightness",
    name="Brightness",
    description="Add a constant to every pixel (point transform).",
    params=[Param("beta", "Brightness", "int", 0, min=-100, max=100, step=1)],
    func=run,
))