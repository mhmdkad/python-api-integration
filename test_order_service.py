from unittest.mock import patch
import requests
import pytest

from order_client import OrderClient
from order_service import OrderService

class FakeOrderClient:
    def get_order(self, order_id):
        return {
        "id": "ORD-123",
        "customer": {
            "email": "alice@example.com"
        },
        "amount": 129.99,
        "currency": "EUR",
        "status": "paid",
        "items": [
            {
                "sku": "SHOE-42",
                "quantity": 1
            }
        ]
    }

class MockResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self.data = data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"{self.status_code} Error"
            )

    def json(self):
        return self.data

def test_order_summary():
    client = FakeOrderClient()
    service = OrderService(client)

    result = service.get_order_summary("ORD-123")

    assert result["order_id"] == "ORD-123"
    assert result["customer_email"] == "alice@example.com"
    assert result["amount"] == 129.99
    assert result["status"] == "paid"
    assert result["item_count"] == 1

def test_get_order_raises_on_404():
    client = OrderClient("http://fake-api")

    with patch("order_client.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = (
            requests.HTTPError("404 Not Found")
        )

        try:
            client.get_order("ORD-123")
            assert False, "Expected HTTPError"
        except requests.HTTPError as exc:
            assert str(exc) == "404 Not Found"

def test_get_order_retries_on_429():
    client = OrderClient("http://fake-api")

    responses = [
        MockResponse(429),
        MockResponse(429),
        MockResponse(
            200,
            {
                "id": "ORD-123",
                "customer": {"email": "alice@example.com"},
                "amount": 129.99,
                "currency": "EUR",
                "status": "paid",
                "items": [
                    {"sku": "SHOE-42", "quantity": 1}
                ],
            },
        ),
    ]

    with patch(
        "order_client.requests.get",
        side_effect=responses,
    ) as mock_get:
        with patch("order_client.time.sleep"):
            result = client.get_order("ORD-123")

    assert result["id"] == "ORD-123"
    assert mock_get.call_count == 3

def test_get_order_retries_on_500_then_fails():
    client = OrderClient("http://fake-api")

    responses = [
        MockResponse(500),
        MockResponse(500),
        MockResponse(500),
    ]

    with patch(
        "order_client.requests.get",
        side_effect=responses,
    ) as mock_get:
        with patch("order_client.time.sleep"):
            with pytest.raises(requests.HTTPError):
                client.get_order("ORD-123")

    assert mock_get.call_count == 3

def test_get_order_retries_on_timeout():
    client = OrderClient("http://fake-api")

    with patch(
        "order_client.requests.get",
        side_effect=requests.Timeout("Request timed out"),
    ) as mock_get:
        with patch("order_client.time.sleep"):
            with pytest.raises(requests.Timeout):
                client.get_order("ORD-123")

    assert mock_get.call_count == 3