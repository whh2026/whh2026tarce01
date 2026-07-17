# -*- coding: utf-8 -*-
"""删除test01_product_protocol.py中的乱码test_11"""

# 读取文件（使用gbk编码）
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'r', encoding='gbk', errors='ignore') as f:
    content = f.read()

# 找到第一个test_11的开始和结束
import re

# 查找第一个test_11（乱码的）
pattern = r'    def test_11_add_protocol_with_single_space_in_name\(self\):.*?(?=\n    def test_1[2-9]|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 删除乱码的test_11
    new_content = content[:match.start()] + content[match.end():]
    
    # 写回文件（使用utf-8编码）
    with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("成功删除乱码的test_11")
else:
    print("未找到需要删除的乱码test_11")
