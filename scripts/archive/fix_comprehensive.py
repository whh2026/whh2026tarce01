with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# 修复所有多余的引号
# 模式: """后面跟着"""
text = re.sub(r'\"\"\"\"\"\"', '"""', text)
text = re.sub(r'\"\"\"\"', '"""', text)

# 修复未闭合的三引号
# 找到所有 """... 但没有闭合的模式
lines = text.split('\n')
fixed_lines = []
in_triple_quote = False
for line in lines:
    triple_count = line.count('"""')
    if triple_count % 2 == 1:
        in_triple_quote = not in_triple_quote
    
    # 如果在三引号内部，不需要处理
    if in_triple_quote:
        fixed_lines.append(line)
        continue
    
    # 修复未闭合的字符串
    # 检查f字符串
    if 'f"' in line:
        quote_count = line.count('"')
        if quote_count % 2 == 1 and not line.strip().endswith('"'):
            line = line.rstrip() + '"'
    
    # 检查普通字符串
    if '"' in line and 'f"' not in line:
        quote_count = line.count('"')
        if quote_count % 2 == 1 and not line.strip().endswith('"'):
            line = line.rstrip() + '"'
    
    # 检查单引号字符串
    if "'" in line:
        quote_count = line.count("'")
        if quote_count % 2 == 1 and not line.strip().endswith("'"):
            line = line.rstrip() + "'"
    
    fixed_lines.append(line)

text = '\n'.join(fixed_lines)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
