from pdf2image import convert_from_path
import os
from pathlib import Path

def convert_pdfs_to_images(pdf_folder, output_folder, dpi=150):
    """Конвертирует PDF в изображения"""
    os.makedirs(output_folder, exist_ok=True)
    
    pdf_files = list(Path(pdf_folder).glob('*.pdf'))
    
    print(f"Найдено PDF файлов: {len(pdf_files)}")
    
    for pdf_path in pdf_files:
        print(f"Конвертирую: {pdf_path.name}")
        
        try:
            images = convert_from_path(str(pdf_path), dpi=dpi)
            
            for page_num, image in enumerate(images, start=1):
                image_name = f"{pdf_path.stem}_page_{page_num}.jpg"
                image_path = os.path.join(output_folder, image_name)
                image.save(image_path, 'JPEG')
                print(f"  ✅ Сохранено: {image_name}")
        
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    print(f"\n✅ Конвертация завершена!")

# ЗАПУСК
convert_pdfs_to_images(
    pdf_folder='pdfs',
    output_folder='dataset/images/all'
)