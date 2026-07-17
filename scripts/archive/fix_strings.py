with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # 修复未闭合的f字符串
    if 'f"' in line and line.count('"') % 2 == 1:
        # 找到最后一个f"并添加闭合引号
        if line.strip().endswith('测试'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('页面'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('信息'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('授权'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('分类'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('名称'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('介绍'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('限制'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('说明'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('标签'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('类型'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('小类'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('北京市'):
            line = line.rstrip() + '"\n'
        elif line.strip().endswith('采矿业'):
            line = line.rstrip() + '"\n'
        elif '?' in line and line.strip().endswith('?'):
            line = line.rstrip('?') + '"\n'
    
    # 修复包含?的print语句
    if 'print(f"' in line and '?"' in line:
        line = line.replace('?"', '")')
    
    # 修复其他未闭合的字符串
    if 'f"' in line and not line.rstrip().endswith('"'):
        # 简单的修复：在末尾添加引号
        line = line.rstrip() + '"\n'
    
    fixed_lines.append(line)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Done')
