#!/bin/sh

# 收集静态文件
python manage.py collectstatic --noinput

# 生成新的迁移文件
python manage.py makemigrations

# 创建数据库和应用迁移
python manage.py migrate

# 创建管理员账户（超级用户）
echo "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '1234')
else:
    print('用户 admin 已存在，跳过创建。')
" | python manage.py shell

# 启动 Django 开发服务器
uvicorn helloDjango.asgi:application --host 0.0.0.0 --port 8999 --workers 10