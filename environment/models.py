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
        """将变量应用到系统 - 修正版本"""
        try:
            if scope == 'global':
                success = self._set_global_env()
                if success:
                    # 设置当前进程的环境变量（立即生效）
                    os.environ[self.key] = self.value
                    return True
                return False
            elif scope == 'session':
                # 只设置当前会话环境变量
                os.environ[self.key] = self.value
                return True
                
        except Exception as e:
            print(f"应用环境变量时出错: {e}")
            return False

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
        """更新环境变量文件 - 修正版本"""
        try:
            # 备份原文件
            if os.path.exists(file_path):
                import shutil
                backup_path = f"{file_path}.bak"
                shutil.copy2(file_path, backup_path)
            
            lines = []
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
            
            # 查找并更新或添加变量
            found = False
            new_lines = []
            for line in lines:
                stripped_line = line.strip()
                # 跳过空行和注释
                if not stripped_line or stripped_line.startswith('#'):
                    new_lines.append(line)
                    continue
                
                # 解析键值对
                if '=' in stripped_line:
                    current_key = stripped_line.split('=', 1)[0].strip()
                    if current_key == self.key:
                        new_lines.append(f'{self.key}="{self.value}"\n')
                        found = True
                        continue
                
                new_lines.append(line)
            
            if not found:
                new_lines.append(f'{self.key}="{self.value}"\n')
            
            # 写入文件
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
                
            # 设置正确的文件权限
            os.chmod(file_path, 0o644)
            
        except PermissionError:
            raise PermissionError("需要sudo权限来修改系统环境变量文件")
        except Exception as e:
            # 恢复备份
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            raise e

    def _create_profile_script(self, profile_dir):
        """创建profile脚本"""
        script_path = os.path.join(profile_dir, f'custom_{self.key}.sh')
        script_content = f'export {self.key}="{self.value}"\n'

        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o644)  # 设置可读权限

    def _reload_environment(self):
        """重新加载环境变量 - 修正版本"""
        try:
            # 方法1: 通过启动新的shell会话重新加载
            # 这只是一个示意，实际全局环境变量需要用户重新登录才能生效
            print(f"环境变量 {self.key} 已更新，需要重新登录或重启服务才能生效")
            
            # 方法2: 通知相关服务重新加载配置（如果有的话）
            # 例如：重启某些服务或者发送信号
            
        except Exception as e:
            print(f"重新加载环境变量时出错: {e}")