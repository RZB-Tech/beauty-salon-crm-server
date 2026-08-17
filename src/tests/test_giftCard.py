from datetime import datetime

import pytest
pytestmark = pytest.mark.asyncio(loop_scope="session")

class TestGiftCard:
    async def test_giftCard_create(self, auth_client):
        payload = {
            "initial_amount": 350000,
            "issue_date": datetime.now().isoformat(),
            "payment_method": "cash"
        }
        response = await auth_client.post("/api/v1/gift-cards", json=payload)
        assert response.status_code == 201