# -*- coding: utf-8 -*-
"""本批全套机检汇总：①①b①c②③④④b⑤⑦＋段落统计＋对话占比＋翻案/省略号/群像。
用法：python ai-tasks/scripts/fullcheck.py 48 49 ...（章号）
硬项：①禁用词序数 ①b破折号 ①c真实地名 ②脸谱化 ③行首那 翻案/省略号/群像/第N序数 ④相邻非空行 ④b check_punct ⑦ check_ai_taste 段长>200或全章无>120段；⑤字数与对话占比只打印，按控制卡章型人工判。
每项单独打印命中条数；任一硬项≠0 则 ALL_RC=1。"""
import sys, re, subprocess, statistics, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, '正文', '卷一')
BAN = r'然而|此外|总之|因此|综上所述|由此可见|首先|其次|最后|第一|第二|第三|一方面|另一方面|至关重要|显而易见|毫无疑问|必然|绝对|赋能|抓手|闭环|底层逻辑|颗粒度|链路|心智'
REAL = r'北京|上海|广州|深圳|杭州|大连|中关村|清华|北大|金山|词霸|新浪|奇安信|华图|有道|欧路|海词|香港'
FACE = r'松木香|瑞凤眼|修长的手指|指节|骨节|指腹|薄茧|勾起一丝|深不见底|猪肝色|暂停键|钢针|指甲深陷入掌心|眸色一暗|眼底闪|死寂|沙哑|好整以暇|一抹|一丝|瞬间|混杂'
EXTRA = [
    ('翻案 不是…而是', r'不是[^。！？]{0,20}而是'),
    ('翻案 并非/与其说/看似实则', r'并非|与其说|看似[^。]{0,15}实则|说白了|说穿了|说到底'),
    ('省略号', r'……|\.\.\.'),
    ('群像 有人…有人', r'有人[^，。；]{2,14}[，；](又|还)?有人'),
    ('序数 头一/末一以外的 第N', r'第[一二三四五六七八九十]+(?![章卷])'),
]
allrc = 0
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

def paras(text):
    lines = text.split('\n')[1:]
    return [l.strip() for l in lines if l.strip()]

for n in sys.argv[1:]:
    p = os.path.join(D, f'第{int(n):02d}章.txt')
    t = open(p, encoding='utf-8').read()
    body = '\n'.join(t.split('\n')[1:])
    rc = 0
    print(f'==== 第{n}章 ====')
    def hit(name, pat, hard=True, src=body):
        global rc
        ms = []
        for i, l in enumerate(src.split('\n'), 2):
            if re.search(pat, l):
                ms.append((i, re.findall(pat, l)))
        print(f'[{name}] {len(ms)}' + ('' if hard else ' (人工)'))
        for i, m in ms:
            print(f'    L{i}: {m}')
        if hard and ms:
            rc = 1
    hit('① 禁用词/序数', BAN)
    hit('①b 破折号', r'——|—|–')
    hit('①c 真实地名机构', REAL)
    hit('② 脸谱化', FACE)
    hit('③ 行首那', r'^\s*那')
    for name, pat in EXTRA:
        hit(name, pat)
    # ④ 对话行连续无空行
    ls = t.split('\n')
    c4 = sum(1 for a, b in zip(ls, ls[1:]) if a.strip() and b.strip())
    print(f'[④ 相邻非空行] {c4}')
    if c4:
        rc = 1
    for script in ['check_punct.py', 'check_ai_taste.py']:
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'ai-tasks', 'scripts', script), p], capture_output=True, text=True, encoding='utf-8', env=ENV)
        out = r.stdout.strip().split('\n')
        blk = [o for o in out if 'BLOCK' in o or 'WARN' in o or 'FAIL' in o]
        print(f'[{script}] rc={r.returncode}')
        for o in blk[:30]:
            print('    ' + o)
        if r.returncode:
            rc = 1
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'ai-tasks', 'scripts', 'zuojia_wc.py'), p], capture_output=True, text=True, encoding='utf-8', env=ENV)
    print('[⑤ 字数] ' + r.stdout.strip().split(': ')[-1])
    ps = paras(t)
    lens = [len(x) for x in ps]
    dia = sum(1 for x in ps if '“' in x)
    print(f'[段落] 段数{len(ps)} 最长{max(lens)} 标准差{statistics.pstdev(lens):.1f} >120段{sum(1 for x in lens if x > 120)} >200段{sum(1 for x in lens if x > 200)}')
    print(f'[对话占比] {dia}/{len(ps)}={dia / len(ps) * 100:.1f}%')
    if max(lens) > 200 or max(lens) <= 120:
        rc = 1
    print(f'RC={rc}')
    allrc |= rc
print(f'ALL_RC {allrc}')
sys.exit(allrc)
