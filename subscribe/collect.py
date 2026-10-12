# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64, socket

# 【核心：云端体检】直接在 GitHub 服务器上拨号测试节点存活
def is_live(server, port):
    try:
        port_num = int(port)
        # GitHub 网络极佳，3秒连不上基本就是废节点
        with socket.create_connection((server, port_num), timeout=3):
            return True
    except:
        return False

def main():
    print(f"🚀 雅典娜 AX6600 (Ultimate_V7_Check) 从零重构启动...")
    
    # 路径初始化
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config', 'config.default.json')
    
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

    for url in urls:
        try:
            print(f"📡 正在拉取源: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                raw_data = res.read().decode('utf-8', errors='ignore')
                
                # 兼容 Base64 订阅
                content = raw_data
                if "proxies" not in raw_data and len(raw_data.strip()) > 64:
                    try: content = base64.b64decode(raw_data + '==').decode('utf-8')
                    except: pass

                # 【暴力格式清洗】解决你之前的缩进报错问题
                blocks = re.split(r'^\s*-\s*name:|^name:', content, flags=re.MULTILINE)
                for block in blocks[1:]:
                    if not block.strip(): continue
                    lines = block.strip().split('\n')
                    
                    # 提取节点名称并清洗广告
                    name_raw = lines[0].split(':', 1)[-1].strip().strip("'\"")
                    if not name_raw or any(ad in name_raw for ad in ["流量", "更新", "重置", "官网"]):
                        continue
                    
                    # 提取属性零件
                    attrs = {}
                    for l in lines[1:]:
                        if ':' in l:
                            k, v = l.split(':', 1)
                            attrs[k.strip().lower()] = v.strip()
                    
                    # 【核心：测速通过才准入库】
                    if 'server' in attrs and 'port' in attrs and 'type' in attrs:
                        srv, prt = attrs['server'], attrs['port']
                        server_key = f"{srv}:{prt}"
                        
                        if server_key in seen_servers: continue
                        
                        print(f"🔎 预检: {name_raw[:15]}...", end="")
                        if is_live(srv, prt):
                            print(" [✅ 活]")
                            seen_servers.add(server_key)
                            
                            # 【金牌重组】强制锁定 2/4 空格标准缩进
                            formatted_node = [f"  - name: \"{name_raw}\""]
                            # 优先写核心三要素
                            for k in ['type', 'server', 'port']:
                                if k in attrs: formatted_node.append(f"    {k}: {attrs[k]}")
                            # 再写其他属性
                            for k, v in attrs.items():
                                if k not in ['type', 'server', 'port', 'name']:
                                    formatted_node.append(f"    {k}: {v}")
                            
                            proxies_list.append("\n".join(formatted_node))
                            proxy_names.append(name_raw)
                        else:
                            print(" [❌ 死]")

        except Exception as e:
            print(f"⚠️ 跳过异常源: {e}")
            continue

    # 构造最终 YAML 文件
    final_yaml = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    final_yaml.extend(proxies_list)
    
    # 策略组逻辑
    final_yaml.append("proxy-groups:")
    final_yaml.append("  - name: \"🚀 雅典娜智能优选\"")
    final_yaml.append("    type: url-test")
    final_yaml.append("    url: http://www.gstatic.com/generate_204")
    final_yaml.append("    interval: 300")
    final_yaml.append("    proxies:")
    
    if proxy_names:
        for p in proxy_names:
            final_yaml.append(f"      - \"{p}\"")
    else:
        final_yaml.append("      - DIRECT")
    
    final_yaml.append("rules:")
    final_yaml.append("  - MATCH,\"🚀 雅典娜智能优选\"")

    # 写入文件
    out_path = os.path.join(base_dir, "clash.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(final_yaml))
    
    print(f"\n🏁 全部完成！本次从零部署筛选出 {len(proxy_names)} 个高品质活节点。")

if __name__ == "__main__":
    main()
