import subprocess
import requests
import time
import os
import re

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
        print("找不到 clash.yaml")
        return

    print("生成临时配置")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = "external-controller: 127.0.0.1:9090\n" + content

    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    start_clash()

    print("开始测速")

    names = re.findall(r'name:\s*"?([^"\n]+)"?', content)

    valid = []

    for name in names:
        delay = clash_delay_test(name)
        if delay and delay < 2000:
            print(f"{name} {delay}ms")
            valid.append((delay, name))
        else:
            print(f"{name} 失败")

    valid.sort(key=lambda x: x[0])
    valid = valid[:50]

    print("测速完成")


if __name__ == "__main__":
    main()
