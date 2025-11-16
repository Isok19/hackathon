from pathlib import Path

def check_dataset():
    """Проверяет соответствие изображений и меток"""
    
    train_images = {f.stem for f in Path('dataset/images/train').glob('*.jpg')}
    train_labels = {f.stem for f in Path('dataset/labels/train').glob('*.txt')}
    
    val_images = {f.stem for f in Path('dataset/images/val').glob('*.jpg')}
    val_labels = {f.stem for f in Path('dataset/labels/val').glob('*.txt')}
    
    print("=" * 60)
    print("TRAIN SET:")
    print(f"Изображений: {len(train_images)}")
    print(f"Меток: {len(train_labels)}")
    print(f"Совпадений: {len(train_images & train_labels)}")
    
    print("\nПримеры изображений:")
    for img in list(train_images)[:3]:
        print(f"  {img}.jpg")
    
    print("\nПримеры меток:")
    for lbl in list(train_labels)[:3]:
        print(f"  {lbl}.txt")
    
    print("\n" + "=" * 60)
    print("VAL SET:")
    print(f"Изображений: {len(val_images)}")
    print(f"Меток: {len(val_labels)}")
    print(f"Совпадений: {len(val_images & val_labels)}")
    
    # Проверяем несовпадения
    train_missing = train_images - train_labels
    val_missing = val_images - val_labels
    
    if train_missing:
        print(f"\n⚠️ Train: {len(train_missing)} изображений БЕЗ меток")
        print("Примеры:")
        for m in list(train_missing)[:5]:
            print(f"  {m}")
    
    if val_missing:
        print(f"\n⚠️ Val: {len(val_missing)} изображений БЕЗ меток")
        print("Примеры:")
        for m in list(val_missing)[:5]:
            print(f"  {m}")
    
    print("\n" + "=" * 60)

check_dataset()