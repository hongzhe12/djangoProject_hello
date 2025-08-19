from django.urls import path
from . import views

app_name = 'environment'

urlpatterns = [
    path('', views.environment_list, name='list'),
    path('add/', views.environment_edit, name='add'),
    path('edit/<int:pk>/', views.environment_edit, name='edit'),
    path('delete/<int:pk>/', views.environment_delete, name='delete'),
    path('refresh/', views.environment_list, name='refresh'),
]