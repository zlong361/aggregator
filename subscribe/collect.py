# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 终极排查：开始深度过滤...")
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
                
                # 自动识别 Base64 并解密
                if "proxies" not in content and (len(content) % 4 == 0 or "proxies" in base64.b64decode(content[:100]).decode('utf-8', 'ignore')):
                    try: content = base64.b64decode(content).decode('utf-8')
                    except: pass

                # 【核心逻辑升级】使用正则匹配整个节点块 (从 - name 到下一个 - name)
                # 这样即使 type 和 server 在不同行也能被抓到
                blocks = re.findall(r"(?m)^- name:[\s\S]+?(?=\n- name:|$)", content)
                
                for block in blocks:
                    # 只有同时具备核心三要素的才是真节点，过滤掉图 13-02-26 里的“广告提示行”
                    if "type:" in block and "server:" in block and "port:" in block:
                        # 过滤常见的广告关键词
                        if not any(x in block for x in ["节点选择", "广告拦截", "自动选择", "官网"]):
                            proxies_list.append(block.strip())
                            # 提取名字用于分组
                            n_match = re.search(r"name:\s*(.+)", block)
                            if n_match:
                                proxy_names.append(n_match.group(1).strip().strip("'\""))

            print(f"✅ 当前已提取真节点总数: {len(proxy_names)}")
        except Exception as e:
            print(f"⚠️ 跳过链接: {url}")

    # 无论是否抓到节点，都生成文件，防止 Actions 报 pathspec 错误
    lines = ["allow-system-fake-dns: true", "mixed-port: 7890", "proxies:"]
    for p in proxies_list:
        lines.append(f"  {p}" if not p.startswith("  ") else p)
    
    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: select")
    lines.append("    proxies:")
    if proxy_names:
        for name in proxy_names: lines.append(f"      - \"{name}\"")
    else:
        lines.append("      - DIRECT")
    
    lines.append("rules:\n  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🏁 处理完毕！成功入库 {len(proxy_names)} 个节点。")

if __name__ == "__main__":
    main()
