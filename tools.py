
import os
import requests
from urllib.parse import quote
from typing import Any

# Backend API URL
BASE_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

TIMEOUT = 30


def _request(method: str, endpoint: str, **kwargs: Any) -> Any:
    """Send an HTTP request to the E-Commerce Backend API."""
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    try:
        response = requests.request(
            method,
            url,
            timeout=TIMEOUT,
            **kwargs
        )
        response.raise_for_status()

        if response.status_code == 204:
            return {"success": True}

        return response.json()

    except requests.exceptions.HTTPError as e:
        try:
            error_details = e.response.json()
        except ValueError:
            error_details = e.response.text

        return {
            "success": False,
            "error": error_details,
            "status_code": e.response.status_code
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


# 1. List Categories
def list_categories() -> Any:
    """Retrieve all available product categories."""
    return _request("GET", "/categories")


# 2. Search Products
def search_products(
    keyword: str,
    category_id: int,
    in_stock_only: bool
) -> Any:
    """Search products by keyword, category, and stock availability."""
    params = {
        "search": keyword,
        "category_id": category_id,
        "in_stock_only": in_stock_only
    }

    return _request("GET", "/products", params=params)


# 3. Get Product Details
def get_product_details(product_id: int) -> Any:
    """Retrieve complete details of a specific product."""
    return _request("GET", f"/products/{product_id}")


# 4. Get Customer Cart
def get_customer_cart(customer_name: str) -> Any:
    """Retrieve the customer's cart and its total price."""
    customer = quote(customer_name, safe="")
    return _request("GET", f"/cart/{customer}")


# 5. Add Item To Cart
def add_item_to_cart(
    customer_name: str,
    product_id: int,
    quantity: int = 1
) -> Any:
    """Add a product to the customer's cart."""
    data = {
        "customer_name": customer_name,
        "product_id": product_id,
        "quantity": quantity
    }

    return _request("POST", "/cart/items", json=data)


# 6. Remove Cart Item
def remove_cart_item(item_id: int) -> Any:
    """Remove a specific item from the customer's cart."""
    return _request("DELETE", f"/cart/items/{item_id}")


# 7. Clear Customer Cart
def clear_customer_cart(customer_name: str) -> Any:
    """Remove all items from the customer's cart."""
    customer = quote(customer_name, safe="")
    return _request("DELETE", f"/cart/{customer}")


# 8. Checkout Cart
def checkout_cart(
    customer_name: str,
    shipping_address: str
) -> Any:
    """Complete checkout with the customer's shipping address."""
    data = {
        "customer_name": customer_name,
        "shipping_address": shipping_address
    }

    return _request("POST", "/orders/checkout", json=data)


# 9. Track Order
def track_order(order_id: int) -> Any:
    """Retrieve the status and details of a specific order."""
    return _request("GET", f"/orders/{order_id}")


# 10. Cancel Order
def cancel_order(order_id: int) -> Any:
    """Cancel an order and request the backend to restore its stock."""
    return _request("PUT", f"/orders/{order_id}/cancel")
