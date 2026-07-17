with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

# 找到第826行
lines = content.split(b'\n')
if len(lines) > 825:
    line826 = lines[825]
    print(f'Line 826: {line826}')
    
    # 检查双引号数量
    quote_count = line826.count(b'"')
    print(f'Double quotes count: {quote_count}')

# 修复第826行 - 使用UTF-8编码的字符串
new_line = '                print(f"   [警告] 页面加载超时,继续执行")\r\n'
lines[825] = new_line.encode('utf-8')

content = b'\n'.join(lines)

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Fixed')
