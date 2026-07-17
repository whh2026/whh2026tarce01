with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_count = 0
for i, line in enumerate(lines):
    # 修复所有包含"?)"的行
    if '?)' in line:
        lines[i] = line.replace('?)', '")')
        fixed_count += 1
    
    # 修复所有包含"?'"的行
    if "?'" in line:
        lines[i] = line.replace("?'", "')")
        fixed_count += 1
    
    # 修复其他被截断的字符
    if '加载超)' in line:
        lines[i] = line.replace('加载超)', '加载超时')
        fixed_count += 1
    if '继续执?' in line:
        lines[i] = line.replace('继续执?', '继续执行')
        fixed_count += 1
    if '跳过本次搜)' in line:
        lines[i] = line.replace('跳过本次搜)', '跳过本次搜索')
        fixed_count += 1
    if '产品名称元' in line:
        lines[i] = line.replace('产品名称元', '产品名称元素')
        fixed_count += 1

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Fixed {fixed_count} lines')
