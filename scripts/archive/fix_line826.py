with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

# 修复第826行的问题 - 把"?)"替换为"行"
content = content.replace(b'\\xe6\\x89\\xa7?)', b'\\xe6\\x89\\xa7\\xe8\\xa1\\x8c')

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Done')
