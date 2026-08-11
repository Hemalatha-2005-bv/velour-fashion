/**
 * VELOUR — UI Utilities
 * Toast notifications, loaders, scroll reveal, modal helpers
 */

// ── Toast ────────────────────────────────────────────────────────
const Toast = {
  icons: {
    success: `<svg class="toast-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`,
    error:   `<svg class="toast-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
    info:    `<svg class="toast-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 110 20A10 10 0 0112 2z"/></svg>`,
  },
  show(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `${this.icons[type]}<span class="toast-msg">${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      toast.addEventListener('animationend', () => toast.remove());
    }, duration);
  },
  success(msg) { this.show(msg, 'success'); },
  error(msg)   { this.show(msg, 'error'); },
  info(msg)    { this.show(msg, 'info'); },
};

// ── Scroll Reveal ────────────────────────────────────────────────
function initReveal() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } });
  }, { threshold: 0.12 });
  els.forEach(el => io.observe(el));
}

// ── Header scroll effect ──────────────────────────────────────────
function initHeader() {
  const header = document.querySelector('.header');
  if (!header) return;
  const update = () => header.classList.toggle('scrolled', window.scrollY > 20);
  update();
  window.addEventListener('scroll', update, { passive: true });
}

// ── Mobile menu ───────────────────────────────────────────────────
function initMobileMenu() {
  const btn  = document.getElementById('mobile-menu-btn');
  const nav  = document.getElementById('mobile-nav');
  const close= document.getElementById('mobile-nav-close');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => nav.classList.add('open'));
  close?.addEventListener('click', () => nav.classList.remove('open'));
}

// ── Render star rating ────────────────────────────────────────────
function renderStars(rating) {
  let html = '<div class="stars">';
  for (let i = 1; i <= 5; i++) {
    const filled = i <= Math.round(rating);
    html += `<svg viewBox="0 0 20 20" fill="${filled ? '#F59E0B' : 'none'}" stroke="#F59E0B" stroke-width="1.5"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>`;
  }
  return html + '</div>';
}

// ── Product card renderer ─────────────────────────────────────────
function renderProductCard(product) {
  const template = document.getElementById('product-card-template');
  if (!template) return document.createElement('div');
  
  const clone = template.content.cloneNode(true);
  const root = clone.querySelector('.product-card');
  root.dataset.id = product.id;
  
  const img = clone.querySelector('.p-img');
  img.src = product.images[0] || 'images/product_tshirt.png';
  img.alt = product.name;
  img.onerror = function() { this.src = 'images/product_tshirt.png'; };
  
  const badges = clone.querySelector('.p-badges');
  if (product.is_new) badges.innerHTML += `<span class="badge badge-new">New</span>`;
  if (product.discount_pct) badges.innerHTML += `<span class="badge badge-sale">-${product.discount_pct}%</span>`;
  
  clone.querySelector('.p-wishlist').dataset.id = product.id;
  clone.querySelector('.p-cat').textContent = `${product.category} · ${product.subcategory || ''}`;
  clone.querySelector('.p-name').textContent = product.name;
  
  clone.querySelector('.p-stars').innerHTML = renderStars(product.rating);
  clone.querySelector('.p-reviews').textContent = `(${product.review_count})`;
  
  clone.querySelector('.p-price').textContent = `$${product.price.toFixed(2)}`;
  if (product.original_price) {
    const orig = clone.querySelector('.p-orig');
    orig.style.display = 'inline';
    orig.textContent = `$${product.original_price.toFixed(2)}`;
  }
  
  const addBtn = clone.querySelector('.p-add');
  addBtn.dataset.id = product.id;
  addBtn.dataset.size = product.sizes[0] || '';
  addBtn.dataset.color = product.colors[0] || '';
  
  return clone;
}

// ── Cart state & drawer ───────────────────────────────────────────
let cartData = null;

