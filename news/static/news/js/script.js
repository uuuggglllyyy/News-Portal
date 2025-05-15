function setTheme() {
    const now = new Date();
    const hour = now.getHours();
    const body = document.getElementById('body');

    if (hour >= 19 || hour < 7) {
        body.classList.add('dark-theme');
    } else {
        body.classList.remove('dark-theme');
    }
}

// Вызываем функцию при загрузке страницы
setTheme();

// Обновляем тему каждый час
setInterval(setTheme, 3600000);

