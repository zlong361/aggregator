# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600：开始深度重构部署...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list = []
    proxy_names = []
    seen_servers = set() # 用于过滤重复服务器
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    for url in urls:
        try:
            print(f"📡 扫描源: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')
                if "proxies" not in content and len(content.strip()) > 64:
                    try: content = base64.b64decode(content + '==').decode('utf-8')
                    except: pass

                # 暴力切割：打破原有乱序缩进，按节点特征重切
                blocks = re.split(r'^\s*-\s*name:|^name:', content, flags=re.MULTILINE)
                for block in blocks[1:]:
                    if not block.strip(): continue
                    lines = block.strip().split('\n')
                    
                    # 提取名字
                    name_raw = lines[0].split(':', 1)[-1].strip().strip("'\"")
                    if not name_raw or any(ad in name_raw for ad in ["选择", "拦截", "更新", "官网"]):
                        continue
                    
                    # 提取属性并重排
                    attrs = {}
                    for l in lines[1:]:
                        if ':' in l:
                            k, v = l.split(':', 1)
                            attrs[k.strip()] = v.strip()
                    
                    # 核心校验：必须有 type 和 server，且不重复
                    if 'type' in attrs and 'server' in attrs:
                        server_key = f"{attrs['server']}:{attrs.get('port', '')}"
                        if server_key in seen_servers: continue
                        seen_servers.add(server_key)
                        
                        # 【标准格式重构】
                        formatted = [f"  - name: \"{name_raw}\""]
                        for key, val in attrs.items():
                            if key != "name": # 排除重复键
                                formatted.append(f"    {key}: {val}")
                        
                        proxies_list.append("\n".join(formatted))
                        proxy_names.append(name_raw)

            print(f"✅ 当前有效节点累计: {len(proxy_names)}")
        except: continue

    # 构造终极 YAML
    final_output = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    final_output.extend(proxies_list)
    
    # 自动测速负载均衡组
    final_output.append("proxy-groups:")
    final_output.append("  - name: \"🚀 雅典娜智能优选\"")
    final_output.append("    type: url-test")
    final_output.append("    url: http://www.gstatic.com/generate_204")
    final_output.append("    interval: 300")   # 每5分钟测速一次
    final_output.append("    tolerance: 50")   # 延迟差小于50ms不频繁切
    final_output.append("    proxies:")
    
    if proxy_names:
        for p in proxy_names:
            final_output.append(f"      - \"{p}\"")
    else:
        final_output.append("      - DIRECT")
    
    final_output.append("rules:")
    final_output.append("  - MATCH,\"🚀 雅典娜智能优选\"")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print(f"🏁 重新部署完成！共整理 {len(proxy_names)} 个高品质节点，格式已锁死。")

if __name__ == "__main__":
    main()
