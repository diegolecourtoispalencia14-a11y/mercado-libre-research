import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.database import get_db, Base
import app.models.product  # noqa: F401 — registers Product table in Base.metadata
import app.models.analysis  # noqa: F401 — registers Analysis/SavedReport tables

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def client():
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
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_get_reports_returns_list(client):
    resp = client.get("/reports")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
