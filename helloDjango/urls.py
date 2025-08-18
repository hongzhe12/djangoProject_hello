"""
URL configuration for helloDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from helloDjango.settings import BASE_URL


def prefixed_path(route, view, BASE_URL = BASE_URL, name=None):
    """自动添加BASE_URL前缀的辅助函数"""
    BASE_URL_stripped = BASE_URL.strip('/')
    full_route = f'{BASE_URL_stripped}/{route}' if BASE_URL_stripped else route
    return path(full_route, view, name=name)

urlpatterns = [
    prefixed_path('admin/', admin.site.urls),
    prefixed_path('', include('app.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)