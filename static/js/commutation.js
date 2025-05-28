// Навигация по кнопкам
document.querySelectorAll('button[data-page]').forEach(button => {
    button.addEventListener('click', () => {
        const page = button.getAttribute('data-page');
        if (page !== 'home') {
            window.location.href = page;
        }
    });
});

// Переключение темы
const toggle = document.createElement('button');
toggle.className = 'theme-toggle';
toggle.textContent = 'Переключить тему';
document.querySelector('.comm-header').appendChild(toggle);

toggle.addEventListener('click', () => {
    const body = document.body;
    const theme = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
});

// Загрузка темы
const savedTheme = localStorage.getItem('theme') || 'light';
document.body.setAttribute('data-theme', savedTheme);

// Удаление подключения (заглушка)
document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', () => {
        const id = button.getAttribute('data-id');
        if (confirm('Удалить подключение?')) {
            button.parentElement.parentElement.remove();
        }
    });
});