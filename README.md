1. 修改`settings.py`配置
```python
# ==============================配置子路径=======================================
# 开头和结束都以斜杠结尾
BASE_URL = '/app/'          # nginx location路径: /app/
STATIC_URL = '/app/static/' # nginx location路径: /app/static/
```

2. 修改项目路由`urls.py`，增加`prefixed_path`函数，原先的`path`函数改为`prefixed_path`

```python
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


def prefixed_path(route, view, base_url=BASE_URL, name=None):
    """自动添加base_url前缀的辅助函数"""
    base_url_stripped = base_url.strip('/')
    full_route = f'{base_url_stripped}/{route}' if base_url_stripped else route
    return path(full_route, view, name=name)


urlpatterns = [
                  prefixed_path('admin/', admin.site.urls),
                  prefixed_path('', include('app.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```


3. 运行部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

