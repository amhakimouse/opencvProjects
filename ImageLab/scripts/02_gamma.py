import cv2
import numpy as np

img = cv2.imread("samples/test.jpg")


def make_lut(g):
    return np.round(255 * (np.arange(256) / 255) ** (1 / g)).astype(np.uint8) #lookup table: Im2 = 255 · (Im1 / 255)^(1/γ)


for g in (0.5, 1.0, 2.0):
    print(f"gamma {g}: LUT at 0,64,128,192,255 ->", make_lut(g)[[0, 64, 128, 192, 255]])

direct = np.round(255 * (img / 255.0) ** (1 / 2.0)).astype(np.uint8)
via_lut = cv2.LUT(img, make_lut(2.0))
print("max diff LUT vs direct:", np.abs(direct.astype(int) - via_lut.astype(int)).max())

outs = [cv2.LUT(img, make_lut(g)) for g in (0.5, 1.0, 2.0)]
print("mean 0.5 / 1.0 / 2.0:", [round(o.mean(), 1) for o in outs])

cv2.imshow("gamma 0.5 | 1.0 | 2.0", np.hstack(outs))
cv2.waitKey(0)
cv2.destroyAllWindows()