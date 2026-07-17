with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 修复转义的引号
text = text.replace('\\"', '"')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
