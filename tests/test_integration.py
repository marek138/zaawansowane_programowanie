import pytest
import requests
import time


def test_full_flow():
    img_url = "http://example.com/image.jpg"

    resp_b = requests.post("http://localhost:8002/analyze", json={"url": img_url})
    assert resp_b.status_code == 200

    time.sleep(5)

    # Tutaj w prawdziwym teście sprawdziłbyś bazę danych Serwisu A
    # W tym przykładzie sprawdzamy czy endpoint A żyje
    resp_a = requests.post("http://localhost:8001/results", json={"url": img_url, "count": 1})
    assert resp_a.status_code == 200