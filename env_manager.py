import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import dotenv_values, set_key, unset_key


class EnvManager:
    """
    使用 python-dotenv 管理 .env 文件的 CRUD 操作类

    功能：
    - 创建新的 .env 文件
    - 读取环境变量
    - 添加/更新环境变量
    - 删除环境变量
    - 检查环境变量是否存在
    - 批量操作环境变量
    """

    def __init__(self, env_path: str = '.env'):
        """
        初始化 EnvManager

        :param env_path: .env 文件路径，默认为当前目录下的 .env 文件
        """
        self.env_path = env_path

    def create_env(self, variables: Dict[str, Any] = None) -> bool:
        """
        创建 .env 文件，可选择性添加初始变量

        :param variables: 初始环境变量字典
        :return: 创建成功返回 True，否则返回 False
        """
        try:
            # 如果文件不存在，创建空文件
            if not os.path.exists(self.env_path):
                open(self.env_path, 'a').close()

            # 添加初始变量
            if variables:
                for key, value in variables.items():
                    set_key(self.env_path, key, str(value))

            return True
        except Exception as e:
            print(f"创建 .env 文件失败: {e}")
            return False

    def read_all(self) -> Dict[str, Optional[str]]:
        """
        读取 .env 文件中所有环境变量

        :return: 包含所有环境变量的字典
        """
        try:
            return dict(dotenv_values(self.env_path))
        except Exception as e:
            print(f"读取 .env 文件失败: {e}")
            return {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取指定环境变量的值

        :param key: 环境变量名
        :param default: 如果变量不存在时返回的默认值
        :return: 环境变量的值或默认值
        """
        try:
            return dotenv_values(self.env_path).get(key, default)
        except Exception as e:
            print(f"获取环境变量失败: {e}")
            return default

    def set(self, key: str, value: Any) -> bool:
        """
        设置或更新环境变量

        :param key: 环境变量名
        :param value: 环境变量值
        :return: 操作成功返回 True，否则返回 False
        """
        try:
            set_key(self.env_path, key, str(value))
            return True
        except Exception as e:
            print(f"设置环境变量失败: {e}")
            return False

    def set_many(self, variables: Dict[str, Any]) -> bool:
        """
        批量设置环境变量

        :param variables: 环境变量字典
        :return: 操作成功返回 True，否则返回 False
        """
        try:
            for key, value in variables.items():
                set_key(self.env_path, key, str(value))
            return True
        except Exception as e:
            print(f"批量设置环境变量失败: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除指定的环境变量

        :param key: 要删除的环境变量名
        :return: 删除成功返回 True，否则返回 False
        """
        try:
            unset_key(self.env_path, key)
            return True
        except Exception as e:
            print(f"删除环境变量失败: {e}")
            return False

    def delete_many(self, keys: List[str]) -> bool:
        """
        批量删除环境变量

        :param keys: 要删除的环境变量名列表
        :return: 全部删除成功返回 True，否则返回 False
        """
        try:
            for key in keys:
                unset_key(self.env_path, key)
            return True
        except Exception as e:
            print(f"批量删除环境变量失败: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查环境变量是否存在

        :param key: 环境变量名
        :return: 存在返回 True，否则返回 False
        """
        return key in self.read_all()

    def reload(self) -> bool:
        """
        重新加载 .env 文件（主要用于外部修改后的刷新）

        :return: 总是返回 True（实际重载发生在下次读取时）
        """
        # python-dotenv 在每次调用 dotenv_values 时都会重新读取文件
        # 所以不需要特殊处理
        return True

    def get_file_path(self) -> str:
        """
        获取 .env 文件路径

        :return: .env 文件路径
        """
        return os.path.abspath(self.env_path)

    def file_exists(self) -> bool:
        """
        检查 .env 文件是否存在

        :return: 文件存在返回 True，否则返回 False
        """
        return os.path.exists(self.env_path)

    # def create_test_config(self) -> dict:
    #     """创建测试环境配置"""
    #     current = self.read_all()
    #     print(current)
    #     test_config = current.copy()
    #
    #
    #     # 修改关键配置
    #     test_config['CONTAINER_NAME'] = f"{current['CONTAINER_NAME']}_test"
    #     test_config['PORT'] = str(int(current['PORT']) + 100)
    #     test_config['BASE_URL'] = current['BASE_URL'] + 'test/'
    #     test_config['STATIC_URL'] = test_config['BASE_URL'] + 'static/'
    #     test_config['POSTGRES_DB'] = f"{current['POSTGRES_DB']}_test"
    #
    #     return test_config

    def backup_and_switch_to_test(self):
        """备份生产配置并切换到测试环境"""

        current = self.read_all()
        test_config = current.copy()




        # 修改关键配置
        test_config['CONTAINER_NAME'] = f"{current['CONTAINER_NAME']}_test"
        test_config['PORT'] = str(int(current['PORT']) + 100)
        test_config['BASE_URL'] = current['BASE_URL'] + 'test/'
        test_config['STATIC_URL'] = test_config['BASE_URL'] + 'static/'
        test_config['POSTGRES_DB'] = f"{current['POSTGRES_DB']}_test"

        # 备份生产配置
        if os.path.exists(self.env_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.env_path}.backup_{timestamp}"
            os.rename(self.env_path, backup_path)
            print(f"生产配置已备份: {backup_path}")


        # 生成并写入测试配置
        for key, value in test_config.items():
            self.set(key, value)

        print("已切换到测试环境配置")



        return test_config

if __name__ == '__main__':
    env_manager = EnvManager()
    # 切换到测试环境
    test_config = env_manager.backup_and_switch_to_test()
    print("测试环境配置:")
    for key, value in test_config.items():
        print(f"{key}={value}")


