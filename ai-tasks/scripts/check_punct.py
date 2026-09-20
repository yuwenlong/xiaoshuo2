#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""机检④b 标点规范（《写作说明》§四-11 配套脚本）

立条背景：原验证脚本用 grep -P '。”[^。”]{1,25}?，“'，在 Git Bash 下 {1,25}
被 shell 当花括号展开，pattern 被拆成两半当文件名报 "No such file or directory"，
该项机检从未真正执行过——控制卡记的"零残留"是假绿。改用本脚本，退出码须为 0。

用法：python ai-tasks/scripts/check_punct.py 正文/卷一/第01章.txt [更多章...]
检查：①ASCII 直引号零残留 ②句中叙述语截断混搭（句号+叙述语+逗号+上引号）
      ③弯引号开闭计数相等 ④中文括号/书名号配对
"""
import sys, io, re
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

TRUNC = re.compile(r'。”[^。”]{1,25}?，“')

def check(path):
    t = io.open(path, encoding='utf-8').read()
    bad = []
    for m in re.finditer(r'"', t):
        bad.append(('直引号', t[max(0, m.start()-12):m.start()+12]))
    for m in TRUNC.finditer(t):
        bad.append(('叙述语截断混搭', m.group(0)))
    for o, c, name in (('“', '”', '引号'), ('（', '）', '括号'), ('《', '》', '书名号')):
        if t.count(o) != t.count(c):
            bad.append((f'{name}不配对', f'{o}{t.count(o)} / {c}{t.count(c)}'))
    return bad

def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__); sys.exit(2)
    total = 0
    for f in files:
        bad = check(f)
        total += len(bad)
        print(f'\n=== {f} ===')
        if not bad:
            print('  PASS 标点规范零残留')
        for kind, ctx in bad:
            print(f'  [BLOCK] {kind}: 「{ctx}」')
    print(f'\n合计 BLOCK {total} 处')
    sys.exit(1 if total else 0)

if __name__ == '__main__':
    main()
