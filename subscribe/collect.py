# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 (Ultimate_Speed_V4_Fixed) 终极同步启动...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    valid_proxy_blocks = []
    proxy_names = []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    for url in urls:
        try:
            print(f"📥 正在获取原生数据: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                # 兼容 Base64
                if "proxies" not in content and len(content.strip()) > 64:
                    try: content = base64.b64decode(content + '==').decode('utf-8')
                    except: pass

                # 【核心融合逻辑】：保留原生缩进，按块抓取
                in_proxies = False
                current_block = []
                
                for line in content.splitlines():
                    if not line.strip(): continue
                    
                    # 侦测 proxies: 区域
                    if re.match(r'^proxies:', line):
                        in_proxies = True
                        continue
                    # 侦测到 rules: 或 proxy-groups: 就跳出当前源
                    elif in_proxies and re.match(r'^[a-zA-Z0-9_-]+:', line):
                        in_proxies = False
                        continue
                        
                    if in_proxies:
                        # 只要遇到 "- name:" 或者 "- {" 就认为是新节点的开始
                        if re.match(r'^\s*-\s*([\'"]?name[\'"]?:|\{)', line):
                            if current_block:
                                valid_proxy_blocks.append('\n'.join(current_block))
                            current_block = [line] # 开启新块
                        elif current_block:
                            # 后续的 type, server, ws-opts 原样塞进去，绝不破坏它原来的空格！
                            current_block.append(line)
                            
                # 补全最后一个节点
                if current_block:
                    valid_proxy_blocks.append('\n'.join(current_block))

        except Exception as e:
            print(f"⚠️ 跳过 {url}")

    # 过滤环节：踢出假节点
    final_blocks = []
    for block in valid_proxy_blocks:
        # 只要有 type 就是真节点（解决之前的 missing type 报错）
        if "type:" in block:
            name_match = re.search(r'name:\s*([^,\n}]+)', block)
            if name_match:
                raw_name = name_match.group(1).strip(' \'"')
                # 踢出广告
                if not any(ad in raw_name for ad in ["选择", "拦截", "官网", "提示", "流量", "更新"]):
                    final_blocks.append(block)
                    proxy_names.append(raw_name)

    print(f"🎯 精准过滤后剩余有效节点: {len(proxy_names)} 个")

    # 组装配置文件
    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    
    # 完美嵌入原生节点
    for block in final_blocks:
        # 如果有些源顶格写了 - name，我们帮它往右推两格，其他的保留原样
        if block.startswith('-'):
            lines.append('\n'.join('  ' + line for line in block.splitlines()))
        else:
            lines.append(block)

    lines.append("proxy-groups:")
    lines.append("  - name: 🚀 雅典娜全节点")
    lines.append("    type: url-test")                     # 改为自动测速并选择最快节点
    lines.append("    url: http://www.gstatic.com/generate_204") # 使用谷歌延迟测试接口
    lines.append("    interval: 300")                      # 每 5 分钟 (300秒) 自动测速一次
    lines.append("    tolerance: 50")                      # 容差 50ms (防止频繁切换节点)
    lines.append("    proxies:")
    
    if proxy_names:
        for name in proxy_names:
            lines.append(f"      - \"{name}\"")
    else:
        lines.append("      - DIRECT")
        
    lines.append("rules:")
    lines.append("  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"🏁 Ultimate_Speed_V4_Fixed 生成完毕，格式锁死！")

if __name__ == "__main__":
    main()
