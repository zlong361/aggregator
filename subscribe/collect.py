# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import re
import base64

def decode_base64_if_needed(content: str) -> str:
    """如果是 Base64 订阅则解码"""
    text = content.strip()
    if "proxies:" in text:
        return text

    try:
        missing_padding = len(text) % 4
        if missing_padding:
            text += "=" * (4 - missing_padding)
        decoded = base64.b64decode(text).decode("utf-8", errors="ignore")
        if "proxies:" in decoded:
            return decoded
    except Exception:
        pass

    return content


def extract_proxy_blocks(content: str):
    """标准方式提取 proxies 下的节点块"""
    lines = content.splitlines()
    blocks = []

    in_proxies = False
    current_block = []

    for line in lines:
        if re.match(r'^proxies:\s*$', line):
            in_proxies = True
            continue

        if in_proxies and re.match(r'^[a-zA-Z0-9_-]+:\s*$', line):
            break

        if in_proxies:
            if re.match(r'^\s*-\s+name:', line):
                if current_block:
                    blocks.append(current_block)
                current_block = [line]
            elif current_block:
                current_block.append(line)

    if current_block:
        blocks.append(current_block)

    return blocks


def normalize_block(block_lines):
    """统一缩进为2空格结构"""
    normalized = []
    for line in block_lines:
        stripped = line.lstrip()
        if stripped.startswith("- name:"):
            normalized.append("  " + stripped)
        else:
            normalized.append("    " + stripped)
    return normalized


def main():
    print("🚀 Clash Ultimate 稳定版生成启动...")

    config_path = os.path.join(os.path.dirname(__file__), 'config/config.default.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    urls = [
        page['url']
        for page in config.get('crawl', {}).get('pages', [])
        if page.get('enable')
    ]

    headers = {'User-Agent': 'Clash-Verge/1.3.8'}

    proxy_blocks = []
    proxy_names = set()

    for url in urls:
        try:
            print(f"📥 获取: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                content = res.read().decode('utf-8', errors='ignore')

            content = decode_base64_if_needed(content)

            blocks = extract_proxy_blocks(content)

            for block in blocks:
                joined = "\n".join(block)

                if "type:" not in joined:
                    continue

                name_match = re.search(r'name:\s*["\']?([^"\']+)', joined)
                if not name_match:
                    continue

                name = name_match.group(1).strip()

                if name in proxy_names:
                    continue

                if any(x in name for x in ["选择", "官网", "流量", "过期", "提示"]):
                    continue

                proxy_names.add(name)
                proxy_blocks.append(normalize_block(block))

        except Exception as e:
            print(f"⚠️ 跳过: {url}")

    print(f"🎯 有效节点: {len(proxy_names)} 个")

    lines = [
        "allow-system-fake-dns: true",
        "mixed-port: 7890",
        "mode: rule",
        "log-level: info",
        "",
        "proxies:"
    ]

    for block in proxy_blocks:
        lines.extend(block)

    lines.extend([
        "",
        "proxy-groups:",
        "  - name: 🚀 自动选择",
        "    type: url-test",
        "    url: http://www.gstatic.com/generate_204",
        "    interval: 300",
        "    tolerance: 50",
        "    proxies:"
    ])

    if proxy_names:
        for name in proxy_names:
            lines.append(f'      - "{name}"')
    else:
        lines.append("      - DIRECT")

    lines.extend([
        "",
        "rules:",
        "  - MATCH,🚀 自动选择"
    ])

    with open("clash.yaml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("🏁 clash.yaml 生成完成，可直接导入。")


if __name__ == "__main__":
    main()