async function refreshCart() {
  if (!Auth.isLoggedIn()) { updateCartBadge(0); return; }
  try {
    cartData = await api.getCart();
    updateCartBadge(cartData.item_count || 0);
    renderCartDrawer();
  } catch(e) { console.warn('Cart refresh failed', e); }
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(b => {
    b.textContent = count;
    b.style.display = count > 0 ? 'flex' : 'none';
  });
}

function renderCartDrawer() {
  const body = document.getElementById('cart-drawer-body');
  const footer = document.getElementById('cart-drawer-footer');
  if (!body) return;
  body.innerHTML = ''; // Clear previous

  if (!cartData || !cartData.items || cartData.items.length === 0) {
    const emptyDiv = document.createElement('div');
    emptyDiv.className = 'empty-state';
    emptyDiv.innerHTML = `
      <div class="empty-state__icon"><svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg></div>
      <p class="empty-state__title">Your cart is empty</p>
      <p class="empty-state__text">Add some items to get started</p>
      <a href="shop.html" class="btn btn-primary btn-sm">Shop Now</a>
    `;
    body.appendChild(emptyDiv);
    if (footer) footer.innerHTML = '';
    return;
  }

  const template = document.getElementById('cart-item-template');
  cartData.items.forEach(item => {
    if (!template) return;
    const clone = template.content.cloneNode(true);
    
    const img = clone.querySelector('.ci-img');
    img.src = item.image;
    img.alt = item.name;
    img.onerror = function() { this.src = 'images/product_tshirt.png'; };
    
    clone.querySelector('.ci-name').textContent = item.name;
    clone.querySelector('.ci-meta').textContent = `${item.size} · ${item.color}`;
    
    const incBtn = clone.querySelector('.ci-qty-inc');
    incBtn.dataset.id = item.item_id;
    incBtn.dataset.qty = item.quantity;
    
    const decBtn = clone.querySelector('.ci-qty-dec');
    decBtn.dataset.id = item.item_id;
    decBtn.dataset.qty = item.quantity;
    
    clone.querySelector('.ci-qty-val').textContent = item.quantity;
    clone.querySelector('.ci-price').textContent = `$${item.subtotal.toFixed(2)}`;
    
    clone.querySelector('.ci-remove').dataset.id = item.item_id;
    
    body.appendChild(clone);
  });

  if (footer) {
    const freeShipping = cartData.shipping === 0;
    footer.innerHTML = `
      <div class="summary-row"><span>Subtotal</span><span>$${cartData.subtotal.toFixed(2)}</span></div>
      <div class="summary-row"><span>Shipping</span><span>${freeShipping ? '<span class="text-green">Free</span>' : '$' + cartData.shipping.toFixed(2)}</span></div>
      ${!freeShipping ? `<p style="font-size:.75rem;color:var(--text-muted);margin:.25rem 0 .75rem">Add $${(100 - cartData.subtotal).toFixed(2)} more for free shipping</p>` : ''}
      <div class="summary-row total"><span>Total</span><span>$${cartData.total.toFixed(2)}</span></div>
      <a href="checkout.html" class="btn btn-primary btn-full" style="margin-top:1rem">Proceed to Checkout</a>
      <a href="cart.html" class="btn btn-secondary btn-full" style="margin-top:.5rem">View Full Cart</a>`;
  }
}

function openCartDrawer() {
  document.getElementById('cart-drawer')?.classList.add('open');
  document.getElementById('drawer-overlay')?.classList.add('open');
  document.body.style.overflow = 'hidden';
  refreshCart();
}
function closeCartDrawer() {
  document.getElementById('cart-drawer')?.classList.remove('open');
  document.getElementById('drawer-overlay')?.classList.remove('open');
  document.body.style.overflow = '';
}

async function quickAddToCart(productId, size, color) {
  if (!Auth.isLoggedIn()) { window.location.href = 'auth.html'; return; }
  try {
    await api.addToCart({ product_id: productId, size, color, quantity: 1 });
    await refreshCart();
    openCartDrawer();
    Toast.success('Added to cart!');
  } catch(e) { Toast.error(e.message || 'Failed to add item'); }
}

