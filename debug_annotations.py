import json
from pathlib import Path

# Проверяем JSON
with open('selected_annotations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("АНАЛИЗ selected_annotations.json")
print("=" * 60)

total_docs = len(data)
total_pages = 0
total_annotations = 0

for pdf_name, pdf_data in data.items():
    pages_in_doc = 0
    anns_in_doc = 0
    
    for page_name, page_data in pdf_data.items():
        if page_name.startswith('page_'):
            pages_in_doc += 1
            annotations = page_data.get('annotations', [])
            anns_in_doc += len(annotations)
    
    if anns_in_doc > 0:
        print(f"\n📄 {pdf_name}")
        print(f"   Страниц: {pages_in_doc}, Аннотаций: {anns_in_doc}")
        
        # Показываем пример
        for page_name, page_data in pdf_data.items():
            if page_name.startswith('page_'):
                annotations = page_data.get('annotations', [])
                if annotations:
                    print(f"   Пример аннотации: {annotations[0]}")
                    break
    
    total_pages += pages_in_doc
    total_annotations += anns_in_doc

print("\n" + "=" * 60)
print(f"ИТОГО:")
print(f"Документов: {total_docs}")
print(f"Страниц: {total_pages}")
print(f"Аннотаций: {total_annotations}")

# Проверяем txt файлы
print("\n" + "=" * 60)
print("ПРОВЕРКА .TXT ФАЙЛОВ")
print("=" * 60)

train_labels = list(Path('dataset/labels/train').glob('*.txt'))
non_empty = 0

for label_file in train_labels[:5]:  # Первые 5
    size = label_file.stat().st_size
    print(f"\n{label_file.name}: {size} байт")
    
    if size > 0:
        non_empty += 1
        with open(label_file, 'r') as f:
            content = f.read()
            print(f"  Содержимое: {content[:100]}")

print(f"\n✅ Непустых файлов (из первых 5): {non_empty}")