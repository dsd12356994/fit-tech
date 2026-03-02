// Store page: product listing, filters/search, cart, checkout (simulated)

const Store = (() => {
  const LOCAL_CART_KEY = 'fittech_cart_cache';

  function loadCartLocal() {
    try {
      const raw = localStorage.getItem(LOCAL_CART_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveCartLocal(cart) {
    localStorage.setItem(LOCAL_CART_KEY, JSON.stringify(cart));
  }

  // 从后端加载购物车
  async function loadCartFromServer() {
    try {
      const items = await Api.getCart();
      // 转换为前端格式
      const cart = items.map(item => ({
        id: item.product_id,
        name: item.name,
        price: parseFloat(item.price),
        quantity: parseInt(item.quantity)
      }));
      saveCartLocal(cart);
      return cart;
    } catch (err) {
      console.warn('Failed to load cart from server, using local cache:', err);
      return loadCartLocal();
    }
  }

  // 更新所有页面的购物车数量
  function updateGlobalCartCount() {
    const cart = loadCartLocal();
    const totalQty = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCountEls = document.querySelectorAll('#cartCount');
    cartCountEls.forEach(el => {
      if (el) el.textContent = String(totalQty);
    });
  }

  function renderCart(cart) {
    const listEl = document.getElementById('cartItemsList');
    const subtotalEl = document.getElementById('cartSubtotal');
    const cartCount = document.getElementById('cartCount');
    if (!listEl || !subtotalEl) return;

    if (!cart.length) {
      listEl.classList.add('empty-state');
      listEl.innerHTML = '<li>Your cart is empty. Add some gear to power up your training.</li>';
      subtotalEl.textContent = '$0.00';
      updateGlobalCartCount();
      return;
    }

    listEl.classList.remove('empty-state');
    let subtotal = 0;
    let totalQty = 0;
    listEl.innerHTML = cart
      .map((item) => {
        const line = item.price * item.quantity;
        subtotal += line;
        totalQty += item.quantity;
        return `
        <li>
          <div class="cart-item-row">
            <div>
              <div class="cart-item-name">${item.name}</div>
              <div class="muted small">$${item.price.toFixed(2)} × ${item.quantity}</div>
              <div class="cart-qty-controls">
                <button class="cart-qty-btn" data-action="dec" data-id="${item.id}" title="Decrease quantity">-</button>
                <span class="cart-qty-display">${item.quantity}</span>
                <button class="cart-qty-btn" data-action="inc" data-id="${item.id}" title="Increase quantity">+</button>
                <button class="cart-remove-btn" data-action="remove" data-id="${item.id}" title="Remove item">Remove</button>
              </div>
            </div>
            <div class="metric-value small">$${line.toFixed(2)}</div>
          </div>
        </li>
      `;
      })
      .join('');

    subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    updateGlobalCartCount();
  }

  function attachCartHandlers() {
    const listEl = document.getElementById('cartItemsList');
    if (!listEl) return;

    listEl.addEventListener('click', async (e) => {
      const btn = e.target.closest('button[data-action][data-id]');
      if (!btn) return;
      
      // 防止重复点击
      if (btn.disabled) return;
      btn.disabled = true;
      
      const id = Number(btn.dataset.id);
      const action = btn.dataset.action;
      let cart = loadCartLocal();
      const index = cart.findIndex((i) => i.id === id);
      if (index === -1) {
        btn.disabled = false;
        return;
      }
      const item = cart[index];
      let newQuantity = item.quantity;

      if (action === 'inc') {
        newQuantity = item.quantity + 1;
        item.quantity = newQuantity;
      } else if (action === 'dec') {
        newQuantity = Math.max(1, item.quantity - 1);
        item.quantity = newQuantity;
      } else if (action === 'remove') {
        newQuantity = 0;
        cart.splice(index, 1);
      }

      // 先更新UI（乐观更新）
      saveCartLocal(cart);
      renderCart(cart);

      // 同步到后端
      try {
        if (action === 'remove') {
          await Api.modifyCart({
            action: 'remove',
            product_id: id,
          });
        } else {
          await Api.modifyCart({
            action: 'update',
            product_id: id,
            quantity: newQuantity,
          });
        }
      } catch (err) {
        console.error('Failed to sync cart to server:', err);
        // 如果同步失败，重新从服务器加载
        await loadCartFromServer();
        renderCart(loadCartLocal());
      } finally {
        btn.disabled = false;
      }
    });
  }

  function attachAddToCartButtons() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.addEventListener('click', async (e) => {
      const btn = e.target.closest('.btn-add-to-cart');
      if (!btn) return;
      
      // 防止重复点击
      if (btn.disabled) return;
      btn.disabled = true;
      const originalText = btn.textContent;
      btn.textContent = 'Adding...';
      
      const id = Number(btn.dataset.id);
      const name = btn.dataset.name;
      const price = Number(btn.dataset.price);

      let cart = loadCartLocal();
      const existing = cart.find((i) => i.id === id);
      if (existing) {
        existing.quantity += 1;
      } else {
        cart.push({ id, name, price, quantity: 1 });
      }
      
      // 乐观更新UI
      saveCartLocal(cart);
      renderCart(cart);

      // 同步到后端
      try {
        await Api.modifyCart({
          action: 'add',
          product_id: id,
          quantity: 1,
        });
        btn.textContent = '✓ Added!';
        setTimeout(() => {
          btn.textContent = originalText;
          btn.disabled = false;
        }, 1000);
      } catch (err) {
        console.error('Failed to add to cart:', err);
        btn.textContent = originalText;
        btn.disabled = false;
        // 如果同步失败，恢复原状态
        await loadCartFromServer();
        renderCart(loadCartLocal());
        alert('Failed to add item to cart. Please try again.');
      }
    });
  }

  function renderProducts(products) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;
    if (!products.length) {
      grid.innerHTML = '<div class="empty-state full-width">No products found.</div>';
      return;
    }

    grid.innerHTML = products
      .map((p) => {
        const badgeMap = {
          bestseller: 'badge-bestseller',
          new: 'badge-new',
          sale: 'badge-sale',
        };
        const badgeClass = badgeMap[p.badge] || '';
        const badgeLabel =
          p.badge === 'bestseller'
            ? 'BESTSELLER'
            : p.badge === 'new'
            ? 'NEW'
            : p.badge === 'sale'
            ? 'SALE'
            : '';
        return `
        <article class="product-card">
          ${badgeLabel ? `<span class="product-badge ${badgeClass}">${badgeLabel}</span>` : ''}
          <h3 class="product-title">${p.name}</h3>
          <p class="muted small">${p.description || ''}</p>
          <div class="product-price-row">
            <span class="product-price-current">$${Number(p.price).toFixed(2)}</span>
            ${
              p.original_price
                ? `<span class="product-price-original">$${Number(p.original_price).toFixed(2)}</span>`
                : ''
            }
          </div>
          <button
            class="btn btn-primary small btn-add-to-cart"
            data-id="${p.id}"
            data-name="${p.name}"
            data-price="${p.price}"
          >
            Add to Cart
          </button>
        </article>
      `;
      })
      .join('');
  }

  async function loadProductsWithFallback() {
    try {
      const products = await Api.getProducts();
      const productsArray = products || [];
      renderProducts(productsArray);
      return productsArray; // 确保返回产品数组
    } catch (err) {
      console.warn('Failed to load products from server, using fallback:', err);
      // fallback to示例数据
      const sample = [
        {
          id: 1,
          name: 'Protein Powder',
          description: 'Premium whey protein isolate for muscle recovery',
          category: 'supplements',
          price: 39.99,
          original_price: 49.99,
          badge: 'bestseller',
        },
        {
          id: 2,
          name: 'Adjustable Dumbbells',
          description: '5-50 lbs adjustable weight set',
          category: 'equipment',
          price: 129.99,
          original_price: null,
          badge: 'new',
        },
        {
          id: 3,
          name: 'Performance T-Shirt',
          description: 'Moisture-wicking fabric for intense workouts',
          category: 'apparel',
          price: 24.99,
          original_price: null,
          badge: 'none',
        },
        {
          id: 4,
          name: 'Fitness Tracker',
          description: 'Track workouts, heart rate, and sleep',
          category: 'accessories',
          price: 89.99,
          original_price: 119.99,
          badge: 'sale',
        },
      ];
      renderProducts(sample);
      return sample;
    }
  }

  function attachFilters(productsArray) {
    const tabs = document.getElementById('productCategoryTabs');
    const searchInput = document.getElementById('productSearchInput');
    if (!tabs || !searchInput) return;

    // 直接使用传入的产品数组，不再依赖Promise
    let cachedProducts = Array.isArray(productsArray) ? productsArray : [];

    function applyFilters() {
      // 如果缓存为空，尝试重新加载
      if (!cachedProducts.length) {
        console.warn('No cached products, reloading...');
        loadProductsWithFallback().then((products) => {
          cachedProducts = Array.isArray(products) ? products : [];
          applyFilters();
        });
        return;
      }

      const activeTab = tabs.querySelector('.pill-tab.active');
      const category = activeTab ? activeTab.dataset.category : '';
      const query = (searchInput.value || '').toLowerCase().trim();

      const filtered = cachedProducts.filter((p) => {
        const matchCategory = !category || p.category === category;
        const matchQuery =
          !query ||
          (p.name || '').toLowerCase().includes(query) ||
          ((p.description || '').toLowerCase().includes(query));
        return matchCategory && matchQuery;
      });
      
      console.log(`Filtering: category="${category}", query="${query}", found ${filtered.length} products`);
      renderProducts(filtered);
    }

    tabs.addEventListener('click', (e) => {
      const btn = e.target.closest('.pill-tab');
      if (!btn) return;
      Array.from(tabs.querySelectorAll('.pill-tab')).forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      applyFilters();
    });

    searchInput.addEventListener('input', applyFilters);
    
    // 初始应用筛选
    applyFilters();
  }

  function attachCheckout() {
    const checkoutBtn = document.getElementById('checkoutBtn');
    const modal = document.getElementById('checkoutModal');
    const backdrop = modal?.querySelector('.modal-backdrop');
    const closeBtn = document.getElementById('closeCheckoutModal');
    const cancelBtn = document.getElementById('cancelCheckout');
    const confirmBtn = document.getElementById('confirmCheckout');
    const itemCountEl = document.getElementById('checkoutItemCount');
    const totalEl = document.getElementById('checkoutTotal');
    const cartItemsEl = document.getElementById('checkoutItemsList');
    const subtotalEl = document.getElementById('cartSubtotal');
    if (!checkoutBtn || !modal) return;

    function open() {
      const cart = loadCartLocal();
      if (!cart.length) {
        alert('Your cart is empty. Add some items before checkout.');
        return;
      }
      
      let count = 0;
      let total = 0;
      const itemsHtml = cart.map(item => {
        const lineTotal = item.price * item.quantity;
        count += item.quantity;
        total += lineTotal;
        return `
          <div class="checkout-item-row">
            <span>${item.name} × ${item.quantity}</span>
            <span>$${lineTotal.toFixed(2)}</span>
          </div>
        `;
      }).join('');
      
      itemCountEl.textContent = String(count);
      totalEl.textContent = `$${total.toFixed(2)}`;
      if (cartItemsEl) {
        cartItemsEl.innerHTML = itemsHtml;
      }
      
      // 强制显示模态框
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
      modal.style.visibility = 'visible';
      modal.style.opacity = '1';
      modal.style.pointerEvents = 'auto';
    }

    function close() {
      modal.classList.add('hidden');
      modal.style.display = 'none';
      modal.style.visibility = 'hidden';
      modal.style.opacity = '0';
      modal.style.pointerEvents = 'none';
    }

    checkoutBtn.addEventListener('click', open);
    closeBtn && closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      close();
    });
    cancelBtn && cancelBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      close();
    });
    
    // 点击背景关闭
    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target === backdrop) {
        close();
      }
    });
    
    // ESC键关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        close();
      }
    });

    confirmBtn &&
      confirmBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        if (confirmBtn.disabled) return;
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Processing...';
        
        const cart = loadCartLocal();
        if (!cart.length) {
          alert('Your cart is empty.');
          confirmBtn.disabled = false;
          confirmBtn.textContent = 'CONFIRM ORDER';
          return;
        }

        try {
          // 调用后端结算API
          await Api.checkout();
          
          // 清空本地购物车
          localStorage.removeItem(LOCAL_CART_KEY);
          const emptyCart = [];
          saveCartLocal(emptyCart);
          renderCart(emptyCart);
          
          // 显示成功消息
          const successMsg = document.createElement('div');
          successMsg.className = 'success-message';
          successMsg.textContent = '✓ Order confirmed successfully!';
          successMsg.style.cssText = 'position: fixed; top: 80px; right: 20px; background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.2); animation: slideIn 0.3s ease-out;';
          document.body.appendChild(successMsg);
          setTimeout(() => {
            successMsg.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => successMsg.remove(), 300);
          }, 3000);
          
          close();
        } catch (err) {
          console.error('Checkout failed:', err);
          alert(err.message || 'Failed to process order. Please try again.');
        } finally {
          confirmBtn.disabled = false;
          confirmBtn.textContent = 'CONFIRM ORDER';
        }
      });
  }

  async function init() {
    // 先从服务器加载购物车
    await loadCartFromServer();
    const cart = loadCartLocal();
    renderCart(cart);
    
    attachCartHandlers();
    attachAddToCartButtons();
    
    // 加载产品并等待完成
    try {
      const products = await loadProductsWithFallback();
      console.log('Products loaded:', products?.length || 0);
      // 直接传递产品数组给筛选函数
      attachFilters(products || []);
    } catch (err) {
      console.error('Failed to load products:', err);
      // 即使失败也设置筛选（使用空数组）
      attachFilters([]);
    }
    
    attachCheckout();
    
    // 定期同步购物车（每30秒）
    setInterval(async () => {
      await loadCartFromServer();
      renderCart(loadCartLocal());
    }, 30000);
  }

  document.addEventListener('DOMContentLoaded', init);

  return {};
})();


