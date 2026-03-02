// Dashboard logic: stats loading, health metrics, recent lists, workout modal

const Dashboard = (() => {
  function safeNumber(val) {
    const n = Number(val);
    return Number.isFinite(n) ? n : 0;
  }

  function computeBMI(weightKg, heightCm) {
    const h = safeNumber(heightCm) / 100;
    const w = safeNumber(weightKg);
    if (!h || !w) return null;
    return w / (h * h);
  }

  function bmiCategory(bmi) {
    if (!bmi) return 'Unknown';
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 24.9) return 'Normal';
    if (bmi < 29.9) return 'Overweight';
    return 'Obese';
  }

  function computeBMR({ gender, weight, height, age }) {
    const w = safeNumber(weight);
    const h = safeNumber(height);
    const a = safeNumber(age);
    if (!w || !h || !a) return null;
    if (gender === 'female') {
      return 10 * w + 6.25 * h - 5 * a - 161;
    }
    return 10 * w + 6.25 * h - 5 * a + 5;
  }

  function renderHealthMetrics(user) {
    const bmiValueEl = document.getElementById('bmiValue');
    const bmiCategoryEl = document.getElementById('bmiCategory');
    const bmrValueEl = document.getElementById('bmrValue');
    const goalLabel = document.getElementById('goalLabel');
    const activityLabel = document.getElementById('activityLabel');
    if (!bmiValueEl) return;

    const bmi = computeBMI(user?.weight, user?.height);
    const cat = bmiCategory(bmi);
    bmiValueEl.textContent = bmi ? bmi.toFixed(1) : '--';
    bmiCategoryEl.textContent = bmi ? cat : 'Enter your data to calculate';

    const bmr = computeBMR({
      gender: user?.gender,
      weight: user?.weight,
      height: user?.height,
      age: user?.age,
    });
    bmrValueEl.textContent = bmr ? `${Math.round(bmr)} kcal` : '-- kcal';

    const goalMap = {
      muscle_gain: 'Muscle Gain',
      fat_loss: 'Fat Loss',
      maintenance: 'Maintenance',
      endurance: 'Endurance',
    };
    goalLabel.textContent = goalMap[user?.fitness_goal] || 'Not set';

    const activityMap = {
      sedentary: 'Sedentary',
      light: 'Light',
      moderate: 'Moderate',
      active: 'Active',
      very_active: 'Very Active',
    };
    activityLabel.textContent = activityMap[user?.activity_level] || 'Not set';
  }

  function renderStats(stats) {
    const totalWorkoutsEl = document.getElementById('totalWorkouts');
    const streakDaysEl = document.getElementById('streakDays');
    const caloriesBurnedEl = document.getElementById('caloriesBurned');
    const achievementsEl = document.getElementById('achievements');
    if (!totalWorkoutsEl) return;

    const totalWorkouts = safeNumber(stats?.total_workouts);
    const streak = safeNumber(stats?.streak_days);
    const calories = safeNumber(stats?.total_calories);
    const ach = safeNumber(stats?.achievements_count);

    console.log('Rendering stats:', { totalWorkouts, calories, streak, ach });

    totalWorkoutsEl.textContent = totalWorkouts;
    streakDaysEl.textContent = streak;
    caloriesBurnedEl.textContent = calories;
    achievementsEl.textContent = ach;

    const workoutsToNext = 5 - (totalWorkouts % 5 || 0);
    const caloriesToNext = 1000 - (calories % 1000 || 0);
    const workoutsToNextEl = document.getElementById('workoutsToNextLevel');
    const caloriesToNextEl = document.getElementById('caloriesToNextLevel');
    const workoutBar = document.getElementById('workoutProgressBar');
    const calorieBar = document.getElementById('calorieProgressBar');

    if (workoutsToNextEl && caloriesToNextEl && workoutBar && calorieBar) {
      workoutsToNextEl.textContent = workoutsToNext === 5 ? '0' : workoutsToNext;
      caloriesToNextEl.textContent = caloriesToNext === 1000 ? '0 kcal' : `${caloriesToNext} kcal`;
      const workoutPct = ((5 - workoutsToNext) / 5) * 100;
      const caloriePct = ((1000 - caloriesToNext) / 1000) * 100;
      workoutBar.style.width = `${Math.max(0, workoutPct)}%`;
      calorieBar.style.width = `${Math.max(0, caloriePct)}%`;
    }

    // 更新角色（确保传入正确的参数）
    console.log('Updating avatar with:', { totalWorkouts, totalCalories: calories });
    Character.updateAvatar({
      totalWorkouts,
      totalCalories: calories,
    });
  }

  function attachWorkoutModal() {
    const openBtn = document.getElementById('logWorkoutBtn');
    const modal = document.getElementById('logWorkoutModal');
    const backdrop = modal?.querySelector('.modal-backdrop');
    const closeBtn = document.getElementById('closeLogWorkoutModal');
    const cancelBtn = document.getElementById('cancelLogWorkout');
    const submitBtn = document.getElementById('submitLogWorkout');
    const form = document.getElementById('logWorkoutForm');
    if (!modal || !form) return;

    const open = () => {
      console.log('Opening modal...');
      // 强制显示
      modal.classList.remove('hidden');
      modal.style.display = 'flex';
      modal.style.visibility = 'visible';
      modal.style.opacity = '1';
      modal.style.pointerEvents = 'auto';
      
      form.reset(); // 打开时重置表单
      submitBtn.disabled = false;
      submitBtn.textContent = 'Save Workout';
      submitBtn.style.backgroundColor = ''; // 重置按钮样式
    };

    const close = () => {
      console.log('Closing modal...');
      // 强制隐藏
      modal.classList.add('hidden');
      modal.style.display = 'none';
      modal.style.visibility = 'hidden';
      modal.style.opacity = '0';
      modal.style.pointerEvents = 'none';
      
      form.reset();
      submitBtn.disabled = false;
      submitBtn.textContent = 'Save Workout';
      submitBtn.style.backgroundColor = ''; // 重置按钮样式
      console.log('Modal closed');
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
    cancelBtn &&
      cancelBtn.addEventListener('click', (e) => {
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

    submitBtn &&
      submitBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        // 表单验证
        if (!form.checkValidity()) {
          form.reportValidity();
          return;
        }

        // 获取表单数据并转换格式
        const formData = new FormData(form);
        const data = {
          workout_type: formData.get('workout_type'),
          duration_minutes: parseInt(formData.get('duration_minutes'), 10),
          intensity: formData.get('intensity'),
          notes: formData.get('notes') || null,
        };

        // 验证必填字段
        if (!data.workout_type || !data.duration_minutes || !data.intensity) {
          alert('Please fill in all required fields');
          return;
        }

        // 设置加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        try {
          const result = await Api.logWorkout(data);
          console.log('Workout saved successfully:', result);
          
          // 立即关闭模态框（在任何其他操作之前）
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
          
          // 刷新用户profile以更新localStorage
          try {
            const profile = await Api.getProfile();
            if (profile) {
              Auth.saveUserToLocal(profile);
              renderHealthMetrics(profile);
            }
          } catch (profileErr) {
            console.warn('Failed to refresh profile:', profileErr);
          }
          
          // 刷新统计数据（等待完成以确保角色更新）
          await loadStats();
          
          // 确保角色更新（双重保险）
          try {
            const stats = await Api.getWorkoutStats();
            if (stats) {
              console.log('Refreshing character with stats:', stats);
              Character.updateAvatar({
                totalWorkouts: safeNumber(stats.total_workouts || 0),
                totalCalories: safeNumber(stats.total_calories || 0),
              });
            }
          } catch (statsErr) {
            console.warn('Failed to refresh stats for character update:', statsErr);
          }
          
          // 检查是否有解锁的成就
          if (result.achievements_unlocked && result.achievements_unlocked.length > 0) {
            // 显示成就解锁通知
            result.achievements_unlocked.forEach((achievement, index) => {
              setTimeout(() => {
                const achievementMsg = document.createElement('div');
                achievementMsg.className = 'achievement-notification';
                achievementMsg.innerHTML = `
                  <div class="achievement-content">
                    <div class="achievement-icon">🏆</div>
                    <div class="achievement-text">
                      <strong>Achievement Unlocked!</strong>
                      <span>${achievement.title}</span>
                      <small>${achievement.description}</small>
                    </div>
                  </div>
                `;
                achievementMsg.style.cssText = 'position: fixed; top: 80px; right: 20px; background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; padding: 16px 24px; border-radius: 12px; z-index: 10001; box-shadow: 0 8px 24px rgba(245, 158, 11, 0.4); animation: slideIn 0.4s ease-out; max-width: 320px;';
                document.body.appendChild(achievementMsg);
                setTimeout(() => {
                  achievementMsg.style.animation = 'slideOut 0.3s ease-out';
                  setTimeout(() => achievementMsg.remove(), 300);
                }, 4000);
              }, index * 500); // 多个成就依次显示
            });
          }
          
          // 显示成功消息提示
          const successMsg = document.createElement('div');
          successMsg.className = 'success-message';
          successMsg.textContent = '✓ Workout saved successfully!';
          successMsg.style.cssText = 'position: fixed; top: 80px; right: 20px; background: #10b981; color: white; padding: 12px 24px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.2); animation: slideIn 0.3s ease-out;';
          document.body.appendChild(successMsg);
          setTimeout(() => {
            successMsg.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => successMsg.remove(), 300);
          }, 2500);
        } catch (err) {
          console.error('Failed to save workout:', err);
          alert(err.message || 'Failed to save workout. Please try again.');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Save Workout';
          submitBtn.style.backgroundColor = '';
        }
      });
  }

  async function loadStats() {
    try {
      const stats = await Api.getWorkoutStats();
      renderStats(stats || {});
    } catch (err) {
      console.warn('Could not load stats yet (likely backend not ready):', err.message);
    }
  }

  async function loadRecentData() {
    const recentWorkoutsList = document.getElementById('recentWorkoutsList');
    const recentNutritionList = document.getElementById('recentNutritionList');
    if (!recentWorkoutsList || !recentNutritionList) return;

    // 最近锻炼
    try {
      const res = await Api.getRecentWorkouts(5);
      const items = res?.items || [];
      if (!items.length) {
        recentWorkoutsList.classList.add('empty-state');
        recentWorkoutsList.innerHTML =
          '<li>No workouts logged yet. Hit “LOG NEW WORKOUT” to start your journey.</li>';
      } else {
        recentWorkoutsList.classList.remove('empty-state');
        recentWorkoutsList.innerHTML = items
          .map((w) => {
            const date = w.date || w.created_at?.slice(0, 10) || '';
            const calories =
              w.calories_burned != null && w.calories_burned !== ''
                ? ` • ${w.calories_burned} kcal`
                : '';
            return `<li>${date} • ${w.workout_type.toUpperCase()} • ${w.duration_minutes} min • ${w.intensity}${calories}</li>`;
          })
          .join('');
      }
    } catch (err) {
      console.warn('Failed to load recent workouts, using placeholder.', err);
    }

    // 今日营养
    try {
      const today = new Date().toISOString().slice(0, 10);
      const data = await Api.getTodayNutrition(today);
      const items = data?.items || [];
      if (!items.length) {
        recentNutritionList.classList.add('empty-state');
        recentNutritionList.innerHTML =
          '<li>No nutrition logs yet. Head to the Training page to log your meals.</li>';
      } else {
        recentNutritionList.classList.remove('empty-state');
        recentNutritionList.innerHTML = items
          .slice(0, 5)
          .map(
            (n) =>
              `<li>${n.meal_type.toUpperCase()} • ${n.food_name || ''} • ${n.calories} kcal • ${n.protein}g P • ${n.carbs}g C • ${n.fats}g F</li>`,
          )
          .join('');
      }
    } catch (err) {
      console.warn('Failed to load today nutrition, using placeholder.', err);
    }
  }

  // 刷新所有数据的函数
  async function refreshAllData() {
    try {
      // 重新获取用户profile
      const profile = await Api.getProfile();
      if (profile) {
        Auth.saveUserToLocal(profile);
        renderHealthMetrics(profile);
      }
    } catch (err) {
      console.warn('Failed to refresh profile:', err);
    }
    
    // 重新加载统计数据
    await loadStats();
    
    // 重新加载最近数据
    loadRecentData();
  }

  async function init() {
    const user = Auth.getUserFromLocal();
    if (user) {
      renderHealthMetrics(user);
    } else {
      try {
        const profile = await Api.getProfile();
        Auth.saveUserToLocal(profile);
        renderHealthMetrics(profile);
      } catch {
        // ignore for now
      }
    }
    attachWorkoutModal();
    await loadStats(); // 确保统计数据加载后再初始化角色
    loadRecentData();
    
    // 初始化角色显示（即使没有统计数据也显示默认角色）
    try {
      const stats = await Api.getWorkoutStats().catch(() => ({}));
      Character.updateAvatar({
        totalWorkouts: safeNumber(stats && stats.total_workouts),
        totalCalories: safeNumber(stats && stats.total_calories),
      });
    } catch (err) {
      console.warn('Failed to initialize character:', err);
      // 如果获取失败，使用默认值
      Character.updateAvatar({
        totalWorkouts: 0,
        totalCalories: 0,
      });
    }
    
    // 监听localStorage变化事件（跨页面通信）
    // 注意：storage事件只在其他页面修改localStorage时触发
    window.addEventListener('storage', async (e) => {
      if (e.key === 'fittech_workout_updated') {
        console.log('Workout updated detected (from another page), refreshing dashboard...');
        await refreshAllData();
      }
    });
    
    // 监听自定义事件（同页面内通信）
    window.addEventListener('workoutLogged', async () => {
      console.log('Workout logged event received, refreshing dashboard...');
      await refreshAllData();
    });
    
    // 监听页面可见性变化，当用户切换回dashboard页面时刷新数据
    let lastRefreshTime = 0;
    document.addEventListener('visibilitychange', async () => {
      if (!document.hidden) {
        // 页面变为可见时，检查是否需要刷新（避免过于频繁）
        const now = Date.now();
        if (now - lastRefreshTime > 2000) { // 至少间隔2秒
          lastRefreshTime = now;
          await refreshAllData();
        }
      }
    });
    
    // 定期检查数据更新（每30秒）
    setInterval(async () => {
      const lastUpdate = parseInt(localStorage.getItem('fittech_workout_updated') || '0');
      const now = Date.now();
      // 如果最近5分钟内有更新，刷新数据
      if (lastUpdate > 0 && (now - lastUpdate) < 300000) {
        await refreshAllData();
        // 清除标记，避免重复刷新
        localStorage.removeItem('fittech_workout_updated');
      }
    }, 30000);
  }

  document.addEventListener('DOMContentLoaded', init);

  return {};
})();


