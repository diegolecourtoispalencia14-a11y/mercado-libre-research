import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from app.adapters.trends_adapter import TrendsAdapter

@pytest.fixture
def adapter():
    return TrendsAdapter()

def test_returns_average_interest(adapter):
    mock_df = pd.DataFrame({"auriculares": [70, 80, 90, 75]})
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.cache_set"), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_pytrends = MagicMock()
        mock_pytrends.interest_over_time.return_value = mock_df
        mock_trend_cls.return_value = mock_pytrends
        result = adapter.get_interest("auriculares")
    assert result == pytest.approx(78.75)

def test_returns_none_on_empty_dataframe(adapter):
    mock_df = pd.DataFrame()
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.cache_set"), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_pytrends = MagicMock()
        mock_pytrends.interest_over_time.return_value = mock_df
        mock_trend_cls.return_value = mock_pytrends
        result = adapter.get_interest("xyznonexistent")
    assert result is None

def test_returns_none_on_exception(adapter):
    with patch("app.adapters.trends_adapter.cache_get", return_value=None), \
         patch("app.adapters.trends_adapter.TrendReq") as mock_trend_cls:
        mock_trend_cls.side_effect = Exception("pytrends error")
        result = adapter.get_interest("auriculares")
    assert result is None

def test_uses_cache(adapter):
    with patch("app.adapters.trends_adapter.cache_get", return_value=72.5):
        result = adapter.get_interest("auriculares")
    assert result == 72.5
