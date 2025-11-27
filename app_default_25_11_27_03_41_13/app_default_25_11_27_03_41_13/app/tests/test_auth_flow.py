import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.user import Base
from app.db.session import get_db
from main import app

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False}, future=True)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine, future=True)


@pytest.fixture
def override_db(session_factory):
    def _get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(override_db):
    return TestClient(app)


def test_signup_and_login_flow(client: TestClient):
    signup_payload = {"email": "test.user@example.com", "password": "StrongPassword1!"}
    signup_response = client.post("/api/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201
    signup_body = signup_response.json()
    assert signup_body["email"] == "test.user@example.com"
    assert signup_body["is_active"] is True
    assert "id" in signup_body
    assert "created_at" in signup_body

    login_response = client.post(
        "/api/auth/login",
        data={"username": signup_payload["email"], "password": signup_payload["password"]},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["token_type"] == "bearer"
    assert login_body["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )
    assert me_response.status_code == 200
    me_body = me_response.json()
    assert me_body["email"] == signup_payload["email"]
