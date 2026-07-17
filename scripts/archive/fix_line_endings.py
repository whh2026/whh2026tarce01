with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

# 将\r替换为\n
content = content.replace(b'\r', b'\n')

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Done')
