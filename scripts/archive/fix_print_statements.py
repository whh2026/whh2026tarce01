import re

# 读取文件内容
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并修复所有print("\n...")格式的语句
# 匹配模式：print("\n...")，其中...是任意字符直到遇到换行
pattern = r'print\(("\n[^"]*?)(\n[^"\)]*?)("\))'

# 替换为使用转义字符的版本
replacement = r'print("\\n\1\2")'

# 执行替换
fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 另一种模式：print("\n...")，其中字符串在多行中
pattern2 = r'print\(("\n)([^"\)]*?)("\))'
replacement2 = r'print("\\n\2")'
fixed_content = re.sub(pattern2, replacement2, fixed_content, flags=re.DOTALL)

# 写入修复后的内容
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("已修复所有print语句的语法错误")
