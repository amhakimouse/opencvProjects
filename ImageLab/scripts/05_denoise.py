import time

import cv2
import numpy as np

clean = cv2.imread("samples/test.jpg")
clean = cv2.resize(clean, (512, int(512 * clean.shape[0] / clean.shape[1])))
rng = np.random.default_rng(42)

gauss = np.clip(clean.astype(np.float32) + rng.normal(0, 25, clean.shape), 0, 255).astype(np.uint8)
sp = clean.copy()
mask = rng.random(clean.shape[:2])
sp[mask < 0.05] = 0
sp[mask > 0.95] = 255

filters = {
    "none": lambda x: x,
    "mean 5x5": lambda x: cv2.blur(x, (5, 5)),
    "gaussian 5x5": lambda x: cv2.GaussianBlur(x, (5, 5), 0),
    "median 5": lambda x: cv2.medianBlur(x, 5),
    "bilateral": lambda x: cv2.bilateralFilter(x, 9, 75, 75),
    "nlm": lambda x: cv2.fastNlMeansDenoisingColored(x, None, 10, 10, 7, 21),
}

print(f"{'filter':14}{'gauss dB':>10}{'s&p dB':>10}{'time ms':>10}")
for name, f in filters.items():
    t0 = time.perf_counter()
    a = f(gauss)
    ms = (time.perf_counter() - t0) * 1000
    b = f(sp)
    print(f"{name:14}{cv2.PSNR(clean, a):10.2f}{cv2.PSNR(clean, b):10.2f}{ms:10.0f}")

best = cv2.fastNlMeansDenoisingColored(gauss, None, 10, 10, 7, 21)
cv2.imshow("clean | noisy | median(s&p) | nlm(gauss)", np.hstack([clean, gauss, cv2.medianBlur(sp, 5), best]))
cv2.waitKey(0)
cv2.destroyAllWindows()