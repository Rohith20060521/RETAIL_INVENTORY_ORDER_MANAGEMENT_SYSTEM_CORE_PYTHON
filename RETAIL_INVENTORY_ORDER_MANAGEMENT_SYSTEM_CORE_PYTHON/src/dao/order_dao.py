def process_payment(order_id: int, method: str) -> dict:
    from datetime import datetime
    sb = get_supabase()
    # Update payment record
    paid_at = datetime.utcnow().isoformat()
    sb.table("payments").update({"status": "PAID", "method": method, "paid_at": paid_at}).eq("order_id", order_id).execute()
    # Update order status
    sb.table("orders").update({"status": "COMPLETED"}).eq("order_id", order_id).execute()
    # Return updated payment and order
    payment = sb.table("payments").select("*").eq("order_id", order_id).order("payment_id", desc=True).limit(1).execute()
    order = sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    return {"order": order.data[0] if order.data else None, "payment": payment.data[0] if payment.data else None}
def insert_payment(order_id: int, amount: float, status: str = "PENDING") -> dict:
    sb = get_supabase()
    payload = {"order_id": order_id, "amount": amount, "status": status}
    sb.table("payments").insert(payload).execute()
    resp = sb.table("payments").select("*").order("payment_id", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None
# Fetch full details of an order (order info + customer info + order items)
def get_order_details(order_id: int) -> dict:
    sb = get_supabase()
    order = sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    order_data = order.data[0] if order.data else None
    if not order_data:
        return {}
    customer = sb.table("customers").select("*").eq("cust_id", order_data["cust_id"]).limit(1).execute()
    customer_data = customer.data[0] if customer.data else None
    items = sb.table("order_items").select("*").eq("order_id", order_id).execute()
    return {
        "order": order_data,
        "customer": customer_data,
        "items": items.data or []
    }
# src/dao/order_dao.py
from src.config import get_supabase
from typing import List, Dict

def list_orders_by_customer(customer_id: int) -> List[Dict]:
    sb = get_supabase()
    resp = sb.table("customers").select("*").eq("customer_id", customer_id).execute()
    return resp.data or []

def insert_order(customer_id: int, total_amount: float) -> Dict:
    sb = get_supabase()
    payload = {"cust_id": customer_id, "total_amount": total_amount}
    sb.table("orders").insert(payload).execute()
    resp = sb.table("orders").select("*").order("order_id", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None

def insert_order_item(order_id: int, prod_id: int, qty: int) -> Dict:
    sb = get_supabase()
    from src.dao.product_dao import get_product_by_id
    product = get_product_by_id(prod_id)
    price = product["price"] if product else None
    payload = {"order_id": order_id, "prod_id": prod_id, "quantity": qty, "price": price}
    sb.table("order_items").insert(payload).execute()
    resp = sb.table("order_items").select("*").order("item_id", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None

def list_orders_by_customer_orders(customer_id: int) -> List[Dict]:
    sb = get_supabase()
    resp = sb.table("orders").select("*").eq("cust_id", customer_id).order("order_id", desc=False).execute()
    return resp.data or []
