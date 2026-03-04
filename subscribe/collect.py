# -*- coding: utf-8 -*-
import os, json, urllib.request, re

def main():
    print(f"🚀 雅典娜 AX6600 最后的冲刺：正在合成极致纯净订阅...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    nodes, node_names = [], []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res:
                content = res.read().decode('utf-8')
                for line in content.splitlines():
                    s_line = line.strip()
                    # 抓取节点定义，并提取节点名称
                    if s_line.startswith("- {") or (s_line.startswith("-") and "name:" in s_line and "type:" in s_line):
                        nodes.append(s_line)
                        # 提取节点名用于分组
                        name_match = re.search(r"name:\s*([^,}\s'\"]+|['\"][^'\"]+['\"])", s_line)
                        if name_match:
                            node_names.append(name_match.group(1))
        except: continue

    # 构建绝对合规的 YAML
    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    lines.extend([f"  {n}" if not n.startswith("  ") else n for n in nodes])
    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")
    # 填入节点名称，严格缩进
    lines.extend([f"      - {name}" for name in node_names])
    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ 大哥，{len(node_names)} 个节点已入库，这次格式绝对稳了！")

if __name__ == "__main__":
    main()
