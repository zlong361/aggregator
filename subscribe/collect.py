# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import re

def main():
    print(f"🚀 雅典娜 AX6600 终极提速模式：纯净节点提取中...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    
    nodes_list = []
    # 模拟浏览器头，防止被拦截
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for url in urls:
        try:
            print(f"📥 正在抓取: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read().decode('utf-8')
                
                # 核心逻辑：只匹配满足 Clash 节点格式的行
                # 寻找形如 "- name: XXX, type: XXX, ..." 的内容
                for line in data.splitlines():
                    s_line = line.strip()
                    # 识别标准的 YAML 节点项
                    if s_line.startswith("- {") or (s_line.startswith("-") and "name:" in s_line and "type:" in s_line):
                        nodes_list.append(s_line)
            print(f"✅ 当前已提取纯净节点: {len(nodes_list)} 个")
        except Exception as e:
            print(f"⚠️ 抓取失败 {url}: {e}")

    # 【关键】构建标准格式，确保 OpenClash 100% 识别
    # 加上基础配置，防止导入时因为缺少某些字段报错
    final_yaml = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    final_yaml.extend(nodes_list)
    
    # 加上一个空的代理组，防止 Clash 因为没有 Proxy Group 报错
    final_yaml.extend([
        "proxy-groups:",
        "  - name: 🚀 雅典娜全节点",
        "    type: select",
        "    proxies:",
    ])
    # 将提取到的节点名字加进组里
    for node in nodes_list:
        # 提取 name: 之后的内容
        match = re.search(r"name:\s*([^,}\s'\"]+|['\"][^'\"]+['\"])", node)
        if match:
            node_name = match.group(1)
            final_yaml.append(f"      - {node_name}")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(final_yaml))
    
    print(f"🏁 任务圆满结束！雅典娜专属纯净订阅已写出。")

if __name__ == "__main__":
    main()
