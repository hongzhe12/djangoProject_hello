import sys

from env_manager import EnvManager

env_manager = EnvManager()
data = env_manager.read_all()
for i in data.values():
    if 'test/' in i:
        print("已经存在测试环境！")
        sys.exit(0)

# 切换到测试环境
test_config = env_manager.backup_and_switch_to_test()
print("成功！请重新部署")
