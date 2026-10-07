# -*- coding: utf-8 -*-
"""本批全套机检汇总：①①b①c②③④④b⑤⑦＋段落统计＋对话占比＋翻案/省略号/群像。
用法：python ai-tasks/scripts/fullcheck.py 48 49 ...（章号）
硬项：①禁用词序数 ①b破折号 ①c真实地名 ②脸谱化 ③行首那 翻案/省略号/群像/第N序数 ④相邻非空行 ④b check_punct ⑦ check_ai_taste 段长>200或全章无>120段；⑤字数与对话占比只打印，按控制卡章型人工判。
每项单独打印命中条数；任一硬项≠0 则 ALL_RC=1。"""
import sys, re, subprocess, statistics, os, glob
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, '正文', '卷一')


def chap_path(n):
    # R32：跨卷后按章号在各卷目录里找，找不到时落到最后一卷目录
    name = f'第{int(n):02d}章.txt'
    vols = sorted(glob.glob(os.path.join(ROOT, '正文', '卷*')))
    for v in vols:
        p = os.path.join(v, name)
        if os.path.exists(p):
            return p
    return os.path.join(vols[-1] if vols else D, name)
BAN = r'然而|此外|总之|因此|综上所述|由此可见|首先|其次|最后|第一|第二|第三|一方面|另一方面|至关重要|显而易见|毫无疑问|必然|绝对|赋能|抓手|闭环|底层逻辑|颗粒度|链路|心智'
REAL = r'北京|上海|广州|深圳|杭州|大连|中关村|清华|北大|金山|词霸|新浪|奇安信|华图|有道|欧路|海词|香港|广东|广西|福建|浙江|江苏|山东|河北|河南|湖北|湖南|四川|云南|贵州|陕西|山西|辽宁|吉林|黑龙江|安徽|江西|海南|甘肃|青海|宁夏|新疆|西藏|内蒙古|台湾|天津|重庆|济南|武汉|南京|成都|西安|长沙'
FACE = r'松木香|瑞凤眼|修长的手指|指节|骨节|指腹|薄茧|勾起一丝|深不见底|猪肝色|暂停键|钢针|指甲深陷入掌心|眸色一暗|眼底闪|死寂|沙哑|好整以暇|一抹|一丝|瞬间|混杂'
# ---- 增补（《写作说明》§五-15／§五-4／§五-13／§五-5／§四-11④；叙述层＝剥掉引号内对白后的文字）----
# ②b 万能副词与套式表情（叙述层硬项）
AIW = (r'不禁|竟然|缓缓|微微|淡淡|似笑非笑|嘴角(?:微扬|上扬|勾起|一勾|一扬)|仿佛|犹如|宛若|宛如'
       r'|(?<!比)如同(?!事|学|行|龄|期|伴)|些许|隐约|深吸一口气|[眼眸][中里底]闪过|眉头微皱'
       r'|瞳孔(?:微缩|一缩|收缩|骤缩)|心中一动|心头一[震凛紧]|心下了然|心中暗道|心猛地一沉|不由得|不由自主'
       r'|情不自禁|话锋一转|映入眼帘|(?:^|[。！？，])只见|此时此刻|[沉冷低]声道|说道|问道|笑道'
       r'|脸色一变|目光如炬|不容置[疑喙]|不易察觉|不可否认|前所未有|可谓|意义深远|未来可期|于是乎'
       r'|与此同时|从而|因而|诚然|不难看出|事实上|取而代之|散发着|深邃|凛冽|狡黠|眼神复杂'
       r'|[他她](?:感到|意识到|终于明白)|这一刻')
# 套式声线（叙述层硬项）
VOICE = (r'[，,]带着(?:一丝|一股|几分|些许|点|股)?[^，。]{0,6}?(?:意味|味道|情绪|笑意|怒意|嘲讽|无奈|疲惫|冷意|寒意|气息|语气)'
         r'|(?:声音|语气|嗓音)[^。！？]{0,4}不(?:大|高|重)[，,][^。！？]{0,6}却'
         r'|(?:语气|声音)[^。！？]{0,12}(?:平静|平淡|冷静|平直)[^。！？]{0,12}(?:像|仿佛|如同)[^。！？]{0,16}(?:念|读|报|宣判)'
         r'|听不出(?:情绪|喜怒)')
# 翻案外衣（叙述与对白都查，硬项；反序「是A，不是B」另列人工）
FANAN = (r'不在于[^。！？\n]{0,40}而在于'
         r'|(?:总|一直|都|还|原)?以为[^！？\n]{2,60}?(?:其实|才发现|才明白|才知道|现在看|原来)'
         r'|回头(?:看|一看)?才(?:发现|明白|知道)'
         r'|表面(?:上)?[^！？\n]{0,60}(?:其实|实际|实则)|恰恰相反'
         r'|[^，。！？\n]{1,12}不重要[，。]\s*(?:重要|要紧)的是|真正[^，。！？\n“”]{0,16}的(?:，)?是(?!不是)|从来(?:都)?与[^。！？，\n]{1,12}无关'
         r'|(?:没有|没)[^，。！？\n]{1,10}，(?:没有|没)[^，。！？\n]{1,10}，[^。！？\n]{0,6}(?:只有|只是)')
# 洞察路标（叙述层硬项）
ROAD = r'更[^，。！？“”\n]{1,3}的是|还有一层|值得注意的是|需要指出的是|从某种意义上(?:说|讲)?|只说对了一半|真正的问题是|(?:^|[。！？])(?:要命|要紧|关键|问题)(?:的)?是'
# 名词化（叙述层硬项）
NOMI = (r'进行(?:了|一次|一场|着)?[^。，！？\n]{0,10}(?:调整|优化|升级|分析|讨论|沟通|梳理|复盘|探索|尝试|思考|规划|布局)'
        r'|实现了?[^。，！？\n]{0,14}(?:提升|增长|突破|转变|跃升|落地)|完成了?对[^。，！？\n]{0,16}的'
        r'|起到了?[^。，！？\n]{0,12}作用|具有[^。，！？\n]{0,10}(?:意义|价值)')
