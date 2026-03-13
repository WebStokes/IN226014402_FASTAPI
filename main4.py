from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
cart = []
order_counter = 1


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


def find_product(product_id: int):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def calculate_total(product: dict, quantity: int):
    return product["price"] * quantity


@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API!"}


@app.get("/products")
def get_products():
    return {"products": products}


# ---------------- CART SYSTEM ----------------

@app.post("/cart/add")
def add_to_cart(product_id: int = Query(...), quantity: int = Query(1)):

    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    subtotal = calculate_total(product, quantity)

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal,
    }

    cart.append(cart_item)

    return {"message": "Added to cart", "cart_item": cart_item}


@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total,
    }


@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    return {"error": "Item not found in cart"}


@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_counter

    if not cart:
        return {"error": "Cart is empty — add items first"}

    placed_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "delivery_address": data.delivery_address,
            "total_price": item["subtotal"],
            "status": "confirmed",
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]

        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total,
    }


@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}