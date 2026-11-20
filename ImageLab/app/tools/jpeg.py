import cv2
import numpy as np

from app.registry import Param, Tool, register

Q_LUM = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61], [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56], [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77], [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101], [72, 92, 95, 98, 112, 100, 103, 99]], np.float32)

Q_CHR = np.full((8, 8), 99, np.float32)
Q_CHR[:4, :4] = [[17, 18, 24, 47], [18, 21, 26, 66], [24, 26, 56, 99], [47, 66, 99, 99]]


def _dct_matrix():
    k = np.arange(8)[:, None]
    n = np.arange(8)[None, :]
    d = np.sqrt(2 / 8) * np.cos((2 * n + 1) * k * np.pi / 16)
    d[0] /= np.sqrt(2)
    return d.astype(np.float32)


D = _dct_matrix()


def _qtable(base, quality):
    scale = 5000 / quality if quality < 50 else 200 - 2 * quality
    return np.clip(np.floor((base * scale + 50) / 100), 1, 255).astype(np.float32)


def _blocks(ch):
    h, w = ch.shape
    return ch.reshape(h // 8, 8, w // 8, 8).swapaxes(1, 2).reshape(-1, 8, 8)


def _unblocks(b, h, w):
    return b.reshape(h // 8, w // 8, 8, 8).swapaxes(1, 2).reshape(h, w)


def codec(ch, q):
    h, w = ch.shape
    coef = D @ _blocks(ch - 128) @ D.T
    quant = np.round(coef / q)
    rec = D.T @ (quant * q) @ D
    return _unblocks(rec, h, w) + 128, quant


def run(img, quality, subsample, view):
    h, w = img.shape[:2]
    pad = cv2.copyMakeBorder(img, 0, (-h) % 16, 0, (-w) % 16, cv2.BORDER_REPLICATE)
    y, cr, cb = cv2.split(cv2.cvtColor(pad, cv2.COLOR_BGR2YCrCb).astype(np.float32))

    qy, qc = _qtable(Q_LUM, quality), _qtable(Q_CHR, quality)
    y2, _ = codec(y, qy)

    chroma = []
    for c in (cr, cb):
        if subsample:
            small = cv2.resize(c, (c.shape[1] // 2, c.shape[0] // 2), interpolation=cv2.INTER_AREA)
            rec, _ = codec(small, qc)
            rec = cv2.resize(rec, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_LINEAR)
        else:
            rec, _ = codec(c, qc)
        chroma.append(rec)

    ycc = np.clip(cv2.merge([y2, chroma[0], chroma[1]]), 0, 255).astype(np.uint8)
    out = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)[:h, :w]

    if view == "error x10":
        return np.clip(np.abs(out.astype(np.int16) - img.astype(np.int16)) * 10, 0, 255).astype(np.uint8)
    return out


register(Tool(
    id="jpeg",
    name="JPEG Simulator",
    description="Simulate JPEG: chroma subsampling, 8x8 DCT, quantization. See blocks and artifacts.",
    params=[
        Param("quality", "Quality", "int", 50, min=1, max=100, step=1),
        Param("subsample", "Chroma subsampling 4:2:0", "bool", True),
        Param("view", "View", "select", "result", options=["result", "error x10"]),
    ],
    func=run,
))