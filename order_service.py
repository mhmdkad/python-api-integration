class OrderService:

    def __init__(self, client):
        self.client = client

    def get_order_summary(self, order_id):
        item_count = 0
        order = self.client.get_order(order_id)
        order_summary = {}

        order_summary["order_id"] = order["id"]
        order_summary["customer_email"] = order["customer"]["email"]
        order_summary["amount"] = order["amount"]
        order_summary["status"] = order["status"]

        for item in order["items"]:
            item_count += item["quantity"]

        order_summary["item_count"] = item_count

        return order_summary