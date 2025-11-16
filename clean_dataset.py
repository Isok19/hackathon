from pathlib import Path
import os

def clean_dataset():
    """Удаляет изображения без соответствующих меток"""
    
    # Train
    train_images = {f.stem: f for f in Path('dataset/images/train').glob('*.jpg')}
    train_labels = {f.stem for f in Path('dataset/labels/train').glob('*.txt')}
    
    print("TRAIN SET:")
    print(f"Изображений: {len(train_images)}")
    print(f"Меток: {len(train_labels)}")
    
    removed_train = 0
    for img_stem, img_path in train_images.items():
        if img_stem not in train_labels:
            os.remove(img_path)
            removed_train += 1
    
    print(f"✅ Удалено train изображений без меток: {removed_train}")
    
    # Val
    val_images = {f.stem: f for f in Path('dataset/images/val').glob('*.jpg')}
    val_labels = {f.stem for f in Path('dataset/labels/val').glob('*.txt')}
    
    print(f"\nVAL SET:")
    print(f"Изображений: {len(val_images)}")
    print(f"Меток: {len(val_labels)}")
    
    removed_val = 0
    for img_stem, img_path in val_images.items():
        if img_stem not in val_labels:
            os.remove(img_path)
            removed_val += 1
    
    print(f"✅ Удалено val изображений без меток: {removed_val}")
    
    print("\n" + "=" * 60)
    print(f"ИТОГО удалено: {removed_train + removed_val} изображений")
    print("Теперь все изображения имеют метки!")

clean_dataset()