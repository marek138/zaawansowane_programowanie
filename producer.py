import csv
import os


def add_tasks(count):
    file_exists = os.path.isfile('queue.csv')

    with open('queue.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['id', 'status'])

        last_id = 0
        if file_exists:
            with open('queue.csv', mode='r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_id = int(lines[-1].split(',')[0])

        for i in range(1, count + 1):
            writer.writerow([last_id + i, 'pending'])


if __name__ == "__main__":
    add_tasks(100)