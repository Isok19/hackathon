from ultralytics import YOLO
import torch

print("🔍 Проверяю устройство...")
print(f"MPS (Apple Silicon) доступен: {torch.backends.mps.is_available()}")

# Загружаем предобученную модель YOLOv8
print("\n📦 Загружаю YOLOv8 nano модель...")
model = YOLO('yolov8n.pt')  # nano - самая быстрая для M1

# Обучаем модель
print("\n🎯 Начинаю обучение...\n")
results = model.train(
    data='data.yaml',           # путь к конфигу
    epochs=50,                   # количество эпох (можно увеличить до 100)
    imgsz=640,                   # размер изображения
    batch=8,                     # размер батча (для M1 Pro подходит)
    device='mps',                # используем Apple Silicon
    patience=10,                 # early stopping
    save=True,                   # сохранять чекпоинты
    project='runs/detect',       # куда сохранять результаты
    name='document_inspector',   # название эксперимента
    exist_ok=True
)

print("\n✅ Обучение завершено!")
print(f"📁 Результаты сохранены в: runs/detect/document_inspector")
print(f"🏆 Лучшая модель: runs/detect/document_inspector/weights/best.pt")