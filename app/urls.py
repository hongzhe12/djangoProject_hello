# 创建一个路由
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
]