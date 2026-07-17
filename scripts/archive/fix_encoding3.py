with open('d:/autotrace/traceai/utils/base.py', 'rb') as f:
    content = f.read()

import re

# 查找所有包含?的位置
question_positions = []
for i in range(len(content)):
    if content[i:i+1] == b'?':
        question_positions.append(i)

print(f'Found {len(question_positions)} question marks')
for pos in question_positions[:20]:
    print(f'Position {pos}: {content[max(0,pos-10):pos+10]}')

# 尝试修复常见模式
# 模式1: UTF-8三字节字符的第三个字节被替换为?
# 例如: '\xe4\xb8\x80?' 应该是 '\xe4\xb8\x80\xe6\xac\xa1' (一次)

# 手动修复已知问题
content = content.replace(b'\xe4\xb8\x80?', b'\xe4\xb8\x80\xe6\xac\xa1')  # 一次
content = content.replace(b'\xe8\x8f\x9c?', b'\xe8\x8f\x9c\xe6\x9e\xb6')  # 窗口
content = content.replace(b'\xe7\x99\xbb?', b'\xe7\x99\xbb\xe5\xbd\x95')  # 登录
content = content.replace(b'\xe5\xa4\xb1?', b'\xe5\xa4\xb1\xe8\xb4\xa5')  # 失败
content = content.replace(b'\xe5\x91\xbd?', b'\xe5\x91\xbd\xe5\x90\x8d')  # 命名
content = content.replace(b'\xe6\x8a\xa5?', b'\xe6\x8a\xa5\xe5\x91\x8a')  # 报告
content = content.replace(b'\xe5\x80\xbc?', b'\xe5\x80\xbc')              # 值
content = content.replace(b'\xe4\xbb\xb6?', b'\xe4\xbb\xb6')              # 件
content = content.replace(b'\xe5\x90\x91?', b'\xe5\x90\x91')              # 向
content = content.replace(b'\xe7\xab\xaf?', b'\xe7\xab\xaf\xe5\x8f\xb7')  # 端口号
content = content.replace(b'\xe5\x90\x8d?', b'\xe5\x90\x8d')              # 名
content = content.replace(b'\xe7\xa0\x81?', b'\xe7\xa0\x81')              # 码
content = content.replace(b'\xe9\xa1\xb5?', b'\xe9\xa1\xb5\xe9\x9d\xa2')  # 页面
content = content.replace(b'\xe5\x85\xa5?', b'\xe5\x85\xa5')              # 输入
content = content.replace(b'\xe5\x87\xbb?', b'\xe5\x87\xbb')              # 点击
content = content.replace(b'\xe7\xbd\x91?', b'\xe7\xbd\x91')              # 网
content = content.replace(b'\xe9\x85\x8d?', b'\xe9\x85\x8d\xe7\xbd\xae')  # 配置
content = content.replace(b'\xe4\xb8\xb2?', b'\xe4\xb8\xb2')              # 串
content = content.replace(b'\xe8\xb7\xb3?', b'\xe8\xb7\xb3')              # 跳过
content = content.replace(b'\xe5\x90\x8d?', b'\xe5\x90\x8d\xe7\xa7\xb0')  # 名称
content = content.replace(b'\xe6\xad\xa5?', b'\xe6\xad\xa5')              # 步骤
content = content.replace(b'\xe4\xba\xa7?', b'\xe4\xba\xa7\xe5\x93\x81')  # 产品
content = content.replace(b'\xe6\xb5\x81?', b'\xe6\xb5\x81\xe7\xa8\x8b')  # 流程
content = content.replace(b'\xe6\xb5\x8b?', b'\xe6\xb5\x8b\xe8\xaf\x95')  # 测试
content = content.replace(b'\xe4\xb8\x9a?', b'\xe4\xb8\x9a')              # 业
content = content.replace(b'\xe5\xb8\x82?', b'\xe5\xb8\x82')              # 市
content = content.replace(b'\xe6\x8e\x88?', b'\xe6\x8e\x88\xe6\x9d\x83')  # 授权
content = content.replace(b'\xe5\xad\x98?', b'\xe5\xad\x98\xe5\x9c\xa8')  # 存在
content = content.replace(b'\xe5\xad\x97?', b'\xe5\xad\x97\xe6\xae\xb5')  # 字段
content = content.replace(b'\xe9\x94\x99?', b'\xe9\x94\x99\xe5\x87\xba')  # 出错
content = content.replace(b'\xe4\xbd\xbf?', b'\xe4\xbd\xbf\xe7\x94\xa8')  # 使用

# 修复webkit?
content = content.replace(b'webkit?', b'webkit')

# 修复浏览器窗口
content = content.replace(b'\xe6\xb5\x8f\xe8\xa7\x88\xe5\x99\xa8\xe7\xaa\x97?', b'\xe6\xb5\x8f\xe8\xa7\x88\xe5\x99\xa8\xe7\xaa\x97\xe5\x8f\xa3')

# 修复'''结尾的问题
content = content.replace(b'"""\r\n', b'"""\r\n')

with open('d:/autotrace/traceai/utils/base.py', 'wb') as f:
    f.write(content)

print('Done')

# 验证修复后的文件
with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    test_content = f.read()
print('File can be read with UTF-8')
