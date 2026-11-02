import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models.opportunity import MarketOpportunity
from app.scoring.economics import compute_reverse_unit_economics


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def test_setup():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    session = TestingSession()
    client = TestClient(app)
    yield client, session
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(engine)



def test_reverse_unit_economics_basic():
    # Item at 499 MXN (above 299 free shipping threshold)
    econ = compute_reverse_unit_economics(retail_price=499.0, desired_margin_pct=0.30)
    assert econ["retail_price"] == 499.0
    assert econ["shipping"] == 85.0
    assert econ["target_profit"] == round(499.0 * 0.30, 2)
    # Total sum check
    total_components = (
        econ["max_supplier_cost"]
        + econ["ml_fee"]
        + econ["shipping"]
        + econ["taxes"]
        + econ["target_profit"]
    )
    assert abs(total_components - 499.0) <= 0.05
    assert econ["max_supplier_cost"] > 0


def test_reverse_unit_economics_low_price():
    # Item at 150 MXN (under 299 threshold, seller doesn't pay 85 free shipping, but pays 25 fixed fee)
    econ = compute_reverse_unit_economics(retail_price=150.0, desired_margin_pct=0.30)
    assert econ["shipping"] == 0.0
    assert econ["ml_fee"] == round(150.0 * 0.175 + 25.0, 2)
    assert econ["max_supplier_cost"] > 0


def test_reverse_unit_economics_zero():
    econ = compute_reverse_unit_economics(retail_price=0.0)
    assert econ["max_supplier_cost"] == 0.0
    assert econ["target_profit"] == 0.0


def test_radar_endpoints(test_setup):
    client, db = test_setup
    # Seed an opportunity
    opp = MarketOpportunity(
        ml_id="MLMTEST001",
        title="Repisa Flotante Minimalista",
        category_name="Hogar y Muebles",
        price=350.0,
        target_supplier_cost=110.0,
        target_profit=105.0,
        estimated_monthly_sales=120.0,
        score=8.5,
        demand_score=8.0,
        competition_score=4.0,
        is_archetype=True,
        leverage_score=8.8,
        gap_type="Gama Media Estratégica",
        permalink="https://listado.mercadolibre.com.mx/repisa-flotante",
        thumbnail_url="https://http2.mlstatic.com/test.webp",
        status="active",
        detected_at=datetime.now(timezone.utc),
    )
    db.add(opp)

    opp2 = MarketOpportunity(
        ml_id="MLMTEST002",
        title="Soporte Genérico",
        category_name="Hogar y Muebles",
        price=120.0,
        target_supplier_cost=30.0,
        target_profit=36.0,
        estimated_monthly_sales=20.0,
        score=6.0,
        demand_score=5.0,
        competition_score=6.0,
        is_archetype=False,
        leverage_score=2.1,
        gap_type=None,
        permalink="https://listado.mercadolibre.com.mx/soporte",
        thumbnail_url="https://http2.mlstatic.com/test2.webp",
        status="active",
        detected_at=datetime.now(timezone.utc),
    )
    db.add(opp2)
    db.commit()

    # 1. Get opportunities (all)
    resp = client.get("/radar")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["ml_id"] == "MLMTEST001"
    assert data[0]["target_supplier_cost"] == 110.0
    assert data[0]["is_archetype"] is True
    assert data[0]["leverage_score"] == 8.8
    assert data[0]["gap_type"] == "Gama Media Estratégica"

    # 1b. Filter by archetype_only
    arch_resp = client.get("/radar?archetype_only=true")
    assert arch_resp.status_code == 200
    arch_data = arch_resp.json()
    assert len(arch_data) == 1
    assert arch_data[0]["ml_id"] == "MLMTEST001"

    # 2. Status endpoint
    s_resp = client.get("/radar/status")
    assert s_resp.status_code == 200
    s_data = s_resp.json()
    assert s_data["total_opportunities"] >= 2
    assert s_data["active_opportunities"] >= 2

    # 3. Patch status to dismissed
    p_resp = client.patch(f"/radar/{opp.id}", json={"status": "dismissed", "notes": "Costo de envío alto"})
    assert p_resp.status_code == 200
    assert p_resp.json()["status"] == "dismissed"
    assert p_resp.json()["notes"] == "Costo de envío alto"

    # 4. Trigger scan
    t_resp = client.post("/radar/scan")
    assert t_resp.status_code == 200
    assert t_resp.json()["status"] in ["started", "running"]
