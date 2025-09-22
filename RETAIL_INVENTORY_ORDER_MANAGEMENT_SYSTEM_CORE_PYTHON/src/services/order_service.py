def process_payment(order_id: int, method: str) -> dict:
    from src.dao.order_dao import process_payment
    return process_payment(order_id, method)
from typing import List, Dict
from src.dao.customer_dao import get_customer_by_id
from src.dao.product_dao import get_product_by_id, update_product
from src.dao.order_dao import insert_order, insert_order_item


class OrderError(Exception):
    pass

def cancel_order(order_id: int) -> dict:
    from src.dao.order_dao import get_order_details
    from src.dao.product_dao import update_product, get_product_by_id
    from src.config import get_supabase
    sb = get_supabase()
    details = get_order_details(order_id)
    order = details.get("order")
    if not order:
        raise OrderError("Order not found")
    if order.get("status") != "PLACED":
        raise OrderError("Only PLACED orders can be cancelled")
    # Restore stock for each item
    for item in details.get("items", []):
        prod_id = item["prod_id"]
        qty = item["quantity"]
        product = get_product_by_id(prod_id)
        if product:
            new_stock = product["stock"] + qty
            update_product(prod_id, {"stock": new_stock})
    # Update order status
    sb.table("orders").update({"status": "CANCELLED"}).eq("order_id", order_id).execute()
    # Mark payment as REFUNDED
    sb.table("payments").update({"status": "REFUNDED"}).eq("order_id", order_id).execute()
    # Return updated order details
    updated = get_order_details(order_id)
    return updated

def create_order(customer_id: int, items: List[Dict]) -> Dict:
   
    customer = get_customer_by_id(customer_id)
    if not customer:
        raise OrderError("Customer not found")

   
    total_amount = 0
    product_updates = []
    for item in items:
        prod_id = item["prod_id"]
        qty = item["qty"]
        product = get_product_by_id(prod_id)
        if not product:
            raise OrderError(f"Product {prod_id} not found")
        if product["stock"] < qty:
            raise OrderError(f"Insufficient stock for product {prod_id}")
        total_amount += product["price"] * qty
        product_updates.append((prod_id, product["stock"] - qty))

    for prod_id, new_stock in product_updates:
        update_product(prod_id, {"stock": new_stock})

    order = insert_order(customer_id, total_amount)
    order_id = order["order_id"]
    for item in items:
        insert_order_item(order_id, item["prod_id"], item["qty"])

    # Insert pending payment record
    from src.dao.order_dao import insert_payment
    payment = insert_payment(order_id, total_amount, status="PENDING")

    return {"order_id": order_id, "customer_id": customer_id, "total_amount": total_amount, "items": items, "payment": payment}