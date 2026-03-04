# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 最后的战斗：正在执行纯净提取...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list, proxy_names = [], []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    for url in urls:
        try:
            print(f"📥 正在攻克: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                # 自动识别并解码 Base64
                if "proxies" not in content and len(content) > 100:
                    try:
                        content = base64.b64decode(content + '===').decode('utf-8')
                    except: pass

                # 【核心逻辑】只抓取包含 type, server, port 的真实节点
                # 这样就能完美过滤掉图 13-02-26 中的“节点选择”等广告行
                for line in content.splitlines():
                    s_line = line.strip()
                    if s_line.startswith("-") and "type:" in s_line and "server:" in s_line:
                        proxies_list.append(s_line)
                        # 提取节点名称用于分组
                        name_match = re.search(r"name:\s*([^,}\s'\"]+|['\"][^'\"]+['\"])", s_line)
                        if name_match:
                            proxy_names.append(name_match.group(1).strip("'\""))
            print(f"✅ 已提取有效节点: {len(proxy_names)}")
        except Exception as e:
            print(f"⚠️ 跳过失效链接: {url}")

    if not proxy_names:
        print("❌ 警告：未发现有效节点！请检查订阅源链接是否有效。")
        return

    # 手动构建标准 YAML，确保缩进绝对正确
    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    # 填入节点详情
    for p in proxies_list:
        lines.append(f"  {p}" if not p.startswith("  ") else p)
    
    # 填入分组信息
    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")
    for name in proxy_names:
        lines.append(f"      - \"{name}\"")
    
    # 填入规则
    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🎉 大功告成！已为雅典娜准备好 {len(proxy_names)} 个纯净节点。")

if __name__ == "__main__":
    main()
