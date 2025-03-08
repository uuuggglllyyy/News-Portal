// Простой пример добавления интерактивности

document.addEventListener('DOMContentLoaded', function() {
    // Добавляем эффект hover для элементов списка новостей
    const newsItems = document.querySelectorAll('.news-list-item');
    newsItems.forEach(item => {
        item.addEventListener('mouseover', function() {
            this.style.backgroundColor = '#f0f0f0';
        });
        item.addEventListener('mouseout', function() {
            this.style.backgroundColor = '#fff';
        });
    });

    // Пример: вывод сообщения в консоль при загрузке страницы
    console.log("Custom JavaScript loaded!");
});