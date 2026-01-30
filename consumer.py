import sqlite3
import time


def get_and_lock_task():
    conn = sqlite3.connect('queue.db')
    cursor = conn.cursor()

    cursor.execute('BEGIN IMMEDIATE')

    cursor.execute('''
        SELECT id FROM tasks 
        WHERE status = "pending" 
        LIMIT 1
    ''')
    row = cursor.fetchone()

    if row:
        task_id = row[0]
        cursor.execute('UPDATE tasks SET status = "in_progress" WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        return task_id

    conn.rollback()
    conn.close()
    return None


def complete_task(task_id):
    conn = sqlite3.connect('queue.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = "done" WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


def run_consumer():
    while True:
        task_id = get_and_lock_task()

        if task_id:
            print(f"Przetwarzanie zadania ID: {task_id}...")
            time.sleep(30)
            complete_task(task_id)
            print(f"Zakończono zadanie ID: {task_id}")
        else:
            print("Brak zadań. Czekam...")
            time.sleep(5)


if __name__ == "__main__":
    run_consumer()