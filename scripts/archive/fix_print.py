with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 修复所有截断的print语句
import re

# 模式1: print(f"   ?已填写XXX?)
pattern = r'print\(f"   \?([^\"]*)\?"\)'
text = re.sub(pattern, r'print(f"   ✓ \1")', text)

# 模式2: print(f'   ?已填写XXX?)  
pattern2 = r"print\(f'   \?([^\']*)\?'\)"
text = re.sub(pattern2, r"print(f'   ✓ \1')", text)

# 模式3: 其他截断的print语句
text = text.replace('print(f"   ?已填写产品介?)', 'print(f"   ✓ 已填写产品介绍")')
text = text.replace('print(f"   ?已填写使用限?)', 'print(f"   ✓ 已填写使用限制")')
text = text.replace('print(f"   ?已填写其他说?)', 'print(f"   ✓ 已填写其他说明")')
text = text.replace('print(f"   ?已填写标?)', 'print(f"   ✓ 已填写标签")')
text = text.replace('print(f"   ?已选择行业分类: 采矿?)', 'print(f"   ✓ 已选择行业分类: 采矿业")')
text = text.replace('print(f"   ?已选择 北京?)', 'print(f"   ✓ 已选择 北京市")')
text = text.replace('print(f"   ?已填写接口名?)', 'print(f"   ✓ 已填写接口名称")')
text = text.replace('print(f"   ?已进入详细信息页?)', 'print(f"   ✓ 已进入详细信息页面")')
text = text.replace('print(f"   ?已填写第', 'print(f"   ✓ 已填写第')
text = text.replace('print(f"   ?(强制) 已填写第', 'print(f"   ✓ (强制) 已填写第')
text = text.replace('print(f"   ?等待详细信息页面元素超时', 'print(f"   ✓ 等待详细信息页面元素超时')
text = text.replace('print(f"   ?继续执行测试', 'print(f"   ✓ 继续执行测试')
text = text.replace('print(f"   ?已设置精准授权为: ?)', 'print(f"   ✓ 已设置精准授权为: 是")')
text = text.replace('print(f"   ?已访问发布页?)', 'print(f"   ✓ 已访问发布页面")')
text = text.replace('print(f"   ?使用自定义产品名?)', 'print(f"   ✓ 使用自定义产品名称")')
text = text.replace('print(f"   ?使用测试数据', 'print(f"   ✓ 使用测试数据')
text = text.replace('print(f"   ?已填写中文名?)', 'print(f"   ✓ 已填写中文名称")')
text = text.replace('print(f"   ?已填写英文名?)', 'print(f"   ✓ 已填写英文名称")')
text = text.replace('print(f"   ?已选择产品类型', 'print(f"   ✓ 已选择产品类型')
text = text.replace('print(f"   ?已选择产品小类', 'print(f"   ✓ 已选择产品小类')

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
