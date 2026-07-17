with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 删除连续的空行，只保留一个空行
fixed_lines = []
empty_count = 0
for line in lines:
    if line.strip() == '':
        empty_count += 1
        if empty_count <= 1:
            fixed_lines.append('\n')
    else:
        empty_count = 0
        fixed_lines.append(line)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Done')
