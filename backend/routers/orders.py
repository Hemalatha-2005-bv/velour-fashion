"""
Orders router — place order, list orders, get single order.
"""
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from models.schemas import OrderCreate, OrderOut, OrderItemOut, Address, PaymentInfo
from middleware.auth import get_current_user
from utils.file_store import read_json, write_json, read_dict, write_dict

router = APIRouter(prefix="/api/orders", tags=["orders"])

PROMO_CODES = {
    "VELOUR10": 10,   # 10% off
    "WELCOME20": 20,  # 20% off
    "SALE15": 15,     # 15% off
}
SHIPPING_THRESHOLD = 100.0
SHIPPING_COST = 9.99


@router.post("", response_model=OrderOut, status_code=201)
async def place_order(data: OrderCreate, current_user: dict = Depends(get_current_user)):
    # Load cart
    carts = await read_dict("carts.json")
    user_cart = carts.get(current_user["user_id"], [])
    if not user_cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Load product prices (re-verify)
    all_products = await read_json("products.json")
    product_map = {p["id"]: p for p in all_products}

    order_items = []
    subtotal = 0.0
    for item in user_cart:
        product = product_map.get(item["product_id"])
        if not product:
            raise HTTPException(status_code=400, detail=f"Product {item['product_id']} no longer available")
        item_total = product["price"] * item["quantity"]
        subtotal += item_total
        order_items.append({
            "product_id": item["product_id"],
            "name": product["name"],
            "image": product["images"][0] if product["images"] else "",
            "price": product["price"],
            "size": item["size"],
            "color": item["color"],
            "quantity": item["quantity"],
            "subtotal": round(item_total, 2),
        })

    # Shipping
    shipping = 0.0 if subtotal >= SHIPPING_THRESHOLD else SHIPPING_COST

    # Promo code discount
    discount = 0.0
    if data.promo_code and data.promo_code.upper() in PROMO_CODES:
        pct = PROMO_CODES[data.promo_code.upper()]
        discount = round(subtotal * pct / 100, 2)

    total = round(subtotal + shipping - discount, 2)

    order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
    now = datetime.utcnow()
    estimated_delivery = (now + timedelta(days=5)).strftime("%B %d, %Y")

    order = {
        "id": order_id,
        "user_id": current_user["user_id"],
        "items": order_items,
        "shipping_address": data.shipping_address.model_dump(),
        "payment_info": data.payment_info.model_dump(),
        "subtotal": round(subtotal, 2),
        "shipping": round(shipping, 2),
        "discount": discount,
        "total": total,
        "status": "confirmed",
        "created_at": now.isoformat(),
        "estimated_delivery": estimated_delivery,
    }

    orders = await read_json("orders.json")
    orders.append(order)
    await write_json("orders.json", orders)

    # Clear cart after order
    carts[current_user["user_id"]] = []
    await write_dict("carts.json", carts)

    return OrderOut(**order)


@router.get("", response_model=list[OrderOut])
async def get_orders(current_user: dict = Depends(get_current_user)):
    orders = await read_json("orders.json")
    user_orders = [o for o in orders if o["user_id"] == current_user["user_id"]]
    user_orders.sort(key=lambda o: o["created_at"], reverse=True)
    return [OrderOut(**o) for o in user_orders]


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    orders = await read_json("orders.json")
    order = next((o for o in orders if o["id"] == order_id and o["user_id"] == current_user["user_id"]), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(**order)
