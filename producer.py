import pika
import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ImageRequest(BaseModel):
    url: str


@app.post("/analyze_img")
async def analyze_img(request: ImageRequest):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='image_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='image_queue',
        body=request.url,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return {"status": "Job queued", "url": request.url}