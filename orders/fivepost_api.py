import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class FivePostAPIClient:
    def __init__(self):
        if getattr(settings, 'FIVEPOST_SANDBOX', True):
            self.base_url = "https://api-preprod.fivepost.ru/api/v1"

        else:
            self.base_url = "https://api-ext.fivepost.ru/api/v1"

        self.client_id = settings.FIVEPOST_CLIENT_ID
        self.client_secret = settings.FIVEPOST_CLIENT_SECRET
        self._token = None

    def _get_jwt_token(self):
        if self._token:
            return self._token
        url = f"{self.base_url}/auth/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code == 200:
                self._token = response.json().get("access_token")
                return self._token
        except requests.RequestException:
            pass
        return None

    def get_headers(self):
        token = self._get_jwt_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}

    def create_delivery_order(self, order):
        url = f"{self.base_url}/orders"
        payload = {
            "senderOrderId": f"YA-STUDIO-{order.id}",
            "receiver": {
                "phone": order.phone.replace("+", "").replace(" ", ""),
                "fullName": f"{order.first_name} {order.last_name}"
            },
            "deliveryPointId": order.postamat_id,
            "cargo": {
                "weightGrams": 800,
                "lengthMm": 300, "widthMm": 150, "heightMm": 20
            },
            "cost": {
                "paymentType": "PREPAID",
                "assessedValue": float(order.total_price)
            }
        }
        try:
            headers = self.get_headers()
            if not headers.get("Authorization"): return None
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code in [200, 201]:
                return response.json().get("fivepostOrderId")
        except requests.RequestException:
            pass
        return None
