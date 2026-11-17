import cv2
import numpy as np

gray = cv2.resize(cv2.imread("samples/test.jpg", cv2.IMREAD_GRAYSCALE), (512, 512))
f = gray.astype(np.float32)
x = np.arange(512)
yy, xx = np.ogrid[:512, :512]
dist = np.hypot(yy - 256, xx - 256)

F = np.fft.fftshift(np.fft.fft2(f))
spec = cv2.normalize(np.log1p(np.abs(F)), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# check 1: a pure sine of 20 cycles gives two peaks at +-20 from the center
S = np.abs(np.fft.fftshift(np.fft.fft2(np.tile(np.sin(2 * np.pi * 20 * x / 512), (512, 1)))))
ys, xs = np.nonzero(S > S.max() * 0.5)
print("sine peaks (dy, dx):", [(int(a - 256), int(b - 256)) for a, b in zip(ys, xs)])

# check 2: Parseval, same energy in both domains
e_space = (f ** 2).sum()
e_freq = (np.abs(np.fft.fft2(f)) ** 2).sum() / f.size
print("energy ratio spatial/frequency:", round(e_space / e_freq, 4))


def apply(mask, offset=0):
    return np.clip(np.fft.ifft2(np.fft.ifftshift(F * mask)).real + offset, 0, 255).astype(np.uint8)


low_ideal = apply((dist <= 30).astype(float))
low_gauss = apply(np.exp(-dist ** 2 / (2 * 30 ** 2)))
high = apply((dist > 30).astype(float), 128)

# stripes: Fourier notch vs mean filter
striped = np.clip(f + 40 * np.sin(2 * np.pi * 40 * x / 512), 0, 255).astype(np.uint8)
cv2.imwrite("samples/striped.png", striped)
Fs = np.fft.fftshift(np.fft.fft2(striped.astype(np.float32)))
m = np.log1p(np.abs(Fs)).astype(np.float32)
spikes = (((m - cv2.GaussianBlur(m, (0, 0), 8)) > 3) & (dist > 15)).astype(np.uint8)
spikes = cv2.dilate(spikes, np.ones((5, 5), np.uint8))
cleaned = np.clip(np.fft.ifft2(np.fft.ifftshift(Fs * (1 - spikes))).real, 0, 255).astype(np.uint8)
blurred = cv2.blur(striped, (9, 9))

print("spike pixels removed:", int(spikes.sum()))
print(f"PSNR striped {cv2.PSNR(gray, striped):.1f} | fourier notch {cv2.PSNR(gray, cleaned):.1f} | mean 9x9 {cv2.PSNR(gray, blurred):.1f}")

cv2.imshow("gray | spectrum | low ideal | low gaussian | high", np.hstack([gray, spec, low_ideal, low_gauss, high]))
cv2.imshow("striped | notch | mean 9x9", np.hstack([striped, cleaned, blurred]))
cv2.waitKey(0)
cv2.destroyAllWindows()