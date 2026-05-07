from ultralytics import YOLO
import cv2
import numpy as np


class MLWeaponDetector:
    def __init__(self, model_path=None):
        """
        Используем предобученную YOLO модель
        Если нет своей модели, используем общую YOLO
        """
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # Используем предобученную модель
            # Она не специализирована на оружии, но может находить некоторые объекты
            self.model = YOLO('yolov8n.pt')

        # Классы, которые могут быть оружием (в COCO датасете)
        self.weapon_classes = [43, 44]  # knife, и похожие

    def detect(self, image, confidence=0.25):
        """
        Детекция объектов с помощью YOLO
        """
        results = self.model(image, conf=confidence)

        weapons = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Получаем координаты
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())

                    # Проверяем, похож ли объект на оружие
                    # Для начала берем все объекты с высокой уверенностью
                    if conf > confidence:
                        weapons.append([
                            int(x1), int(y1),
                            int(x2), int(y2)
                        ])

        return weapons