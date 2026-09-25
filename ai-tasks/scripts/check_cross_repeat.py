# -*- coding: utf-8 -*-
"""机检⑧ 跨章重复片段扫描（《写作说明》强制执行协议步骤12c 配套脚本）

立条背景：check_ai_taste.py 的 near-repeat 只查章内，跨章复用是盲区。
实证：ch5/ch6「百叶窗留着条缝，人影举着电话走来走去」一字不差跨章复用；
      新写 ch9/ch10 一次性撞上既有章 6 处（椅子腿刮地、往椅背上靠、手心全是汗、
      QQ头像闪了、头像灰下去、论坛骂街原话）。

用法：python ai-tasks/scripts/check_cross_repeat.py [正文glob]
判定：命中项须逐条人工裁「刻意呼应」或「生成冗余」，保留项理由入控制卡。
"""
import sys, io, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

N = 8            # 片段长度阈值
files = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else '正文/卷一/第*.txt'))
occ = defaultdict(list)
for f in files:
    raw = io.open(f, encoding='utf-8').read()
    ch = raw.split('\n')[0].strip()
    body = ''.join(x.strip() for x in raw.split('\n')[1:] if x.strip())
    seen_in_ch = set()
    for i in range(len(body) - N + 1):
        g = body[i:i+N]
        if re.search(r'[，。！？、“”：；0-9A-Za-z]', g):
            continue
        if g in seen_in_ch:
            continue
        seen_in_ch.add(g)
        occ[g].append((ch, i))

# 只保留出现在 ≥2 个不同章的片段，并做最长化合并
cross = {g: v for g, v in occ.items() if len({c for c, _ in v}) >= 2}
keys = sorted(cross, key=len, reverse=True)
kept = []
for g in keys:
    if any(g in k for k in kept):
        continue
    kept.append(g)

if not kept:
    print('跨章重复：无')
for g in sorted(kept, key=lambda x: -len(x)):
    chs = sorted({c for c, _ in cross[g]})
    print(f'「{g}」  出现于：{" / ".join(chs)}')

# ── 第二轮（⑧b）：去标点后按10字比对 ──
# 立条背景：第21-25章六路审查查出，逗号把一句切成几截、每截都不到8字时，上面一轮看不见。
# 实证：「看了他好一会儿，嘴角往下压了压」（ch17）与「盯了他好一会儿，嘴角往下压了压」（ch21）。
# 去掉标点再比，命中项同样逐条裁「刻意呼应／生成冗余」，保留理由入控制卡。
M = 10
occ2 = defaultdict(set)
for f in files:
    raw = io.open(f, encoding='utf-8').read()
    lines2 = raw.splitlines()
    ch = lines2[0].strip()
    body = re.sub(r'[，。！？、“”：；（）《》\s]', '', ''.join(x.strip() for x in lines2[1:] if x.strip()))
    for i in range(len(body) - M + 1):
        g = body[i:i+M]
        if re.search(r'[0-9A-Za-z]', g):
            continue
        occ2[g].add(ch)
merged = defaultdict(list)
for g, v in occ2.items():
    if len(v) >= 2:
        merged[tuple(sorted(v))].append(g)
print()
print('── ⑧b 去标点后10字 ──')
if not merged:
    print('去标点跨章重复：无')
for key, grams in sorted(merged.items()):
    grams = sorted(grams)
    print(f'{" / ".join(key)}：' + '；'.join(grams[:4]) + ('…' if len(grams) > 4 else ''))
