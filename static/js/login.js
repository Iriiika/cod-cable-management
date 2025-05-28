// Проверка формы
  document.querySelector('form').addEventListener('submit', (e) => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.querySelector('.login-error');

    if (!username || !password) {
      e.preventDefault();
      if (errorDiv) {
        errorDiv.textContent = 'Заполните все поля';
      }
    }
  });