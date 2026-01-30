from ultralytics import YOLO
import torch


def train_model():
    print(f"CUDA dostępne: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Urządzenie: {torch.cuda.get_device_name(0)}")


    model = YOLO('yolov8n.pt')

    results = model.train(
        data='data.yaml',
        epochs=50,
        imgsz=640,
        device=0,
        batch=16,
        name='yolo_plate_detector'  #folder z wynikami
    )

    print("Trening zakończony")


if __name__ == '__main__':
    train_model()