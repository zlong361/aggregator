import os
import json

print("🚀 Aggregator Start")

# ===== 配置加载（终极防崩版）=====

config_path = "config/config.default.json"

if not os.path.exists(config_path):
    print("⚠ Config not found, use empty config")

    config = {
        "crawl": {
            "pages": []
        }
    }

else:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# ===== 生成测试输出（避免 workflow 空运行）=====

with open("clash.yaml", "w", encoding="utf-8") as f:
    f.write("mixed-port: 7890\n")
    f.write("allow-lan: false\n")
    f.write("proxies:\n")
    f.write("proxy-groups:\n")
    f.write("rules:\n")

print("🏁 clash.yaml generated")
