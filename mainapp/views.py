from django.shortcuts import render
from django.views.generic import ListView, TemplateView

menu = [
    {'title': 'Главная', 'url_name': 'main'},
    {'title': 'Новости', 'url_name': 'show_all_news'},
    {'title': 'Статьи', 'url_name': 'show_all_articles'},
]


class MainPage(TemplateView):
    # model = Post
    template_name = 'mainapp/board.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Главная'
        return context

