with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    lines = f.readlines()

if len(lines) > 893:
    line894 = lines[893]
    print(f'Line 894: {line894}')
    print(f'Double quote count: {line894.count(b"\"")}')

# 直接修复第894行
new_line = '                    print(f"   [警告] 搜索后页面加载超时")\r\n'
lines[893] = new_line.encode('utf-8')

content = b''.join(lines)

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Fixed')
