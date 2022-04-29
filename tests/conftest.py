import pytest


@pytest.fixture(autouse=True)
def use_forecast_url(settings):
    settings.ISCC_ID_FORECAST_URL = "https://testnet.iscc.id/api/v1/forecast"
