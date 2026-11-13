import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def png(value=100):
    img = np.full((50, 50, 3), value, np.uint8)
    return cv2.imencode(".png", img)[1].tobytes()


def post(tool, params="{}", data=None):
    return client.post(f"/api/process/{tool}",
                       files={"file": ("a.png", data or png(), "image/png")},
                       data={"params": params})


def test_list_tools():
    r = client.get("/api/tools")
    assert r.status_code == 200
    assert any(t["id"] == "brightness" for t in r.json())


def test_brightness_adds_50():
    r = post("brightness", '{"beta": 50}')
    assert r.status_code == 200
    out = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
    assert out.mean() == 150


def test_out_of_range():
    assert post("brightness", '{"beta": 500}').status_code == 400


def test_unknown_tool():
    assert post("nope").status_code == 404


def test_invalid_image():
    assert post("brightness", data=b"not an image").status_code == 400