# models.py

# models.py 新增部分
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import os
import json
import logging

logger = logging.getLogger(__name__)

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
    {% endif %}

    # 请求体大小限制
    client_max_body_size 30M;

    {% for app in apps %}
    # 应用: {{ app.name }}
    location /{{ app.path }}/ {
        proxy_pass http://{{ app.host }}:{{ app.port }}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /{{ app.path }}/static/ {
        alias {{ app.static_root }}/;
        expires 1d;
    }

    # 媒体文件
    location /{{ app.path }}/media/ {
        alias {{ app.static_root }}/media/;
        expires 7d;
    }
    {% endfor %}

    # 保护敏感文件
    location ~ /\. {
        deny all;
    }
}
"""


from django.db import models

class AppConfigModel(models.Model):
    # 必填字段
    name = models.CharField(
        max_length=100,
        verbose_name="应用名称",
        help_text="应用的显示名称，例如：主应用"
    )
    path = models.CharField(
        max_length=100,
        verbose_name="应用路径",
        help_text="应用在项目中的路径，例如：app1",
        default='app1',
        unique=True
    )
    host = models.CharField(
        max_length=100,
        verbose_name="主机地址",
        help_text="域名或IP地址，例如：localhost 或 example.com",
        default='localhost'
    )
    port = models.PositiveIntegerField(
        verbose_name="端口号",
        help_text="服务监听的端口，例如：8000",
        default=8000,
        unique=True
    )
    static_root = models.CharField(
        max_length=255,
        verbose_name="静态文件根目录",
        help_text="Django collectstatic 输出的静态文件路径，例如：/var/www/app/static",
        default='/var/www/app/static'
    )

    # 可选字段（非必填）
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="描述",
        help_text="应用的详细说明"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="标记该应用配置是否处于激活状态"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="最后更新时间"
    )
    environment = models.CharField(
        max_length=50,
        choices=[
            ('development', '开发环境'),
            ('staging', '预发布环境'),
            ('production', '生产环境'),
            ('testing', '测试环境'),
        ],
        blank=True,
        null=True,
        verbose_name="运行环境"
    )
    ssl_enabled = models.BooleanField(
        default=False,
        verbose_name="SSL 启用",
        help_text="是否启用 HTTPS"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="备注",
        help_text="管理员备注信息"
    )

    # 新增字段：配置文件目录
    config_path = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="配置文件路径",
        help_text="自动生成的Nginx配置文件路径",
        # default='/etc/nginx/conf.d/app.conf'
        default='test'
    )

    @classmethod
    def regenerate_all_configs(cls):
        """
        重新生成所有配置文件的类方法
        """
        generate_global_nginx_config()
        for app in cls.objects.filter(is_active=True):
            config_content = app.generate_nginx_config([app])
            with open(app.config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                print(f"✅ Nginx 配置已生成：{app.config_path}")

    def save(self, *args, **kwargs):
        """重写save方法，在保存时设置默认的配置路径"""
        if not self.config_path:
            # 设置默认的配置文件路径
            self.config_path = os.path.join(
                getattr(settings, 'NGINX_CONFIG_DIR', '/etc/nginx/conf.d/'),
                f"{self.host}_{self.port}_{self.path}.conf"
            )
        super().save(*args, **kwargs)

    def generate_nginx_config(self, apps=None):
        """生成当前应用的Nginx配置"""
        from jinja2 import Template

        # 如果没有传入apps参数，使用当前应用
        if apps is None:
            apps = [self]

        config_data = {
            "server_name": self.host,
            "ssl_enabled": self.ssl_enabled,
            "ssl_certificate": getattr(settings, 'SSL_CERTIFICATE_PATH', '/etc/ssl/certs/cert.pem'),
            "ssl_certificate_key": getattr(settings, 'SSL_CERTIFICATE_KEY_PATH', '/etc/ssl/private/key.pem'),
            "apps": [
                {
                    "name": app.name,
                    "path": app.path,
                    "host": app.host,
                    "port": app.port,
                    "static_root": app.static_root
                }
                for app in apps if app.is_active
            ]
        }

        template = Template(NGINX_TEMPLATE)
        return template.render(config_data)




    class Meta:
        verbose_name = "应用配置"
        verbose_name_plural = "应用配置"
        # 可选：防止重复配置（host + port + path 唯一）
        unique_together = ('host', 'port', 'path')

    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"

    def get_absolute_url(self):
        protocol = "https" if self.ssl_enabled else "http"
        return f"{protocol}://{self.host}:{self.port}/{self.path.strip('/')}/"



# 信号处理函数
@receiver(post_save, sender=AppConfigModel)
def generate_nginx_config_on_save(sender, instance, created, **kwargs):
    """
    在 AppConfigModel 保存后自动生成 Nginx 配置
    添加详细调试信息，便于排查问题
    """
    logger.info("【Nginx 配置生成】信号触发")
    logger.debug(f"当前保存的实例: {instance.name} (ID: {instance.id})")
    logger.debug(f"是否为新建: {created}")

    try:
        # 1. 获取所有活跃的应用配置
        logger.debug("正在查询所有 is_active=True 的应用配置...")
        active_apps = AppConfigModel.objects.filter(is_active=True)
        logger.info(f"共找到 {active_apps.count()} 个活跃应用: {[app.name for app in active_apps]}")

        if not active_apps.exists():
            logger.warning("没有找到任何活跃的应用配置，跳过 Nginx 配置生成。")
            return

        # 2. 为每个应用生成单独的配置文件
        for app in active_apps:
            logger.debug(f"处理应用: {app.name}")
            logger.debug(f"  - Host: {app.host}, Port: {app.port}, Path: {app.path}")
            logger.debug(f"  - Static Root: {app.static_root}")
            logger.debug(f"  - Config Path: {app.config_path}")

            # 检查 config_path 是否设置
            if not app.config_path:
                logger.error(f"应用 {app.name} 的 config_path 未设置，跳过生成。")
                continue

            # 生成配置内容
            try:
                config_content = app.generate_nginx_config([app])
                logger.debug(f"  ✔️  成功生成配置内容（前200字符）:\n{config_content[:200]}...")
            except Exception as e:
                logger.error(f"  ❌  生成配置内容失败 (应用: {app.name}): {str(e)}", exc_info=True)
                continue

            # 写入配置文件
            try:
                with open(app.config_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                logger.info(f"  ✔️  Nginx 配置文件已成功写入: {app.config_path}")

                # 可选：输出文件大小
                size = os.path.getsize(app.config_path)
                logger.debug(f"  - 配置文件大小: {size} 字节")

            except Exception as e:
                logger.error(f"  ❌  写入配置文件失败: {app.config_path}, 错误: {str(e)}", exc_info=True)

        # 3. 生成全局配置文件
        logger.info("开始生成全局 Nginx 配置文件...")
        try:
            generate_global_nginx_config()
            logger.info("✔️ 全局 Nginx 配置文件生成成功。")
        except Exception as e:
            logger.error(f"❌ 生成全局配置失败: {str(e)}", exc_info=True)

    except Exception as e:
        logger.critical(f"【严重错误】生成 Nginx 配置时发生未预期异常: {str(e)}", exc_info=True)
        # 可选：发送告警或记录到监控系统
        raise  # 保留原异常向上抛出
        print(f"生成Nginx配置时出错: {e}")


@receiver(post_delete, sender=AppConfigModel)
def cleanup_nginx_config_on_delete(sender, instance, **kwargs):
    """
    在AppConfigModel删除后清理Nginx配置
    """
    try:
        # 删除对应的配置文件
        if instance.config_path and os.path.exists(instance.config_path):
            os.remove(instance.config_path)
            print(f"已删除配置文件: {instance.config_path}")

        # 重新生成全局配置
        generate_global_nginx_config()

    except Exception as e:
        print(f"清理Nginx配置时出错: {e}")


def generate_global_nginx_config():
    """
    生成包含所有活跃应用的全局Nginx配置
    """
    try:
        active_apps = AppConfigModel.objects.filter(is_active=True)
        if not active_apps.exists():
            return

        # 使用第一个应用作为基础生成全局配置
        first_app = active_apps.first()
        config_content = first_app.generate_nginx_config(active_apps)

        global_config_path = getattr(settings, 'NGINX_GLOBAL_CONFIG_PATH',
                                     '/etc/nginx/conf.d/global_apps.conf')

        # 确保目录存在
        config_dir = os.path.dirname(global_config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        # 写入全局配置文件
        with open(global_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)

        print(f"全局Nginx配置文件已生成: {global_config_path}")

    except Exception as e:
        print(f"生成全局Nginx配置时出错: {e}")


# 在AppConfig类中添加一个类方法
