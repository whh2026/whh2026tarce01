import os
import re

def generate_test_doc(filepath):
    """为测试文件生成文档"""
    if not os.path.exists(filepath):
        print(f'✗ 文件不存在: {filepath}')
        return
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 提取类名
    class_match = re.search(r'class (\w+)\(.*\):', content)
    class_name = class_match.group(1) if class_match else 'Unknown'
    
    # 提取类的文档字符串（如果有）
    class_doc_match = re.search(r'class \w+\(.*\):\s*"""([\s\S]*?)"""', content)
    class_doc = class_doc_match.group(1).strip() if class_doc_match else '待补充'
    
    # 提取测试方法
    methods = re.findall(r'def (test_\d+.*?)\(', content)
    
    # 提取setup和teardown方法
    setup_methods = re.findall(r'def (setup_|teardown_)\w+\(', content)
    
    # 创建文档
    doc_content = f'''# {class_name} 测试文档

## 文件路径
`{filepath}`

## 测试类概述
{class_doc}

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
'''
    
    for i, method in enumerate(methods, 1):
        doc_content += f'| {i} | `{method}` | 待补充 |\n'
    
    doc_content += f'''
## 测试覆盖范围

## 生命周期方法
- {', '.join(set(setup_methods)) if setup_methods else '无'}

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
'''
    
    # 写入文档
    doc_filename = f'docs/{filepath.split("/")[-1].replace(".py", ".md")}'
    with open(doc_filename, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print(f'✓ 已生成: {doc_filename}')

def main():
    test_files = [
        'tests/ui_tests/test01_product_protocol.py',
        'tests/ui_tests/test02_product_strategy.py',
        'tests/ui_tests/test03_data_product.py',
        'tests/ui_tests/test04_data_product_cross_env.py',
        'tests/ui_tests/test05_product_list_page.py',
        'tests/ui_tests/test06_application_approval_page.py',
        'tests/ui_tests/test07_approve_page.py',
        'tests/ui_tests/test08_received_list_page.py',
        'tests/ui_tests/test09_source_received_list_page.py',
        'tests/ui_tests/test02_protocol_security_injection.py',
        'tests/ui_tests/test002_user_management_rules.py',
        'tests/ui_tests/testd001_company_management.py',
        'tests/ui_tests/testd002_user_management.py'
    ]
    
    for filepath in test_files:
        generate_test_doc(filepath)
    
    print('\n✅ 文档生成完成！')

if __name__ == '__main__':
    main()
