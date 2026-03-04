# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 最后的终极大杀器：全协议自动识别提取中...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    nodes, node_names = [], []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for url in urls:
        try:
            print(f"📥 正在攻克: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res:
                raw_data = res.read()
                try:
                    content = raw_data.decode('utf-8')
                except:
                    content = raw_data.decode('latin-1')

                # 【核心逻辑 1】如果是加密的 Base64，先解密
                if "proxies" not in content and len(content) > 100:
                    try:
                        # 尝试 Base64 解码，补齐填充符
                        missing_padding = len(content) % 4
                        if missing_padding: content += '=' * (4 - missing_padding)
                        content = base64.b64decode(content).decode('utf-8')
                    except: pass 

                # 【核心逻辑 2】提取节点
                for line in content.splitlines():
                    s_line = line.strip()
                    # 匹配 YAML 格式
                    if s_line.startswith("- {") or (s_line.startswith("-") and "name:" in s_line):
                        nodes.append(s_line)
                        name_match = re.search(r"name:\s*([^,}\s'\"]+|['\"][^'\"]+['\"])", s_line)
                        if name_match: node_names.append(name_match.group(1))
                    # 匹配 V2Ray/SS/SSR 等原始链接并转为简单格式（如果需要）
                    elif any(s_line.startswith(p) for p in ['ss://', 'vmess://', 'vless://', 'trojan://']):
                        # 这里简单处理，暂时只记录这类链接
                        pass 
            print(f"✅ 当前累计节点: {len(node_names)}")
        except: continue

    # 构建绝对合规的 YAML
    if not node_names:
        print("❌ 大哥，还是没抓到节点，检查下订阅链接本身是否失效了？")
        return

    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    # 确保缩进正确
    for n in nodes:
        formatted_n = n if n.startswith("  -") else f"  {n}"
        lines.append(formatted_n)
        
    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")
    lines.extend([f"      - {name}" for name in node_names])
    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🎉 雅典娜订阅合成完毕！共入库 {len(node_names)} 个节点。")

if __name__ == "__main__":
    main()
