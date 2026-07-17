import os

def replace_port_in_file(filepath, old_port, new_port):
    """替换文件中的端口号"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_port in content:
            new_content = content.replace(old_port, new_port)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    old_port = "30201"
    new_port = "30001"
    updated_count = 0
    
    # 需要修改的文件列表
    files_to_update = [
        "tests/ui_tests/test04_data_product_cross_env.py",
        "utils/base.py",
        "docs/base_methods.md",
        "test_debug.py",
        "debug-login-timeout-183.md"
    ]
    
    for filepath in files_to_update:
        if os.path.exists(filepath):
            if replace_port_in_file(filepath, old_port, new_port):
                updated_count += 1
    
    print(f"\n✅ 已更新 {updated_count} 个文件，端口从 {old_port} 改为 {new_port}")

if __name__ == "__main__":
    main()
