# ===============================
# Ultimate Aggregator Speed Core
# GitHub Actions Industrial Version
# ===============================

import os
import json
import urllib.request
import base64
import re
import subprocess
import requests
import time


CONFIG_FILE = "clash.yaml"
TEMP_FILE = "clash_temp.yaml"


# ==============================
# Clash Core 启动
# ==============================
def start_clash():
    subprocess.Popen(
        ["./clash", "-f", TEMP_FILE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(6)


# ==============================
# 真 API 测速
# ==============================
def clash_delay_test(name):
    try:
        url = f"http://127.0.0.1:9090/proxies/{name}/delay?timeout=5000&url=http://www.gstatic.com/generate_204"

        r = requests.get(url, timeout=8)
        data = r.json()

        if "delay" in data and data["delay"] > 0:
            return data["delay"]

    except:
        pass

    return None


# ==============================
# 主流程
# ==============================
def main():

    print("🚀 Ultimate Aggregator Industrial Version Start")

    # ===== 读取配置源 =====
    config_path = "config/config.default.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    urls = [
        page["url"]
        for page in config.get("crawl", {}).get("pages", [])
        if page.get("enable")
    ]

    proxy_blocks = []

    # ===== 抓取订阅 =====
    for url in urls:

        try:
            print("📥 Fetch:", url)

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Clash"}
            )

            with urllib.request.urlopen(req, timeout=15) as res:

                content = res.read().decode("utf-8", errors="ignore")

                # Base64 兼容
                if "proxies" not in content and len(content.strip()) > 64:
                    try:
                        content = base64.b64decode(content + "==").decode()
                    except:
                        pass

                in_proxy = False
                block = []

                for line in content.splitlines():

                    if re.match(r"^proxies:", line):
                        in_proxy = True
                        continue

                    elif in_proxy and re.match(r"^[a-zA-Z0-9_-]+:", line):
                        in_proxy = False
                        continue

                    if in_proxy:

                        if re.match(r"^\s*-\s*", line):
                            if block:
                                proxy_blocks.append("\n".join(block))
                            block = [line]

                        elif block:
                            block.append(line)

                if block:
                    proxy_blocks.append("\n".join(block))

        except:
            print("⚠ Skip:", url)

    print("📦 Raw Nodes:", len(proxy_blocks))

    # ===== 生成临时 Clash 配置 =====
    proxy_names = []

    lines = [
        "mixed-port: 7890",
        "allow-lan: false",
        "mode: Rule",
        "log-level: silent",
        "external-controller: 127.0.0.1:9090",
        "proxies:"
    ]

    for block in proxy_blocks:

        if block.startswith("-"):
            lines.append("\n".join("  " + l for l in block.splitlines()))
        else:
            lines.append(block)

        name_match = re.search(r"name:\s*\"?([^\n\"]+)\"?", block)

        if name_match:
            proxy_names.append(name_match.group(1))

    lines.append("proxy-groups:")
    lines.append("  - name: AUTO")
    lines.append("    type: select")
    lines.append("    proxies:")

    for name in proxy_names:
        lines.append(f"      - \"{name}\"")

    lines.append("rules:")
    lines.append("  - MATCH,AUTO")

    # 写临时配置
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ===== 下载 Clash Core（Actions 已经下载也可）=====
    if not os.path.exists("./clash"):
        print("📦 Download clash core")
        subprocess.run([
            "wget",
            "https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz"
        ])

        subprocess.run(["gunzip", "clash-linux-amd64.gz"])
        subprocess.run(["chmod", "+x", "clash-linux-amd64"])
        subprocess.run(["mv", "clash-linux-amd64", "clash"])

    # ===== 启动 Clash =====
    print("🚀 Start Clash Core")
    start_clash()

    # ===== 真测速 =====
    print("⚡ Real Proxy Speed Test")

    valid = []

    for name in proxy_names:

        delay = clash_delay_test(name)

        if delay and delay < 2000:
            print("✔", name, delay)
            valid.append((delay, name))

        else:
            print("✖", name)

    # 排序
    valid.sort(key=lambda x: x[0])

    # 只保留前50
    valid = valid[:50]

    good_names = [v[1] for v in valid]

    print("🎯 Good Nodes:", len(good_names))

    # ===== 重写最终配置 =====
    final_lines = []

    for block in proxy_blocks:

        name_match = re.search(r"name:\s*\"?([^\n\"]+)\"?", block)

        if name_match and name_match.group(1) in good_names:

            if block.startswith("-"):
                final_lines.append(
                    "\n".join("  " + l for l in block.splitlines())
                )
            else:
                final_lines.append(block)

    final_config = [
        "mixed-port: 7890",
        "allow-lan: false",
        "mode: Rule",
        "proxies:"
    ]

    final_config.extend(final_lines)

    final_config.append("proxy-groups:")
    final_config.append("  - name: 🚀 AUTO BEST")
    final_config.append("    type: select")
    final_config.append("    proxies:")

    for name in good_names:
        final_config.append(f"      - \"{name}\"")

    final_config.append("rules:")
    final_config.append("  - MATCH,🚀 AUTO BEST")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_config))

    print("🏁 Aggregation Finished")


if __name__ == "__main__":
    main()
