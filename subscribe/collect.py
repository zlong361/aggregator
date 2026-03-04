# -*- coding: utf-8 -*-
import os
import sys
import argparse

# 强制将当前目录加入路径，确保能写进去
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subscribe.utils import Tool
from subscribe.process import Processor

def main():
    parser = argparse.ArgumentParser(description="SubScribe Collector")
    parser.add_argument("-s", "--skip", action="store_true", help="skip check")
    parser.add_argument("-a", "--all", action="store_true", help="collect all")
    parser.add_argument("-o", "--overwrite", action="store_true", help="overwrite exist")
    # 增加一个参数占位防止报错
    parser.add_argument("--source", type=str, help="source path")
    
    args = parser.parse_args()

    # 【核心手术点 1】：强行锁死配置
    # 不管你传什么参数，我都让它只走本地配置，且绝对不开启内置采集
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')
    
    print(f"🚀 大哥，雅典娜专属模式已启动！")
    print(f"📂 正在加载配置文件: {config_path}")

    # 初始化处理器
    processor = Processor(config_path)
    
    # 【核心手术点 2】：物理屏蔽爬虫逻辑
    # 强制修改内存中的配置对象，确保 crawl 下的 enable 永远为 False
    if hasattr(processor, 'config') and 'crawl' in processor.config:
        processor.config['crawl']['enable'] = False
        print("🚫 已物理屏蔽全网采集（10231 节点模式已断开）")

    # 执行处理（只处理你在 JSON 里写的那两个链接）
    processor.run()
    
    print("✅ 雅典娜 Ultimate Speed 订阅处理完成！")

if __name__ == "__main__":
    main()
