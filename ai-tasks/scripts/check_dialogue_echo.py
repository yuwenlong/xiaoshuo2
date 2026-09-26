# -*- coding: utf-8 -*-
"""机检⑧d 同场景对白来回比对（《写作说明》强制执行协议步骤11e 配套脚本）

立条背景：第31-37章六路审查文字路查出，35 章食堂劝割把 23 章「吃饭／吃着呢／你还等什么」
  一来一回整套又走了一遍；更早的 ch13↔ch20「你图啥→不答→对方等了一会儿」也是如此。
  措辞换过几个字，⑧／⑧b／⑧c 按字串比对全部漏掉，因为撞的不是句子，是一问一答的骨架。

口径：
  一来一回＝同一章里相邻或隔一句的两句引号内的话（中间隔不超过三段）；
  两处「一来一回」前后两句各自相似（长短相差不过一倍，重合÷较短那句 ≥0.6；
  四字以上按二字组算，短句按单字算），
  且至少一处落在新章，即报；
  另报新章里与别章一字不差的单句（去标点后 ≥5 字）。
  命中项逐条裁「刻意呼应／生成冗余」，保留项理由入控制卡。

用法：python ai-tasks/scripts/check_dialogue_echo.py --new 起章 止章 [正文glob]
"""
import sys, io, re, glob
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

argv = sys.argv[1:]
if '--new' not in argv:
    print('用法：check_dialogue_echo.py --new 起章 止章 [正文glob]')
    sys.exit(2)
k = argv.index('--new')
lo, hi = int(argv[k + 1]), int(argv[k + 2])
argv = argv[:k] + argv[k + 3:]
files = sorted(glob.glob(argv[0] if argv else '正文/卷一/第*.txt'))

PUNCT = r'[，。！？、“”：；（）《》…\s]'


def norm(q):
    return re.sub(PUNCT, '', q)


def sim(a, b):
    if not a or not b or max(len(a), len(b)) > 2 * min(len(a), len(b)):
        return 0.0
    if len(a) <= 3 or len(b) <= 3:
        sa, sb = set(a), set(b)
        return len(sa & sb) / min(len(sa), len(sb))
    ga = {a[i:i + 2] for i in range(len(a) - 1)}
    gb = {b[i:i + 2] for i in range(len(b) - 1)}
    return len(ga & gb) / min(len(ga), len(gb))


quotes = {}      # 章号 -> [(段号, 原句, 规范句)]
for f in files:
    lines = io.open(f, encoding='utf-8').read().splitlines()
    m = re.match(r'第(\d+)章', lines[0].strip())
    if not m:
        continue
    c = int(m.group(1))
    paras = [x.strip() for x in lines[1:] if x.strip()]
    qs = []
    for pi, p in enumerate(paras):
        for q in re.findall(r'“([^”]{1,60})”', p):
            qs.append((pi, q, norm(q)))
    quotes[c] = qs

pairs = defaultdict(list)   # 章号 -> [(原句1, 原句2, 规范1, 规范2)]
for c, qs in quotes.items():
    for i in range(len(qs) - 1):
        for j in (i + 1, i + 2):
            if j >= len(qs):
                continue
            (p1, q1, n1), (p2, q2, n2) = qs[i], qs[j]
            if p2 - p1 > 3 or n1 == n2:
                continue
            if len(n1) + len(n2) < 6 or len(n1) <= 1 or len(n2) <= 1:
                continue
            pairs[c].append((q1, q2, n1, n2))

TH = 0.6
found = []
chs = sorted(pairs)
for a in chs:
    for b in chs:
        if b <= a or not (lo <= a <= hi or lo <= b <= hi):
            continue
        for x in pairs[a]:
            for y in pairs[b]:
                s1, s2 = sim(x[2], y[2]), sim(x[3], y[3])
                if s1 >= TH and s2 >= TH:
                    found.append((round((s1 + s2) / 2, 2), a, b, x, y))

print(f'── ⑧d 新章 {lo}-{hi} 的对白来回比对 ──')
if not found:
    print('一来一回撞骨架：无')
seen = set()
for s, a, b, x, y in sorted(found, key=lambda t: -t[0]):
    key = (a, b, x[0], y[0])
    if key in seen:
        continue
    seen.add(key)
    print(f'ch{a}「{x[0]}」「{x[1]}」 ↔ ch{b}「{y[0]}」「{y[1]}」  相似 {s}')

single = defaultdict(set)
for c, qs in quotes.items():
    for _, q, n in qs:
        if len(n) >= 5:
            single[n].add(c)
print()
same = [(n, v) for n, v in single.items() if len(v) >= 2 and any(lo <= x <= hi for x in v)]
if not same:
    print('跨章一字不差的单句：无')
for n, v in sorted(same, key=lambda t: sorted(t[1])):
    print(f'单句「{n}」  ' + ' / '.join(f'ch{x}' for x in sorted(v)))
