import hashlib
import requests
from django.conf import settings


def generate_tbank_token(payload: dict, secret_key: str) -> str:
    """Генерация обязательного SHA-256 токена для боевого Т-Банка"""
    params = {k: v for k, v in payload.items() if not isinstance(v, (dict, list))}
    params['Password'] = secret_key
    sorted_keys = sorted(params.keys())
    raw_string = "".join(str(params[key]) for key in sorted_keys)
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()


def init_payment(order, total_amount_kopecks, receipt_items):
    """Запрос /Init в Т-Банк для получения платежной ссылки"""
    headers = {'Content-Type': 'application/json'}

    payload = {
        "TerminalKey": settings.TINKOFF_TERMINAL_KEY,
        "Amount": total_amount_kopecks,
        "OrderId": f"YEN-{order.id}",
        "Description": f"Оплата заказа №{order.id} в ЯсеньStudio",
        "SuccessURL": f"https://ya-studio.shop{order.id}/",
        "FailURL": "https://ya-studio.shop",
        "Receipt": {
            "Email": "info@ya-studio.shop",
            "Phone": order.phone,
            "Taxation": "usn_income",
            "Items": receipt_items
        }
    }

    payload["Token"] = generate_tbank_token(payload, settings.TINKOFF_SECRET_KEY)

    try:
        url = f"{settings.TINKOFF_API_URL.rstrip('/')}/Init"
        response = requests.post(url, json=payload, headers=headers, timeout=7,verify=False)

        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            response_data = response.json()
            if response_data.get('Success') and 'PaymentURL' in response_data:
                return {
                    'PaymentURL': response_data['PaymentURL'],
                    'PaymentId': response_data['PaymentId']
                }
            print(f"Ошибка шлюза Т-Банка: {response_data.get('Message')}")
    except Exception as e:
        print(f"Сбой вызова API Т-Банка: {e}")

    return None
