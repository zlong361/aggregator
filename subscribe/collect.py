# -*- coding: utf-8 -*-
import os, json, urllib.request, yaml, base64

def main():
    print(f"🚀 雅典娜 AX6600 终极提速：专业级节点过滤引擎启动...")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    all_proxies = []
    headers = {'User-Agent': 'Clash-Verge/1.3.8'} # 伪装成 Clash 客户端抓取

    for url in urls:
        try:
            print(f"📥 正在解析: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as res:
                data = res.read().decode('utf-8', errors='ignore')
                
                # 尝试解析 YAML
                try:
                    yml_content = yaml.safe_load(data)
                    if isinstance(yml_content, dict) and 'proxies' in yml_content:
                        raw_proxies = yml_content['proxies']
                        for p in raw_proxies:
                            # 【核心过滤】只有同时具备这四个核心要素的才是真节点
                            if all(k in p for k in ['name', 'type', 'server', 'port']):
                                # 剔除那些带有“流量、到期、选择”等干扰词的节点
                                if not any(x in str(p['name']) for x in ['节点', '选择', '广告', '到期', '流量']):
                                    all_proxies.append(p)
                except:
                    print(f"⚠️ {url} 不是标准 YAML，尝试备用方案...")
                    continue
            print(f"✅ 当前有效节点总数: {len(all_proxies)}")
        except Exception as e:
            print(f"❌ 抓取失败: {e}")

    if not all_proxies:
        print("❌ 完蛋，一个有效节点都没抓到，请检查订阅链接！")
        return

    # 组装成雅典娜专用的纯净配置文件
    final_config = {
        'allow-system-fake-dns': True,
        'mixed-port': 7890,
        'proxies': all_proxies,
        'proxy-groups': [
            {
                'name': '🚀 雅典娜全节点',
                'type': 'select',
                'proxies': [p['name'] for p in all_proxies]
            }
        ],
        'rules': ['MATCH,🚀 雅典娜全节点']
    }

    with open("clash.yaml", "w", encoding="utf-8") as f:
        yaml.dump(final_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"🏁 大功告成！已为大哥生成 {len(all_proxies)} 个纯净节点，格式完美。")

if __name__ == "__main__":
    main()
