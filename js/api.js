// Simple API client wrapper around fetch.
// All actual后端接口地址基于 includes/config.php 中的 BASE_URL。

const Api = (() => {
  const base = FITTECH_CONFIG.BASE_URL.replace(/\/+$/, '');

  async function request(path, options = {}) {
    const url = `${base}/${path.replace(/^\/+/, '')}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const opts = {
      credentials: 'include',
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
    };

    try {
      const res = await fetch(url, opts);
      const isJson = res.headers.get('content-type')?.includes('application/json');
      if (!res.ok) {
        const payload = isJson ? await res.json().catch(() => ({})) : {};
        throw new Error(payload.error || `Request failed with status ${res.status}`);
      }
      return isJson ? res.json() : res.text();
    } catch (err) {
      console.error('API error:', err);
      throw err;
    }
  }

  // Auth
  function register(data) {
    // 后端对应: POST /api/auth/register.php
    return request('/api/auth/register.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  function login(data) {
    // 后端对应: POST /api/auth/login.php
    return request('/api/auth/login.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  function logout() {
    return request('/api/auth/logout.php', {
      method: 'POST',
    });
  }

  // User
  function getProfile() {
    return request('/api/user/profile.php');
  }

  function updateProfile(data) {
    return request('/api/user/update.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Workouts
  function logWorkout(data) {
    return request('/api/workouts/log.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  function getWorkoutStats() {
    return request('/api/workouts/stats.php');
  }

  function getRecentWorkouts(limit = 5) {
    const params = new URLSearchParams({ limit: String(limit) }).toString();
    return request(`/api/workouts/get.php?${params}`);
  }

  // Nutrition
  function getNutritionPlan() {
    return request('/api/nutrition/plan.php');
  }

  function logNutrition(data) {
    return request('/api/nutrition/log.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  function getTodayNutrition(dateStr) {
    const params = new URLSearchParams();
    if (dateStr) params.set('date', dateStr);
    const q = params.toString();
    const path = q ? `/api/nutrition/today.php?${q}` : '/api/nutrition/today.php';
    return request(path);
  }

  // Store
  function getProducts(params = '') {
    const query = params ? `?${params}` : '';
    return request(`/api/store/products.php${query}`);
  }

  function modifyCart(data) {
    return request('/api/store/cart.php', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  function getCart() {
    return request('/api/store/cart.php');
  }

  function checkout() {
    return request('/api/store/checkout.php', {
      method: 'POST',
    });
  }

  return {
    register,
    login,
    logout,
    getProfile,
    updateProfile,
    logWorkout,
    getWorkoutStats,
    getRecentWorkouts,
    getNutritionPlan,
    logNutrition,
    getTodayNutrition,
    getProducts,
    modifyCart,
    getCart,
    checkout,
  };
})();


