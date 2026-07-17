import re

# Read the file
with open('tests/ui_tests/test04_data_product_cross_env.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the end of test function with adding order process
old_code = '''        if detail_button_found:
            time.sleep(2)
            print("   ✓ 已点击查看详情按钮")
        
        print("\\n=== test_03_authorized_product_application_flow 执行完成 ===")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])'''

new_code = '''        if detail_button_found:
            time.sleep(2)
            print("   ✓ 已点击查看详情按钮")
        
        # 步骤 11: 去下单流程
        print("\\n=== 11. 去下单流程 ===")
        
        # 查找下单按钮
        order_button_selectors = [
            "button:has-text('下单')",
            "button:has-text('去下单')",
            "button:has-text('立即下单')",
            ".order-btn",
            ".el-button--primary:has-text('下单')"
        ]
        
        order_button_found = False
        for selector in order_button_selectors:
            order_button = self.page.locator(selector).first
            if order_button.count() > 0:
                try:
                    order_button.wait_for(state="visible", timeout=10000)
                    self.page.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", order_button)
                    time.sleep(1)
                    order_button.click()
                    print(f"   ✓ 使用选择器 '{selector}' 点击下单按钮成功")
                    order_button_found = True
                    break
                except Exception as e:
                    print(f"   ⚠️  选择器 '{selector}' 点击失败: {str(e)[:30]}")
                    continue
        
        if not order_button_found:
            try:
                order_button = self.page.locator("button:has-text('下单')").first
                if order_button.count() > 0:
                    self.page.evaluate("(el) => el.click()", order_button)
                    print("   ✓ 使用JavaScript强制点击下单按钮成功")
                    order_button_found = True
            except Exception as e:
                print(f"   ⚠️  JavaScript点击下单按钮失败: {str(e)[:30]}")
        
        if order_button_found:
            time.sleep(3)
            print("   ✓ 已进入下单页面")
            
            # 确认下单（如果有确认按钮）
            confirm_order_button = self.page.locator("button:has-text('确认下单'), button:has-text('提交订单')").first
            if confirm_order_button.count() > 0:
                try:
                    confirm_order_button.wait_for(state="visible", timeout=5000)
                    confirm_order_button.click()
                    time.sleep(2)
                    print("   ✓ 已确认下单")
                except Exception as e:
                    print(f"   ⚠️  确认下单失败: {str(e)[:30]}")
        
        print("\\n=== test_03_authorized_product_application_flow 执行完成 ===")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('tests/ui_tests/test04_data_product_cross_env.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('File updated successfully - added order process')
else:
    print('Old code not found')