async function updateCartQty(itemId, qty) {
  try {
    cartData = await api.updateCartItem(itemId, qty);
    updateCartBadge(cartData.item_count || 0);
    renderCartDrawer();
  } catch(e) { Toast.error(e.message); }
}

async function removeCartItem(itemId) {
  try {
    cartData = await api.removeCartItem(itemId);
    updateCartBadge(cartData.item_count || 0);
    renderCartDrawer();
    Toast.info('Item removed');
  } catch(e) { Toast.error(e.message); }
}

// ── Wishlist toggle ───────────────────────────────────────────────
async function toggleWishlist(productId, btn) {
  if (!Auth.isLoggedIn()) { window.location.href = 'auth.html'; return; }
  try {
    const data = await api.toggleWishlist(productId);
    const inList = data.product_ids.includes(productId);
    btn?.classList.toggle('active', inList);
    Toast.success(inList ? 'Added to wishlist' : 'Removed from wishlist');
  } catch(e) { Toast.error(e.message); }
}

// ── Render header auth state ──────────────────────────────────────
function renderHeaderAuth() {
  const authBtns = document.getElementById('header-auth');
  if (!authBtns) return;
  if (Auth.isLoggedIn()) {
    const u = Auth.getUser();
    authBtns.innerHTML = `
      <a href="wishlist.html" class="icon-btn hide-mobile" title="Wishlist">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></svg>
      </a>
      <a href="account.html" class="icon-btn hide-mobile" title="Account">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
      </a>`;
  } else {
    authBtns.innerHTML = `<a href="auth.html" class="btn btn-secondary btn-sm">Sign In</a>`;
  }
}

// ── Init ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initMobileMenu();
  initReveal();
  renderHeaderAuth();
  refreshCart();

  // Cart drawer toggle
  document.getElementById('cart-btn')?.addEventListener('click', openCartDrawer);
  document.getElementById('drawer-overlay')?.addEventListener('click', closeCartDrawer);
  document.getElementById('cart-drawer-close')?.addEventListener('click', closeCartDrawer);

  // Re-render on auth change
  window.addEventListener('auth:changed', () => { renderHeaderAuth(); refreshCart(); });

  // ── Global Event Delegation ──
  document.addEventListener('click', (e) => {
    // Product Card Navigation
    const card = e.target.closest('.product-card');
    if (card && !e.target.closest('button')) {
      window.location.href = `product.html?id=${card.dataset.id}`;
    }

    // Quick Add
    const addBtn = e.target.closest('.p-add');
    if (addBtn) {
      quickAddToCart(addBtn.dataset.id, addBtn.dataset.size, addBtn.dataset.color);
    }

    // Wishlist
    const wishBtn = e.target.closest('.wishlist-toggle');
    if (wishBtn) {
      toggleWishlist(wishBtn.dataset.id, wishBtn);
    }

    // Cart Qty Adjust
    const incBtn = e.target.closest('.ci-qty-inc');
    if (incBtn) updateCartQty(incBtn.dataset.id, parseInt(incBtn.dataset.qty) + 1);
    
    const decBtn = e.target.closest('.ci-qty-dec');
    if (decBtn) updateCartQty(decBtn.dataset.id, parseInt(decBtn.dataset.qty) - 1);

    // Cart Remove
    const rmBtn = e.target.closest('.ci-remove');
    if (rmBtn) removeCartItem(rmBtn.dataset.id);
  });
});

window.Toast = Toast;
window.renderProductCard = renderProductCard;
window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;
window.quickAddToCart = quickAddToCart;
window.updateCartQty = updateCartQty;
window.removeCartItem = removeCartItem;
window.toggleWishlist = toggleWishlist;
window.refreshCart = refreshCart;
window.renderStars = renderStars;
window.initReveal = initReveal;
