import time
import requests


class OrderClient:

    def __init__(self, base_url):
        self.base_url = base_url

    def get_order(self, order_id):
        for attempt in range(3):
            try:
                response = requests.get(
                    f"{self.base_url}/orders/{order_id}",
                    timeout=10,
                )

                response.raise_for_status()

                return response.json()

            except requests.HTTPError:
                if response.status_code not in (429, 500, 502, 503, 504):
                    raise

                if attempt == 2:
                    raise

                time.sleep(2 ** attempt)

            except (requests.Timeout, requests.ConnectionError):
                if attempt == 2:
                    raise

                time.sleep(2 ** attempt)