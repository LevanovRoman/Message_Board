from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, DeleteView, UpdateView, ListView
from .utils import send_otp
from datetime import datetime
import pyotp
from django.contrib.auth.models import User

from .forms import RegisterUserForm, PostForm
from .models import *


menu = [
    {'title': 'Главная', 'url_name': 'main'},
    {'title': 'Yet now', 'url_name': 'login'},
    {'title': 'Статьи', 'url_name': 'logout'},
]


def main_view(request):
    posts = Post.objects.all()
    if 'username' in request.session:
        del request.session['username']
    context = {'menu': menu,
               'posts': posts,
               'title': 'Главная'}
    return render(request, 'mainapp/board.html', context=context)


class ShowPost(DetailView):
    model = Post
    template_name = 'mainapp/post-page.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = "Пост"
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('post', kwargs={'post_slug': self.get_object().slug})


class CategoryPostList(ListView):
    model = Category
    template_name = 'mainapp/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = Category.objects.get(slug=self.kwargs['category_slug'])
        context['title'] = 'Категория:    ' + cat.name
        context['cat'] = cat.slug
        context['cat_name'] = cat.name
        context['cat_list'] = cat.get_users_list
        context['menu'] = menu
        return context

    def get_queryset(self):
        return Post.objects.filter(category__slug=self.kwargs['category_slug'])


def subscr(request, slug):
    users = User.objects.all()
    if request.user in users:
        cat = Category.objects.get(slug=slug)
        cat.subscribers.add(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('register')


class CreatePost(CreateView):
    # permission_required = ('mainapp.add_post',)
    # form_class = PostForm
    model = Post
    template_name = 'mainapp/post-create.html'
    success_url = reverse_lazy('main')
    fields = ('title', 'text', 'category', 'photo', 'video_file')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Создание поста'
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        us = self.request.user.username
        post.user = User.objects.get(username=us)
        post.save()
        return super().form_valid(form)


class UpdatePost(UpdateView):
    # permission_required = ('mainapp.change_post',)
    model = Post
    fields = ('title', 'text', 'category', 'photo', 'video_file')
    template_name = 'mainapp/post-update.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Изменение поста'
        return context


class DeletePost(DeleteView):
    permission_required = ('mainapp.delete_post',)
    model = Post
    template_name = 'mainapp/post-delete.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        context['title'] = 'Удаление поста'
        return context


def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('main')
        else:
            error_message = "Invalid username or password"
    return render(request, 'mainapp/login.html', {error_message: error_message})
    #     if user is not None:
    #         send_otp(request)
    #         request.session['username'] = username
    #         return redirect('otp')
    #     else:
    #         error_message = "Invalid username or password"
    # return render(request, 'mainapp/login.html', {error_message: error_message})


def otp_view(request):
    error_message = None
    if request.method == "POST":
        otp = request.POST["otp"]
        username = request.session['username']

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']
        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)

            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(otp):
                    user = get_object_or_404(User, username=username)
                    login(request, user)

                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    return redirect('main')
                else:
                    error_message = 'invalid one time password'
            else:
                error_message = 'one time password has expired'
        else:
            error_message = 'ups... something went wrong'
    return render(request, 'mainapp/otp.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('main')


def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # создание объекта без сохранения в БД
            user.set_password(form.cleaned_data['password'])
            user.save()
            send_otp(request, request.POST['email'])
            username = request.POST['username']
            request.session['username'] = username
            return redirect('otp')
    else:
        form = RegisterUserForm()
    return render(request, 'mainapp/registration.html', {'form': form})
