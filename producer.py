import sqlite3


def add_tasks(count):
    conn = sqlite3.connect('queue.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL
        )
    ''')

    tasks = [('pending',) for _ in range(count)]
    cursor.executemany('INSERT INTO tasks (status) VALUES (?)', tasks)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    add_tasks(100)