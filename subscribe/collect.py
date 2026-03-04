# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 最后的终极大杀器：正在剔除无效干扰项...")
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
                raw_data = res.read()
                try: content = raw_data.decode('utf-8')
                except: content = raw_data.decode('latin-1')

                # Base64 解码逻辑保持不变
                if "proxies" not in content and len(content) > 100:
                    try:
                        missing_padding = len(content) % 4
                        if missing_padding: content += '=' * (4 - missing_padding)
                        content = base64.b64decode(content).decode('utf-8')
                    except: pass 

                for line in content.splitlines():
                    s_line = line.strip()
                    # 【关键修正】必须同时包含 name: 和 type: 才是真正的节点！
                    # 这样就能过滤掉图 13-02-26 中那些“手动切换”之类的假节点
                    if s_line.startswith("-") and "name:" in s_line and "type:" in s_line:
                        nodes.append(s_line)
                        name_match = re.search(r"name:\s*([^,}\s'\"]+|['\"][^'\"]+['\"])", s_line)
                        if name_match: node_names.append(name_match.group(1))
            print(f"✅ 成功提取有效节点: {len(node_names)}")
        except: continue

    # 构建 YAML
    lines = ["proxies:"]
    lines.extend([f"  {n}" if not n.startswith("  ") else n for n in nodes])
    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")
    lines.extend([f"      - {name}" for name in node_names])
    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🎉 雅典娜订阅合成完毕！共入库 {len(node_names)} 个真实节点。")

if __name__ == "__main__":
    main()
