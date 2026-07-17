with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

# 将\r\n替换为\n
content = content.replace(b'\r\n', b'\n')
content = content.replace(b'\r', b'\n')

# 将二进制内容解码为字符串
text = content.decode('utf-8', errors='replace')

# 修复常见的被截断字符
replacements = {
    '默认?': '默认值',
    '文?': '文件',
    '截图': '截图',
    '附加截?': '附加截图',
    '保存截?': '保存截图',
    '端口?': '端口号',
    '用户?': '用户名',
    '验证?': '验证码',
    '输入框并输?': '输入框并输入',
    '点?': '点击',
    '正在点?': '正在点击',
    'login?': 'login',
    'IP字符?': 'IP字符串',
    'IP:端口?': 'IP:端口',
    '参数或默认?': '参数或默认值',
    '支持格式:': '支持格式:',
}

for old, new in replacements.items():
    text = text.replace(old, new)

# 修复字符串未闭合的问题
# 找到所有包含?的print语句并修复
import re
text = re.sub(r'print\(f"([^"]*)\?"\)', r'print(f"\1")', text)
text = re.sub(r'print\(f\'([^\']*)\?\'', r"print(f'\1')", text)
text = re.sub(r'input\[placeholder\*=\'([^\']*)\?\']', r"input[placeholder*='\1']", text)

# 修复三引号未闭合的问题
text = re.sub(r'"""\?', r'"""', text)

# 将中文标点替换为英文标点
text = text.replace('，', ',')
text = text.replace('。', '.')
text = text.replace('；', ';')
text = text.replace('：', ':')
text = text.replace('？', '?')
text = text.replace('！', '!')
text = text.replace('（', '(')
text = text.replace('）', ')')
text = text.replace('【', '[')
text = text.replace('】', ']')

# 修复特殊的问号问题
text = text.replace('?""', '""')
text = text.replace('?"', '"')
text = text.replace("?'", "'")

# 修复占位符中的问号
text = text.replace("placeholder*='验证?", "placeholder*='验证码")
text = text.replace("placeholder*='用户?", "placeholder*='用户名")

# 修复字典格式中的问号
text = text.replace("} ?{", "}, {")
text = text.replace("}?{", "},{")

# 将修复后的文本写回文件
with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
