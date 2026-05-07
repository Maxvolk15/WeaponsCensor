from detector import SimpleWeaponDetector
from ml_detector import MLWeaponDetector
import numpy as np


class HybridWeaponDetector:
    def __init__(self):
        self.simple_detector = SimpleWeaponDetector()
        # ML детектор может не работать без GPU, поэтому делаем опциональным
        try:
            self.ml_detector = MLWeaponDetector()
            self.use_ml = True
        except:
            print("ML детектор недоступен, использую простой метод")
            self.use_ml = False
            self.ml_detector = None

    def detect(self, image):
        """Комбинируем результаты обоих детекторов"""
        weapons = []

        # Всегда используем простой детектор
        weapons.extend(self.simple_detector.detect(image))

        # Если ML доступен, добавляем его результаты
        if self.use_ml:
            try:
                ml_weapons = self.ml_detector.detect(image)
                weapons.extend(ml_weapons)
            except:
                pass

        # Убираем дубликаты (пересекающиеся области)
        if weapons:
            weapons = self._remove_duplicates(weapons)

        return weapons

    def _remove_duplicates(self, boxes, iou_threshold=0.5):
        """Удаление пересекающихся боксов"""
        if len(boxes) == 0:
            return []

        # Сортируем по размеру (большие сначала)
        boxes = sorted(boxes, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]), reverse=True)
        kept = []

        for box1 in boxes:
            keep = True
            for box2 in kept:
                if self._iou(box1, box2) > iou_threshold:
                    keep = False
                    break
            if keep:
                kept.append(box1)

        return kept

    def _iou(self, box1, box2):
        """Вычисление Intersection over Union"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

