import csv
import time
import os

FILE_NAME = 'queue.csv'


def get_and_lock_task():
    if not os.path.exists(FILE_NAME):
        return None

    rows = []
    task_to_do = None

    with open(FILE_NAME, mode='r', newline='') as file:
        reader = list(csv.reader(file))
        if not reader:
            return None

        rows = reader
        for row in rows[1:]:
            if row[1] == 'pending':
                row[1] = 'in_progress'
                task_to_do = row
                break

    if task_to_do:
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    return task_to_do


def complete_task(task_id):
    rows = []
    with open(FILE_NAME, mode='r', newline='') as file:
        rows = list(csv.reader(file))
        for row in rows:
            if row[0] == str(task_id):
                row[1] = 'done'
                break

    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def run_consumer():
    while True:
        task = get_and_lock_task()

        if task:
            task_id = task[0]
            print(f"Przetwarzanie zadania ID: {task_id}...")
            time.sleep(30)
            complete_task(task_id)
            print(f"Zakończono zadanie ID: {task_id}")
        else:
            print("Brak zadań. Czekam...")
            time.sleep(5)


if __name__ == "__main__":
    run_consumer()