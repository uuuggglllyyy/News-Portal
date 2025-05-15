
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Author, Category
from .forms import PostForm, NewsSearchForm  # Создадим PostForm ниже
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone  # Добавлено
import pytz  # Добавлено
import logging
from .tasks import send_notifications  # Import Celery task
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.translation import gettext as _  # импортируем функцию для перевода


logger = logging.getLogger(__name__)
security_logger = logging.getLogger('django.security')


# тест логов, вызывает ошибку
def test_logging_view(request):
    logger.debug(_("This is a debug message."))
    logger.info(_("This is an info message."))
    logger.warning(_("This is a warning message."))
    try:
        1 / 0
    except Exception as e:
        logger.error(_(f"This is an error message: {e}"), exc_info=True)  # Включаем стек трейс
        logger.critical(_("This is a critical message."))
        raise  # Важно: перебросить исключение, чтобы Django обработал его
    security_logger = logging.getLogger('django.security')  # Получаем существующий логгер
    security_logger.warning(_("Security warning: Unauthorized access attempt!"))

    return HttpResponse(_("Logging test page."))


class PostList(ListView):
    model = Post
    ordering = '-date_created'
    template_name = 'news/post_list.html'  # Убедитесь, что этот шаблон существует
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.post_type = self.request.GET.get('post_type', 'NW')  # NW как default
        if self.post_type not in ['NW', 'AR']:
            self.post_type = 'NW'  # Validation
        queryset = queryset.filter(post_type=self.post_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.post_type
        context['is_news'] = self.post_type == 'NW'
        context['is_article'] = self.post_type == 'AR'
        context['timezones'] = pytz.common_timezones # Добавлено
        context['current_time'] = timezone.now() # Добавлено
        return context

    def post(self, request):  #  Для обработки выбора часового пояса
        request.session['django_timezone'] = request.POST['timezone']
        return redirect(request.META['HTTP_REFERER']) #  Используйте имя URL


class PostDetail(DetailView):
    model = Post
    template_name = 'news/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj_id = self.kwargs.get('pk')
        cache_key = f'post-{obj_id}'

        # Сначала пробуем получить из кэша
        obj = cache.get(cache_key)

        if obj is None:
            # Если в кэше нет, получаем из базы данных
            obj = get_object_or_404(Post, pk=obj_id)  # используем get_object_or_404
            # Сохраняем в кэш
            cache.set(cache_key, obj)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timezones'] = pytz.common_timezones # Добавлено
        context['current_time'] = timezone.now() # Добавлено
        return context



class BasePostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        author = Author.objects.get(user=self.request.user)
        post.author = author
        post.post_type = self.post_type

        # Проверка количества публикаций за последние 24 часа
        now = timezone.now()
        start_of_day = now - timezone.timedelta(days=1)
        post_count = Post.objects.filter(
            author=author,
            date_created__gte=start_of_day
        ).count()

        if post_count >= 3:
            form.add_error(None, _("You have reached the limit of 3 publications per day."))
            return self.form_invalid(form)

        post.save()

        # Сохраняем категории после сохранения поста
        form.save_m2m()
        logger.info(f"Вызываем send_notifications.delay {_('for a post with an id')} {post.pk}")

        #  ВАЖНО: Залогировать, что функция выполнилась один раз:
        logger.info(f"form_valid {_('completed once for a post with the id')} {post.pk}")

        return super().form_valid(form)  # Или просто return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Вызывается, если форма не прошла валидацию.
        """
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('news_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type_name'] = _('News') if self.post_type == 'NW' else _('Article')
        context['timezones'] = pytz.common_timezones # Добавлено
        context['current_time'] = timezone.now() # Добавлено
        return context


class NewsCreate(BasePostCreate):
    post_type = 'NW'  # Новости


class ArticleCreate(BasePostCreate):
    post_type = 'AR'  # Статьи


class BasePostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = PostForm
    template_name = 'news/post_edit.html'

    def get_success_url(self):
        return reverse('news_list')  # Перенаправляем на news_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_type_name'] = _('News') if post.post_type == 'NW' else _('Article')
        context['timezones'] = pytz.common_timezones # Добавлено
        context['current_time'] = timezone.now() # Добавлено
        return context


class NewsUpdate(LoginRequiredMixin, BasePostUpdate):
    pass


class ArticleUpdate(LoginRequiredMixin, BasePostUpdate):
    pass


class BasePostDelete(DeleteView):
    model = Post
    template_name = 'news/post_delete.html'  # Убедитесь, что этот шаблон существует

    def get_success_url(self):
        return reverse('news_list')  # Перенаправляем на news_list


class NewsDelete(BasePostDelete):
    pass


class ArticleDelete(BasePostDelete):
    pass


def news_search(request):
    form = NewsSearchForm(request.GET)  # Заполняем форму данными из GET-запроса
    news = Post.objects.all()  # Получаем все новости (изначально)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        author = form.cleaned_data.get('author')
        date_after = form.cleaned_data.get('date_after')

        # Фильтрация
        if title:
            news = news.filter(title__icontains=title)  # Поиск по названию

        if author:
            news = news.filter(
                author__user__username__icontains=author)  # Поиск по автору (предполагается поле author в модели)

        if date_after:
            news = news.filter(date_created__gte=date_after)  # Дата позже указанной

    context = {
        'form': form,
        'news': news,
        'timezones': pytz.common_timezones, # Добавлено
        'current_time': timezone.now() # Добавлено
    }
    return render(request, 'news/news_search.html', context)


@cache_page(60)  # Кешируем на 1 минуту (60 секунд)
def news_list(request):
    news = Post.objects.all().order_by('-date_created')  # Сортируем по дате в убывающем порядке
    total_news = news.count()  # Получаем общее количество новостей

    # Пагинация
    paginator = Paginator(news, 10)  # 10 новостей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Получаем нужную страницу

    context = {
        'page_obj': page_obj,  # Передаём объект страницы
        'total_news': total_news,
        'categories': Category.objects.all(),
        'timezones': pytz.common_timezones,  # Добавлено
        'current_time': timezone.now()  # Добавлено
    }

    return render(request, 'news/news_list.html', context)


@cache_page(60 * 5)  # Кешируем на 5 минут (300 секунд)
def news_detail(request, news_id):
    news = Post.objects.get(id=news_id)

    context = {
        'news': news,
        'timezones': pytz.common_timezones,  # Добавлено
        'current_time': timezone.now(),  # Добавлено
    }

    return render(request, 'news/news_detail.html', context)


@login_required
def subscribe(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    if user in category.subscribers.all():
        category.subscribers.remove(user)
    else:
        category.subscribers.add(user)

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))  # Возврат на предыдущую страницу или на news_list, если предыдущей нет
