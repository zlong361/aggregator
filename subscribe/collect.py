# -*- coding: utf-8 -*-
import os
import json
import urllib.request

def main():
    print(f"🚀 大哥，雅典娜专属增强模式启动！")
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    urls = [page['url'] for page in config.get('crawl', {}).get('pages', []) if page.get('enable')]
    
    final_content = ""
    # 模拟浏览器头，防止被对方服务器拦截导致返回空白
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for url in urls:
        try:
            print(f"📥 正在抓取: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read().decode('utf-8')
                if data.strip():
                    final_content += data + "\n"
                    print(f"✅ 抓取成功，获得数据大小: {len(data)} 字节")
                else:
                    print(f"❌ 抓取失败: {url} 返回内容为空")
        except Exception as e:
            print(f"⚠️ 出错了 {url}: {e}")

    if not final_content.strip():
        final_content = "# 警告：所有订阅源抓取失败，请检查链接是否有效\n"

    output_path = "clash.yaml" 
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"✅ 任务结束，文件已写出。")

if __name__ == "__main__":
    main()
