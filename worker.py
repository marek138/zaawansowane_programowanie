import time
import queue_service
from ocr import PlateRecognizer


def run_worker():
    print("Worker gotowy do pracy. Czekam na zadania...")

    #worker ma własny model
    recognizer = PlateRecognizer('best.pt')

    while True:
        task = queue_service.get_pending_task()

        if task:
            task_id, data = task
            file_path = data['path']
            print(f"Przetwarzam zadanie: {task_id}")

            try:
                #ocr
                start_time = time.time()
                result = recognizer.analyze_image(file_path)
                duration = time.time() - start_time

                #info o czasie przetwarzania
                result['processing_time_sec'] = round(duration, 4)

                #zapis wyniku
                queue_service.save_result(task_id, result)
                print(f"Zakończono {task_id}: {result.get('plate', 'BRAK')}")

            except Exception as e:
                print(f"Błąd w zadaniu {task_id}: {e}")
                queue_service.save_result(task_id, {"error": str(e)})
        else:
            #jak nie ma pracy
            time.sleep(1)


if __name__ == "__main__":
    run_worker()