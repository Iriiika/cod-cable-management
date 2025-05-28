// Переключение светлой/темной темы
document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.createElement('button');
    toggle.className = 'admin-theme-toggle';
    toggle.textContent = 'Переключить тему';
    document.querySelector('.admin-header').appendChild(toggle);

    toggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
    });

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
});