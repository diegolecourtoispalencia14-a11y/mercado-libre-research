import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.database import get_db, Base
from app.config import settings
from app.routers.auth import ensure_admin_user, brute_force_protector
import app.models.user  # noqa: F401

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def auth_client():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db

    # Enable auth strictly for these tests
    orig_auth = settings.auth_enabled
    settings.auth_enabled = True

    # Seed admin user in test db
    db = TestingSession()
    ensure_admin_user(db)
    db.close()

    # Clear brute force tracker
    brute_force_protector.failures.clear()

    yield TestClient(fastapi_app)

    fastapi_app.dependency_overrides.clear()
    settings.auth_enabled = orig_auth
    Base.metadata.drop_all(engine)


def test_login_success(auth_client):
    resp = auth_client.post(
        "/auth/login",
        json={"username": settings.admin_username, "password": settings.admin_password},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == settings.admin_username
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(auth_client):
    resp = auth_client.post(
        "/auth/login",
        json={"username": settings.admin_username, "password": "WrongPassword123!"},
    )
    assert resp.status_code == 401
    assert "Credenciales no válidas" in resp.json()["detail"]


def test_login_honeypot_bot_defense(auth_client):
    resp = auth_client.post(
        "/auth/login",
        json={
            "username": settings.admin_username,
            "password": settings.admin_password,
            "honeypot": "spam_bot_field_value",
        },
    )
    assert resp.status_code == 400


def test_brute_force_lockout_trigger(auth_client):
    for i in range(5):
        resp = auth_client.post(
            "/auth/login",
            json={"username": settings.admin_username, "password": f"Wrong_{i}"},
        )
    # The 5th or 6th attempt must trigger 429
    resp = auth_client.post(
        "/auth/login",
        json={"username": settings.admin_username, "password": "AnyPassword"},
    )
    assert resp.status_code == 429
    assert "bloqueado" in resp.json()["detail"].lower()
    assert "Retry-After" in resp.headers


def test_protected_me_endpoint(auth_client):
    # 1. Unauthenticated -> 401
    resp = auth_client.get("/auth/me")
    assert resp.status_code == 401

    # 2. Login to get token
    login_resp = auth_client.post(
        "/auth/login",
        json={"username": settings.admin_username, "password": settings.admin_password},
    )
    token = login_resp.json()["access_token"]

    # 3. Authenticated -> 200
    me_resp = auth_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == settings.admin_username


def test_security_headers_present(auth_client):
    resp = auth_client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
    assert resp.headers.get("Server") == "Flamante-Engine"
