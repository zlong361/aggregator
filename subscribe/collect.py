# -*- coding: utf-8 -*-
import os, json, urllib.request, re, base64

def main():
    print(f"🚀 雅典娜 AX6600 深度提取：正在扫描订阅源...")
    
    # 1. 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    proxies_list, proxy_names = [], []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    # 2. 遍历抓取
    for url in urls:
        try:
            print(f"📡 正在攻克: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')
                
                # 如果是 Base64 格式则解密
                if "proxies" not in content and len(content.strip()) > 64:
                    try: content = base64.b64decode(content + '==').decode('utf-8')
                    except: pass

                # 【核心逻辑】按 "- name:" 分割整个文件，提取节点块
                # 这样可以解决图 13-02-26 中的多行匹配问题
                blocks = re.split(r'^- name:', content, flags=re.MULTILINE)
                
                for block in blocks[1:]: # 跳过第一个分割符前的空内容
                    # 只有同时具备核心三要素的块，才是“真节点”
                    # 这能完美解决图 13-01-58 的 missing type 错误
                    if "type:" in block and "server:" in block and "port:" in block:
                        full_proxy = "- name: " + block.strip()
                        # 提取名字用于分组
                        name_match = re.search(r'name:\s*(.*)', "- name: " + block)
                        if name_match:
                            p_name = name_match.group(1).strip().strip("'\"")
                            # 过滤掉广告、提示、选择行
                            if not any(x in p_name for x in ["选择", "拦截", "官网", "提示", "流量"]):
                                proxies_list.append(full_proxy)
                                proxy_names.append(p_name)

            print(f"✅ 成功提取有效节点: {len(proxy_names)}")
        except Exception as e:
            print(f"❌ 链接请求失败: {url}")

    # 3. 强制生成合规文件 (防止图 13-09-44 的 pathspec 错误)
    yaml_content = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "proxies:"
    ]
    
    for p in proxies_list:
        yaml_content.append(f"  {p}" if not p.startswith("  ") else p)
    
    yaml_content.append("proxy-groups:")
    yaml_content.append("  - name: 🚀 雅典娜全节点")
    yaml_content.append("    type: select")
    yaml_content.append("    proxies:")
    
    if proxy_names:
        for name in proxy_names:
            yaml_content.append(f"      - \"{name}\"")
    else:
        yaml_content.append("      - DIRECT")
    
    yaml_content.append("rules:\n  - MATCH,🚀 雅典娜全节点")

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(yaml_content))
    
    print(f"🏁 任务完成！共入库 {len(proxy_names)} 个节点，配置已就绪。")

if __name__ == "__main__":
    main()
