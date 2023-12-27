from django.urls import path, include

from .views import *

urlpatterns = [
    # path('', MainPage.as_view(), name='main'),
    path('', main_view, name='main'),
    path('login/', login_view, name='login'),
    path('otp/', otp_view, name='otp'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    # path('news/', ShowAllNews.as_view(), name='show_all_news'),
    # path('articles/', ShowAllArticles.as_view(), name='show_all_articles'),
    # path('news/create/', CreateNews.as_view(), name='create_news'),
    path('post/create/', CreatePost.as_view(), name='create_post'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('post/update/<slug:slug>/', UpdatePost.as_view(), name='update_post'),
    path('news/delete/<slug:slug>/', DeletePost.as_view(), name='delete_post'),
    # path('accounts/', include('allauth.urls'), name='accounts'),
    # path('get_author/', get_author, name='upgrade'),
    path('category/<slug:category_slug>/', CategoryPostList.as_view(), name='category'),
    path('subscr/<slug:slug>/', subscr, name='subscr'),
]