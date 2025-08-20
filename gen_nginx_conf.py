from jinja2 import Template
import os
from dotenv import load_dotenv
import subprocess
import sys
# 加载环境变量
load_dotenv()

def gen_nginx_conf(path: str, port: int, host: str, static_root: str, server_name: str = "", output_dir: str = "/etc/nginx/conf.d/"):
    """
    生成 Nginx 配置文件
    :param path: 应用路径，如 '/app1'
    :param port: 后端服务端口
    :param host: 后端服务主机
    :param static_root: 静态文件根目录
    :param server_name: 域名（可选）
    :param output_dir: 输出目录
    """
    # 确保路径格式正确
    path = path.strip('/')
    # if path:
    #     path = f"/{path}"

    # 处理 static_root 路径（转为绝对路径）
    if not os.path.isabs(static_root):
        # 假设 static_root 相对于当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # static_root = os.path.join(script_dir, static_root)
        static_root = os.path.join(script_dir, 'static')


    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 配置文件名：基于路径或 server_name
    filename = f"{path.strip('/').replace('/', '_') or 'default'}.conf"
    full_path = os.path.join(output_dir, filename)

    # 读取模板
    template_path = 'nginx_template.conf'
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        template_str = f.read()

    template = Template(template_str)

    # 渲染配置
    nginx_config = template.render(
        path=path,
        port=port,
        host=host,
        static_root=static_root,
        server_name=server_name
    )

    # 写入文件
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(nginx_config)
    print(f"Nginx 配置已生成：{full_path}")




# ====================== 从环境变量读取配置 =====================
BASE_URL = os.getenv('BASE_URL', '').strip('/')
STATIC_ROOT = os.getenv('STATIC_ROOT', 'static').strip('/')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8000))
SERVER_NAME = os.getenv('SERVER_NAME', '127.0.0.1')

# 生成配置
gen_nginx_conf(
    path=BASE_URL,
    port=PORT,
    host=HOST,
    static_root=STATIC_ROOT,
    server_name=SERVER_NAME,
    output_dir="/etc/nginx/conf.d/"  # 可改为 './output/' 测试
)


try:
    # 测试 Nginx 配置
    result = subprocess.run(['nginx', "-t"], capture_output=True, text=True, check=True)
    out = result.stdout + result.stderr
    if "warn" in result.stderr:
        print(f"存在警告！请检查配置！\n{result.stderr}")
    elif "err" in result.stderr:
        print("配置错误！")
        sys.exit(0)

    if "syntax is ok" in out and "test is successful" in out:
        # 重新加载 Nginx
        print("重新加载 Nginx 服务...")
        result = subprocess.run(['nginx', "-s", "reload"], capture_output=True, text=True, check=True)
        print(f"Nginx 服务已成功重新加载")
        
    
except subprocess.CalledProcessError as e:
    print(f"❌ Nginx 命令执行失败: {e}")
    print(f"错误输出: {e.stderr}")
    print("请手动检查 Nginx 配置并执行 nginx -t && nginx -s reload")
    
except FileNotFoundError:
    print(f"❌ 找不到 nginx 命令")
    print("请确保 Nginx 已安装并在系统路径中，或指定正确的 nginx_bin_path")
    
except Exception as e:
    print(f"❌ 执行 Nginx 命令时发生未知错误: {e}")