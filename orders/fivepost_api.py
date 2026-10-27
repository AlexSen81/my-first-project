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

    def calculate_parcel_box(self, order_items):
        """
        Умный упаковщик ЯСЕНЬ-STUDIO.
        Принимает товары из корзины и подбирает коробку S, M или L.
        """
        max_length = 0
        max_width = 0
        total_height = 0
        total_weight = 0

        for item in order_items:
            # Высчитываем максимальные габариты среди товаров в корзине
            if item.product.length_cm > max_length:
                max_length = item.product.length_cm
            if item.product.width_cm > max_width:
                max_width = item.product.width_cm

            # Высоту складываем, как будто кладем изделия друг на друга
            total_height += (item.product.height_cm * item.quantity)
            # Примерный вес крафтового декора: 800 грамм на одну позицию
            total_weight += (800 * item.quantity)

        # Добавляем по 3 см на пупырку и коробку
        final_l = max_length + 3
        final_w = max_width + 3
        final_h = total_height + 3

        # Сверяем с официальными лимитами ячеек 5Post (в мм)
        if final_l <= 45 and final_w <= 38 and final_h <= 19:
            return {"length": 450, "width": 380, "height": 190, "weight": total_weight, "class": "S"}

        elif final_l <= 60 and final_w <= 38 and final_h <= 19:
            return {"length": 600, "width": 380, "height": 190, "weight": total_weight, "class": "M"}

        elif final_l <= 60 and final_w <= 38 and final_h <= 36:
            return {"length": 600, "width": 380, "height": 360, "weight": total_weight, "class": "L"}

        else:
            # Если это журнальный стол или огромная консоль из массива
            return None

    def create_delivery_order(self, order):
        url = f"{self.base_url}/orders"

        # Передаем товары заказа в наш упаковщик
        items = order.items.all()
        box = self.calculate_parcel_box(items)

        # Если заказ слишком огромный и превысил ячейку L — отменяем 5Post
        if box is None:
            return None

        payload = {
            "senderOrderId": f"YA-STUDIO-{order.id}",
            "receiver": {
                "phone": order.phone.replace("+", "").replace(" ", ""),
                "fullName": f"{order.first_name} {order.last_name}"
            },
            "deliveryPointId": order.postamat_id,
            "cargo": {
                "weightGrams": box["weight"],
                "lengthMm": box["length"],
                "widthMm": box["width"],
                "heightMm": box["height"]
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
