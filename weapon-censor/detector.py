import cv2
import numpy as np


class SimpleWeaponDetector:
    def __init__(self):
        # Используем базовые методы компьютерного зрения
        # вместо тяжелой ML-модели для начала
        pass

    def detect(self, image):
        """
        Улучшенный метод поиска оружия без ML
        Использует несколько эвристик:
        - Поиск темных продолговатых объектов
        - Анализ формы (соотношение сторон)
        - Поиск характерных паттернов
        """
        height, width = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 1. Ищем темные объекты
        _, dark_objects = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

        # 2. Морфологические операции для улучшения
        kernel = np.ones((5, 5), np.uint8)
        dark_objects = cv2.morphologyEx(dark_objects, cv2.MORPH_CLOSE, kernel)
        dark_objects = cv2.morphologyEx(dark_objects, cv2.MORPH_OPEN, kernel)

        # 3. Находим контуры
        contours, _ = cv2.findContours(dark_objects, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        weapons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 3000:  # Минимальный размер
                continue

            # Получаем прямоугольник
            x, y, w, h = cv2.boundingRect(contour)

            # Проверяем соотношение сторон (оружие обычно продолговатое)
            aspect_ratio = w / h if h > 0 else 0

            # Пистолеты и винтовки обычно имеют соотношение 1.5-5
            if 1.2 < aspect_ratio < 6:
                # Добавляем небольшой отступ
                padding = 20
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(width, x + w + padding)
                y2 = min(height, y + h + padding)
                weapons.append([x1, y1, x2, y2])

        return weapons