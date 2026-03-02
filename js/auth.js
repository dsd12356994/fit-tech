// Basic front-end auth handling: login, register, logout, user menu & profile modal

const Auth = (() => {
  const STORAGE_KEY = 'fittech_user_cache';

  function saveUserToLocal(user) {
    if (!user) return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  }

  function getUserFromLocal() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function clearUserLocal() {
    localStorage.removeItem(STORAGE_KEY);
  }

  function updateNavbarUser(user) {
    const navUsername = document.getElementById('navUsername');
    const heroUsername = document.getElementById('heroUsername');
    const initialsEl = document.getElementById('avatarInitials');
    if (!navUsername || !initialsEl) return;

    const name = user?.full_name || user?.username || 'Athlete';
    navUsername.textContent = name;
    if (heroUsername) heroUsername.textContent = name;
    const initials = name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join('');
    initialsEl.textContent = initials || 'FT';
  }

  async function bootstrapUser() {
    // 1st priority: server session
    try {
      const profile = await Api.getProfile();
      if (profile && profile.id) {
        saveUserToLocal(profile);
        updateNavbarUser(profile);
        return profile;
      }
    } catch {
      // ignore, fallback to local cache
    }

    const cached = getUserFromLocal();
    if (cached) {
      updateNavbarUser(cached);
      return cached;
    }
    return null;
  }

  function attachUserMenuHandlers() {
    const toggle = document.getElementById('userMenuToggle');
    const dropdown = document.getElementById('userDropdown');
    if (!toggle || !dropdown) return;

    toggle.addEventListener('click', () => {
      dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!dropdown.classList.contains('hidden') && !toggle.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
      }
    });
  }

  function attachProfileModalHandlers() {
    const openBtn = document.getElementById('openProfileModal');
    const closeBtn = document.getElementById('closeProfileModal');
    const cancelBtn = document.getElementById('cancelProfileChanges');
    const modal = document.getElementById('profileModal');
    const backdrop = modal?.querySelector('.modal-backdrop');
    const saveBtn = document.getElementById('saveProfileBtn');
    const form = document.getElementById('profileForm');
    if (!modal || !form) return;

    const open = async () => {
      console.log('Opening profile modal...');
      // 强制显示
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
      modal.style.visibility = 'visible';
      modal.style.opacity = '1';
      modal.style.pointerEvents = 'auto';
      
      try {
        const profile = await Api.getProfile();
        for (const [key, value] of Object.entries(profile || {})) {
          const el = form.querySelector(`[name="${key}"]`);
          if (el) el.value = value ?? '';
        }
      } catch {
        const cached = getUserFromLocal();
        if (cached) {
          for (const [key, value] of Object.entries(cached)) {
            const el = form.querySelector(`[name="${key}"]`);
            if (el) el.value = value ?? '';
          }
        }
      }
    };

    const close = () => {
      console.log('Closing profile modal...');
      // 强制隐藏
      modal.classList.add('hidden');
      modal.style.display = 'none';
      modal.style.visibility = 'hidden';
      modal.style.opacity = '0';
      modal.style.pointerEvents = 'none';
      console.log('Profile modal closed');
    };

    // 打开按钮
    openBtn && openBtn.addEventListener('click', open);
    
    // 关闭按钮（X）
    closeBtn && closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      close();
    });
    
    // Cancel 按钮
    cancelBtn && cancelBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      close();
    });
    
    // 点击背景关闭（但点击对话框内容时不关闭）
    modal.addEventListener('click', (e) => {
      // 如果点击的是模态框本身（背景）而不是对话框内容，则关闭
      if (e.target === modal || e.target === backdrop) {
        close();
      }
    });
    
    // 防止点击对话框内容时关闭
    const dialog = modal.querySelector('.modal-dialog');
    if (dialog) {
      dialog.addEventListener('click', (e) => {
        e.stopPropagation();
      });
    }
    
    // ESC 键关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        close();
      }
    });

    saveBtn &&
      saveBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // 设置加载状态
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        const data = Object.fromEntries(new FormData(form).entries());
        try {
          const updated = await Api.updateProfile(data);
          saveUserToLocal(updated);
          updateNavbarUser(updated);
          
          // 立即关闭模态框
          try {
            close();
          } catch (closeErr) {
            console.error('Error closing modal:', closeErr);
            // 强制关闭
            modal.classList.add('hidden');
            modal.style.display = 'none';
            modal.style.visibility = 'hidden';
            modal.style.opacity = '0';
            modal.style.pointerEvents = 'none';
          }
          
          // 显示成功消息
          const successMsg = document.createElement('div');
          successMsg.className = 'success-message';
          successMsg.textContent = '✓ Profile updated successfully!';
          successMsg.style.cssText = 'position: fixed; top: 80px; right: 20px; background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.2); animation: slideIn 0.3s ease-out;';
          document.body.appendChild(successMsg);
          setTimeout(() => {
            successMsg.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => successMsg.remove(), 300);
          }, 2500);
        } catch (err) {
          console.error('Failed to update profile:', err);
          alert(err.message || 'Failed to update profile');
          saveBtn.disabled = false;
          saveBtn.textContent = 'Save Changes';
        }
      });
  }

  function attachAuthForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    if (loginForm) {
      const loginError = document.getElementById('loginError');
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError && loginError.classList.add('hidden');
        const formData = Object.fromEntries(new FormData(loginForm).entries());
        try {
          const user = await Api.login(formData);
          saveUserToLocal(user);
          window.location.href = 'index.html';
        } catch (err) {
          if (loginError) {
            loginError.textContent = err.message || 'Login failed';
            loginError.classList.remove('hidden');
          } else {
            alert(err.message || 'Login failed');
          }
        }
      });
    }

    if (registerForm) {
      const regError = document.getElementById('registerError');
      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        regError && regError.classList.add('hidden');
        const data = Object.fromEntries(new FormData(registerForm).entries());
        try {
          const user = await Api.register(data);
          saveUserToLocal(user);
          window.location.href = 'index.html';
        } catch (err) {
          if (regError) {
            regError.textContent = err.message || 'Registration failed';
            regError.classList.remove('hidden');
          } else {
            alert(err.message || 'Registration failed');
          }
        }
      });
    }

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        try {
          await Api.logout();
        } catch {
          // ignore
        }
        clearUserLocal();
        window.location.href = 'login.html';
      });
    }
  }

  function attachThemeToggle() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
      document.body.classList.toggle('theme-default');
      // 可扩展暗黑/明亮主题，这里简单示例
    });
  }

  // 更新全局购物车数量
  async function updateGlobalCartCount() {
    try {
      const cart = await Api.getCart().catch(() => []);
      const totalQty = cart.reduce((sum, item) => sum + (parseInt(item.quantity) || 0), 0);
      const cartCountEls = document.querySelectorAll('#cartCount');
      cartCountEls.forEach(el => {
        if (el) el.textContent = String(totalQty);
      });
    } catch (err) {
      console.warn('Failed to update cart count:', err);
    }
  }

  async function init() {
    await bootstrapUser();
    attachUserMenuHandlers();
    attachProfileModalHandlers();
    attachAuthForms();
    attachThemeToggle();
    
    // 更新购物车数量（如果用户已登录）
    try {
      await Api.getProfile();
      updateGlobalCartCount();
    } catch {
      // 用户未登录，跳过
    }
  }

  document.addEventListener('DOMContentLoaded', init);

  return {
    getUserFromLocal,
    saveUserToLocal,
    updateNavbarUser,
  };
})();


