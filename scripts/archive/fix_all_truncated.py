with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有被截断的字符串
import re

# 修复所有未闭合的字符串
content = re.sub(r'print\(f"([^"]*)\?"\)', r'print(f"\1")', content)
content = re.sub(r'print\(f\'([^\']*)\?\'\)', r"print(f'\1')", content)

# 修复特定的被截断字符
content = content.replace('继续执?', '继续执行')
content = content.replace('?已访问', '✓ 已访问')

# 修复其他常见问题
content = content.replace('?已填写', '✓ 已填写')
content = content.replace('?已选择', '✓ 已选择')
content = content.replace('?已设置', '✓ 已设置')
content = content.replace('?已进入', '✓ 已进入')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
