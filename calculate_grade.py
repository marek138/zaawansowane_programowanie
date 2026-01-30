"""   Calculates the final grade based on license plate OCR accuracy and processing time.
    Parameters:
    - accuracy_percent: OCR accuracy as a percentage (0–100)
    - processing_time_sec: total time to process 100 images in seconds
    Returns:
    - Grade on a scale from 2.0 to 5.0 (rounded to the nearest 0.5)
"""

import os
import xml.etree.ElementTree as ET
import time
import re
from ocr import PlateRecognizer

XML_FILE = "dataset/annotations.xml"
IMAGES_DIR = "dataset/images"
LIMIT_IMAGES = 100


def calculate_iou(boxA, boxB):
    # Współrzędne przecięcia (Intersection)
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # Pole przecięcia
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # Pola obu prostokątów
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # IoU = Przecięcie / (Suma - Przecięcie)
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou


def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:

    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0

    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    score = 0.7 * accuracy_norm + 0.3 * time_norm

    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2


def normalize_text(text):
    if not text: return ""
    return re.sub(r'[^A-Z0-9]', '', text.upper())


def run_evaluation():
    print("Rozpoczynam ewaluację projektu...")

    recognizer = PlateRecognizer('best.pt')

    if not os.path.exists(XML_FILE):
        print(f"BŁĄD: Brak pliku {XML_FILE}")
        return

    tree = ET.parse(XML_FILE)
    root = tree.getroot()
    images_nodes = root.findall('image')

    total_samples = min(len(images_nodes), LIMIT_IMAGES)
    test_set = images_nodes[:total_samples]

    print(f"Zbiór testowy: {total_samples} zdjęć.")

    correct_ocr_count = 0
    ious = []
    start_time = time.time()

    print("\n--- ROZPOCZYNAM PRZETWARZANIE ---")

    for i, img_node in enumerate(test_set):
        filename = img_node.get('name')
        image_path = os.path.join(IMAGES_DIR, filename)

        #pobranie danych wzorcowych (Ground Truth)
        gt_plate = ""
        gt_box = []

        #szukanie atrybutu plate
        for box in img_node.findall('box'):
            if box.get('label') == 'plate':
                #pobierz tekst z atrybutu
                for attr in box.findall('attribute'):
                    if attr.get('name') == 'plate number':
                        gt_plate = attr.text

                #pobierz ramkę
                xtl = float(box.get('xtl'))
                ytl = float(box.get('ytl'))
                xbr = float(box.get('xbr'))
                ybr = float(box.get('ybr'))
                gt_box = [int(xtl), int(ytl), int(xbr), int(ybr)]
                break


        result = recognizer.analyze_image(image_path)

        #porównanie
        pred_plate = result.get("plate", "")
        pred_box = result.get("bbox", [0, 0, 0, 0])

        #normalizacja
        gt_clean = normalize_text(gt_plate)
        pred_clean = normalize_text(pred_plate)

        is_correct = (gt_clean == pred_clean) and (len(gt_clean) > 0)

        if is_correct:
            correct_ocr_count += 1
            status = "OK"
        else:
            status = f"ŹLE (Oczekiwano: {gt_clean}, Odczytano: {pred_clean})"

        #obliczenie iou
        current_iou = 0.0
        if result["found"] and gt_box:
            current_iou = calculate_iou(gt_box, pred_box)
            ious.append(current_iou)
        elif gt_box:
            ious.append(0.0)

        print(f"[{i + 1}/{total_samples}] {filename} -> {status} | IoU: {current_iou:.2f}")

    #wynik
    end_time = time.time()
    total_time = end_time - start_time

    accuracy = (correct_ocr_count / total_samples) * 100
    avg_iou = sum(ious) / len(ious) if ious else 0.0

    grade = calculate_final_grade(accuracy, total_time)

    print("\n" + "=" * 30)
    print(f"WYNIKI")
    print("=" * 30)
    print(f"Całkowity czas (100 zdj): {total_time:.2f} s (Wymagane < 60s)")
    print(f"Dokładność OCR: {accuracy:.2f}% (Wymagane > 60%)")
    print(f"Średnie IoU (Pokrycie ramki): {avg_iou:.2f}")
    print("-" * 30)
    print(f"OCENA SUGEROWANA: {grade}")
    print("=" * 30)


if __name__ == "__main__":
    run_evaluation()