from ultralytics import YOLO
import easyocr
import cv2
import torch
import re
import numpy as np



class PlateRecognizer:
    def __init__(self, model_path='best.pt'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Inicjalizacja OCR (Device: {self.device})")

        try:
            self.detector = YOLO(model_path)
        except Exception as e:
            print(f"Brak modelu {model_path}!")
            raise e

        self.reader = easyocr.Reader(['pl'], gpu=(self.device == 'cuda'))
        self.allowlist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def fix_common_errors(self, text):

        int_to_char = {'0': 'O', '1': 'I', '2': 'Z', '3': 'B', '4': 'A', '5': 'S', '6': 'G', '8': 'B'}

        text_list = list(text)

        # dwa pierwsze znaki litery
        for i in range(min(len(text), 2)):
            if text_list[i] in int_to_char:
                text_list[i] = int_to_char[text_list[i]]

        #rejestracje głównie S__
        if text_list[0] in ['G','B','C','I','P']:
            text_list[0] = 'S'

        return "".join(text_list)

    def get_variants(self, img):
        variants = []

        # Wariant 1: Upscale x3 + Szarość
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scaled = cv2.resize(gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        variants.append(scaled)

        # Wariant 2: Wyostrzanie
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(scaled, -1, kernel)
        variants.append(sharpened)

        return variants

    def analyze_image(self, image_path: str) -> dict:
        img = cv2.imread(image_path)
        if img is None: return {"error": "Brak pliku", "found": False}

        results = self.detector(img, conf=0.20, verbose=False)

        if len(results[0].boxes) == 0:
            return {"plate": "", "confidence": 0.0, "found": False}

        box = results[0].boxes[0]
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        yolo_conf = float(box.conf)

        #ciecie dołu
        h, w, _ = img.shape
        crop_x1 = max(0, x1 + int((x2 - x1) * 0.03))
        crop_x2 = min(w, x2 - int((x2 - x1) * 0.02))
        crop_y1 = max(0, y1 + int((y2 - y1) * 0.03))
        crop_y2 = min(h, y2 - int((y2 - y1) * 0.10))

        plate_img = img[crop_y1:crop_y2, crop_x1:crop_x2]

        #warianty
        variants = self.get_variants(plate_img)
        best_candidate = {"text": "", "conf": 0.0}

        #wzór: 2-3 litery + cyfry/litery
        polish_plate_pattern = re.compile(r'^[A-Z]{2,3}[0-9A-Z]{3,5}$')

        for variant in variants:
            try:
                ocr_res = self.reader.readtext(variant, detail=1, allowlist=self.allowlist, batch_size=1)

                for (bbox, text, conf) in ocr_res:
                    clean = re.sub(r'[^A-Z0-9]', '', text.upper())

                    if 5 <= len(clean) <= 8:
                        fixed = self.fix_common_errors(clean)
                        score = conf
                        if polish_plate_pattern.match(fixed):
                            score += 1.0
                        if 7 <= len(fixed) <= 8:
                            score += 0.5

                        if score > best_candidate["conf"]:
                            best_candidate = {"text": fixed, "conf": score}
            except Exception:
                continue

        if best_candidate["text"]:
            return {
                "plate": best_candidate["text"],
                "confidence": round(yolo_conf, 4),
                "found": True,
                "bbox": [x1, y1, x2, y2]
            }

        return {"plate": "", "confidence": 0.0, "found": False}