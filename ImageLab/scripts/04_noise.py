import cv2
import numpy as np

img = cv2.imread("samples/test.jpg")
rng = np.random.default_rng(42)
f = img.astype(np.float32)


def clip(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def psnr(a, b):  #(peak signal-to-noise ratio) measures how close a noisy image B is to the clean one A
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return 10 * np.log10(255**2 / mse)


gauss = clip(f + rng.normal(0, 25, f.shape))
speckle = clip(f + f * rng.normal(0, 0.25, f.shape))

sp = img.copy()
mask = rng.random(img.shape[:2])
sp[mask < 0.05] = 0
sp[mask > 0.95] = 255

for name, n in [("gaussian s=25", gauss), ("speckle 0.25", speckle), ("salt&pepper 10%", sp)]:
    print(f"{name:16} PSNR mine: {psnr(img, n):.2f} dB | OpenCV: {cv2.PSNR(img, n):.2f} dB")

cv2.imshow("original | gaussian | speckle | salt&pepper", np.hstack([img, gauss, speckle, sp]))
cv2.waitKey(0)
cv2.destroyAllWindows()