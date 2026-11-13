import cv2
import numpy as np

MAX_BYTES = 10 * 1024 * 1024 # 10mb * w * h
MAX_SIDE = 1600


def decode_image(data: bytes) -> np.ndarray:
    if len(data) > MAX_BYTES:
        raise ValueError("File too large (max 10 MB)")
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image file")
    scale = MAX_SIDE / max(img.shape[:2])
    if scale < 1:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return img


def encode_png(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise ValueError("Encoding failed")
    return buf.tobytes()