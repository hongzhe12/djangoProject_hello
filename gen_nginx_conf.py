#!/usr/bin/env python3
"""
Nginx 配置生成器
精简版模板，支持多个应用和可选SSL配置
"""
import os

from jinja2 import Template

from env_manager import EnvManager

# 精简版Nginx配置模板
# Nginx配置模板（放在模型类外面）
NGINX_TEMPLATE = """# {{ server_name }}.conf
server {
    listen 80;
    {% if server_name %}
    server_name {{ server_name }};
    {% endif %}
    {% if ssl_enabled and ssl_certificate and ssl_certificate_key %}
    # HTTPS重定向
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name {{ server_name }};

    # SSL证书配置
    ssl_certificate {{ ssl_certificate }};
    ssl_certificate_key {{ ssl_certificate_key }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    {% endif %}

    # 请求体大小限制
    client_max_body_size 30M;

    {% for app in apps %}
    # 应用: {{ app.name }}
    location /{{ app.path }}/ {
        proxy_pass http://127.0.0.1:{{ app.port }}/{{app.path}}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # 静态文件
    location /{{ app.path }}/static/ {
        alias {{ app.static_root }}/;
        expires 1d;
        add_header Cache-Control "public, max-age=86400";
        autoindex off;
        try_files $uri $uri/ =404;
    }

    # 媒体文件
    location /{{ app.path }}/media/ {
        alias {{ app.static_root }}/media/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
        autoindex off;
        try_files $uri $uri/ =404;
    }
    {% endfor %}

    # 防止暴露 .git、.env 等敏感文件
    location ~ /\.(env|git|ht|svn) {
        deny all;
    }
}
"""


class NginxConfigGenerator:
    def __init__(self, template_str=NGINX_TEMPLATE):
        """初始化配置生成器"""
        self.template = Template(template_str)

    def generate_config(self, config_data, output_file=None):
        """
        生成Nginx配置文件

        Args:
            config_data: 配置数据字典
            output_file: 输出文件路径，如果为None则返回配置内容

        Returns:
            如果output_file为None，返回配置内容字符串
        """
        rendered_config = self.template.render(config_data)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_config)
            print(f"配置文件已生成: {output_file}")
            return None
        else:
            return rendered_config


# 使用示例
if __name__ == "__main__":
    # 获取脚本当前路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    env_manager = EnvManager()
    # 创建生成器实例
    generator = NginxConfigGenerator()

    config_data = env_manager.read_all()
    # 示例2: 带SSL的配置
    config_data_with_ssl = {
        "server_name": config_data['SERVER_NAME'],
        "ssl_certificate": config_data['SSL_CRT'],
        "ssl_certificate_key": config_data['SSL_KEY'],
        "apps": [
            {
                "name": config_data['BASE_URL'].strip('/'),
                "path": config_data['BASE_URL'].strip('/'),
                "host": config_data['HOST'],
                "port": config_data['PORT'],
                "static_root": os.path.join(script_dir, config_data['STATIC_ROOT'].strip('/'))
            }
        ],
        "ssl_enabled": True
    }
    # 生成带SSL的配置
    generator.generate_config(config_data_with_ssl, "/etc/nginx/conf.d/nginx_with_ssl.conf")
    # generator.generate_config(config_data_with_ssl, "nginx_with_ssl.conf")
