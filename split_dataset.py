import os
import shutil
from pathlib import Path
import random

def split_dataset(source_folder, train_folder, val_folder, split_ratio=0.8):
    """Разделяет изображения на train (80%) и val (20%)"""
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)
    
    images = list(Path(source_folder).glob('*.jpg'))
    random.shuffle(images)
    
    split_point = int(len(images) * split_ratio)
    train_images = images[:split_point]
    val_images = images[split_point:]
    
    print(f"Всего изображений: {len(images)}")
    print(f"Train: {len(train_images)}")
    print(f"Val: {len(val_images)}")
    
    for img in train_images:
        shutil.copy(img, os.path.join(train_folder, img.name))
    
    for img in val_images:
        shutil.copy(img, os.path.join(val_folder, img.name))
    
    print("✅ Разделение завершено!")

# ЗАПУСК
split_dataset(
    source_folder='dataset/images/all',
    train_folder='dataset/images/train',
    val_folder='dataset/images/val'
)