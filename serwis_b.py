import pika
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AnalysisRequest(BaseModel):
    url: str


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=request.url,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
    return {"message": "Queued"}