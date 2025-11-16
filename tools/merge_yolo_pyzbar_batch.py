# tools/merge_yolo_pyzbar_batch.py
import os, sys
from ultralytics import YOLO
from PIL import Image
from pyzbar.pyzbar import decode
import cv2
import numpy as np

MODEL = sys.argv[1] if len(sys.argv)>1 else "runs/exp/weights/best.pt"
IMG_DIR = sys.argv[2] if len(sys.argv)>2 else "dataset/images/val"
OUT_DIR = "outputs/merged"
os.makedirs(OUT_DIR, exist_ok=True)

model = YOLO(MODEL)

def iou(a,b):
    ax1,ay1,ax2,ay2 = a; bx1,by1,bx2,by2 = b
    inter_x1 = max(ax1,bx1); inter_y1 = max(ay1,by1)
    inter_x2 = min(ax2,bx2); inter_y2 = min(ay2,by2)
    if inter_x2<=inter_x1 or inter_y2<=inter_y1: return 0.0
    inter = (inter_x2-inter_x1)*(inter_y2-inter_y1)
    area_a = (ax2-ax1)*(ay2-ay1); area_b = (bx2-bx1)*(by2-by1)
    return inter/(area_a+area_b-inter)

files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(('.png','.jpg','.jpeg'))]
summary = []
for fn in files:
    path = os.path.join(IMG_DIR, fn)
    print("Processing", fn)
    res = model.predict(source=path, conf=0.2, imgsz=1280, save=False)[0]
    yolo_boxes = []
    for box in res.boxes:
        x1,y1,x2,y2 = map(int, box.xyxy[0].tolist())
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        yolo_boxes.append((x1,y1,x2,y2,cls,conf))
    pil = Image.open(path).convert("RGB")
    py = decode(pil)
    py_boxes = []
    for d in py:
        x,y,w,h = d.rect
        py_boxes.append((x,y,x+w,y+h,d.data.decode('utf-8')))

    merged = yolo_boxes.copy()
    for (bx1,by1,bx2,by2,data) in [(p[0],p[1],p[2],p[3],p[4]) for p in py_boxes]:
        b = (bx1,by1,bx2,by2)
        overlap = False
        for yb in yolo_boxes:
            if iou(b, (yb[0],yb[1],yb[2],yb[3])) > 0.4:
                overlap = True; break
        if not overlap:
            merged.append((bx1,by1,bx2,by2,"pyzbar",1.0))

    img_cv = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    for item in merged:
        x1,y1,x2,y2 = item[0],item[1],item[2],item[3]
        tag = item[4]
        color = (0,255,0) if tag=="pyzbar" else (0,0,255)
        cv2.rectangle(img_cv,(x1,y1),(x2,y2),color,2)
    outpath = os.path.join(OUT_DIR, fn)
    cv2.imwrite(outpath, img_cv)
    summary.append((fn, len(yolo_boxes), len(py_boxes), len(merged)))
print("Done. Summary:")
for s in summary:
    print(s)
