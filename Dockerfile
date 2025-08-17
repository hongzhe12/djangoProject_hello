# 使用官方 Python 运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /code

# 替换 APT 源为国内源，加快下载速度
# RUN echo "deb http://mirrors.aliyun.com/debian bullseye main" > /etc/apt/sources.list && \
#     echo "deb http://mirrors.aliyun.com/debian bullseye-updates main" >> /etc/apt/sources.list && \
#     echo "deb http://mirrors.aliyun.com/debian-security bullseye-security main" >> /etc/apt/sources.list && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends \
#         python3-dev \
#         build-essential \
#         pkg-config && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install uv -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN uv pip install --system --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 复制项目代码
COPY . .

# 设置环境变量
ENV DJANGO_SETTINGS_MODULE=djangoProject.settings