
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_create_list_and_delete_task():
    with TestClient(app) as client:

        created = client.post(
            "/api/tasks",
            json={
                "title": "Study Python",
                "priority": "high"
            }
        )

        assert created.status_code == 201

        task_id = created.json()["id"]

        response = client.get("/api/tasks")

        assert response.status_code == 200
        assert response.json()[0]["title"] == "Study Python"

        deleted = client.delete(
            f"/api/tasks/{task_id}"
        )

        assert deleted.status_code == 204


def test_title_is_required():
    with TestClient(app) as client:

        response = client.post(
            "/api/tasks",
            json={"title": " "}
        )

        assert response.status_code == 422
      
