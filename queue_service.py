import redis
import json
import time

# decode_responses=True stringi zamiast bajtów
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()  # test połączenia
    print("Połączono z Redisem!")
except redis.ConnectionError:
   print("BŁĄD: Nie można połączyć z Redisem. Uruchom Docker")

# stałe nazwy kluczy
QUEUE_NAME = "ocr_tasks_queue"
RESULTS_PREFIX = "result:"


def add_task(task_id, data_dict):
    #rpush koniec kolejki.
    packet = {
        "id": task_id,
        "data": data_dict,
        "created_at": time.time()
    }
    #zapis json do kolejki
    r.rpush(QUEUE_NAME, json.dumps(packet))

    #ustawiony wstępny status w osobnym kluczu (dla podglądu)
    r.set(f"{RESULTS_PREFIX}{task_id}", json.dumps({"status": "queued"}))


def get_pending_task():
    """
    blpop bierze z początku kolejki.
    jeśli kolejka pusta, czeka.
    """
    item = r.blpop(QUEUE_NAME, timeout=1)

    if item:
        #item to krotka: (nazwa_kolejki, dane)
        queue_name, data_str = item
        packet = json.loads(data_str)

        task_id = packet["id"]
        data_dict = packet["data"]

        #aktualizujemy status na 'processing'
        r.set(f"{RESULTS_PREFIX}{task_id}", json.dumps({"status": "processing"}))

        return task_id, data_dict

    return None


def save_result(task_id, result_dict):
    #zapisany wynik jako json
    r.setex(f"{RESULTS_PREFIX}{task_id}", 3600, json.dumps(result_dict))


def get_result(task_id):
    data = r.get(f"{RESULTS_PREFIX}{task_id}")
    if data:
        return json.loads(data)
    return None