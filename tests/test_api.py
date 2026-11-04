import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def test_task_lifecycle(client):
    assert client.get("/health").json() == {"status": "ok"}
    created = client.post("/api/tasks", json={"title": "  Deploy  "})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Deploy" and task["done"] is False
    task_id = task["id"]
    assert client.get("/api/tasks").json() == [task]
    assert client.patch(f"/api/tasks/{task_id}", json={"done": True}).json()["done"] is True
    assert client.get(f"/api/tasks/{task_id}").status_code == 200
    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_home_serves_frontend(client):
    page = client.get("/")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "/api/tasks" in page.text
    assert client.get("/info").json()["service"] == "hello-station"


def test_validation_and_missing_tasks(client):
    assert client.post("/api/tasks", json={"title": "  "}).status_code == 422
    assert client.post("/api/tasks", json={"title": "x", "unknown": 1}).status_code == 422
    assert client.patch("/api/tasks/1", json={}).status_code == 422
    assert client.patch("/api/tasks/1", json={"done": None}).status_code == 422
    assert client.patch("/api/tasks/1", json={"done": True}).status_code == 404
    assert client.delete("/api/tasks/1").status_code == 404
