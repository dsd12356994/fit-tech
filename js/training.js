// Training page: nutrition plan, quick workout log, food search + logs, video links

const Training = (() => {
  const LOCAL_FOOD_KEY = 'fittech_food_logs';
  const LOCAL_VIDEOS_KEY = 'fittech_training_videos';

  const sampleFoods = [
    { name: 'Chicken Breast (100g)', calories: 165, protein: 31, carbs: 0, fats: 3.6 },
    { name: 'Oatmeal (40g)', calories: 150, protein: 5, carbs: 27, fats: 2.5 },
    { name: 'Greek Yogurt (150g)', calories: 130, protein: 13, carbs: 5, fats: 4 },
    { name: 'Apple (1 medium)', calories: 95, protein: 0.5, carbs: 25, fats: 0.3 },
    { name: 'Almonds (30g)', calories: 174, protein: 6, carbs: 6, fats: 15 },
  ];

  function loadLocalFoods() {
    try {
      const raw = localStorage.getItem(LOCAL_FOOD_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveLocalFoods(list) {
    localStorage.setItem(LOCAL_FOOD_KEY, JSON.stringify(list));
  }

  async function renderTodayFoods() {
    const listEl = document.getElementById('todayNutritionList');
    const totalEl = document.getElementById('todayTotals');
    if (!listEl || !totalEl) return;
    const today = new Date().toISOString().slice(0, 10);

    // 优先从后端加载
    try {
      const data = await Api.getTodayNutrition(today);
      const items = data?.items || [];
      const totals = data?.totals || { calories: 0, protein: 0, carbs: 0, fats: 0 };

      if (!items.length) {
        listEl.classList.add('empty-state');
        listEl.innerHTML = '<li>No foods logged yet. Add from the search on the left.</li>';
      } else {
        listEl.classList.remove('empty-state');
        listEl.innerHTML = items
          .map(
            (f) =>
              `<li>${f.meal_type.toUpperCase()} • ${f.food_name} • ${f.calories} kcal • ${f.protein}g P • ${f.carbs}g C • ${f.fats}g F</li>`,
          )
          .join('');
      }

      totalEl.textContent = `${totals.calories} kcal • ${totals.protein}g P • ${totals.carbs}g C • ${totals.fats}g F`;
      return;
    } catch (err) {
      console.warn('Failed to load today nutrition from API, falling back to local cache.', err);
    }

    // 后端不可用时，回退到本地存储
    const all = loadLocalFoods();
    const todays = all.filter((item) => item.log_date === today);

    if (!todays.length) {
      listEl.classList.add('empty-state');
      listEl.innerHTML = '<li>No foods logged yet. Add from the search on the left.</li>';
      totalEl.textContent = '0 kcal • 0g P • 0g C • 0g F';
      return;
    }

    listEl.classList.remove('empty-state');
    listEl.innerHTML = todays
      .map(
        (f) =>
          `<li>${f.meal_type.toUpperCase()} • ${f.food_name} • ${f.calories} kcal • ${f.protein}g P • ${
            f.carbs
          }g C • ${f.fats}g F</li>`,
      )
      .join('');

    const totals = todays.reduce(
      (acc, f) => {
        acc.calories += f.calories;
        acc.protein += f.protein;
        acc.carbs += f.carbs;
        acc.fats += f.fats;
        return acc;
      },
      { calories: 0, protein: 0, carbs: 0, fats: 0 },
    );
    totalEl.textContent = `${totals.calories} kcal • ${totals.protein}g P • ${totals.carbs}g C • ${totals.fats}g F`;
  }

  function attachFoodSearch() {
    const input = document.getElementById('foodSearchInput');
    const listEl = document.getElementById('foodResultsList');
    const tabs = document.getElementById('foodFilterTabs');
    if (!input || !listEl || !tabs) return;

    let activeMealType = 'all';

    function renderList(query = '') {
      listEl.classList.remove('empty-state');
      const q = query.toLowerCase();
      const filtered = sampleFoods.filter((f) => f.name.toLowerCase().includes(q));
      if (!filtered.length) {
        listEl.classList.add('empty-state');
        listEl.innerHTML = '<li>No matching foods found. Try another keyword.</li>';
        return;
      }

      listEl.innerHTML = filtered
        .map(
          (f) =>
            `<li data-name="${f.name}" data-calories="${f.calories}" data-protein="${f.protein}" data-carbs="${f.carbs}" data-fats="${f.fats}">${f.name} • ${f.calories} kcal</li>`,
        )
        .join('');
    }

    input.addEventListener('input', () => renderList(input.value));

    tabs.addEventListener('click', (e) => {
      const btn = e.target.closest('.pill-tab');
      if (!btn) return;
      activeMealType = btn.dataset.type || 'all';
      Array.from(tabs.querySelectorAll('.pill-tab')).forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
    });

    listEl.addEventListener('click', async (e) => {
      const li = e.target.closest('li[data-name]');
      if (!li) return;
      const mealType = activeMealType === 'all' ? 'snack' : activeMealType;
      const payload = {
        meal_type: mealType,
        food_name: li.dataset.name,
        calories: Number(li.dataset.calories),
        protein: Number(li.dataset.protein),
        carbs: Number(li.dataset.carbs),
        fats: Number(li.dataset.fats),
      };

      try {
        await Api.logNutrition(payload);
      } catch {
        // 如果后端未完成，则先写入本地
        const all = loadLocalFoods();
        all.push({
          ...payload,
          log_date: new Date().toISOString().slice(0, 10),
        });
        saveLocalFoods(all);
      }
      renderTodayFoods();
    });

    renderList();
  }

  function attachGeneratePlan() {
    const btn = document.getElementById('generatePlanBtn');
    const caloriesEl = document.getElementById('planCalories');
    const proteinEl = document.getElementById('planProtein');
    const carbsEl = document.getElementById('planCarbs');
    const fatsEl = document.getElementById('planFats');
    const mealsList = document.getElementById('planMealsList');
    if (!btn || !caloriesEl) return;

    btn.addEventListener('click', async () => {
      try {
        const plan = await Api.getNutritionPlan();
        caloriesEl.textContent = `${plan.calories} kcal`;
        proteinEl.textContent = `${plan.protein} g`;
        carbsEl.textContent = `${plan.carbs} g`;
        fatsEl.textContent = `${plan.fats} g`;
        if (Array.isArray(plan.meals) && plan.meals.length) {
          mealsList.classList.remove('empty-state');
          mealsList.innerHTML = plan.meals
            .map((m) => `<li>${m.meal_type.toUpperCase()} • ${m.description} • ${m.calories} kcal</li>`)
            .join('');
        }
      } catch {
        // 如果后端未准备好，根据前端规则做一个简易方案
        const user = Auth.getUserFromLocal();
        const weight = Number(user?.weight) || 70;
        const goal = user?.fitness_goal || 'maintenance';
        let baseCalories;
        let protein;
        if (goal === 'muscle_gain') {
          protein = weight * 2;
          baseCalories = 2500 + 500;
        } else if (goal === 'fat_loss') {
          protein = weight * 2;
          baseCalories = 2200 - 500;
        } else if (goal === 'endurance') {
          protein = weight * 1.6;
          baseCalories = 2600;
        } else {
          protein = weight * 1.6;
          baseCalories = 2300;
        }
        const fats = Math.round((0.25 * baseCalories) / 9);
        const carbs = Math.round((baseCalories - protein * 4 - fats * 9) / 4);

        caloriesEl.textContent = `${baseCalories} kcal`;
        proteinEl.textContent = `${Math.round(protein)} g`;
        carbsEl.textContent = `${carbs} g`;
        fatsEl.textContent = `${fats} g`;

        mealsList.classList.remove('empty-state');
        mealsList.innerHTML = `
          <li>BREAKFAST • Oatmeal + Greek yogurt + berries • ~600 kcal</li>
          <li>LUNCH • Chicken breast, rice & veggies • ~800 kcal</li>
          <li>DINNER • Salmon, potatoes & salad • ~800 kcal</li>
          <li>SNACKS • Nuts & fruit • ~300 kcal</li>
        `;
      }
    });
  }

  function attachQuickWorkout() {
    const form = document.getElementById('quickWorkoutForm');
    const logBtn = document.getElementById('logWorkoutTrainingBtn');
    const durationInput = document.getElementById('qwDuration');
    const caloriesInput = document.getElementById('qwCalories');
    const typeSelect = document.getElementById('qwType');
    if (!form || !logBtn) return;

    const MET_MAP = {
      strength: 6,
      cardio: 7,
      hiit: 9,
      yoga: 3,
      other: 5,
    };

    function updateCaloriesEstimate() {
      const user = Auth.getUserFromLocal();
      const weight = Number(user?.weight) || 70;
      const durationMin = Number(durationInput.value) || 0;
      const type = typeSelect.value || 'other';
      const met = MET_MAP[type] || 5;
      const hours = durationMin / 60;
      const cals = Math.round(met * weight * hours);
      caloriesInput.value = cals || '';
    }

    durationInput && durationInput.addEventListener('input', updateCaloriesEstimate);
    typeSelect && typeSelect.addEventListener('change', updateCaloriesEstimate);

    logBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      
      // 构建数据对象，确保数值字段正确转换
      const data = {
        workout_type: formData.get('workout_type') || '',
        duration_minutes: parseInt(formData.get('duration_minutes') || '0', 10),
        intensity: formData.get('intensity') || '',
        notes: formData.get('notes') || null,
      };
      
      // 处理卡路里（如果表单中有calories_burned字段，使用它；否则使用估算值）
      const caloriesValue = formData.get('calories_burned') || caloriesInput.value;
      if (caloriesValue) {
        data.calories_burned = parseInt(caloriesValue, 10);
      }
      
      // 验证必填字段
      if (!data.workout_type || !data.duration_minutes || !data.intensity) {
        alert('Please fill in all required fields.');
        return;
      }
      
      if (data.duration_minutes < 1 || data.duration_minutes > 600) {
        alert('Duration must be between 1 and 600 minutes.');
        return;
      }
      
      // 设置加载状态
      logBtn.disabled = true;
      logBtn.textContent = 'Saving...';
      
      try {
        console.log('Sending workout data:', data);
        const result = await Api.logWorkout(data);
        console.log('Workout saved successfully:', result);
        
        // 重新获取用户profile以更新统计数据
        try {
          const profile = await Api.getProfile();
          if (profile) {
            // 更新localStorage中的用户数据
            if (typeof Auth !== 'undefined' && Auth.saveUserToLocal) {
              Auth.saveUserToLocal(profile);
            }
          }
        } catch (profileErr) {
          console.warn('Failed to refresh user profile:', profileErr);
        }
        
        // 显示成功消息
        alert('Workout logged successfully!');
        
        // 使用localStorage时间戳通知其他页面刷新数据（跨页面通信）
        localStorage.setItem('fittech_workout_updated', Date.now().toString());
        
        // 触发自定义事件通知同页面的dashboard（同页面通信）
        window.dispatchEvent(new CustomEvent('workoutLogged'));
        
        // 重置表单
        form.reset();
        caloriesInput.value = '';
      } catch (err) {
        console.error('Failed to log workout:', err);
        alert(err.message || 'Failed to log workout. Please try again.');
      } finally {
        logBtn.disabled = false;
        logBtn.textContent = 'Log Workout';
      }
    });
  }

  function loadVideos() {
    try {
      const raw = localStorage.getItem(LOCAL_VIDEOS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  function saveVideos(arr) {
    localStorage.setItem(LOCAL_VIDEOS_KEY, JSON.stringify(arr));
  }

  function renderVideos() {
    const listEl = document.getElementById('savedVideosList');
    if (!listEl) return;
    const videos = loadVideos();
    if (!videos.length) {
      listEl.textContent = 'No saved training videos yet.';
      return;
    }
    listEl.innerHTML = videos.map((v) => `<div>${v.type}: <a href="${v.url}" target="_blank">${v.url}</a></div>`).join('');
  }

  function attachVideoLinks() {
    const container = document.querySelector('.training-resources');
    const urlRow = document.getElementById('videoUrlInputRow');
    const urlInput = document.getElementById('videoUrlInput');
    const saveBtn = document.getElementById('saveVideoUrlBtn');
    if (!container || !urlRow) return;

    let currentType = null;

    container.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-video-type]');
      if (!btn) return;
      currentType = btn.dataset.videoType;
      urlRow.classList.remove('hidden');
      urlInput.focus();
    });

    saveBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = urlInput.value.trim();
      if (!url || !currentType) return;
      const all = loadVideos();
      all.push({ url, type: currentType });
      saveVideos(all);
      urlInput.value = '';
      urlRow.classList.add('hidden');
      renderVideos();
    });

    renderVideos();
  }

  function init() {
    attachFoodSearch();
    renderTodayFoods();
    attachGeneratePlan();
    attachQuickWorkout();
    attachVideoLinks();
  }

  document.addEventListener('DOMContentLoaded', init);

  return {};
})();


