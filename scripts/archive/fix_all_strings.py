with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # 修复未闭合的f字符串
    if 'f"' in line and line.count('"') % 2 == 1:
        if not line.strip().endswith('"'):
            line = line.rstrip() + '"\n'
    
    # 修复未闭合的普通字符串
    if '"' in line and line.count('"') % 2 == 1 and 'f"' not in line:
        if not line.strip().endswith('"'):
            line = line.rstrip() + '"\n'
    
    # 修复未闭合的单引号字符串
    if "'" in line and line.count("'") % 2 == 1:
        if not line.strip().endswith("'"):
            line = line.rstrip() + "'\n"
    
    # 修复未闭合的三引号
    if '"""' in line:
        count = line.count('"""')
        if count % 2 == 1:
            line = line.rstrip() + '"""\n'
    
    fixed_lines.append(line)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Done')
