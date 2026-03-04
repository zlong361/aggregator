# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600：正在执行标准格式化抓取...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list, proxy_names = [], []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')
                if "proxies" not in content and len(content.strip()) > 64:
                    try: content = base64.b64decode(content + '==').decode('utf-8')
                    except: pass

                # 暴力切割：按 "- name:" 切分
                blocks = re.split(r'^-?\s*name:', content, flags=re.MULTILINE)
                for block in blocks[1:]:
                    if "type:" in block and "server:" in block:
                        # --- 核心修正：重新构造标准 YAML 块 ---
                        lines = block.strip().split('\n')
                        name_line = lines[0].strip().strip("'\"")
                        
                        # 提取核心参数
                        info = {"name": name_line}
                        for l in lines[1:]:
                            if ':' in l:
                                k, v = l.split(':', 1)
                                info[k.strip()] = v.strip()
                        
                        # 过滤掉广告
                        if any(x in info['name'] for x in ["选择", "拦截", "官网", "流量"]): continue
                        
                        # 按照 Clash 标准缩进重新写死
                        formatted = [f"  - name: \"{info['name']}\""]
                        for key, value in info.items():
                            if key != "name":
                                formatted.append(f"    {key}: {value}")
                        
                        proxies_list.append("\n".join(formatted))
                        proxy_names.append(info['name'])
            print(f"✅ 成功提取并格式化: {len(proxy_names)} 个节点")
        except: continue

    # 构造最终 YAML
    final_yaml = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    final_yaml.extend(proxies_list)
    
    final_yaml.append("proxy-groups:")
    final_yaml.append("  - name: 🚀 雅典娜全节点")
    final_yaml.append("    type: select")
    final_yaml.append("    proxies:")
    for name in proxy_names:
        final_yaml.append(f"      - \"{name}\"")
    
    final_yaml.append("rules:\n  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(final_yaml))
    print(f"🏁 格式化完成！生成的 clash.yaml 现在绝对标准。")

if __name__ == "__main__":
    main()
