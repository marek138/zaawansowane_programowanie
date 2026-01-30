from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ResultData(BaseModel):
    url: str
    count: int

@app.post("/results")
async def save_results(data: ResultData):
    print(f"Received results for {data.url}: {data.count}")
    return {"status": "saved"}