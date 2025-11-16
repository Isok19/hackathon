# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, FileResponse
# from ultralytics import YOLO
# from PIL import Image, ImageDraw, ImageFont
# import io
# import os

# app = FastAPI(title="Document Inspector API")

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",   # React Dev Server
#         "http://127.0.0.1:5173",
#         "http://localhost:5174",   # запас на случай смены порта
#         "http://localhost:5175",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Загрузка модели (после обучения)
# MODEL_PATH = "runs/detect/document_inspector/weights/best.pt"
# model = None

# # Маппинг классов
# CLASS_NAMES = {
#     0: "Подпись",
#     1: "Печать",
#     2: "QR-код",
#     3: "Другое"
# }

# COLORS = {
#     0: "#FF0000",  # красный для подписи
#     1: "#00FF00",  # зеленый для печати
#     2: "#0000FF",  # синий для QR
#     3: "#FFFF00"   # желтый для другого
# }

# @app.on_event("startup")
# async def load_model():
#     """Загружаем модель при старте сервера"""
#     global model
#     if os.path.exists(MODEL_PATH):
#         print(f"✅ Загружаю модель: {MODEL_PATH}")
#         model = YOLO(MODEL_PATH)
#     else:
#         print(f"⚠️ Модель не найдена: {MODEL_PATH}")
#         print("Сначала обучите модель запустив: python train_model.py")

# @app.get("/")
# async def root():
#     return {
#         "status": "ok",
#         "message": "Document Inspector API",
#         "model_loaded": model is not None
#     }

# @app.get("/api/health")
# async def health():
#     return {
#         "status": "healthy",
#         "model_loaded": model is not None
#     }

# @app.post("/api/inspect")
# async def inspect_document(file: UploadFile = File(...)):
#     """
#     Анализирует документ и находит подписи, печати, QR-коды
#     """
#     if model is None:
#         raise HTTPException(
#             status_code=503,
#             detail="Модель не загружена. Обучите модель сначала!"
#         )
    
#     # Читаем изображение
#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents))
    
#     # Запускаем детекцию
#     results = model(image)
    
#     # Парсим результаты
#     detections = []
#     for result in results:
#         boxes = result.boxes
#         for box in boxes:
#             x1, y1, x2, y2 = box.xyxy[0].tolist()
#             confidence = float(box.conf[0])
#             class_id = int(box.cls[0])
            
#             detections.append({
#                 "class_id": class_id,
#                 "class_name": CLASS_NAMES[class_id],
#                 "confidence": round(confidence, 3),
#                 "bbox": {
#                     "x1": round(x1, 2),
#                     "y1": round(y1, 2),
#                     "x2": round(x2, 2),
#                     "y2": round(y2, 2)
#                 }
#             })
    
#     # Рисуем bounding boxes
#     draw = ImageDraw.Draw(image)
    
#     try:
#         font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
#     except:
#         font = ImageFont.load_default()
    
#     for det in detections:
#         bbox = det["bbox"]
#         class_name = det["class_name"]
#         confidence = det["confidence"]
#         color = COLORS[det["class_id"]]
        
#         # Рисуем рамку
#         draw.rectangle(
#             [(bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"])],
#             outline=color,
#             width=3
#         )
        
#         # Рисуем текст
#         text = f"{class_name} {confidence:.2f}"
#         draw.text((bbox["x1"], bbox["y1"] - 25), text, fill=color, font=font)
    
#     # Сохраняем результат
#     output_path = "result.jpg"
#     image.save(output_path)
    
#     return {
#         "status": "success",
#         "detections": detections,
#         "total_found": len(detections),
#         "result_image": "/api/result"
#     }

# @app.get("/api/result")
# async def get_result():
#     """Возвращает изображение с bounding boxes"""
#     if not os.path.exists("result.jpg"):
#         raise HTTPException(status_code=404, detail="Результат не найден")
#     return FileResponse("result.jpg", media_type="image/jpeg")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# остальное без изменений

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import io
import os
import uuid
import asyncio
from config_with_env import load_config_with_env
cfg = load_config_with_env()

# внутри твоего async endpoint

