"""
Wishlist router — toggle, list wishlist items.
"""
from fastapi import APIRouter, Depends

from models.schemas import WishlistToggle, WishlistOut, ProductOut
from middleware.auth import get_current_user
from utils.file_store import read_json, read_dict, write_dict

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistOut)
async def get_wishlist(current_user: dict = Depends(get_current_user)):
    wishlists = await read_dict("wishlists.json")
    product_ids = wishlists.get(current_user["user_id"], [])
    all_products = await read_json("products.json")
    products = [ProductOut(**p) for p in all_products if p["id"] in product_ids]
    return WishlistOut(product_ids=product_ids, products=products)


@router.post("", response_model=WishlistOut)
async def toggle_wishlist(data: WishlistToggle, current_user: dict = Depends(get_current_user)):
    wishlists = await read_dict("wishlists.json")
    user_wishlist = wishlists.get(current_user["user_id"], [])

    if data.product_id in user_wishlist:
        user_wishlist.remove(data.product_id)
    else:
        user_wishlist.append(data.product_id)

    wishlists[current_user["user_id"]] = user_wishlist
    await write_dict("wishlists.json", wishlists)

    all_products = await read_json("products.json")
    products = [ProductOut(**p) for p in all_products if p["id"] in user_wishlist]
    return WishlistOut(product_ids=user_wishlist, products=products)
