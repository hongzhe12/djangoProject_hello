# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /code

# 安装Python依赖
COPY requirements.txt .
RUN pip install uv -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN uv pip install --system --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 复制项目代码
COPY . .

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=helloDjango.settings