# -*- coding: utf-8 -*-
"""机检⑧ 跨章重复片段扫描（《写作说明》强制执行协议步骤12c 配套脚本）

立条背景：check_ai_taste.py 的 near-repeat 只查章内，跨章复用是盲区。
实证：ch5/ch6「百叶窗留着条缝，人影举着电话走来走去」一字不差跨章复用；
      新写 ch9/ch10 一次性撞上既有章 6 处（椅子腿刮地、往椅背上靠、手心全是汗、
      QQ头像闪了、头像灰下去、论坛骂街原话）。

用法：python ai-tasks/scripts/check_cross_repeat.py [正文glob] [--new 起章 止章]
      给了 --new 才跑 ⑧c（本批新章对全书的 6-7 字串），不给只跑 ⑧ ⑧b。
判定：命中项须逐条人工裁「刻意呼应」或「生成冗余」，保留项理由入控制卡。
"""
import sys, io, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

argv = sys.argv[1:]
NEW = None
if '--new' in argv:
    k = argv.index('--new')
    NEW = (int(argv[k + 1]), int(argv[k + 2]))
    argv = argv[:k] + argv[k + 3:]

N = 8            # 片段长度阈值
files = sorted(glob.glob(argv[0] if argv else '正文/卷一/第*.txt'))
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

# ── 第三轮（⑧c）：本批新章对全书，按分句取 6-7 字 ──
# 立条背景：第31-37章六路审查文字路指出，8 字、10 字两轮都漏掉短一截的撞句，
#   改写复刻常只留下六七个字的骨头（如「一截比一截矮」「拿指甲一格一格」）。
# 口径：只在分句内取字串（不跨标点），只报至少一处落在新章的；
#   出现在 ≤3 章的列「撞句」逐条裁，出现在 ≥4 章的列「口癖」看是不是又添了一回。
if NEW:
    def chno(title):
        m = re.match(r'第(\d+)章', title)
        return int(m.group(1)) if m else -1
    occ3 = defaultdict(set)
    for f in files:
        raw = io.open(f, encoding='utf-8').read()
        ls = raw.splitlines()
        c = chno(ls[0].strip())
        for line in ls[1:]:
            for seg in re.split(r'[，。！？、“”：；（）《》…\s]+', line):
                if len(seg) < 6:
                    continue
                for L in (7, 6):
                    for i in range(len(seg) - L + 1):
                        g = seg[i:i + L]
                        if re.search(r'[0-9A-Za-z]', g):
                            continue
                        occ3[g].add(c)
    # 设定名词与汉字数字串本来就该反复出现，挪进只计数的桶，不逐条列
    TERMS = ['在线版', '测试库', '测试服务器', '会员', '接口', '集团', '两条线', '考研词汇', '少儿英语',
             '访问日志', '备件间', '机房', '苹果', '安卓', '诺基亚', '比特币', '论坛', '纪要', '规划会',
             '词库', '模拟器', '存储卡', '数据线', '隔板', '出租屋', '笔记本', '显示器', '保温杯', '便签',
             '对话框', '回帖', '活动页', '移动端', '手机上', '接口文档', '会员表', '评审', '转正']
    NUMS = set('零一二三四五六七八九十百千万两')
    def is_noise(g):
        return any(t in g for t in TERMS) or sum(ch in NUMS for ch in g) >= 4
    lo, hi = NEW
    hits = {g: v for g, v in occ3.items()
            if len(v) >= 2 and any(lo <= x <= hi for x in v)}
    noise = {g for g in hits if is_noise(g)}
    hits = {g: v for g, v in hits.items() if g not in noise}
    kept3 = []
    for g in sorted(hits, key=len, reverse=True):
        if any(g in k and hits[k] == hits[g] for k in kept3):
            continue
        kept3.append(g)
    rare = sorted([g for g in kept3 if len(hits[g]) <= 3], key=lambda g: sorted(hits[g]))
    tics = sorted([g for g in kept3 if len(hits[g]) >= 4], key=lambda g: -len(hits[g]))
    print()
    print(f'── ⑧c 新章 {lo}-{hi} 的 6-7 字串 ──')
    if not rare:
        print('撞句（≤3章）：无')
    for g in rare:
        print(f'撞句「{g}」  ' + ' / '.join(f'ch{x}' for x in sorted(hits[g])))
    for g in tics[:20]:
        print(f'口癖「{g}」  {len(hits[g])} 章：' + ' '.join(f'ch{x}' for x in sorted(hits[g])))
    print(f'（设定名词、数字串 {len(noise)} 条未列）')
