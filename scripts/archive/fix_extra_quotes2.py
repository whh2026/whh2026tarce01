with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有的 """" 为 """
content = content.replace('""""', '"""')

# 修复所有的 """""" 为 """
content = content.replace('""""""', '"""')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
