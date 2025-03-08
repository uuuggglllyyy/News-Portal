from django import template

register = template.Library()

censored_words = ['редиска', 'Редиска']  # Добавьте больше слов сюда

@register.filter(name='censor')
def censor(value):
    """
    Цензурирует указанные слова в строке. Заменяет их первой
    буквой, за которой следуют звездочки.

    Аргументы:
        value: Строка для цензурирования.

    Возвращает:
        Цензурированная строка.
    """
    if not isinstance(value, str):
        raise ValueError("Фильтр censor может быть применен только к строкам.")

    words = value.split()
    censored_text = []
    for word in words:
        if word in censored_words:
            censored_word = word[0] + '*' * (len(word) - 1)
            censored_text.append(censored_word)
        else:
            censored_text.append(word)
    return ' '.join(censored_text)

# Пример использования в шаблоне:
# {{ article.title|censor }}
# {{ article.text|censor }}

