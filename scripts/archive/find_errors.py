import ast

with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
errors = []

for i in range(len(lines)):
    # 检查单行的语法
    try:
        ast.parse(lines[i])
    except SyntaxError as e:
        # 检查是否是字符串未闭合
        if 'EOL while scanning string literal' in str(e):
            if 'f"' in lines[i] or '"' in lines[i]:
                errors.append(f"Line {i+1}: Unclosed string - {lines[i][:50]}...")
            elif '"""' in lines[i]:
                errors.append(f"Line {i+1}: Unclosed triple quote - {lines[i][:50]}...")
        elif 'invalid syntax' in str(e):
            errors.append(f"Line {i+1}: Invalid syntax - {lines[i][:50]}...")

print(f"Found {len(errors)} potential syntax errors:")
for err in errors[:50]:
    print(err)
