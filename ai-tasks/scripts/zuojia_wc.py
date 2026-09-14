# -*- coding: utf-8 -*-
# 作家助手口径字数统计（《写作说明》§一-2 唯一验收口径）：
# 中文字符与中文标点逐字计，连续的数字/字母/半角标点串整串只算1字；
# 与起点作家助手显示值一致（估算误差±2字，验收目标值须预留余量）。
# 用法：python ai-tasks/scripts/zuojia_wc.py 第X章*.txt（可多文件，输出极差）
import re
import sys


def zuojia(body: str) -> int:
    no_ws = re.sub(r'\s', '', body)
    non_ascii = len(re.sub(r'[!-~]', '', no_ws))
    runs = len(re.findall(r'[!-~]+', no_ws))
    return non_ascii + runs


def main() -> None:
    vals = []
    for path in sys.argv[1:]:
        with open(path, encoding='utf-8') as f:
            t = f.read()
        body = '\n'.join(t.split('\n')[1:])  # 去标题行
        v = zuojia(body)
        vals.append(v)
        print(f'{path}: {v}')
    if len(vals) > 1:
        mx, mn = max(vals), min(vals)
        flag = 'OK' if mx - mn >= 500 else 'LOW'
        print(f'range: {mx}-{mn}={mx - mn} [{flag}]')


if __name__ == '__main__':
    main()
