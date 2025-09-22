# src/dao/customer_dao.py
from typing import Optional, List, Dict
from src.config import get_supabase

def _sb():
    return get_supabase()

def create_customer(name: str, email: str, phone: int, city: Optional[str] = None) -> Optional[Dict]:
    """
    Insert a customer and return the inserted row (two-step: insert then select by unique email).
    """
    payload = {"name": name, "email": email, "phone": phone}
    if city is not None:
        payload["city"] = city

    # Insert (no select chaining)
    _sb().table("customers").insert(payload).execute()

    # Fetch inserted row by unique column (email)
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_id(cust_id: int) -> Optional[Dict]:
    """
    Fetch a customer by their unique ID.
    """
    resp = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_customer_by_email(email: str) -> Optional[Dict]:
    """
    Fetch a customer by email.
    """
    resp = _sb().table("customers").select("*").eq("email", email).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_customer(cust_id: int, fields: Dict) -> Optional[Dict]:
    """
    Update a customer's details and return the updated row (two-step).
    """
    _sb().table("customers").update(fields).eq("cust_id", cust_id).execute()
    resp = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def delete_customer(cust_id: int) -> Optional[Dict]:
    """
    Delete a customer and return the deleted row.
    """
    resp_before = _sb().table("customers").select("*").eq("cust_id", cust_id).limit(1).execute()
    row = resp_before.data[0] if resp_before.data else None
    _sb().table("customers").delete().eq("cust_id", cust_id).execute()
    return row

def list_customers(limit: int = 100) -> List[Dict]:
    """
    List customers with a limit.
    """
    resp = _sb().table("customers").select("*").order("cust_id", desc=False).limit(limit).execute()
    return resp.data or []

def get_customers_by_city(city: str) -> List[Dict]:
    """
    Fetch all customers from a specific city.
    """
    resp = _sb().table("customers").select("*").eq("city", city).execute()
    return resp.data or []
