# -*- coding: utf-8 -*-
"""使用chardet自动检测并修复test01_product_protocol.py文件的编码问题"""

import chardet

# 读取文件的二进制内容
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'rb') as f:
    raw_data = f.read()

# 检测编码
result = chardet.detect(raw_data)
detected_encoding = result['encoding']
confidence = result['confidence']

print(f"检测到的编码: {detected_encoding} (置信度: {confidence:.2f})")

# 尝试使用检测到的编码读取文件
if detected_encoding:
    try:
        content = raw_data.decode(detected_encoding)
        # 写回文件（使用utf-8编码）
        with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"成功使用{detected_encoding}编码读取并转换为utf-8")
    except Exception as e:
        print(f"使用{detected_encoding}编码读取失败: {e}")
        # 尝试使用gbk编码
        try:
            content = raw_data.decode('gbk', errors='ignore')
            # 写回文件（使用utf-8编码）
            with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("使用gbk编码读取并转换为utf-8")
        except Exception as e:
            print(f"使用gbk编码读取失败: {e}")
            # 尝试使用utf-8编码
            try:
                content = raw_data.decode('utf-8', errors='ignore')
                # 写回文件（使用utf-8编码）
                with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("使用utf-8编码读取并转换为utf-8")
            except Exception as e:
                print(f"使用utf-8编码读取失败: {e}")
else:
    print("无法检测到文件编码")
