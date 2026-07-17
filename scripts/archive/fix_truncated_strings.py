with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_count = 0
for i, line in enumerate(lines):
    # 修复所有被截断的字符串
    if '加载超)' in line:
        lines[i] = line.replace('加载超)', '加载超时')
        fixed_count += 1
    if '继续执?' in line:
        lines[i] = line.replace('继续执?', '继续执行')
        fixed_count += 1
    if '跳过本次搜)' in line:
        lines[i] = line.replace('跳过本次搜)', '跳过本次搜索')
        fixed_count += 1

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Fixed {fixed_count} lines')
