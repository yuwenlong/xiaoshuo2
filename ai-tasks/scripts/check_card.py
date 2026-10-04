# -*- coding: utf-8 -*-
"""控制卡必含栏目检查（《写作说明》〇·七「控制卡必含栏目」）。
用法：python ai-tasks/scripts/check_card.py ai-tasks/控制卡-第NN-MM章.md [--pre]
  --pre  动笔前：查结构，不查交付后才有的「契约四问」「精读三处」。
  不带   交付前：全查。
查：①skill登记行（NCS／HW／SLW）②「已过签约红线自检」④必含小节 ⑤逐章规格表头各栏 ⑥前世回望计数行
⑦「上一次当众兑现：第N章」＋逐章规格「兑现」格〔众〕〔大〕标记，相邻间隔>3章须有「超限理由」
⑧交付前：契约四问、精读三处。
任一缺失 CARD_RC=1。只查结构，不替人判内容；内容由协议步骤与审查轮把关。"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECTIONS = ['## skill登记', '## 批次约束', '## 本批应完成', '## 逐章规格', '## 爽点循环', '## 先演对照',
            '## 线索热度', '## 场次清单', '## 时间链', '## 法条与账', '## 伏笔计划']
SPEC_COLS = ['章型', '字数目标', '日期', '循环步', '兑现', '五感点', '废笔', '长段材料']



def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pre = '--pre' in sys.argv
    if not args:
        print('用法：python ai-tasks/scripts/check_card.py <控制卡路径> [--pre]')
        return 2
    path = args[0] if os.path.isabs(args[0]) else os.path.join(ROOT, args[0])
    if not os.path.exists(path):
        print(f'[卡] 找不到 {path}')
        print('CARD_RC 1')
        return 1
    with open(path, encoding='utf-8') as f:
        card = f.read()
    rc = 0

    def need(ok, msg):
        nonlocal rc
        print(('  OK ' if ok else '  缺 ') + msg)
        if not ok:
            rc = 1

    line = next((l for l in card.split('\n') if 'skill登记：' in l), '')
    need(all(k in line for k in ('NCS', 'HW', 'SLW')), 'skill登记行（NCS／HW／SLW）')
    need('已过签约红线自检' in card, '批次约束写明「已过签约红线自检」')
    for s in SECTIONS:
        need(s in card, f'小节「{s}」')

    i = card.find('## 逐章规格')
    head_row, rows = '', []
    if i >= 0:
        for l in card[i:].split('\n')[1:30]:
            if l.startswith('|') and '章型' in l and not head_row:
                head_row = l
            elif re.match(r'\|\s*\d{2,3}\s*\|', l):
                rows.append(l)
    for c in SPEC_COLS:
        need(c in head_row, f'逐章规格表头含「{c}」')
    need(bool(rows), '逐章规格有逐章行')
    need(bool(re.search(r'前世回望[^\n]{0,40}(≤|<=)\s*2', card)), '前世回望本批计数（≤2）')

    # ⑦ 当众兑现间隔
    m = re.search(r'上一次当众兑现：\s*第\s*(\d+)\s*章', card)
    need(bool(m), '爽点循环写明「上一次当众兑现：第N章」')
    if m:
        chs = [int(m.group(1))] + [int(re.match(r'\|\s*(\d+)', r).group(1)) for r in rows if re.search('〔(众|大)〕', r)]
        gaps = [b - a for a, b in zip(chs, chs[1:])]
        last = int(re.match(r'\|\s*(\d+)', rows[-1]).group(1)) if rows else chs[0]
        tail_gap = last - chs[-1]
        over = [g for g in gaps if g > 3] + ([tail_gap] if tail_gap > 3 else [])
        print(f'  ·· 当众兑现章 {chs}，间隔 {gaps}，批末距上次 {tail_gap}')
        if over:
            need('超限理由' in card, f'当众兑现间隔超 3 章（{over}），卡上须写「超限理由」')
        if len(gaps) >= 3 and len(set(gaps)) == 1:
            print('  WARN 当众兑现间隔全等，落点须参差')

    if not pre:
        need('契约四问' in card, '交付前：契约四问结论')
        need('精读三处' in card, '交付前：精读三处结论')
    print(f'CARD_RC {rc}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
