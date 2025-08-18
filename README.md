# 使用nginx-proxy-manager代理全部容器
```yaml
version: '3'  
services:    
  app:       
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'  
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt  
      - /root/helloDjango/static:/usr/share/nginx/static  # 添加静态文件目录挂载（宿主机路径:容器内路径）
    networks:
      - shared_network  # 加入同一个共享网络

networks:
  shared_network:
    external: true  # 同样声明为外部网络
```

## nginx-proxy-manager完整配置
```bash
# ------------------------------------------------------------
# 192.168.64.128
# ------------------------------------------------------------

map $scheme $hsts_header {
    https   "max-age=63072000; preload";
}

server {
    set $forward_scheme http;
    set $server         "127.0.0.1";
    set $port           8001;

    listen 80;
    listen [::]:80;

    server_name 192.168.64.128;
    http2 off;

    access_log /data/logs/proxy-host-1_access.log proxy;
    error_log /data/logs/proxy-host-1_error.log warn;
    # --------------------------Custom Nginx Configuration----------------------------------
    location /app1/ {
        proxy_pass http://hello-django:8000/app1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 确保路径末尾的斜杠正确处理
        proxy_redirect off;
    }

    # 可选：如果需要代理该路径下的所有子资源（如/static/下的文件）
    location /app1/static/ {
        # 直接指向容器内挂载的静态文件目录（与docker-compose中的容器内路径对应）
        alias /usr/share/nginx/static/;

        # 静态文件缓存配置（可选，优化性能）
        expires 1d;
        add_header Cache-Control "public, max-age=86400";

        # 防止403错误
        autoindex off;
        try_files $uri $uri/ =404;
    }
    # --------------------------Custom Nginx Configuration----------------------------------

    location / {
        # Proxy!
        include conf.d/include/proxy.conf;
    }

    # Custom
    include /data/nginx/custom/server_proxy[.]conf;
}
```

## 一个域名，一个主机的情况下，nginx子路径代理多个django应用

1. 修改`settings.py`配置
```python
# ==============================配置子路径=======================================
# 开头和结束都以斜杠结尾
BASE_URL = '/app1/'          # nginx location路径: /app1/
STATIC_URL = '/app1/static/' # nginx location路径: /app1/static/
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
                  prefixed_path('', include('app1.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```


3. nginx-proxy-manager中配置Custom Nginx Configuration
注意，Edit Proxy Host部分自行填写。
```bash
location /app1/ {
    proxy_pass http://hello-django:8000/app1/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # 确保路径末尾的斜杠正确处理
    proxy_redirect off;
}

# 可选：如果需要代理该路径下的所有子资源（如/static/下的文件）
location /app1/static/ {
    # 直接指向容器内挂载的静态文件目录（与docker-compose中的容器内路径对应）
    alias /usr/share/nginx/static/;
    
    # 静态文件缓存配置（可选，优化性能）
    expires 1d;
    add_header Cache-Control "public, max-age=86400";
    
    # 防止403错误
    autoindex off;
    try_files $uri $uri/ =404;
}
```

