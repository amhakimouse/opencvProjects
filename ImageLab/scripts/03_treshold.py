import cv2
import numpy as np

gray = cv2.imread("samples/test.jpg", cv2.IMREAD_GRAYSCALE)

hist = np.bincount(gray.ravel(), minlength=256).astype(float)
p = hist / hist.sum()
k = np.arange(256)
w0 = np.cumsum(p)                 # class 0 weight for each t
mu = np.cumsum(p * k)             # cumulative mean
mu_t = mu[-1]                     # global mean

with np.errstate(divide="ignore", invalid="ignore"):
    sigma_b = (mu_t * w0 - mu) ** 2 / (w0 * (1 - w0))
sigma_b = np.nan_to_num(sigma_b)
t_manual = int(np.argmax(sigma_b))

t_cv, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
_, tri = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5)

print("Otsu, our formula:", t_manual, "| OpenCV:", int(t_cv))
print("white pixels %: otsu", round(otsu.mean() / 2.55, 1), "| adaptive", round(adapt.mean() / 2.55, 1))

cv2.imshow("gray | otsu | triangle | adaptive", np.hstack([gray, otsu, tri, adapt]))
cv2.waitKey(0)
cv2.destroyAllWindows()