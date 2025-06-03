document.querySelector('form').addEventListener('submit', (e) => {
    const fullName = document.getElementById('full_name').value;
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    if (!fullName || !login || !password || !email) {
      e.preventDefault();
      alert('Пожалуйста, заполните все поля');
    } else if (password.length < 6) {
      e.preventDefault();
      alert('Пароль должен быть не менее 6 символов');
    }
  });