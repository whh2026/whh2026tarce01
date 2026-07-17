with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有被截断的字符串
import re

# 模式1: 修复所有 f"..." 中未闭合的字符串
# 查找所有以 f" 开头但没有正确闭合的字符串
# 匹配模式: f"..." 中间包含?但没有正确闭合
pattern = r'print\(f"([^"]*?)\?"\)'
content = re.sub(pattern, lambda m: f'print(f"{m.group(1)}")', content)

# 模式2: 修复所有 f'...' 中未闭合的字符串
pattern2 = r"print\(f'([^']*?)\?'\)"
content = re.sub(pattern2, lambda m: f"print(f'{m.group(1)}')", content)

# 模式3: 修复所有普通字符串中未闭合的情况
pattern3 = r'"([^"]*?)\?"'
content = re.sub(pattern3, lambda m: f'"{m.group(1)}"', content)

# 模式4: 修复选择器字符串中未闭合的情况
pattern4 = r"'([^']*?)\?'"
content = re.sub(pattern4, lambda m: f"'{m.group(1)}'", content)

# 修复特定的被截断字符
content = content.replace('申请理]', '申请理由]')
content = content.replace('未找到立即申请按', '未找到立即申请按钮')
content = content.replace('页面加载超', '页面加载超时')
content = content.replace('继续执', '继续执行')
content = content.replace('跳过本次搜', '跳过本次搜索')
content = content.replace('产品名称元', '产品名称元素')
content = content.replace('验证码]', '验证码]')
content = content.replace('用户名]', '用户名]')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
