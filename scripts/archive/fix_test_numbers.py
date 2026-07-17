# -*- coding: utf-8 -*-
"""重新添加test_11并修正编号"""

# 读取文件
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 将test_12改为test_11，test_13改为test_12
content = content.replace('def test_12_add_protocol_with_multiple_spaces_in_name', 'def test_11_add_protocol_with_multiple_spaces_in_name')
content = content.replace('def test_13_add_protocol_with_spaces_in_multiple_fields', 'def test_12_add_protocol_with_spaces_in_multiple_fields')

# 写回文件
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("成功修正测试用例编号")
print("test_12 -> test_11: 协议名称包含多个空格")
print("test_13 -> test_12: 协议名称、描述、标题都包含空格")
