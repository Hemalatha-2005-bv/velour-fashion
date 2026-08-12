/**
 * VELOUR — Centralized API Client
 * All backend calls go through this module.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : (window.location.hostname.includes('onrender.com') ? '' : 'https://velour-fashion.onrender.com');

function getToken() {
  return localStorage.getItem('velour_token');
}

async function request(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, options);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || `Request failed (${res.status})`);
  }
  return data;
}

const api = {
  // Products
  getProducts: (params = {}) => {
    const q = new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([,v]) => v !== null && v !== undefined && v !== '')));
    return request('GET', `/api/products?${q}`);
  },
  getProduct: (id) => request('GET', `/api/products/${id}`),

  // Auth
  register: (data) => request('POST', '/api/auth/register', data),
  login:    (data) => request('POST', '/api/auth/login', data),

  // Cart
  getCart:       ()              => request('GET',    '/api/cart'),
  addToCart:     (data)          => request('POST',   '/api/cart', data),
  updateCartItem:(itemId, qty)   => request('PUT',    `/api/cart/${itemId}`, { quantity: qty }),
  removeCartItem:(itemId)        => request('DELETE', `/api/cart/${itemId}`),
  clearCart:     ()              => request('DELETE', '/api/cart'),

  // Wishlist
  getWishlist:     ()   => request('GET',  '/api/wishlist'),
  toggleWishlist:  (id) => request('POST', '/api/wishlist', { product_id: id }),

  // Orders
  placeOrder:  (data) => request('POST', '/api/orders', data),
  getOrders:   ()     => request('GET',  '/api/orders'),
  getOrder:    (id)   => request('GET',  `/api/orders/${id}`),
};

window.api = api;
