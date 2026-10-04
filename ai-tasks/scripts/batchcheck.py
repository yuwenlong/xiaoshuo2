# -*- coding: utf-8 -*-
"""一键全套机检（《写作说明》自动验证脚本的唯一入口）。
用法：python ai-tasks/scripts/batchcheck.py 起章 止章 [--card 控制卡路径]
默认控制卡：ai-tasks/控制卡-第起-止章.md。依次跑：
  ⓪ check_card（控制卡必含栏目）
  ①—⑦ fullcheck（禁用词、破折号、真实名、脸谱化与万能副词、那字句首、翻案外衣、洞察路标、对话行格式、标点、字数、深层 AI 指纹）
  ⑤b 字数区间与极差（每章 2000—3500，<2030 记压线；五章极差≥500）
  ⑤c 对白占比按控制卡登记章型验收（常规 40—50／独处≥25／双人静场 40—60）
  ⑧ check_cross_repeat --new、⑧d check_dialogue_echo --new（只列，人工裁定入卡）
  ⑧e check_tics
  ⑩ story-review 三脚本（normalize-punctuation／check-ai-patterns／check-degeneration），blocking 须为 0
任一硬项不过 BATCH_RC=1；改任何一句都重跑本脚本，不得只跑相关一项（R20）。"""
import glob
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(ROOT, 'ai-tasks', 'scripts')
D = os.path.join(ROOT, '正文', '卷一')
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
RANGES = {'常规': (40, 50), '独处': (25, 101), '双人静场': (40, 60)}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=ENV, cwd=ROOT)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def chapter_path(n):
    return os.path.join(D, f'第{int(n):02d}章.txt')


def review_scripts_dir():
    cands = [os.path.join(ROOT, '.claude', 'skills', 'story-review', 'scripts'),
             os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'story-review', 'scripts')]
    for c in cands:
        if os.path.exists(os.path.join(c, 'check-ai-patterns.js')):
            return c
    return ''


def chapter_types(card):
    """从逐章规格表读每章登记的章型。"""
    types = {}
    i = card.find('## 逐章规格')
    if i < 0:
        return types
    for l in card[i:].split('\n')[1:30]:
        m = re.match(r'\|\s*(\d+)\s*\|\s*([^|]+)\|', l)
        if m:
            t = m.group(2)
            types[int(m.group(1))] = '双人静场' if '双人' in t else '独处' if '独处' in t else '常规'
    return types


def dialogue_ratio(path):
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')[1:]
    ps = [l.strip() for l in lines if l.strip()]
    return sum(1 for x in ps if '“' in x) * 100 / max(1, len(ps))


