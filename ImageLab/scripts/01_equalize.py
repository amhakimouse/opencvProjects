import cv2
import numpy as np

gray = cv2.imread("samples/test.jpg", cv2.IMREAD_GRAYSCALE)
N = gray.size

hist = np.bincount(gray.ravel(), minlength=256)    # H(k)
cdf = hist.cumsum()                                # Hc(k)
cdf_min = cdf[cdf > 0].min()

lut_course = np.round(255 * cdf / N).astype(np.uint8) #manuel
lut_opencv = np.round((cdf - cdf_min) / (N - cdf_min) * 255).astype(np.uint8)

ref = cv2.equalizeHist(gray)
print("diff, course formula:", np.abs(lut_course[gray].astype(int) - ref.astype(int)).max())
print("diff, OpenCV-style:  ", np.abs(lut_opencv[gray].astype(int) - ref.astype(int)).max())
print("std before/after:", gray.std().round(1), ref.std().round(1))

cv2.imshow("original | equalized", np.hstack([gray, ref]))
cv2.waitKey(0)
cv2.destroyAllWindows()