with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复所有的 "" 为 """
content = content.replace('""\n\n        使用', '"""\n\n        使用')
content = content.replace('""\n\n    使用', '"""\n\n    使用')
content = content.replace('""\n\n    参数:', '"""\n\n    Args:')
content = content.replace('""\n\n        参数:', '"""\n\n        Args:')
content = content.replace('        ""\n\n        创建', '        """\n\n        创建')
content = content.replace('        ""\n\n        填写', '        """\n\n        填写')
content = content.replace('        ""\n\n        搜索', '        """\n\n        搜索')
content = content.replace('        ""\n\n        登录', '        """\n\n        登录')
content = content.replace('        ""\n\n        获取', '        """\n\n        获取')
content = content.replace('        ""\n\n        根据', '        """\n\n        根据')
content = content.replace('        ""\n\n        检查', '        """\n\n        检查')
content = content.replace('        ""\n\n        确认', '        """\n\n        确认')

# 修复其他未闭合的docstrings
content = content.replace('""\n', '"""\n')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
