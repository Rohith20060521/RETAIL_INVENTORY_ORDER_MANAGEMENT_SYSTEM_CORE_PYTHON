from src.config import get_supabase
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Top 5 selling products (by total quantity)
def top_selling_products(limit=5):
    sb = get_supabase()
    items = sb.table("order_items").select("prod_id, quantity").execute().data
    counter = Counter()
    for item in items:
        counter[item["prod_id"]] += item["quantity"]
    return counter.most_common(limit)

# Total revenue in the last month
def total_revenue_last_month():
    sb = get_supabase()
    today = datetime.utcnow()
    first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = today.replace(day=1) - timedelta(days=1)
    orders = sb.table("orders").select("order_date, total_amount").execute().data
    revenue = sum(o["total_amount"] for o in orders if first_day.isoformat() <= o["order_date"] <= last_day.isoformat())
    return revenue

# Total orders placed by each customer
def total_orders_per_customer():
    sb = get_supabase()
    orders = sb.table("orders").select("cust_id").execute().data
    counter = Counter(o["cust_id"] for o in orders)
    return dict(counter)

# Customers who placed more than 2 orders
def customers_with_more_than_n_orders(n=2):
    counts = total_orders_per_customer()
    return [cust_id for cust_id, total in counts.items() if total > n]

if __name__ == "__main__":
    import json
    print("Top 5 selling products:")
    print(json.dumps(top_selling_products(), indent=2))
    print("\nTotal revenue last month:")
    print(total_revenue_last_month())
    print("\nTotal orders per customer:")
    print(json.dumps(total_orders_per_customer(), indent=2))
    print("\nCustomers with more than 2 orders:")
    print(json.dumps(customers_with_more_than_n_orders(2), indent=2))