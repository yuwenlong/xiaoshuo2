# -*- coding: utf-8 -*-
"""UserPromptSubmit 钩子：圣上的话里出现续写、审查类字样时，把重启续写启动清单注入上下文。
不含这些字样时什么也不输出。由 .claude/settings.json 调用。"""
import json
import os
import re
import sys

try:
    data = json.loads(sys.stdin.buffer.read().decode('utf-8', errors='replace'))
except Exception:
    sys.exit(0)
prompt = str(data.get('prompt', ''))
if not re.search(r'续写|继续|接着写|日更|写第|review|审查|通审|润色|重写', prompt, re.I):
    sys.exit(0)


msg = (f'【写作执行提醒·项目钩子】本条指令涉及续写或审校，须照 AGENTS.md §6「重启续写启动清单」执行：'
       f'①看 ai-tasks/todo.md 末节与 lessons（R100：有在办批次照前例走，不连发四问）；'
       f'②按《写作说明》〇-1 加载 NCS／human-writing／story-long-write（审校另加 story-review）；'
       f'③全文读 说明/写作说明.md 到 EOF（随时更新，一律以最新内容为准）；'
       f'④照 ai-tasks/控制卡模板.md 起卡，`python ai-tasks/scripts/check_card.py 卡 --pre` CARD_RC 0 才动笔；'
       f'⑤每章写完跑 fullcheck.py 与 check_tics.py，改任何一句都重跑；'
       f'⑥交付前 `python ai-tasks/scripts/batchcheck.py 起章 止章` BATCH_RC 0，WARN 逐条裁定入卡，再做 12b 对表、通读、精读三处、契约四问与回写。')
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': msg}}, ensure_ascii=True))
