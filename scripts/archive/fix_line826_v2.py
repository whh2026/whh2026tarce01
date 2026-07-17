with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

# 找到第826行
lines = content.split(b'\n')
if len(lines) > 825:
    line826 = lines[825]
    print(f'Line 826: {line826}')
    print(f'Line 826 length: {len(line826)}')
    
    # 检查双引号数量
    quote_count = line826.count(b'"')
    print(f'Double quotes count: {quote_count}')
    
    # 检查是否有未闭合的字符串
    if quote_count % 2 != 0:
        print('UNBALANCED QUOTES!')
    else:
        print('Quotes are balanced')

# 直接修复第826行
lines[825] = b'                print(f"   [警告] 页面加载超时,继续执行")\r'

content = b'\n'.join(lines)

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Fixed')
