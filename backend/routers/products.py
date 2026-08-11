"""
Products router — list, filter, search, and single product endpoints.
"""
import math
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query

from models.schemas import ProductOut, ProductListResponse
from utils.file_store import read_json

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = Query(None, description="men | women | accessories"),
    subcategory: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    size: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    is_new: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    has_discount: Optional[bool] = Query(None),
    sort: Optional[str] = Query("featured", description="featured | price_asc | price_desc | newest | rating"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=48),
):
    products = await read_json("products.json")

    # ── Filters ────────────────────────────────────────────────────────────
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]
    if subcategory:
        products = [p for p in products if p.get("subcategory", "").lower() == subcategory.lower()]
    if search:
        q = search.lower()
        products = [
            p for p in products
            if q in p["name"].lower()
            or q in p["description"].lower()
            or any(q in t for t in p.get("tags", []))
        ]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]
    if size:
        products = [p for p in products if size in p.get("sizes", [])]
    if color:
        products = [p for p in products if any(color.lower() in c.lower() for c in p.get("colors", []))]
    if is_new is not None:
        products = [p for p in products if p.get("is_new") == is_new]
    if is_featured is not None:
        products = [p for p in products if p.get("is_featured") == is_featured]
    if has_discount is not None:
        if has_discount:
            products = [p for p in products if p.get("discount_pct") is not None]
        else:
            products = [p for p in products if p.get("discount_pct") is None]

    # ── Sort ───────────────────────────────────────────────────────────────
    if sort == "price_asc":
        products.sort(key=lambda p: p["price"])
    elif sort == "price_desc":
        products.sort(key=lambda p: p["price"], reverse=True)
    elif sort == "newest":
        products.sort(key=lambda p: p.get("is_new", False), reverse=True)
    elif sort == "rating":
        products.sort(key=lambda p: p.get("rating", 0), reverse=True)
    # default: featured first
    else:
        products.sort(key=lambda p: (p.get("is_featured", False), p.get("rating", 0)), reverse=True)

    total = len(products)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    paginated = products[start: start + page_size]

    return ProductListResponse(
        products=[ProductOut(**p) for p in paginated],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: str):
    products = await read_json("products.json")
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut(**product)

