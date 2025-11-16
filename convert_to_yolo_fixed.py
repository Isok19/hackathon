import json
import os
from pathlib import Path

# Маппинг категорий
CATEGORIES = {
    "signature": 0,
    "stamp": 1,
    "qr": 2,
    "other": 3
}

def convert_bbox(bbox, img_width, img_height):
    """Конвертирует bbox в YOLO формат"""
    x = bbox['x']
    y = bbox['y']
    width = bbox['width']
    height = bbox['height']
    
    x_center = (x + width / 2) / img_width
    y_center = (y + height / 2) / img_height
    norm_width = width / img_width
    norm_height = height / img_height
    
    return x_center, y_center, norm_width, norm_height

def convert_json_to_yolo_fixed(json_file, train_images_dir, val_images_dir, 
                                train_labels_dir, val_labels_dir):
    
    print("Загружаю JSON...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    os.makedirs(train_labels_dir, exist_ok=True)
    os.makedirs(val_labels_dir, exist_ok=True)
    
    # Получаем списки изображений
    train_images = {f.stem for f in Path(train_images_dir).glob('*.jpg')}
    val_images = {f.stem for f in Path(val_images_dir).glob('*.jpg')}
    
    print(f"Train изображений: {len(train_images)}")
    print(f"Val изображений: {len(val_images)}")
    print("\nКонвертирую аннотации...")
    
    train_count = 0
    val_count = 0
    total_annotations = 0
    
    for pdf_name, pdf_data in data.items():
        for page_name, page_data in pdf_data.items():
            if page_name.startswith('page_'):
                # Получаем размеры страницы
                page_size = page_data.get('page_size', {})
                img_width = page_size.get('width', 1684)
                img_height = page_size.get('height', 1190)
                
                # ВОТ ИСПРАВЛЕНИЕ! Аннотации в виде словаря, а не списка
                annotations_dict = page_data.get('annotations', {})
                
                # Имя изображения
                image_stem = f"{pdf_name.replace('.pdf', '')}_{page_name}"
                
                # Определяем train или val
                if image_stem in train_images:
                    label_dir = train_labels_dir
                    train_count += 1
                elif image_stem in val_images:
                    label_dir = val_labels_dir
                    val_count += 1
                else:
                    continue
                
                label_path = os.path.join(label_dir, f"{image_stem}.txt")
                
                # Открываем файл для записи
                with open(label_path, 'w') as label_file:
                    # Проходимся по аннотациям (это словарь!)
                    for ann_id, ann_data in annotations_dict.items():
                        category = ann_data.get('category', '')
                        bbox = ann_data.get('bbox', {})
                        
                        if category in CATEGORIES and bbox:
                            class_id = CATEGORIES[category]
                            x_c, y_c, w, h = convert_bbox(bbox, img_width, img_height)
                            label_file.write(f"{class_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")
                            total_annotations += 1
                
                if total_annotations > 0 and train_count + val_count <= 5:
                    print(f"✅ {label_path}")
    
    print(f"\n{'='*60}")
    print(f"✅ Конвертация завершена!")
    print(f"Train меток: {train_count}")
    print(f"Val меток: {val_count}")
    print(f"Всего аннотаций: {total_annotations}")
    print(f"{'='*60}")

# ЗАПУСК
convert_json_to_yolo_fixed(
    json_file='selected_annotations.json',
    train_images_dir='dataset/images/train',
    val_images_dir='dataset/images/val',
    train_labels_dir='dataset/labels/train',
    val_labels_dir='dataset/labels/val'
)