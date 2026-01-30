from fastapi import FastAPI, UploadFile, File
import shutil
import os
import uuid
import queue_service
from ocr import PlateRecognizer

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

print("Ładowanie modelu do API...")
recognizer = PlateRecognizer('best.pt')

app = FastAPI(title="System OCR Tablic Rejestracyjnych")


@app.post("/analyze")
def analyze_sync(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = recognizer.analyze_image(file_path)

    return result


@app.post("/queue")
async def queue_image(file: UploadFile = File(...)):
    #wygenerowany id taska
    task_id = str(uuid.uuid4())

    file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #dodaje do bazy kolejki
    task_data = {"path": file_path, "original_name": file.filename}
    queue_service.add_task(task_id, task_data)

    return {"status": "queued", "task_id": task_id}


#sprawdza wynik taska
@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = queue_service.get_result(task_id)

    if result:
        return {"status": "completed", "data": result}
    else:
        return {"status": "pending", "message": "Jeszcze pracuję..."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)