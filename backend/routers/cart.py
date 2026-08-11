"""
Cart router — get cart, add item, update quantity, remove item, clear cart.
"""
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from models.schemas import CartItemAdd, CartItemUpdate, CartItemOut, CartOut
from middleware.auth import get_current_user
from utils.file_store import read_json, read_dict, write_dict

router = APIRouter(prefix="/api/cart", tags=["cart"])

SHIPPING_THRESHOLD = 100.0
SHIPPING_COST = 9.99


def _calculate_totals(items: list) -> CartOut:
    subtotal = sum(i["price"] * i["quantity"] for i in items)
    shipping = 0.0 if subtotal >= SHIPPING_THRESHOLD else SHIPPING_COST
    total = subtotal + shipping
    return CartOut(
        items=[CartItemOut(
            item_id=i["item_id"],
            product_id=i["product_id"],
            name=i["name"],
            image=i["image"],
            price=i["price"],
            size=i["size"],
            color=i["color"],
            quantity=i["quantity"],
            subtotal=round(i["price"] * i["quantity"], 2),
        ) for i in items],
        subtotal=round(subtotal, 2),
        shipping=round(shipping, 2),
        total=round(total, 2),
        item_count=sum(i["quantity"] for i in items),
    )


@router.get("", response_model=CartOut)
async def get_cart(current_user: dict = Depends(get_current_user)):
    carts = await read_dict("carts.json")
    items = carts.get(current_user["user_id"], [])
    return _calculate_totals(items)


@router.post("", response_model=CartOut)
async def add_to_cart(data: CartItemAdd, current_user: dict = Depends(get_current_user)):
    products = await read_json("products.json")
    product = next((p for p in products if p["id"] == data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.size not in product["sizes"]:
        raise HTTPException(status_code=400, detail=f"Size '{data.size}' not available")
    if data.quantity < 1 or data.quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    carts = await read_dict("carts.json")
    user_cart = carts.get(current_user["user_id"], [])

    # Check if same product+size+color already in cart
    existing = next(
        (i for i in user_cart if i["product_id"] == data.product_id and i["size"] == data.size and i["color"] == data.color),
        None,
    )
    if existing:
        existing["quantity"] = min(existing["quantity"] + data.quantity, product["stock"])
    else:
        user_cart.append({
            "item_id": str(uuid.uuid4()),
            "product_id": data.product_id,
            "name": product["name"],
            "image": product["images"][0] if product["images"] else "",
            "price": product["price"],
            "size": data.size,
            "color": data.color,
            "quantity": data.quantity,
        })

    carts[current_user["user_id"]] = user_cart
    await write_dict("carts.json", carts)
    return _calculate_totals(user_cart)


@router.put("/{item_id}", response_model=CartOut)
async def update_cart_item(item_id: str, data: CartItemUpdate, current_user: dict = Depends(get_current_user)):
    carts = await read_dict("carts.json")
    user_cart = carts.get(current_user["user_id"], [])
    item = next((i for i in user_cart if i["item_id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if data.quantity <= 0:
        user_cart = [i for i in user_cart if i["item_id"] != item_id]
    else:
        item["quantity"] = data.quantity

    carts[current_user["user_id"]] = user_cart
    await write_dict("carts.json", carts)
    return _calculate_totals(user_cart)


@router.delete("/{item_id}", response_model=CartOut)
async def remove_cart_item(item_id: str, current_user: dict = Depends(get_current_user)):
    carts = await read_dict("carts.json")
    user_cart = carts.get(current_user["user_id"], [])
    user_cart = [i for i in user_cart if i["item_id"] != item_id]
    carts[current_user["user_id"]] = user_cart
    await write_dict("carts.json", carts)
    return _calculate_totals(user_cart)


@router.delete("", response_model=CartOut)
async def clear_cart(current_user: dict = Depends(get_current_user)):
    carts = await read_dict("carts.json")
    carts[current_user["user_id"]] = []
    await write_dict("carts.json", carts)
    return _calculate_totals([])
