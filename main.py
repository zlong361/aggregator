import requests
import re
import subprocess
import time
import yaml
import os

# =============================
# 1️⃣ 读取抓取网页
# =============================

def load_sources():
    with open("sources.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


# =============================
# 2️⃣ 抓取网页内容
# =============================

def fetch_nodes(url):
    print(f"正在抓取: {url}")
    try:
        r = requests.get(url, timeout=10)
        text = r.text

        # 提取常见协议
        patterns = [
            r"ss://[^\s\"']+",
            r"vmess://[^\s\"']+",
            r"trojan://[^\s\"']+",
            r"vless://[^\s\"']+"
        ]

        nodes = []
        for pattern in patterns:
            nodes += re.findall(pattern, text)

        return nodes

    except Exception as e:
        print("抓取失败:", e)
        return []


# =============================
# 3️⃣ 生成 clash 临时配置
# =============================

def generate_clash_config(nodes):
    config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "global",
        "proxies": [],
        "proxy-groups": [{
            "name": "auto",
            "type": "select",
            "proxies": []
        }],
        "rules": ["MATCH,auto"]
    }

    for i, node in enumerate(nodes):
        proxy = {
            "name": f"node{i}",
            "type": "ss",
            "server": "example.com",
            "port": 443,
            "cipher": "aes-128-gcm",
            "password": "password"
        }

        # ⚠️ 这里只是示例
        # 你可以改成真实解析
        config["proxies"].append(proxy)
        config["proxy-groups"][0]["proxies"].append(f"node{i}")

    with open("config.yaml", "w") as f:
        yaml.dump(config, f)


# =============================
# 4️⃣ 调用 clash 测速
# =============================

def test_speed():
    print("启动 clash 测速...")
    p = subprocess.Popen(["./clash-linux", "-f", "config.yaml"])
    time.sleep(10)

    results = {}

    for i in range(20):
        try:
            r = requests.get("http://127.0.0.1:9090/proxies/auto/delay?timeout=5000")
            data = r.json()
            delay = data.get("delay", 9999)
            results[f"node{i}"] = delay
        except:
            results[f"node{i}"] = 9999

    p.kill()
    return results


# =============================
# 5️⃣ 筛选好节点
# =============================

def filter_nodes(results, threshold=500):
    good = []
    for name, delay in results.items():
        if delay < threshold:
            good.append(name)
    return good


# =============================
# 主程序
# =============================

if __name__ == "__main__":

    urls = load_sources()

    all_nodes = []

    for url in urls:
        nodes = fetch_nodes(url)
        all_nodes += nodes

    print("抓取到节点数量:", len(all_nodes))

    generate_clash_config(all_nodes)

    results = test_speed()

    good_nodes = filter_nodes(results)

    print("优质节点数量:", len(good_nodes))

    with open("output.yaml", "w") as f:
        yaml.dump({"good_nodes": good_nodes}, f)

    print("完成 ✅ 结果已保存 output.yaml")
