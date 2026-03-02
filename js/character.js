// Avatar level & animated character system

const Character = (() => {
  const LEVELS = [
    { 
      minLevel: 1, 
      title: 'Rookie', 
      className: 'stage-rookie',
      color: 'linear-gradient(180deg, #6366f1, #22c55e)',
      glowColor: 'rgba(99, 102, 241, 0.4)',
      size: '72px'
    },
    { 
      minLevel: 4, 
      title: 'Advanced', 
      className: 'stage-advanced',
      color: 'linear-gradient(180deg, #8b5cf6, #06b6d4)',
      glowColor: 'rgba(139, 92, 246, 0.5)',
      size: '80px'
    },
    { 
      minLevel: 8, 
      title: 'Elite', 
      className: 'stage-elite',
      color: 'linear-gradient(180deg, #f59e0b, #ef4444)',
      glowColor: 'rgba(245, 158, 11, 0.6)',
      size: '88px'
    },
    { 
      minLevel: 12, 
      title: 'Master', 
      className: 'stage-master',
      color: 'linear-gradient(180deg, #ec4899, #fbbf24)',
      glowColor: 'rgba(236, 72, 153, 0.7)',
      size: '96px'
    },
  ];

  function computeLevel(totalWorkouts, totalCalories) {
    const fromWorkouts = Math.floor((totalWorkouts || 0) / 5);
    const fromCalories = Math.floor((totalCalories || 0) / 1000);
    const base = 1 + fromWorkouts + fromCalories;
    return Math.max(1, base);
  }

  function renderCharacter(canvas, stage, variant) {
    if (!canvas) return;
    
    const figure = canvas.querySelector('.character-figure') || document.createElement('div');
    figure.className = 'character-figure';
    
    // 应用等级样式
    figure.style.background = stage.color;
    figure.style.width = stage.size;
    figure.style.height = `${parseInt(stage.size) * 1.67}px`;
    figure.style.boxShadow = `0 0 20px ${stage.glowColor}, 0 0 40px ${stage.glowColor}`;
    
    // 应用变体
    figure.dataset.variant = variant;
    canvas.dataset.levelStage = stage.className;
    canvas.dataset.variant = variant;
    
    // 如果还没有添加到DOM，添加进去
    if (!figure.parentElement) {
      const placeholder = canvas.querySelector('.character-placeholder');
      if (placeholder) {
        placeholder.innerHTML = '';
        placeholder.appendChild(figure);
        const text = document.createElement('p');
        text.className = 'muted small';
        text.textContent = 'Keep training to evolve your avatar';
        placeholder.appendChild(text);
      } else {
        canvas.appendChild(figure);
      }
    }
    
    // 添加升级动画效果
    figure.classList.add('character-animate');
    setTimeout(() => {
      figure.classList.remove('character-animate');
    }, 1000);
  }

  function updateAvatar({ totalWorkouts, totalCalories }) {
    console.log('Character.updateAvatar called with:', { totalWorkouts, totalCalories });
    const level = computeLevel(totalWorkouts, totalCalories);
    console.log('Computed level:', level);
    
    const levelEl = document.getElementById('avatarLevel');
    const titleEl = document.getElementById('avatarTitle');
    const canvas = document.getElementById('characterCanvas');
    
    if (!levelEl || !titleEl || !canvas) {
      console.warn('Character elements not found:', { levelEl: !!levelEl, titleEl: !!titleEl, canvas: !!canvas });
      return;
    }

    const oldLevel = parseInt(levelEl.textContent) || 1;
    console.log('Old level:', oldLevel, 'New level:', level);
    
    levelEl.textContent = level;

    const stage = LEVELS.slice()
      .reverse()
      .find((s) => level >= s.minLevel) || LEVELS[0];
    titleEl.textContent = stage.title;

    // 获取当前变体
    const currentVariant = canvas.dataset.variant || 'variant-a';
    
    // 渲染角色
    renderCharacter(canvas, stage, currentVariant);
    
    // 如果升级了，显示升级提示
    if (level > oldLevel) {
      console.log('Level up! From', oldLevel, 'to', level);
      showLevelUpAnimation(level, stage.title);
    }
  }
  
  function showLevelUpAnimation(level, title) {
    const canvas = document.getElementById('characterCanvas');
    if (!canvas) return;
    
    const notification = document.createElement('div');
    notification.className = 'level-up-notification';
    notification.innerHTML = `
      <div class="level-up-content">
        <div class="level-up-icon">🎉</div>
        <div class="level-up-text">
          <strong>Level Up!</strong>
          <span>You reached Level ${level} • ${title}</span>
        </div>
      </div>
    `;
    notification.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 100;
      animation: levelUpPop 0.6s ease-out;
    `;
    
    canvas.style.position = 'relative';
    canvas.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'levelUpFadeOut 0.4s ease-out';
      setTimeout(() => notification.remove(), 400);
    }, 2000);
  }

  function init() {
    const prev = document.getElementById('prevCharacter');
    const next = document.getElementById('nextCharacter');
    const canvas = document.getElementById('characterCanvas');
    if (!canvas) return;

    let variantIndex = 0;
    const variants = ['variant-a', 'variant-b', 'variant-c'];
    
    function applyVariant() {
      const currentStage = LEVELS.find(s => 
        canvas.dataset.levelStage === s.className
      ) || LEVELS[0];
      renderCharacter(canvas, currentStage, variants[variantIndex]);
    }
    
    prev &&
      prev.addEventListener('click', () => {
        variantIndex = (variantIndex - 1 + variants.length) % variants.length;
        applyVariant();
      });
    next &&
      next.addEventListener('click', () => {
        variantIndex = (variantIndex + 1) % variants.length;
        applyVariant();
      });

    // 初始化默认变体
    applyVariant();
  }

  document.addEventListener('DOMContentLoaded', init);

  return {
    updateAvatar,
  };
})();


