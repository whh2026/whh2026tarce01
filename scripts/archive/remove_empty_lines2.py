with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    if line.strip() != '':
        fixed_lines.append(line)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Done. Removed {len(lines) - len(fixed_lines)} lines")
print(f"Original: {len(lines)} lines")
print(f"Fixed: {len(fixed_lines)} lines")
