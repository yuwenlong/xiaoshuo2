#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""投稿件自检（R18 闸门·核对清单第5项配套脚本）

立条背景：清单第5项原文引用 `check-ai-patterns.js`，**该文件从不存在**，
于是这一项历批被跳过（与 lessons R24「永远报错的 grep 被当成零残留」同源）。
实证：圣上查问「桌面的投稿大纲改了吗」，臣实查才发现大纲文案整体从未过机检，
      漏掉卷六「第一个部门」与庞坚「摆在第一位」两处序数词。

要点：**大纲文案是硬编码，正文是实时读取**。重跑脚本只同步正文；
      大纲文案必须当成一篇独立新稿，整体过全套机检，而非只核改动处。

用法：python ai-tasks/scripts/check_submission.py [docx路径]
退出码 0 方为通过。
"""
import sys, io, re, zipfile, html, os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

DEFAULT = 'C:/Users/yuwen/Desktop/《重生2011：从被优化开始》投稿材料（大纲+正文1-10章）.docx'

CHECKS = [
    ('① 序数词',        r'第[一二三四五六七八九十](?!章)|首先|其次|最后(?!一)'),
    ('①b 破折号/省略号', r'——|……'),
    ('①c 真实地名',      r'北京|上海|广州|深圳|杭州|济南|天津|南京|成都|武汉|西安|中关村|清华|北大'),
    ('② 脸谱化词库',     r'指节|指腹|骨节|薄茧|一丝|一抹|瞬间|死寂|沙哑|眸色一暗|眼底闪'),
    ('③ 「那」字开头句',  r'(?m)^那'),
    ('④b 直引号',        r'"'),
    ('④b 叙述语截断混搭', r'。”[^。”]{1,25}?，“'),
    ('反AI·不是X而是Y',  r'不是[^，。]{1,12}[，]?而是|并非[^，。]{1,12}而是|与其说[^，。]{1,12}不如说'),
    ('反AI·看似实则',    r'看似[^，。]{1,12}实则|表面[^，。]{1,12}实际'),
    ('行话黑名单',       r'赋能|抓手|闭环|底层逻辑|颗粒度|链路|心智|复盘一下|对齐'),
    ('模型腔',           r'说白了|说穿了|先说结论|值得注意的是|需要指出的是|从某种意义上说'),
]

def extract(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    x = x.replace('</w:p>', '\n')
    x = re.sub(r'<w:br[^>]*/>', '\n', x)
    x = re.sub(r'<[^>]+>', '', x)
    return html.unescape(x)

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    if not os.path.exists(path):
        print(f'[FAIL] 找不到投稿件：{path}'); sys.exit(2)
    t = extract(path)
    marker = '正文（第1—10章）'
    if marker not in t:
        print(f'[WARN] 未找到正文分界标记「{marker}」，退回全件检查')
        head = t
    else:
        head = t.split(marker)[0]

    print(f'=== 投稿件大纲文案自检 ===\n件：{os.path.basename(path)}\n大纲文案 {len(head)} 字\n')
    total = 0
    for name, pat in CHECKS:
        hits = [m.group(0) for m in re.finditer(pat, head)]
        if hits:
            total += len(hits)
            ctx = []
            for m in list(re.finditer(pat, head))[:3]:
                s = max(0, m.start()-16); e = min(len(head), m.end()+16)
                ctx.append(head[s:e].replace('\n', ' '))
            print(f'  [BLOCK] {name}：{len(hits)}处')
            for c in ctx:
                print(f'          …{c}…')
        else:
            print(f'  [OK]    {name}')
    print(f'\n合计 BLOCK {total} 处' if total else '\n大纲文案机检零残留 ✓')
    sys.exit(1 if total else 0)

if __name__ == '__main__':
    main()
