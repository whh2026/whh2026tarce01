# -*- coding: utf-8 -*-
"""删除test01_product_protocol.py中的乱码test_11"""

# 读取文件
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到第一个test_11的开始和结束行
start_line = None
end_line = None

for i, line in enumerate(lines):
    # 查找第一个test_11（乱码的）
    if 'def test_11_add_protocol_with_single_space_in_name(self):' in line and start_line is None:
        start_line = i
        # 查找这个方法的结束（下一个def之前）
        for j in range(i + 1, len(lines)):
            if lines[j].strip().startswith('def ') and 'test_11' not in lines[j]:
                end_line = j
                break
        break

if start_line is not None and end_line is not None:
    # 删除乱码的test_11
    new_lines = lines[:start_line] + lines[end_line:]
    
    # 写回文件
    with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"成功删除乱码的test_11（第{start_line+1}行到第{end_line}行）")
else:
    print("未找到需要删除的乱码test_11")
