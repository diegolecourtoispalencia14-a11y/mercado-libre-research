from app.models.product import Product
from app.models.analysis import Analysis, AnalysisProduct, SavedReport
from datetime import datetime, timezone


def test_product_create(db):
    p = Product(
        ml_id="MLM123",
        title="Auriculares Bluetooth",
        price=299.0,
        sold_quantity=150,
        seller_id="seller1",
        category_id="MLM1051",
        thumbnail_url="https://example.com/img.jpg",
        fetched_at=datetime.now(timezone.utc),
    )
    db.add(p)
    db.flush()
    assert p.id is not None


def test_analysis_create(db):
    a = Analysis(keyword="auriculares", score=7.5,
                 demand_score=8.0, competition_score=4.0, trend_score=6.5)
    db.add(a)
    db.flush()
    assert a.id is not None
