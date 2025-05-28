// Навигация по кнопкам
  document.querySelectorAll('button[data-page]').forEach(button => {
    button.addEventListener('click', () => {
      const page = button.getAttribute('data-page');
      if (page !== 'home') {
        window.location.href = page;
      }
      // Закрываем бургер-меню после клика
      document.querySelector('.base-nav').classList.remove('active');
    });
  });

  // Переключение темы
  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.createElement('button');
    toggle.className = 'theme-toggle';
    toggle.innerHTML = '<i class="fas fa-moon"></i>';
    document.querySelector('.base-header-right').appendChild(toggle);

    toggle.addEventListener('click', () => {
      const body = document.body;
      const theme = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      body.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      toggle.innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    toggle.innerHTML = savedTheme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';

    // Бургер-меню
    const burger = document.querySelector('.base-burger');
    const nav = document.querySelector('.base-nav');
    burger.addEventListener('click', () => {
      nav.classList.toggle('active');
    });
  });