# 抽象主语抒情（叙述层硬项）
ABSV = r'(?:时间|岁月|日子|年月|记忆|焦虑|孤独|命运|时代)(?:会|把|在|正)?[^。，！？\n]{0,4}(?:带走|磨平|冲淡|保管|收走|显出|发芽|教会|吞掉|甩下)'
# 情绪翻译（硬项）
EMOTR = r'一如[^。！？\n]{0,8}(?:心境|心情|此刻)|(?:心境|心情)[^。\n]{0,4}一样'
EXTRA = [
    ('翻案 不是…而是', r'不是[^。！？]{0,20}而是'),
    ('翻案 并非/与其说/看似实则', r'并非|与其说|看似[^。]{0,15}实则|说白了|说穿了|说到底'),
    ('省略号', r'……|\.\.\.'),
    ('群像 有人…有人', r'有人[^，。；]{2,14}[，；](又|还)?有人|有人[^。]{2,40}；(又|还)?有人[^。]{2,40}；(又|还)?有人'),
    ('序数 头一/末一以外的 第N', r'第[一二三四五六七八九十]+(?![章卷])'),
    ('翻案外衣', FANAN),
]
allrc = 0
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

def paras(text):
    lines = text.split('\n')[1:]
    return [l.strip() for l in lines if l.strip()]

for n in sys.argv[1:]:
    p = chap_path(n)
    t = open(p, encoding='utf-8').read()
    body = '\n'.join(t.split('\n')[1:])
    narr = re.sub(r'“[^”]*”', '', body)  # 叙述层：剥掉引号内文字，行结构不变
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
    hit('②b 万能副词（叙述层）', AIW, src=narr)
    hit('②c 套式声线（叙述层）', VOICE, src=narr)
    hit('洞察路标（叙述层）', ROAD, src=narr)
    hit('名词化（叙述层）', NOMI, src=narr)
    hit('抽象抒情（叙述层）', ABSV, src=narr)
    hit('情绪翻译', EMOTR)
    hit('④c 叙述冒号', r'(?<!\d)[：:](?!\d)', src=narr)
    hit('①b2 双连字符', r'(?<![A-Za-z0-9])--(?![A-Za-z0-9])')
    hit('③ 行首那', r'^\s*那')
    for name, pat in EXTRA:
        hit(name, pat)
    # 翻案变体「不是A，是B」（省掉而）：口语里也有正常用法，列出来人工裁，不计硬项（58-62 审查轮漏网补）
    hit('翻案变体 不是A，是B', r'不是[^。！？，“”]{1,14}，(是|就是)[^。！？]', hard=False)
    hit('翻案反序 是A，不是B', r'是[^，。！？\n“”]{1,12}，(?:而)?不是[^，。！？\n“”]{1,12}', hard=False)
    # 天气起场（段首 20 字内「日子＋天气」；每章≤2，超出改成人和事的过渡）
    wx = [i for i, l in enumerate(body.split(chr(10)), 2) if re.search(r'^(礼拜.|周.|今天|这天|那天|隔天|早上|上午|下午|傍晚|夜里|晚上|半夜)[^。，]{0,12}(雨|雪|雾|霾|风|晴|阴天|冷|热|白霜|结冰)', l.strip())]
    print(f'[天气起场] {len(wx)} (人工，≤2)' + (' 行' + ','.join(map(str, wx)) if wx else ''))
    # ⑪ WARN 项（《写作说明》§五-3／§五-6／§五-7／§四-12；只打印，人工裁定入卡）
    qs = re.findall(r'“([^”]*)”', body)
    tone = sum(len(re.findall(r'[吧呢啊嘛呗哎嗯哦呀啦]', q)) for q in qs)
    print(f'[对白语气词] {tone} (WARN：为 0 须入卡说明)')
    ENVW = r'天|云|雨|雪|风|阳光|太阳|月亮|灯|光|窗外|楼下|空气|霾|雾|树|街|路面|玻璃|墙'
    PRON = r'他|她|我|你|们|陈序|秦深|林见夏|袁野|乔漫|庞坚|组长|孙鹏|小满|老|小'
    sents = [x for x in re.split(r'[。！？\n]', narr) if x.strip()]
    envs = [bool(re.search(ENVW, x)) and not re.search(PRON, x) for x in sents]
    runmax = run = 0
    for e in envs:
        run = run + 1 if e else 0
        runmax = max(runmax, run)
    print(f'[环境句] 连续最长 {runmax}（WARN>2）占比 {sum(envs) * 100 / max(1, len(sents)):.1f}%（WARN>12%）')
    ps0 = paras(t)
    r3 = r3m = 0
    for x in ps0:
        r3 = r3 + 1 if (not x.startswith('“') and len(x) <= 15) else 0
        r3m = max(r3m, r3)
    print(f'[碎段] 连续单句叙述短段最长 {r3m}（WARN≥3）')
    head, tail = body.strip()[:500], body.strip()[-200:]
    TICW = r'两秒|几秒|半晌|一会儿|好一阵|笑了笑|点头|像是|没说话|没吭声|静了|安静|了一下|了一眼|了一声|仿佛|似的'
    hh, th = re.findall(TICW, head), re.findall(TICW, tail)
    print(f'[精读三处] 开头500 {hh} 章末200 {th}（WARN：非空须精修）')
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
