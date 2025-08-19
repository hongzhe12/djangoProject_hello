import os
import subprocess
from django.db import models


class EnvironmentVariable(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "环境变量"
        verbose_name_plural = "环境变量"

    def __str__(self):
        return f"{self.key}={self.value}"

    @classmethod
    def load_from_system(cls):
        """从系统环境变量加载到数据库"""
        for key, value in os.environ.items():
            if not key.startswith('_'):  # 跳过一些系统变量
                obj, created = cls.objects.get_or_create(
                    key=key,
                    defaults={'value': value, 'description': f'系统环境变量: {key}'}
                )
                if not created:
                    obj.value = value
                    obj.save()

    def apply_to_system(self, scope='global'):
        """将变量应用到系统"""
        if scope == 'global':
            # 写入到 /etc/environment 或 /etc/profile.d/
            self._set_global_env()
        elif scope == 'session':
            # 设置当前会话环境变量
            os.environ[self.key] = self.value

    def _set_global_env(self):
        """设置全局环境变量"""
        try:
            # 方法1: 写入 /etc/environment
            env_file = '/etc/environment'
            if os.access(env_file, os.W_OK):
                self._update_env_file(env_file)

            # 方法2: 创建单独的配置文件
            profile_dir = '/etc/profile.d'
            if os.path.exists(profile_dir) and os.access(profile_dir, os.W_OK):
                self._create_profile_script(profile_dir)

            # 立即生效（可选）
            self._reload_environment()

        except PermissionError:
            # 需要sudo权限
            return False
        return True

    def _update_env_file(self, file_path):
        """更新环境变量文件"""
        lines = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()

        # 查找并更新或添加变量
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f'{self.key}='):
                lines[i] = f'{self.key}="{self.value}"\n'
                found = True
                break

        if not found:
            lines.append(f'{self.key}="{self.value}"\n')

        with open(file_path, 'w') as f:
            f.writelines(lines)

    def _create_profile_script(self, profile_dir):
        """创建profile脚本"""
        script_path = os.path.join(profile_dir, f'custom_{self.key}.sh')
        script_content = f'export {self.key}="{self.value}"\n'

        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o644)  # 设置可读权限

    def _reload_environment(self):
        """重新加载环境变量"""
        try:
            # 让所有用户会话重新读取配置
            subprocess.run(['source', '/etc/environment'], shell=True, check=True)
        except subprocess.CalledProcessError:
            pass