app = FastAPI(title="Document Inspector API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Убедимся что папки есть
os.makedirs("results", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# монтируем outputs чтобы по URL /outputs/имя.png отдавались файлы
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# Модель
MODEL_PATH = "runs/detect/document_inspector/weights/best.pt"
model = None

# Маппинг (оставлю на английском ключи, чтобы фронтенд легче работал)
CLASS_MAP = {
    0: ("signature", "Подпись"),
    1: ("stamp", "Печать"),
    2: ("qr", "QR-код"),
    3: ("other", "Другое"),
}

COLORS = {
    0: "#FF0000",
    1: "#00FF00",
    2: "#0000FF",
    3: "#FFFF00",
}

@app.on_event("startup")
async def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        print(f"✅ Загружаю модель: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
    else:
        print(f"⚠️ Модель не найдена: {MODEL_PATH}")
        model = None

@app.get("/")
async def root():
    return {"status": "ok", "model_loaded": model is not None}

import asyncio


"""@app.post("/api/inspect")
async def inspect_document(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    width, height = image.size

    # Запуск инференса в отдельном потоке (не блокирует loop)
    results = await asyncio.to_thread(model, image)


    detections = []
    # results может быть итерируемым (по страницам), берем все boxes
    for result in results:
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue
        for box in boxes:
            # Получаем координаты и класс/score
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            # Переводим в формат [x, y, w, h]
            x = float(x1)
            y = float(y1)
            w = float(x2 - x1)
            h = float(y2 - y1)

            label_en, label_ru = CLASS_MAP.get(cls, (f"class_{cls}", "Класс"))
            detections.append({
                "label": label_en,           # 'signature' / 'stamp' ...
                "label_ru": label_ru,        # дополнительное поле с названием по-русски
                "score": round(conf, 3),
                "bbox": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)]
            })

    # Нарисуем рамки на изображении
    draw = ImageDraw.Draw(image)
    # Попытка загрузить переносимый шрифт, fallback на default
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None

    for det in detections:
        x, y, w, h = det["bbox"]
        cls_label = det["label"]
        # находим id по label (обратно)
        # цвет по cls можно не совпадать, используем nearest match by label
        color = "#3b82f6"
        # draw rect
        draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=3)
        text = f"{det['label_ru']} {det['score']:.2f}"
        if font:
            draw.text((x, max(0, y - 18)), text, fill=color, font=font)
        else:
            draw.text((x, max(0, y - 18)), text, fill=color)

    # Сохранение в уникальный файл, чтобы не перезаписывать result.jpg
    outname = f"result_{uuid.uuid4().hex[:8]}.jpg"
    outpath = os.path.join("results", outname)
    os.makedirs("results", exist_ok=True)
    image.save(outpath, format="JPEG", quality=85)
    # Возвращаем формат, который удобен фронтенду
    return JSONResponse({
        "status": "success",
        "detections": detections,
        "total_found": len(detections),
        "width": width,
        "height": height,
        "result_image": f"/api/result?file={outname}"
    })
"""

@app.post("/api/inspect")
async def inspect_document(request: Request, file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    contents = await file.read()

    # Если PDF — конвертируем первую страницу, иначе открываем изображение
    if file.filename.lower().endswith('.pdf') or file.content_type == 'application/pdf':
        try:
            import fitz  # PyMuPDF
            pdf_document = fitz.open(stream=contents, filetype="pdf")
            first_page = pdf_document[0]
            pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data)).convert("RGB")
            pdf_document.close()
        except ImportError:
            raise HTTPException(status_code=500, detail="PyMuPDF not installed. Run: pip install PyMuPDF")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")
    else:
        try:
            image = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to open image: {str(e)}")

    width, height = image.size

    # Запуск inference в отдельном потоке
    results = await asyncio.to_thread(model, image)

    detections = []
    for result in results:
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            continue
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            x = float(x1); y = float(y1); w = float(x2 - x1); h = float(y2 - y1)
            label_en, label_ru = CLASS_MAP.get(cls, (f"class_{cls}", "Класс"))
            detections.append({
                "label": label_en,
                "label_ru": label_ru,
                "score": round(conf, 3),
                "bbox": [round(x, 2), round(y, 2), round(w, 2), round(h, 2)]
            })

    # Нарисовать рамки
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    for det in detections:
        x, y, w, h = det["bbox"]
        color = "#3b82f6"
        draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=3)
        text = f"{det['label_ru']} {det['score']:.2f}"
        if font:
            draw.text((x, max(0, y - 18)), text, fill=color, font=font)
        else:
            draw.text((x, max(0, y - 18)), text, fill=color)

    # Сохранение РЕЗУЛЬТАТА в outputs (чтобы /outputs/<file> был доступен)
    outname = f"result_{uuid.uuid4().hex[:8]}.jpg"
    outpath = os.path.join("outputs", outname)
    os.makedirs("outputs", exist_ok=True)
    image.save(outpath, format="JPEG", quality=85)

    # Формируем абсолютные URL для фронтенда
    base_url = str(request.base_url).rstrip("/")
    result_url = f"{base_url}/api/result?file={outname}"
    outputs_url = f"{base_url}/outputs/{outname}"

    return JSONResponse({
        "status": "success",
        "detections": detections,
        "total_found": len(detections),
        "width": width,
        "height": height,
        "result_image": result_url,
        "outputs_image": outputs_url
    })


    
@app.get("/api/result")
async def get_result(file: str = Query(...)):
    # SECURITY: проверим имя файла на простую валидность
    safe_name = os.path.basename(file)
    path = os.path.join("results", safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Result not found")
    return FileResponse(path, media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    