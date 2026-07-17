with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复第826行
if len(lines) > 825:
    lines[825] = lines[825].replace('继续执?', '继续执行')

# 修复第828行
if len(lines) > 827:
    lines[827] = lines[827].replace('?已访问', '✓ 已访问')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done')
