def cmd_order_refund(args):
    try:
        from src.config import get_supabase
        sb = get_supabase()
        order = sb.table("orders").select("*").eq("order_id", args.order).limit(1).execute()
        order_data = order.data[0] if order.data else None
        if not order_data:
            print(f"Order {args.order} not found.")
            return
        if order_data.get("status") != "CANCELLED":
            print(f"Only CANCELLED orders can be refunded. Current status: {order_data.get('status')}")
            return
        sb.table("payments").update({"status": "REFUNDED"}).eq("order_id", args.order).execute()
        payment = sb.table("payments").select("*").eq("order_id", args.order).order("payment_id", desc=True).limit(1).execute()
        print(f"Order {args.order} payment marked as REFUNDED:")
        print(json.dumps(payment.data[0] if payment.data else None, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
def cmd_order_pay(args):
    try:
        from src.services.order_service import process_payment
        result = process_payment(args.order, args.method)
        print(f"Order {args.order} payment processed:")
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
def cmd_order_cancel(args):
    try:
        from src.services.order_service import cancel_order, OrderError
        result = cancel_order(args.order)
        print(f"Order {args.order} cancelled (updated):")
        print(json.dumps(result, indent=2, default=str))
    except OrderError as oe:
        print("Order error:", oe)
    except Exception as e:
        print("Error:", e)
import argparse
import json
from src.services import product_service
from src.dao import product_dao

def cmd_product_add(args):
    try:
        p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
        print("Created product:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_product_list(args):
    try:
        ps = product_dao.list_products(limit=100)
        print(json.dumps(ps, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_add(args):
    try:
        from src.services import customer_service
        c = customer_service.add_customer(args.name, args.email, args.phone, args.city)
        print("Created customer:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_search(args):
    try:
        from src.services import customer_service
        customers = customer_service.customer_service.search_customers(email=args.email, city=args.city)
        print(json.dumps(customers, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_list(args):
    try:
        from src.services import customer_service
        customers = customer_service.customer_service.list_customers()
        print(json.dumps(customers, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_update(args):
    try:
        from src.services import customer_service
        c = customer_service.customer_service.update_customer(
            args.cust_id,
            new_phone=args.phone,
            new_city=args.city
        )
        print(f"Updated customer {args.cust_id}:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_delete(args):
    try:
        from src.services import customer_service
        customer_service.customer_service.delete_customer(args.cust_id)
        print(f"Deleted customer with ID {args.cust_id}")
    except Exception as e:
        print("Error:", e)

def cmd_order_create(args):
    items = []
    for item in args.item:
        try:
            pid, qty = item.split(":")
            items.append({"prod_id": int(pid), "qty": int(qty)})
        except Exception:
            print("Invalid item format:", item)
            return
    try:
        from src.services.order_service import create_order, OrderError
        order = create_order(args.customer, items)
        print("Order created:")
        print(json.dumps(order, indent=2, default=str))
    except OrderError as oe:
        print("Order error:", oe)
    except Exception as e:
        print("Error:", e)

def cmd_order_show(args):
    try:
        from src.dao.order_dao import get_order_details
        details = get_order_details(args.order)
        print("Order details:")
        print(json.dumps(details, indent=2, default=str))
    except Exception as e:
        print("Error:", e)


def cmd_order_list(args):
    try:
        from src.dao.order_dao import list_orders_by_customer_orders
        orders = list_orders_by_customer_orders(args.customer)
        print(f"Orders for customer {args.customer}:")
        print(json.dumps(orders, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def build_parser():
    parser = argparse.ArgumentParser(prog="retail-cli")
    sub = parser.add_subparsers(dest="cmd")

    p_prod = sub.add_parser("product", help="product commands")
    pprod_sub = p_prod.add_subparsers(dest="action")

    addp = pprod_sub.add_parser("add")
    addp.add_argument("--name", required=True)
    addp.add_argument("--sku", required=True)
    addp.add_argument("--price", type=float, required=True)
    addp.add_argument("--stock", type=int, default=0)
    addp.add_argument("--category", default=None)
    addp.set_defaults(func=cmd_product_add)

    listp = pprod_sub.add_parser("list")
    listp.set_defaults(func=cmd_product_list)

    pcust = sub.add_parser("customer")
    pcust_sub = pcust.add_subparsers(dest="action")
    addc = pcust_sub.add_parser("add")
    addc.add_argument("--name", required=True)
    addc.add_argument("--email", required=True)
    addc.add_argument("--phone", required=True)
    addc.add_argument("--city", default=None)
    addc.set_defaults(func=cmd_customer_add)

    searchc = pcust_sub.add_parser("search")
    searchc.add_argument("--email", default=None)
    searchc.add_argument("--city", default=None)
    searchc.set_defaults(func=cmd_customer_search)

    listc = pcust_sub.add_parser("list")
    listc.set_defaults(func=cmd_customer_list)

    updc = pcust_sub.add_parser("update")
    updc.add_argument("--cust_id", type=int, required=True)
    updc.add_argument("--phone", type=int, default=None)
    updc.add_argument("--city", default=None)
    updc.set_defaults(func=cmd_customer_update)

    delc = pcust_sub.add_parser("delete")
    delc.add_argument("--cust_id", type=int, required=True)
    delc.set_defaults(func=cmd_customer_delete)

    porder = sub.add_parser("order")
    porder_sub = porder.add_subparsers(dest="action")

    createo = porder_sub.add_parser("create")
    createo.add_argument("--customer", type=int, required=True)
    createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
    createo.set_defaults(func=cmd_order_create)

    showo = porder_sub.add_parser("show")
    showo.add_argument("--order", type=int, required=True)
    showo.set_defaults(func=cmd_order_show)

    cano = porder_sub.add_parser("cancel")
    cano.add_argument("--order", type=int, required=True)
    cano.set_defaults(func=cmd_order_cancel)

    listo = porder_sub.add_parser("list")
    listo.add_argument("--customer", type=int, required=True)
    listo.set_defaults(func=cmd_order_list)

    payo = porder_sub.add_parser("pay")
    payo.add_argument("--order", type=int, required=True)
    payo.add_argument("--method", choices=["Cash", "Card", "UPI"], required=True)
    payo.set_defaults(func=cmd_order_pay)

    refundo = porder_sub.add_parser("refund")
    refundo.add_argument("--order", type=int, required=True)
    refundo.set_defaults(func=cmd_order_refund)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
# import argparse
# import json
# from src.services import product_service
# from src.dao import product_dao

# def cmd_product_add(args):
#     try:
#         p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
#         print("Created product:")
#         print(json.dumps(p, indent=2, default=str))
#     except Exception as e:
#         print("Error:", e)
# def build_parser():
#     parser = argparse.ArgumentParser(prog="retail-cli")
#     sub = parser.add_subparsers(dest="cmd")

#     p_prod = sub.add_parser("product", help="product commands")
#     pprod_sub = p_prod.add_subparsers(dest="action")

#     addp = pprod_sub.add_parser("add")
#     addp.add_argument("--name", required=True)
#     addp.add_argument("--sku", required=True)
#     addp.add_argument("--price", type=float, required=True)
#     addp.add_argument("--stock", type=int, default=0)
#     addp.add_argument("--category", default=None)
#     addp.set_defaults(func=cmd_product_add)

#     listp = pprod_sub.add_parser("list")
#     listp.set_defaults(func=cmd_product_list)

#     pcust = sub.add_parser("customer")
#     pcust_sub = pcust.add_subparsers(dest="action")
#     addc = pcust_sub.add_parser("add")
#     addc.add_argument("--name", required=True)
#     addc.add_argument("--email", required=True)
#     addc.add_argument("--phone", required=True)
#     addc.add_argument("--city", default=None)
#     addc.set_defaults(func=cmd_customer_add)

#     porder = sub.add_parser("order")
#     porder_sub = porder.add_subparsers(dest="action")
#     createo = porder_sub.add_parser("create")
#     createo.add_argument("--customer", type=int, required=True)
#     createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
#     createo.set_defaults(func=cmd_order_create)

#     return parser

# def main():
#     parser = build_parser()
#     args = parser.parse_args()
#     if not hasattr(args, "func"):
#         parser.print_help()
#         return
#     args.func(args)

# if __name__ == "__main__":
#     main()


#         """
#         showo = porder_sub.add_parser("show")
#         showo.add_argument("--order", type=int, required=True)
#         showo.set_defaults(func=self.cmd_order_show)

#         cano = porder_sub.add_parser("cancel")
#         cano.add_argument("--order", type=int, required=True)
#         cano.set_defaults(func=self.cmd_order_cancel)
#         """

#         return parser

#     def cmd_product_add(self, args):
#         try:
#             p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
#             print("Created product:")
#             print(json.dumps(p, indent=2, default=str))
#         except Exception as e:
#             print("Error:", e)

#     def cmd_product_list(self, args):
#         try:
#             ps = product_dao.list_products(limit=100)
#             print(json.dumps(ps, indent=2, default=str))
#         except Exception as e:
#             print("Error:", e)

#     def cmd_customer_add(self, args):
#         try:
#             from src.services import customer_service
#             c = customer_service.add_Customer(args.name, args.email, args.phone, args.city)
#             print("Created customer:")
#             print(json.dumps(c, indent=2, default=str))
#         except Exception as e:
#             print("Error:", e)

#     def cmd_order_create(self, args):
#         items = []
#         for item in args.item:
#             try:
#                 pid, qty = item.split(":")
#                 items.append({"prod_id": int(pid), "quantity": int(qty)})
#             except Exception:
#                 print("Invalid item format:", item)
#                 return
#         # try:
#         #     ord = order_service.create_order(args.customer, items)
#         #     print("Order created:")
#         #     print(json.dumps(ord, indent=2, default=str))
#         # except Exception as e:
#         #     print("Error:", e)

#     # def cmd_order_show(self, args):
#     #     try:
#     #         o = order_service.get_order_details(args.order)
#     #         print(json.dumps(o, indent=2, default=str))
#     #     except Exception as e:
#     #         print("Error:", e)

#     # def cmd_order_cancel(self, args):
#     #     try:
#     #         o = order_service.cancel_order(args.order)
#     #         print("Order cancelled (updated):")
#     #         print(json.dumps(o, indent=2, default=str))
#     #     except Exception as e:
#     #         print("Error:", e)

#     def run(self):
#         args = self.parser.parse_args()
#         if not hasattr(args, "func"):
#             self.parser.print_help()
#             return
#         args.func(args)


# if __name__ == "__main__":
#     cli = RetailCLI()
#     cli.run()
