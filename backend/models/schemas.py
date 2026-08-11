"""
Pydantic models for request/response validation and serialization.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum


# ── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Products ─────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    subcategory: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    discount_pct: Optional[int] = None
    description: str
    images: List[str]
    sizes: List[str]
    colors: List[str]
    stock: int
    rating: float
    review_count: int
    tags: List[str]
    is_new: bool
    is_featured: bool


class ProductListResponse(BaseModel):
    products: List[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Cart ─────────────────────────────────────────────────────────────────────

class CartItemAdd(BaseModel):
    product_id: str
    size: str
    color: str
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    item_id: str
    product_id: str
    name: str
    image: str
    price: float
    size: str
    color: str
    quantity: int
    subtotal: float


class CartOut(BaseModel):
    items: List[CartItemOut]
    subtotal: float
    shipping: float
    total: float
    item_count: int


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistToggle(BaseModel):
    product_id: str


class WishlistOut(BaseModel):
    product_ids: List[str]
    products: List[ProductOut]


# ── Orders ────────────────────────────────────────────────────────────────────

class Address(BaseModel):
    full_name: str
    email: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    country: str


class PaymentInfo(BaseModel):
    method: str = "card"
    card_last4: Optional[str] = None


class OrderCreate(BaseModel):
    shipping_address: Address
    payment_info: PaymentInfo
    promo_code: Optional[str] = None


class OrderItemOut(BaseModel):
    product_id: str
    name: str
    image: str
    price: float
    size: str
    color: str
    quantity: int
    subtotal: float


class OrderOut(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemOut]
    shipping_address: Address
    payment_info: PaymentInfo
    subtotal: float
    shipping: float
    discount: float
    total: float
    status: str
    created_at: str
    estimated_delivery: str
