# -*- coding: utf-8 -*-
"""口癖四类按功能计数（《写作说明》§五-16⑦；lessons R35／R97 扩词表）。
用法：python ai-tasks/scripts/check_tics.py 98 99 ...（章号）
逐章逐类打印命中数与命中词，任一类 >2 标「!」并令退出码为 1。
计数口径按功能、不按字面（98-102 审查轮文字路补：没急着／没马上／没先说／没再追／没抬头／没再看，另立「V了V」一类；103-107 审查轮文字路补：计时「隔／过／搁／等了一阵」「有一口气的工夫」并排除「后半晌」误报，V了V 补凑压站搁推翻瞅瞄等试问）：同功能变体一并计入；削口癖须换成人物自己的动作，
不得换成另一种不作为（「没说话」改「没接话」不算改）。写作轮与审查轮用同一张词表。
命中词不等于病句，逐处人工复核：技术数值（「一秒半」）、引语计数（「十个字」为大纲定句）等可留，理由入控制卡。"""
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = os.path.join(ROOT, '正文', '卷一')
CATS = [
    ('不作为', r'没说话|没吭声|没出声|没接话|没应声|没理|没答|没再说|没人说话|没往下|谁也没|没人接|没急着|没马上|没先说|没再追|没抬头|没再看'),
    ('计时', r'两秒|几秒|半秒|一秒|(?<!后)半晌|看了一会儿|看了好一阵|一会儿|好一阵|半天|[隔过搁等]了一阵|有一口气的工夫|很久|挺长时间|好一会儿'),
    ('计数', r'[一二三四五六七八九十两]个字'),
    ('万能', r'笑了笑|点了点头|点点头|点头|像是|琢磨了一下'),
    ('静', r'静了|安静|静下来|鸦雀无声'),
    ('V了V', r'(看|想|咧|仰|笑|顿|停|点|摸|拍|摆|揉|搓|抿|挪|晃|扬|抬|擦|蹭|敲|戳|凑|压|站|搁|推|翻|瞅|瞄|等|试|问|让|抹|碰|吹)了\1'),
]


def main() -> int:
    rc = 0
    for n in sys.argv[1:]:
        p = os.path.join(D, f'第{int(n):02d}章.txt')
        with open(p, encoding='utf-8') as f:
            body = '\n'.join(f.read().split('\n')[1:])
        out = []
        for name, pat in CATS:
            ms = [m.group(0) for m in re.finditer(pat, body)]
            flag = '!' if len(ms) > 2 else ''
            if flag:
                rc = 1
            out.append(f'{name}{len(ms)}{flag}({",".join(ms)})')
        # 另两类（《写作说明》§五-16⑦之⑥⑦；叙述层＝剥掉引号内对白）
        narr = re.sub(r'“[^”]*”', '', body)
        kchars = max(1, len(re.sub(r'\s', '', body))) / 1000
        light = [m.group(0) for m in re.finditer(r'了(?:[一两三几半])?[下阵圈道声眼口气会]', narr)]
        flag = '!' if (len(light) >= 5 and len(light) / kchars >= 6) else ''
        if flag:
            rc = 1
        out.append(f'轻补语{len(light)}({len(light) / kchars:.1f}/千字){flag}')
        neg = [m.group(0) for m in re.finditer(r'(?:没有|没|不)[^，。！？；\n]{1,10}[，；]\s*[^，。！？；\n]{0,6}?也(?:没有|没|不)', narr)]
        flag = '!' if len(neg) > 2 else ''
        if flag:
            rc = 1
        out.append(f'否定对偶{len(neg)}{flag}({",".join(neg)})')
        print(f'第{n}章 ' + ' | '.join(out))
    print(f'TICS_RC {rc}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
