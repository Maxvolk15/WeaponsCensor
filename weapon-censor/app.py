from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import base64
import uuid
from ultralytics import YOLO

app = Flask(__name__)

# Настройка папок
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Загружаем вашу обученную модель
print("Загрузка модели детекции оружия...")
model = YOLO('best.pt')  # Ваша обученная модель!
print("Модель готова!")

# Классы оружия
WEAPON_CLASSES = ['pistol', 'knife', 'rifle', 'gun']


def detect_weapons(image):
    """
    Детекция оружия с помощью обученной модели.
    Возвращает список словарей с bbox, confidence и class_name.
    """
    # Детекция
    results = model(image, conf=0.25, iou=0.45)

    weapons = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Получаем данные
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = box.conf[0].item()
                class_id = int(box.cls[0].item())
                class_name = model.names[class_id]

                # Фильтруем только оружие
                if class_name.lower() in [w.lower() for w in WEAPON_CLASSES]:
                    weapons.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'class': class_name
                    })

    return weapons


def apply_blur(image, bbox, strength=51):
    """Размытие области"""
    x1, y1, x2, y2 = bbox
    roi = image[y1:y2, x1:x2]
    if roi.size > 0:
        if strength % 2 == 0:
            strength += 1
        image[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (strength, strength), 0)
    return image


def apply_black_box(image, bbox):
    """Черный прямоугольник"""
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), -1)
    return image


def apply_pixelate(image, bbox, pixel_size=15):
    """Пикселизация"""
    x1, y1, x2, y2 = bbox
    roi = image[y1:y2, x1:x2]
    if roi.size > 0:
        h, w = roi.shape[:2]
        temp = cv2.resize(roi, (max(1, w // pixel_size), max(1, h // pixel_size)))
        image[y1:y2, x1:x2] = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
    return image


def censor_weapons(image, weapons, method='blur', blur_strength=51, pixel_size=15):
    """Применяем цензуру выбранным методом ко всем найденным оружиям"""
    for weapon in weapons:
        bbox = weapon['bbox']
        if method == 'blur':
            image = apply_blur(image, bbox, strength=blur_strength)
        elif method == 'black':
            image = apply_black_box(image, bbox)
        elif method == 'pixelate':
            image = apply_pixelate(image, bbox, pixel_size=pixel_size)
    return image


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Файл не найден'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'})

    try:
        # Сохраняем оригинал
        filename = f"{uuid.uuid4()}.jpg"
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        # Читаем изображение
        image = cv2.imread(input_path)
        if image is None:
            return jsonify({'success': False, 'error': 'Неверный формат изображения'})

        # Получаем метод цензуры
        method = request.form.get('method', 'blur')
        blur_strength = int(request.form.get('blur_strength', 51))
        pixel_size = int(request.form.get('pixel_size', 15))

        # Детекция оружия вашей моделью
        weapons = detect_weapons(image)

        # Применяем цензуру
        if weapons:
            image = censor_weapons(image, weapons, method, blur_strength, pixel_size)

        # Сохраняем результат
        output_filename = f"processed_{filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        cv2.imwrite(output_path, image)

        # Конвертируем в base64 для отправки
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # Информация о найденном оружии
        weapons_info = [
            {
                'class': w['class'],
                'confidence': round(w['confidence'], 2)
            }
            for w in weapons
        ]

        return jsonify({
            'success': True,
            'processed_image': f'data:image/jpeg;base64,{img_base64}',
            'weapons_found': len(weapons),
            'weapons_info': weapons_info,
            'method_used': method
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'model': 'weapon_detector'})


if __name__ == '__main__':
    print("=" * 50)
    print("Сервер цензуры оружия запущен!")
    print("Откройте в браузере: http://localhost:5000")
    print("Модель детекции оружия загружена")
    print("Поддерживаемые методы цензуры:")
    print("- blur (размытие)")
    print("- black (черный квадрат)")
    print("- pixelate (пикселизация)")
    print("=" * 50)
    app.run(host='0.0.0.0', debug=False, port=5000)