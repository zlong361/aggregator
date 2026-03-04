# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 终极排查：正在执行原生块提取...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list, proxy_names = [], []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    for url in urls:
        try:
            print(f"📥 正在解析: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                # 处理 Base64 加密源
                if "proxies" not in content and len(content) > 100:
                    try:
                        content = base64.b64decode(content + '===').decode('utf-8')
                    except: pass

                # 【核心逻辑升级】使用正则匹配整个节点块 (从 - name 到下一个 - name 之前)
                # 这样即使 type 和 server 在不同行也能被精准抓到
                blocks = re.findall(r"(?m)^- name:[\s\S]+?(?=\n- name:|$)", content)
                
                for block in blocks:
                    # 只有同时具备核心三要素的才是真节点
                    # 自动过滤掉图 13-02-26 里的“广告/文字提示行”
                    if "type:" in block and "server:" in block and "port:" in block:
                        clean_block = block.strip()
                        proxies_list.append(clean_block)
                        # 提取节点名用于分组
                        n_match = re.search(r"name:\s*(.+)", clean_block)
                        if n_match:
                            name = n_match.group(1).strip().strip("'\"")
                            # 过滤掉带有“节点选择”等广告词的节点
                            if not any(x in name for x in ["选择", "拦截", "官网", "提示"]):
                                proxy_names.append(name)

            print(f"✅ 当前有效节点总数: {len(proxy_names)}")
        except Exception as e:
            print(f"⚠️ 跳过失效链接: {url}")

    # 构建标准 YAML 字符串
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
    if proxy_names:
        for name in proxy_names: lines.append(f"      - \"{name}\"")
    else:
        lines.append("      - DIRECT") # 防崩溃保底
    
    # 填入规则
    lines.append("rules:\n  - MATCH,🚀 雅典娜全节点")

    # 写入文件
    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🏁 处理完毕！成功入库 {len(proxy_names)} 个节点。")

if __name__ == "__main__":
    main()
