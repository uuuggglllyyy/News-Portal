from django import forms
from .models import Post, Category
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

class NewsSearchForm(forms.Form):
    title = forms.CharField(label='Название', required=False)
    author = forms.CharField(label='Автор', required=False)
    date_after = forms.DateField(label='Позже даты', required=False, widget=forms.DateInput(attrs={'type': 'date'}))  # Указываем тип для HTML5

    def clean_date_after(self): # Если нужно, добавляем валидацию даты
        date_after = self.cleaned_data.get('date_after')
        return date_after


class PostForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Категории'
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'categories']


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
