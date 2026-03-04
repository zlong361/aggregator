# -*- coding: utf-8 -*-
import os
import json
import urllib.request

def main():
    print(f"🚀 雅典娜 AX6600 终极提速模式启动！")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    
    nodes_list = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for url in urls:
        try:
            print(f"📥 正在提取: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read().decode('utf-8')
                # 【核心逻辑】只抓取以 - name: 或 - { 开头的节点行，彻底避开 invalid yaml
                for line in data.splitlines():
                    if line.strip().startswith("- {") or (line.strip().startswith("-") and "name:" in line):
                        nodes_list.append(line)
            print(f"✅ 当前累计节点数: {len(nodes_list)}")
        except Exception as e:
            print(f"⚠️ 抓取失败 {url}: {e}")

    # 强行拼装成合法的 Clash 配置文件
    final_yaml = "proxies:\n" + "\n".join(nodes_list)

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write(final_yaml)
    
    print(f"🏁 任务圆满结束！雅典娜专属订阅已就绪。")

if __name__ == "__main__":
    main()
