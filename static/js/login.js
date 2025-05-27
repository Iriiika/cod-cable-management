// Переключение светлой/темной темы
document.getElementById('theme-toggle').addEventListener('click', () => {
    const currentTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
});

// Загрузка сохраненной темы
const savedTheme = localStorage.getItem('theme') || 'light';
document.body.setAttribute('data-theme', savedTheme);