with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# 查找所有未闭合的三引号
pattern = r'\"\"\"([^\"]*)\"\"'
matches = re.findall(pattern, text)
print(f'Found {len(matches)} unclosed triple quotes')
for m in matches[:10]:
    print(f'  """{m}""')

# 修复所有未闭合的三引号
text = re.sub(r'\"\"\"([^\"]*)\"\"', r'\"\"\"\1\"\"\"', text)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
