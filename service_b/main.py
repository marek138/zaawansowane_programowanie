import pika
import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")


class ImageTask(BaseModel):
    url: str


@app.post("/analyze")
async def analyze(task: ImageTask):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='ai_tasks', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='ai_tasks',
        body=task.url,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return {"status": "task_queued"}