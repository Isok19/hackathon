from ultralytics import YOLO

# 1. Загружаем модель
model = YOLO("runs/exp/weights/best.pt")   # <-- путь к твоей модели

# 2. Делаем предсказание
result = model.predict(
    source="dataset/images/val/your_image.png",  # <-- файл для проверки
    conf=0.25,
    save=True
)

print("Готово! Результаты сохранены в папке runs/predict/")

