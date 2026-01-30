import pika
import cv2
import requests
import numpy as np
import os
import time

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://service_a:8000/results")


def perform_ai_analysis(url):
    try:
        resp = requests.get(url, timeout=5)
        arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        boxes, _ = hog.detectMultiScale(img, winStride=(8, 8))
        return len(boxes)
    except:
        return 0


def callback(ch, method, properties, body):
    url = body.decode()
    count = perform_ai_analysis(url)

    success = False
    while not success:
        try:
            response = requests.post(SERVICE_A_URL, json={"url": url, "count": count}, timeout=5)
            if response.status_code == 200:
                success = True
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                time.sleep(5)
        except Exception:
            time.sleep(5)


connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
channel = connection.channel()
channel.queue_declare(queue='ai_tasks', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='ai_tasks', on_message_callback=callback, auto_ack=False)

channel.start_consuming()