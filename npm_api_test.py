import requests

# 配置信息 - 请根据你的实际环境修改
NPM_URL = "http://192.168.64.128:81"  # 例如: http://192.168.1.100:81
USERNAME = "hongzhe2022@163.com"
PASSWORD = "GNPnx2y24WY9bjU"

def get_auth_token():
    """获取认证令牌"""
    url = f"{NPM_URL}/api/tokens"
    payload = {
        "identity": USERNAME,
        "secret": PASSWORD
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["token"]
    except requests.exceptions.RequestException as e:
        print(f"获取令牌失败: {e}")
        return None

def get_proxy_hosts(token):
    """获取所有代理主机列表"""
    url = f"{NPM_URL}/api/nginx/proxy-hosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取代理主机失败: {e}")
        return None

if __name__ == "__main__":
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        exit(1)
    
    print("成功获取令牌")
    
    # 获取代理主机列表
    proxy_hosts = get_proxy_hosts(token)
    if proxy_hosts:
        print(f"\n共找到 {len(proxy_hosts)} 个代理主机:")
        for host in proxy_hosts:
            print(f"- {host['domain_names'][0]} -> {host['forward_host']}:{host['forward_port']}")
