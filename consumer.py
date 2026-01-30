import pika
import requests
import time


def process_image(url):
    # Tu logika AI (np. YOLO / OpenCV)
    return 5  # przykładowy wynik


def callback(ch, method, properties, body):
    url = body.decode()
    try:
        result = process_image(url)
        # Próba wysłania do Serwisu A
        response = requests.post("http://service_a:8000/results", json={"count": result})
        response.raise_for_status()

        # Jeśli się udało, potwierdzamy (Ack)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Błąd (Serwis A leży lub Cloudflare): {e}")
        # Punkt 7: Nie potwierdzamy, wiadomość wraca do kolejki (Nack)
        # requeue=True sprawi, że spróbuje ponownie
        time.sleep(5)  # Krótka przerwa przed ponowną próbą
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# Połączenie z RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='ai_tasks', durable=True)
channel.basic_consume(queue='ai_tasks', on_message_callback=callback, auto_ack=False)
channel.start_consuming()