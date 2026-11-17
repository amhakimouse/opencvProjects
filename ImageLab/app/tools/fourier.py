import cv2
import numpy as np

from app.registry import Param, Tool, register


def _freq_mask(shape, mode, d0, kind):
    h, w = shape
    yy, xx = np.ogrid[:h, :w]
    dist = np.hypot(yy - h // 2, xx - w // 2)
    low = (dist <= d0).astype(np.float32) if kind == "ideal" else np.exp(-dist ** 2 / (2 * d0 ** 2)).astype(np.float32)
    return low if mode == "low-pass" else 1 - low


def _notch_mask(gray, sensitivity):
    h, w = gray.shape
    F = np.fft.fftshift(np.fft.fft2(gray))
    m = np.log1p(np.abs(F)).astype(np.float32)
    yy, xx = np.ogrid[:h, :w]
    dist = np.hypot(yy - h // 2, xx - w // 2)
    spikes = (((m - cv2.GaussianBlur(m, (0, 0), 8)) > sensitivity) & (dist > 0.03 * min(h, w))).astype(np.uint8)
    spikes = cv2.dilate(spikes, np.ones((5, 5), np.uint8))
    return 1 - spikes.astype(np.float32)


def run(img, mode, cutoff, shape, sensitivity):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h, w = gray.shape

    if mode == "spectrum":
        F = np.fft.fftshift(np.fft.fft2(gray))
        return cv2.normalize(np.log1p(np.abs(F)), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    if mode == "remove periodic noise":
        mask, offset = _notch_mask(gray, sensitivity), 0
    else:
        d0 = cutoff / 100 * min(h, w) / 2
        mask = _freq_mask(gray.shape, mode, d0, shape)
        offset = 128 if mode == "high-pass" else 0

    out = []
    for c in cv2.split(img.astype(np.float32)):
        F = np.fft.fftshift(np.fft.fft2(c))
        out.append(np.fft.ifft2(np.fft.ifftshift(F * mask)).real + offset)
    return np.clip(cv2.merge(out), 0, 255).astype(np.uint8)


register(Tool(
    id="fourier",
    name="Fourier Transform",
    description="See the frequency spectrum, filter frequencies, or remove periodic noise.",
    params=[
        Param("mode", "Mode", "select", "spectrum",
              options=["spectrum", "low-pass", "high-pass", "remove periodic noise"]),
        Param("cutoff", "Cutoff radius %", "float", 30, min=1, max=100, step=1),
        Param("shape", "Filter shape", "select", "gaussian", options=["ideal", "gaussian"]),
        Param("sensitivity", "Spike sensitivity", "float", 3, min=1, max=8, step=0.5),
    ],
    func=run,
))