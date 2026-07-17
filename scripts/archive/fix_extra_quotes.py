with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 修复多余的引号
import re

# 模式: 去掉行末多余的引号
text = re.sub(r'(print\(f"[^"]*"\))"', r'\1', text)
text = re.sub(r'(print\(f\'[^\']*\'\))"', r'\1', text)
text = re.sub(r'(print\("[^"]*"\))"', r'\1', text)
text = re.sub(r'(print\(\'[^\']*\'\))"', r'\1', text)

# 修复其他多余引号的情况
text = re.sub(r'"\n', '\n', text)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
