# -*- coding: utf-8 -*-
"""
机检⑨ 简介口径一致性（lessons R32）

《全书大纲》「作品简介（平台投稿用）」是投稿简介的唯一事实源，
build-submission-docx.js 的 intro 数组必须与之逐字一致。
任一边改动后须跑本脚本，退出码 0 方可重新生成投稿 docx。

用法：python ai-tasks/scripts/check_intro_sync.py
"""
import io
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MD = os.path.join(ROOT, "说明", "全书大纲.md")
JS = os.path.join(ROOT, "ai-tasks", "scripts", "build-submission-docx.js")

for f in (MD, JS):
    if not os.path.exists(f):
        print("[FAIL] 找不到文件：%s" % f)
        sys.exit(2)

md = io.open(MD, encoding="utf-8").read()
js = io.open(JS, encoding="utf-8").read()

try:
    start = md.index("### 作品简介（平台投稿用）")
    seg = md[start:md.index("**简介对板条款**", start)]
except ValueError:
    print("[FAIL] 大纲里定位不到「作品简介」节或「简介对板条款」锚点")
    sys.exit(2)

md_lines = [l[2:].strip() for l in seg.splitlines()
            if l.startswith("> ") and l.strip() != ">"]

m = re.search(r"const intro = \[(.*?)\];", js, re.S)
if not m:
    print("[FAIL] 脚本里定位不到 const intro 数组")
    sys.exit(2)
js_lines = re.findall(r"'(.*?)',", m.group(1))

if not md_lines or not js_lines:
    print("[FAIL] 抽出的简介为空（大纲%d行／脚本%d行）" % (len(md_lines), len(js_lines)))
    sys.exit(2)

ok = len(md_lines) == len(js_lines)
for i, (a, b) in enumerate(zip(md_lines, js_lines)):
    if a != b:
        ok = False
        print("DIFF 第%d段" % (i + 1))
        print("  大纲：%s" % a)
        print("  脚本：%s" % b)

if len(md_lines) != len(js_lines):
    print("段数不一致：大纲 %d 段，脚本 %d 段" % (len(md_lines), len(js_lines)))

print("=== 机检⑨ 简介口径一致性 ===")
print("大纲 %d 段 / 脚本 %d 段 -> %s" % (len(md_lines), len(js_lines), "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
