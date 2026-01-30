import os
import shutil
import xml.etree.ElementTree as ET
import random


XML_FILE = "dataset/annotations.xml"

IMAGES_DIR = "dataset/images"

OUTPUT_DIR = "dataset_yolo"


def convert_box(size, box):
    """
    konwersja z formatu cvat (xtl, ytl, xbr, ybr) na yolo (x_center, y_center, width, height)
    """
    dw = 1. / size[0]
    dh = 1. / size[1]

    x_center = (box[0] + box[2]) / 2.0
    y_center = (box[1] + box[3]) / 2.0
    w = box[2] - box[0]
    h = box[3] - box[1]

    return (x_center * dw, y_center * dh, w * dw, h * dh)


def prepare_dataset_cvat():
    if not os.path.exists(XML_FILE):
        print(f"BŁĄD: Nie znaleziono pliku {XML_FILE}")
        return

    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    #pobieranie tagu image
    images = root.findall('image')
    print(f"Znaleziono {len(images)} obrazów w pliku XML.")

    #losowy podział na zbiory
    random.shuffle(images)
    split_idx = int(len(images) * 0.7)

    datasets = {
        'train': images[:split_idx],
        'val': images[split_idx:]
    }


    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    for split in ['train', 'val']:
        os.makedirs(f"{OUTPUT_DIR}/{split}/images", exist_ok=True)
        os.makedirs(f"{OUTPUT_DIR}/{split}/labels", exist_ok=True)


    count_processed = 0

    for split, image_nodes in datasets.items():
        print(f"Przetwarzam zestaw {split} ({len(image_nodes)} zdjęć)...")

        for img_node in image_nodes:
            filename = img_node.get('name')
            width = int(img_node.get('width'))
            height = int(img_node.get('height'))

            src_path = os.path.join(IMAGES_DIR, filename)

            if not os.path.exists(src_path):
                print(f"⚠️ Nie znaleziono pliku zdjęcia: {src_path}")
                continue

            #kopia zdj
            dst_img_path = os.path.join(OUTPUT_DIR, split, "images", filename)
            shutil.copy(src_path, dst_img_path)

            #plik labels.txt
            txt_filename = os.path.splitext(filename)[0] + ".txt"
            dst_label_path = os.path.join(OUTPUT_DIR, split, "labels", txt_filename)

            with open(dst_label_path, 'w') as f:
                #pętla po ramkach <box> wewnątrz <image>
                for box in img_node.findall('box'):
                    label = box.get('label')
                    if label == 'plate':
                        xtl = float(box.get('xtl'))
                        ytl = float(box.get('ytl'))
                        xbr = float(box.get('xbr'))
                        ybr = float(box.get('ybr'))

                        b = [xtl, ytl, xbr, ybr]
                        bb = convert_box((width, height), b)

                        # Zapis: class x y w h (class 0 = plate)
                        f.write(f"0 {bb[0]:.6f} {bb[1]:.6f} {bb[2]:.6f} {bb[3]:.6f}\n")

            count_processed += 1

    #plik konfiguracyjny yaml
    yaml_content = f"""
path: {os.path.abspath(OUTPUT_DIR)} 
train: train/images
val: val/images

names:
  0: license_plate
"""
    with open("data.yaml", "w") as f:
        f.write(yaml_content)

    print(f"\nPrzygotowano {count_processed} zdjęć w formacie YOLO.")


if __name__ == "__main__":
    prepare_dataset_cvat()