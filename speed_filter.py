# -*- coding: utf-8 -*-
import subprocess
import requests
import time
import re
import os

CONFIG_FILE = "clash.yaml"
TEMP_FILE = "clash_temp.yaml"

def start_clash():
    subprocess.Popen(
        ["./clash", "-f", TEMP_FILE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(6)

def clash_delay_test(proxy_name):
    try:
        url = f"http://127.0.0.1:9090/proxies/{proxy_name}/delay?timeout=5000&url=http://www.gstatic.com/generate_204"
        r = requests.get(url, timeout=8)
        data = r.json()
        if "delay" in data and data["delay"] > 0:
            return data["delay"]
    except:
        return None

def main():

    if not os.path.exists(CONFIG_FILE):
        print("❌ 找不到 clash.yaml")
        return

    print("🛠 注入 external-controller")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 注入 API 控制器
    content = "external-controller: 127.0.0.1:9090\nmode: Rule\nlog-level: silent\n" + content

    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("🚀 启动 Clash")
    start_clash()

    print("⚡ 开始真实代理测速")

    proxy_names = re.findall(r'name:\s*"?([^"\n]+)"?', content)

    valid = []

    for name in proxy_names:
        delay = clash_delay_test(name)
        if delay and delay < 2000:
            print(f"⚡ {name} {delay}ms")
            valid.append((delay, name))
        else:
            print(f"❌ {name} 失败")

    valid.sort(key=lambda x: x[0])
    valid = valid[:50]   # 只保留前50个

    good_names = [v[1] for v in valid]

    print(f"🎯 可用节点: {len(good_names)}")

    # 重新生成最终配置
    final_lines = []
    keep = False
    current_block = []

    for line in content.splitlines():
        if re.match(r'^\s*-\s*name:', line):
            if current_block:
                block_text = "\n".join(current_block)
                name_match = re.search(r'name:\s*"?([^"\n]+)"?', block_text)
                if name_match and name_match.group(1) in good_names:
                    final_lines.extend(current_block)
            current_block = [line]
            keep = True
        elif keep:
            current_block.append(line)
        else:
            final_lines.append(line)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))

    print("🏁 已过滤坏节点，覆盖 clash.yaml")

if __name__ == "__main__":
    main()
