# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import re
import base64
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ==========================
# 多线程测速函数
# ==========================
def test_node_speed(server, port, timeout=3):
    try:
        start = time.time()
        sock = socket.create_connection((server, int(port)), timeout=timeout)
        sock.close()
        delay = int((time.time() - start) * 1000)
        return True, delay
    except:
        return False, None


# ==========================
# 主程序
# ==========================
def main():
    print("🚀 雅典娜 AX6600 Ultimate_Speed_V5_Multithreading 启动...")

    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]

    valid_proxy_blocks = []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    # ==========================
    # 抓取节点
    # ==========================
    for url in urls:
        try:
            print(f"📥 获取数据: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')

                if "proxies" not in content and len(content.strip()) > 64:
                    try:
                        content = base64.b64decode(content + '==').decode('utf-8')
                    except:
                        pass

                in_proxies = False
                current_block = []

                for line in content.splitlines():
                    if not line.strip():
                        continue

                    if re.match(r'^proxies:', line):
                        in_proxies = True
                        continue
                    elif in_proxies and re.match(r'^[a-zA-Z0-9_-]+:', line):
                        in_proxies = False
                        continue

                    if in_proxies:
                        if re.match(r'^\s*-\s*([\'"]?name[\'"]?:|\{)', line):
                            if current_block:
                                valid_proxy_blocks.append('\n'.join(current_block))
                            current_block = [line]
                        elif current_block:
                            current_block.append(line)

                if current_block:
                    valid_proxy_blocks.append('\n'.join(current_block))

        except Exception:
            print(f"⚠️ 跳过 {url}")

    print(f"📦 抓取到原始节点: {len(valid_proxy_blocks)} 个")

    # ==========================
    # 多线程测速
    # ==========================
    final_nodes = []

    def process_block(block):
        if "type:" not in block:
            return None

        name_match = re.search(r'name:\s*([^,\n}]+)', block)
        server_match = re.search(r'server:\s*([^\n]+)', block)
        port_match = re.search(r'port:\s*(\d+)', block)

        if not (name_match and server_match and port_match):
            return None

        raw_name = name_match.group(1).strip(' \'"')
        server = server_match.group(1).strip()
        port = port_match.group(1).strip()

        # 过滤广告
        if any(ad in raw_name for ad in ["选择", "拦截", "官网", "提示", "流量", "更新"]):
            return None

        ok, delay = test_node_speed(server, port)

        if ok:
            print(f"⚡ {raw_name} 延迟 {delay} ms")
            return (delay, raw_name, block)
        else:
            print(f"❌ {raw_name} 不可连接")
            return None

    # 线程池数量（可以调整）
    max_workers = 50

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_block, block) for block in valid_proxy_blocks]

        for future in as_completed(futures):
            result = future.result()
            if result:
                final_nodes.append(result)

    # ==========================
    # 排序（按延迟从低到高）
    # ==========================
    final_nodes.sort(key=lambda x: x[0])

    print(f"🎯 可用节点数量: {len(final_nodes)}")

    # ==========================
    # 生成 Clash 配置
    # ==========================
    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]

    proxy_names = []

    for delay, name, block in final_nodes:
        proxy_names.append(name)

        if block.startswith('-'):
            lines.append('\n'.join('  ' + line for line in block.splitlines()))
        else:
            lines.append(block)

    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")

    if proxy_names:
        for name in proxy_names:
            lines.append(f"      - \"{name}\"")
    else:
        lines.append("      - DIRECT")

    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("🏁 Ultimate_Speed_V5_Multithreading 生成完毕！")


if __name__ == "__main__":
    main()