def main():
    args = sys.argv[1:]
    pre = '--pre' in args  # 只在写作中途自查时用；交付必须不带 --pre
    args = [x for x in args if x != '--pre']
    card = None
    if '--card' in args:
        k = args.index('--card')
        card = args[k + 1]
        args = args[:k] + args[k + 2:]
    a, b = int(args[0]), int(args[1])
    nums = list(range(a, b + 1))
    card = card or os.path.join('ai-tasks', f'控制卡-第{a}-{b}章.md')
    rc = 0

    print('==== ⓪ 控制卡 ====')
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'check_card.py'), card] + (['--pre'] if pre else []))
    print(out.strip())
    rc |= c
    card_text = ''
    cp = card if os.path.isabs(card) else os.path.join(ROOT, card)
    if os.path.exists(cp):
        with open(cp, encoding='utf-8') as f:
            card_text = f.read()

    print('==== ①—⑦ fullcheck ====')
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'fullcheck.py')] + [str(n) for n in nums])
    keep = [l for l in out.split('\n') if l.startswith('====') or re.search(r'\] [1-9]|BLOCK|WARN|RC|字数|对话占比|段落|\s+L\d+|^\[(对白语气词|环境句|碎段|精读三处|天气起场)', l)]
    print('\n'.join(l for l in keep if 'BLOCK 0' not in l))
    rc |= c

    print('==== ⑤b 字数 ====')
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'zuojia_wc.py')] + [chapter_path(n) for n in nums])
    print(out.strip())
    vals = [int(x) for x in re.findall(r'\.txt: (\d+)', out)]
    for n, v in zip(nums, vals):
        if v < 2000 or v > 3500:
            print(f'  第{n}章 {v} 字，出 2000—3500')
            rc = 1
        elif v < 2030:
            print(f'  第{n}章 {v} 字，压线（<2030，须留 30 字余量）')
            rc = 1
    if len(vals) >= 5 and max(vals) - min(vals) < 500:
        print('  极差 <500')
        rc = 1

    print('==== ⑤c 对白占比按章型 ====')
    types = chapter_types(card_text)
    for n in nums:
        t = types.get(n)
        r = dialogue_ratio(chapter_path(n))
        if not t:
            print(f'  第{n}章 {r:.1f}% 控制卡未登记章型')
            rc = 1
            continue
        lo, hi = RANGES[t]
        ok = lo <= r <= hi
        print(f'  第{n}章 {t} {r:.1f}% ' + ('OK' if ok else f'出区间 {lo}—{hi}'))
        if not ok:
            rc = 1

    print('==== ⑧ 跨章重复（人工裁定入卡） ====')
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'check_cross_repeat.py'), '--new', str(a), str(b)])
    hits = [l for l in out.split('\n') if l.startswith('「') and re.search('|'.join(f'第{n}章' for n in nums), l)]
    print(f'  新章相关命中 {len(hits)} 条（逐条裁「刻意呼应／生成冗余」）')
    for l in hits[:40]:
        print('  ' + l[:90])
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'check_dialogue_echo.py'), '--new', str(a), str(b)])
    print('  ' + out.strip().replace('\n', '\n  '))

    print('==== ⑧e 口癖 ====')
    c, out = run([sys.executable, os.path.join(SCRIPTS, 'check_tics.py')] + [str(n) for n in nums])
    print(out.strip())
    rc |= c

    print('==== ⑩ story-review 三脚本 ====')
    sd = review_scripts_dir()
    node = shutil.which('node')
    if not sd or not node:
        print('  缺：story-review/scripts 或 node 不可用（不得跳过，先修环境）')
        rc = 1
    else:
        files = [chapter_path(n) for n in nums]
        for js, extra in (('normalize-punctuation.js', ['--check']),
                          ('check-ai-patterns.js', ['--check', '--fail-on=blocking']),
                          ('check-degeneration.js', ['--check'])):
            c, out = run([node, os.path.join(sd, js)] + extra + files)
            blocking = len(re.findall(r'\[blocking\]', out))
            if js == 'normalize-punctuation.js':
                blocking = len([l for l in out.split('\n') if re.search(r'(ellipsis|double-hyphen|markdown-divider)', l)])
            adv = len(re.findall(r'\[advisory\]', out))
            print(f'  {js} blocking {blocking} advisory {adv}')
            for l in [l for l in out.split('\n') if '[blocking]' in l][:10]:
                print('    ' + l[:160])
            if blocking:
                rc = 1

    print('==== ⑪ WARN：新术语／线索热度（人工裁定入卡） ====')
    files = sorted(glob.glob(os.path.join(D, '第*章.txt')), key=lambda f: int(re.search(r'第(\d+)章', f).group(1)))
    seen, last = set(), {}
    core = ['林见夏', '秦深', '袁野', '孙鹏', '小满', '乔漫', '庞坚', '谭师傅', '老方', '杜磊']
    for f in files:
        k = int(re.search(r'第(\d+)章', f).group(1))
        if k > b:
            break
        with open(f, encoding='utf-8') as fh:
            body = '\n'.join(fh.read().split('\n')[1:])
        toks = set(re.findall(r'[A-Za-z][A-Za-z0-9.+#_\-]{1,}', body))
        new = toks - seen
        seen |= toks
        if k >= a and len(new) > 3:
            print(f'  第{k}章 新英文术语 {len(new)} 个（WARN>3）：{sorted(new)[:12]}')
        for name in core:
            if name in body:
                last[name] = k
    for name in core:
        gap = b - last.get(name, 0)
        if gap > 5:
            print(f'  {name} 最近一次出场第{last.get(name, "无")}章，距批末 {gap} 章（WARN>5：线索热度表须写处置）')

    print(f'BATCH_RC {rc}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
