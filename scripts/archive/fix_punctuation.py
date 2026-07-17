with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换中文标点符号为英文标点
content = content.replace('，', ',')
content = content.replace('。', '.')
content = content.replace('；', ';')
content = content.replace('：', ':')
content = content.replace('？', '?')
content = content.replace('！', '!')
content = content.replace('（', '(')
content = content.replace('）', ')')
content = content.replace('【', '[')
content = content.replace('】', ']')
content = content.replace('“', '"')
content = content.replace('”', '"')
content = content.replace('‘', "'")
content = content.replace('’', "'")
content = content.replace('—', '-')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
