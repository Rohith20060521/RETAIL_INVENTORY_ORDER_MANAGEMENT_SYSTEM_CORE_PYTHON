from typing import List, Dict, Optional
import src.dao.customer_dao as customer_dao
from src.dao.order_dao import list_orders_by_customer

class CustomerError(Exception):
    pass

class CustomerService:
    def add_customer(self, name: str, email: str, phone: int, city: Optional[str] = None) -> Dict:
        """
        Validate and insert a new customer.
        Raises CustomerError on validation failure.
        """
        existing = customer_dao.get_customer_by_email(email)
        if existing:
            raise CustomerError(f"Email already exists: {email}")
        return customer_dao.create_customer(name, email, phone, city)

    def update_customer(self, cust_id: int, new_phone: Optional[int] = None, new_city: Optional[str] = None) -> Dict:
        """
        Update customer's phone or city.
        """
        existing = customer_dao.get_customer_by_id(cust_id)
        if not existing:
            raise CustomerError("Customer not found")
        update_data = {}
        if new_phone is not None:
            update_data["phone"] = new_phone
        if new_city is not None:
            update_data["city"] = new_city
        if not update_data:
            raise CustomerError("No data provided for update")
        return customer_dao.update_customer(cust_id, update_data)

    def delete_customer(self, cust_id: int) -> None:
        """
        Delete a customer only if they have no orders.
        Raises CustomerError if orders exist.
        """
        orders = list_orders_by_customer(cust_id)
        if orders:
            raise CustomerError("Cannot delete customer: orders exist.")
        customer_dao.delete_customer(cust_id)

    def list_customers(self, limit: int = 1000) -> List[Dict]:
        """
        Return a list of customers.
        """
        return customer_dao.list_customers(limit=limit)

    def search_customers(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        """
        Search customers by email or city.
        """
        if email:
            cust = customer_dao.get_customer_by_email(email)
            return [cust] if cust else []
        if city:
            return customer_dao.get_customers_by_city(city)
        # If no filters provided, return all customers
        return self.list_customers()

customer_service = CustomerService()

def add_customer(name: str, email: str, phone: int, city: Optional[str] = None) -> Dict:
    return customer_service.add_customer(name, email, phone, city)
    raise CustomerError("Customer not found")

    #     update_data = {}
    #     if new_phone is not None:
    #         update_data["phone"] = new_phone
    #     if new_city is not None:
    #         update_data["city"] = new_city

    #     if not update_data:
    #         raise CustomerError("No data provided for update")

    #     return customer_dao.update_customer(cust_id, update_data)

    # def delete_customer(self, cust_id: int) -> None:
    #     """
    #     Delete a customer only if they have no orders.
    #     Raises CustomerError if orders exist.
    #     """
    #     orders = list_orders_by_customer(cust_id)
    #     if orders:
    #         raise CustomerError("Cannot delete customer: orders exist.")
    #     customer_dao.delete_customer(cust_id)

    # def list_customers(self, limit: int = 1000) -> List[Dict]:
    #     """
    #     Return a list of customers.
    #     """
    #     return customer_dao.list_customers(limit=limit)

    # def search_customers(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
    #     """
    #     Search customers by email or city.
    #     """
    #     if email:
    #         cust = customer_dao.get_customer_by_email(email)
    #         return [cust] if cust else []

    #     if city:
    #         return customer_dao.get_customers_by_city(city)

    #     # If no filters provided, return all customers
    #     return self.list_customers()
