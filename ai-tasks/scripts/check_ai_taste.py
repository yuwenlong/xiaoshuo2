#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""机检⑦ 深层AI味检测（《写作说明》§五-16 配套脚本）

用途：检出表层机检（破折号/省略号/禁用词）抓不到的深层AI指纹。
      含①事后全知旁白 ②对偶回环 ③数字金句模板 ④群像列举 ⑤要是X要是不X
      ⑥昨天今天对照 ⑦近距离重复片段 ⑧「没人X／谁都X／静了几秒」群体反应模板
      ⑨口癖节拍器（「两秒」停顿／「X个字」计数／「笑了笑」）⑩叙述句首「那」
      ＋段落节奏（天花板/上限/标准差）与废笔启发式。
用法：python ai-tasks/scripts/check_ai_taste.py 正文/卷一/第01章.txt [更多章...]

判定分级：
  [BLOCK] 必须改，改完重检
  [WARN]  人工过目，确属模板腔再改；有叙事功能可留，须在控制卡登记理由
"""
import sys, re, io, statistics

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ① 事后全知旁白：跳出当下叙事时间做点评（§五-8 的时间维度补充）
OMNISCIENT = r'(后来[他她](?:才)?知道|今天[他她]才知道|多年以后|[他她]不知道的是|若干年后[他她]才)'

# ② 对偶回环句：AI中文最强指纹
ANTITHESIS = [
    (r'有些[^，。；！？]{1,10}[^。！？]{0,25}有些', '有些X…有些X…'),
    (r'是[^，。]{1,12}，也是[^。]{1,12}。', '是A，也是B'),
    (r'([^，。]{1,6})，或者不\1', 'X，或者不X'),
    (r'如果是前者|如果是后者', '前者/后者（书面腔＋对仗）'),
    (r'前一[种个样条][^。！？]{0,30}后一[种个样条]', '前一种…后一种（前者/后者同族·写法变体）'),
    (r'([^，。]{2,8})的[^，。]{1,8}是[^，。]{1,6}，\1', '回环顶针'),
]

# ③ 数字对比金句模板：同模板相邻复用是重灾区
NUM_EPIGRAM = r'([一二三四五六七八九十百千]+[年月日分钟秒个])[^。！？]{0,14}(只要|只需|才用了|不过)[^。！？]{0,12}[。！？]'

# ④ 群像列举模板：AI 写群像用列举，真人写群像只盯一个人
CROWD = r'有人[^，。；]{2,14}[，；](又|还)?有人'

# ⑤ 「要是X…要是不X」回环（与 ANTITHESIS 的「X，或者不X」同族，换了壳）
IFNOT = r'要是[^，。；]{1,10}[，。；][^。]{0,40}要是(不|没)'

# ⑥ 同段「昨天…今天…」对照句
DAYPAIR = r'昨天[^。！？]{0,30}今天'

# ⑦ 近距离重复片段：同一动作/措辞在短距内写两遍，是生成冗余的物理指纹
#    实证：「把本子摊在桌上」隔1段写两遍；「搁在枕头边上」隔56字写两遍；
#          第5/6章「百叶窗留着条缝，人影举着电话走来走去」跨章一字不差复用。
REPEAT_N, REPEAT_WIN, REPEAT_HARD = 6, 1200, 120

# ⑧ 「没人X／谁都X」群体反应模板：真人换着写，模型复读同一壳子
#    实证：五、六章合计6处「没人敢接话/没人答得上来×2/没人接茬/没人接话」。
NOBODY = r'(没人(敢)?(接话|接茬|答得上来|吭声|说话|应)|谁也没(人)?接|谁都知道|谁也不敢|静了[一两几]?[秒拍下]|静了几秒|静得反常|安静下来|鸦雀无声|一点声音都没有|谁也没(说话|明说|抬头|看他|吭声))'

# ⑨ 口癖节拍器（R35 实证：十章「两秒/几秒/半秒」32处、「X个字」计数27处且数错一处、「笑了笑」8处）
#    每章各≤2，超额报 WARN；计数类还须人工数对
TICS = [
    (r'(?<![十百])[一两几半]秒', 'tic-seconds', '「两秒/几秒/半秒」式计时停顿'),
    (r'[两三四五六七八九十]个字', 'tic-charcount', '「X个字」式计数（引号内字数须数对）'),
    (r'笑了笑', 'tic-smile', '「笑了笑」式万能反应'),
]

# ⑩ 叙述句首「那」（§五-15；对白内口语指示代词放行，故先剥掉引号内文字）
NA_START = r'(^|[。！？；])\s*那'

def analyze(path):
    raw = io.open(path, encoding='utf-8').read()
    paras = [p.strip() for p in raw.split('\n') if p.strip()]
    body = paras[1:] if len(paras) > 1 else paras   # 跳过标题行
    lens = [len(p) for p in body]
    findings = []

    # --- 段落节奏 ---
    longest = max(lens) if lens else 0
    sd = statistics.pstdev(lens) if len(lens) > 1 else 0
    if longest < 120:
        findings.append(('BLOCK', 'para-ceiling',
            f'全章最长段仅{longest}字，无一段过120字。段落天花板整齐是模型生成的物理指纹，'
            f'真人写回忆/心理/场面必然失控出长段。补一段150-190字的长段。'))
    over = [(i, x) for i, x in enumerate(lens, 1) if x > 200]
    if over:
        locs = '、'.join(f'第{i}段{x}字' for i, x in over)
        findings.append(('BLOCK', 'para-runaway',
            f'{locs}：超200字硬上限。按镜头/新动作/新线索/视线切换断段——'
            f'"一段到底"是与"段段等长"相对的另一种模板腔，破天花板与控上限须同做。'))
    if sd < 25:
        findings.append(('WARN', 'para-even',
            f'段落长度标准差{sd:.1f}<25，节奏过匀。压短爽点段、放长氛围段。'))

    # --- 废笔检测（启发式：极短段占比） ---
    short = sum(1 for x in lens if x <= 12)
    if lens and short / len(lens) < 0.10:
        findings.append(('WARN', 'no-breath',
            f'≤12字的短段仅占{short/len(lens)*100:.0f}%，全章段段饱满。'
            f'真人写作有停顿和留白，考虑加短段换气。'))

    # --- 逐段扫描 ---
    epigram_hits = []
    for i, p in enumerate(body, 1):
        for m in re.finditer(OMNISCIENT, p):
            findings.append(('BLOCK', 'omniscient-aside',
                f'第{i}段「{m.group(0)}」：事后全知旁白，跳出角色当下。删掉，让读者自己得出结论。'))
        for pat, name in ANTITHESIS:
            for m in re.finditer(pat, p):
                findings.append(('BLOCK', 'antithesis',
                    f'第{i}段「{m.group(0)[:22]}」：对偶回环（{name}）。拆成白话或改成动作。'))
        for m in re.finditer(NUM_EPIGRAM, p):
            epigram_hits.append((i, m.group(0)))
        for m in re.finditer(CROWD, p):
            findings.append(('BLOCK', 'crowd-list',
                f'第{i}段「{m.group(0)[:20]}」：群像列举模板。AI 写群像用列举，'
                f'真人写群像只盯一个人——改成点名写一个人的具体动作。'))
        for m in re.finditer(IFNOT, p):
            findings.append(('BLOCK', 'antithesis',
                f'第{i}段「{m.group(0)[:22]}」：「要是X…要是不X」回环，'
                f'与「X，或者不X」同族。拆成白话或只写其中一支。'))
        for m in re.finditer(DAYPAIR, p):
            findings.append(('WARN', 'day-contrast',
                f'第{i}段「{m.group(0)[:22]}」：同段「昨天…今天…」对照句，'
                f'一章至多一处；确有对照功能可留，理由入控制卡。'))

    # --- 近距离重复片段（⑦） ---
    flat = ''.join(body)
    p2i = []
    for i, p in enumerate(body, 1):
        p2i += [i] * len(p)
    seen, shown = {}, set()
    for i in range(len(flat) - REPEAT_N + 1):
        g = flat[i:i+REPEAT_N]
        if re.search(r'[，。！？、“”：；0-9A-Za-z]', g):
            continue
        prev = seen.get(g)
        if prev is not None and i - prev < REPEAT_WIN:
            a, b = p2i[prev], p2i[i]
            if a != b and (a, b) not in shown:   # 同段内重复多为刻意排比，不报
                shown.add((a, b))
                d = i - prev
                findings.append((
                    'BLOCK' if d < REPEAT_HARD else 'WARN', 'near-repeat',
                    f'第{a}段↔第{b}段相隔{d}字重复「{g}」：同一措辞近距离写两遍＝生成冗余。'
                    f'刻意呼应（题眼句/悬念锚点）可留，理由须入控制卡。'))
        seen[g] = i

    # --- 群体反应模板复用（⑧） ---
    nb = [(i, m.group(0)) for i, p in enumerate(body, 1) for m in re.finditer(NOBODY, p)]
    if len(nb) >= 3:
        findings.append(('BLOCK', 'crowd-template',
            f'「没人X／谁都X」群体反应模板{len(nb)}处（'
            + '、'.join(f'第{i}段{s}' for i, s in nb)
            + '）：一章至多2处，其余改写成某个具体的人的具体动作。'))

    # --- 口癖节拍器（⑨） ---
    for pat, code, name in TICS:
        hits = [(i, m.group(0)) for i, p in enumerate(body, 1) for m in re.finditer(pat, p)]
        if len(hits) > 2:
            findings.append(('WARN', code,
                f'{name}{len(hits)}处（' + '、'.join(f'第{i}段{s}' for i, s in hits)
                + '）：每章至多2处，余者改成具体动作或直接删。'))

    # --- 叙述句首「那」（⑩） ---
    for i, p in enumerate(body, 1):
        narr = re.sub(r'“[^”]*”', '', p)
        for m in re.finditer(NA_START, narr):
            s = narr[m.end()-1:m.end()+8]
            findings.append(('BLOCK', 'na-start',
                f'第{i}段「{s}」：叙述句以「那」开头（§五-15）。换主语或并入上句。'))

    # --- 金句模板复用 ---
    if len(epigram_hits) >= 2:
        locs = '、'.join(f'第{i}段' for i, _ in epigram_hits)
        findings.append(('BLOCK', 'epigram-template',
            f'数字对比金句{len(epigram_hits)}处（{locs}），同模板复用。'
            f'真人一章舍得给一个已算奢侈，只留最强的一处。'))
    elif len(epigram_hits) == 1:
        findings.append(('WARN', 'epigram-single',
            f'数字对比金句1处（第{epigram_hits[0][0]}段），在限额内，确认是全章最强的一处再留。'))

    return findings, longest, sd, len(body)

def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__); sys.exit(2)
    total_block = 0
    for f in files:
        findings, longest, sd, n = analyze(f)
        blocks = [x for x in findings if x[0] == 'BLOCK']
        total_block += len(blocks)
        print(f'\n=== {f} ===')
        print(f'  段数{n} 最长段{longest}字 标准差{sd:.1f}')
        if not findings:
            print('  PASS 无深层AI味命中')
        for lv, code, msg in findings:
            print(f'  [{lv}] {code}: {msg}')
    print(f'\n合计 BLOCK {total_block} 处')
    sys.exit(1 if total_block else 0)

if __name__ == '__main__':
    main()
