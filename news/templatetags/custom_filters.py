from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='censor')
def censor(value):
    """
    Цензурирует указанные слова в строке. Заменяет их первой
    буквой, за которой следует звездочки.
    """
    censored_words = ['редиска', 'редиска']  # Добавьте больше слов сюда

    # Преобразуем значение в строку, если это необходимо
    value = str(value)

    words = value.split()
    censored_text = []
    for word in words:
        if word in censored_words:
            censored_word = word[0] + '*' * (len(word) - 1)
            censored_text.append(censored_word)
        else:
            censored_text.append(word)
    return ' '.join(censored_text)
