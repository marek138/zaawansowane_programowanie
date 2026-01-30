import pika
import cv2
import requests
import numpy as np
import time


def detect_people(url):
    try:
        response = requests.get(url, timeout=10)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        boxes, weights = hog.detectMultiScale(image, winStride=(8, 8))
        return len(boxes)
    except:
        return 0


def callback(ch, method, properties, body):
    url = body.decode()
    print(f"Rozpoczęto analizę: {url}")

    count = detect_people(url)

    print(f"Wynik dla {url}: znaleziono {count} osób")

    # Tutaj można dodać zapis wyniku do bazy (np. SQLite z poprzedniego zadania)
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='image_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='image_queue', on_message_callback=callback)

print("Konsument uruchomiony. Oczekiwanie na zadania...")
channel.start_consuming()