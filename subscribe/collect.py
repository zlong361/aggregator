# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64, socket

# 【核心功能】在线测速：确保节点在写入前是活的
def is_live(server, port):
    try:
        # 设置3秒超时，GitHub环境网络极快，3秒不通基本就是废了
        port_num = int(port)
        with socket.create_connection((server, port_num), timeout=3):
            return True
    except:
        return False

def main():
    print(f"🚀 雅典娜 AX6600：开始全流程『从零重构』部署...")
    
    # 1. 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    if not os.path.exists(config_path):
        print("❌ 错误：找不到 config.default.json")
        return
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list = []
    proxy_names = []
    seen_servers = set()
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    # 2. 抓取与清洗
    for url in urls:
        try:
            print(f"📡 正在拉取源: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                # Base64 解码逻辑
                if "proxies" not in content and len(content.strip()) > 64:
                    try: content = base64.b64decode(content + '==').decode('utf-8')
                    except: pass

                # 暴力切割：无视原有缩进，只认节点起始标志
                blocks = re.split(r'^\s*-\s*name:|^name:', content, flags=re.MULTILINE)
                for block in blocks[1:]:
                    if not block.strip(): continue
                    lines = block.strip().split('\n')
                    
                    # 提取节点名
                    name_raw = lines[0].split(':', 1)[-1].strip().strip("'\"")
                    if not name_raw or any(ad in name_raw for ad in ["选择", "拦截", "更新", "官网"]):
                        continue
                    
                    # 提取属性零件
                    attrs = {}
                    for l in lines[1:]:
                        if ':' in l:
                            k, v = l.split(':', 1)
                            attrs[k.strip()] = v.strip()
                    
                    # 3. 核心校验与测速
                    if 'type' in attrs and 'server' in attrs and 'port' in attrs:
                        server = attrs['server']
                        port = attrs['port']
                        server_key = f"{server}:{port}"
                        
                        if server_key in seen_servers: continue
                        
                        # 在 GitHub 端进行预测试
                        print(f"🔎 正在预检: {name_raw[:15]}...", end="")
                        if is_live(server, port):
                            print(" [✅ 活]")
                            seen_servers.add(server_key)
                            
                            # 【标准格式化输出】强制 2/4 空格对齐，解决导入报错
                            formatted = [f"  - name: \"{name_raw}\""]
                            for key, val in attrs.items():
                                if key != "name": # 过滤重复键
                                    formatted.append(f"    {key}: {val}")
                            
                            proxies_list.append("\n".join(formatted))
                            proxy_names.append(name_raw)
                        else:
                            print(" [❌ 死]")
        except Exception as e:
            print(f"⚠️ 采集出错: {e}")
            continue

    # 4. 组装完整 Clash YAML
    final_output = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    final_output.extend(proxies_list)
    
    # 自动优选策略组
    final_output.append("proxy-groups:")
    final_output.append("  - name: \"🚀 雅典娜智能优选\"")
    final_output.append("    type: url-test")
    final_output.append("    url: http://www.gstatic.com/generate_204")
    final_output.append("    interval: 300")
    final_output.append("    tolerance: 50")
    final_output.append("    proxies:")
    
    if proxy_names:
        for p in proxy_names:
            final_output.append(f"      - \"{p}\"")
    else:
        final_output.append("      - DIRECT")
    
    # 简易规则，让所有流量走优选组
    final_output.append("rules:")
    final_output.append("  - MATCH,\"🚀 雅典娜智能优选\"")

    # 5. 最终写入
    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
    
    print(f"\n🏁 全部完成！共筛选出 {len(proxy_names)} 个高品质活节点。")

if __name__ == "__main__":
    main()
