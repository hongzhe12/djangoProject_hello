# models.py
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
        help_text="应用在项目中的路径，例如：app1"
    )
    host = models.CharField(
        max_length=100,
        verbose_name="主机地址",
        help_text="域名或IP地址，例如：localhost 或 example.com"
    )
    port = models.PositiveIntegerField(
        verbose_name="端口号",
        help_text="服务监听的端口，例如：8000"
    )
    static_root = models.CharField(
        max_length=255,
        verbose_name="静态文件根目录",
        help_text="Django collectstatic 输出的静态文件路径，例如：/var/www/app/static"
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