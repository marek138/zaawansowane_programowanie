from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DetectionResult(BaseModel):
    url: str
    count: int

@app.post("/results")
async def receive_results(data: DetectionResult):
    print(f"Zapisano: {data.url} - {data.count} osób")
    return {"status": "success"}