from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .utils import send_otp
from datetime import datetime
import pyotp
from django.contrib.auth.models import User
from .forms import RegisterUserForm


menu = [
    {'title': 'Главная', 'url_name': 'main'},
    {'title': 'Новости', 'url_name': 'show_all_news'},
    {'title': 'Статьи', 'url_name': 'show_all_articles'},
]


def main_view(request):
    if 'username' in request.session:
        del request.session['username']
    context = {'menu': menu,
               'title': 'Главная'}
    return render(request, 'mainapp/board.html', context=context)


# class MainPage(TemplateView):
#     # model = Post
#     template_name = 'mainapp/board.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['menu'] = menu
#         context['title'] = 'Главная'
#         return context


def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            send_otp(request)
            request.session['username'] = username
            return redirect('otp')
        else:
            error_message = "Invalid username or password"
    return render(request, 'mainapp/login.html', {error_message: error_message})


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
            return redirect('main')
    else:
        form = RegisterUserForm()
    return render(request, 'mainapp/reg-2.html', {'form': form})
