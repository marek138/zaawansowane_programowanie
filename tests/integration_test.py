import pytest
import requests
import time


def test_full_pipeline():
    url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/basketball1.png"

    # Test Serwisu B
    resp_b = requests.post("http://localhost:8002/analyze", json={"url": url})
    assert resp_b.status_code == 200

    # Test Serwisu A
    resp_a = requests.post("http://localhost:8001/results", json={"url": url, "count": 1})
    assert resp_a.status_code == 200