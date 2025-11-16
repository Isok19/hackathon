# tools/check_pyzbar.py
from PIL import Image
from pyzbar.pyzbar import decode
import sys

img = sys.argv[1] if len(sys.argv) > 1 else "dataset/images/val/your_image.png"
d = decode(Image.open(img))
print(img, "pyzbar found:", len(d))
for i, det in enumerate(d,1):
    print(i, det.type, det.data.decode('utf-8'), det.rect)
