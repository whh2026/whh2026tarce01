#!/usr/bin/env python3
"""
简化版数据产品流程调试脚本
专注于关键步骤：基础配置→详细信息→上架信息
"""

import time
from playwright.sync_api import sync_playwright
from tests.test_data.data_product_data import TEST_URLS, SELECTORS, WAIT_TIMES

def debug_data_product_flow():
    """调试数据产品完整流程"""
    with sync_playwright() as playwright:
        # 启动浏览器（非无头模式，便于查看）
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录系统
            print("=== 1. 登录系统 ===")
            page.goto("http://192.168.0.183:30001/login")
            time.sleep(WAIT_TIMES["page_load"])
        # 查找用户名输入框并输入
            page.fill("input[name='username'], input[id='username'], input[placeholder*='用户名']", username)
            
            # 查找密码输入框并输入
            page.fill("input[name='password'], input[id='password'], input[placeholder*='密码']", password)

            # 查找验证码输入框并输入
            page.fill("input[name='captchaAnswer'], input[id='captchaAnswer'], input[placeholder*='验证码']", captchaAnswer)
            
            # 查找登录按钮并点击
            page.click("button[type='submit'], button:has-text('登录'), input[type='submit']")
            print("登录成功！")
            
            # 2. 访问数据产品发布页面
            print("\n=== 2. 访问数据产品发布页面 ===")
            page.goto(TEST_URLS["data_product_create"])
            time.sleep(WAIT_TIMES["page_load"])
            print(f"已访问页面: {TEST_URLS['data_product_create']}")
            
            # 3. 填写基础配置
            print("\n=== 3. 填写基础配置 ===")
            
            # 填写中文名称
            if page.is_visible(SELECTORS["data_product_name_input"]):
                page.fill(SELECTORS["data_product_name_input"], "测试数据产品_2024")
                print("✓ 已填写中文名称: 测试数据产品_2024")
            
            # 填写英文名称
            if page.is_visible(SELECTORS["data_product_english_name_input"]):
                page.fill(SELECTORS["data_product_english_name_input"], "TestDataProduct_2024")
                print("✓ 已填写英文名称: TestDataProduct_2024")
            
            # 填写产品介绍
            if page.is_visible(SELECTORS["data_product_desc_textarea"]):
                page.fill(SELECTORS["data_product_desc_textarea"], "这是一个用于自动化测试的数据产品")
                print("✓ 已填写产品介绍")
            
            # 选择行业分类
            if page.is_visible(SELECTORS["data_product_category_select"]):
                page.click(SELECTORS["data_product_category_select"])
                time.sleep(0.5)
                page.get_by_text("采矿业").click()
                print("✓ 已选择行业分类: 采矿业")
            
            # 选择产品类型
            if page.is_visible(SELECTORS["data_product_type_select"]):
                page.click(SELECTORS["data_product_type_select"])
                time.sleep(0.5)
                page.get_by_text("数据接口").click()
                print("✓ 已选择产品类型: 数据接口")
            
            # 选择产品小类
            if page.is_visible(SELECTORS["data_product_subtype_select"]):
                page.click(SELECTORS["data_product_subtype_select"])
                time.sleep(0.5)
                page.get_by_text("API接口").click()
                print("✓ 已选择产品小类: API接口")
            
            # 选择地域分类
            if page.is_visible(SELECTORS["data_product_region_select"]):
                page.click(SELECTORS["data_product_region_select"])
                time.sleep(0.5)
                page.get_by_text("北京市").click()
                print("✓ 已选择地域分类: 北京市")
            
            # 4. 点击下一步
            print("\n=== 4. 点击下一步 ===")
            if page.is_visible(SELECTORS["next_step_button"]):
                page.click(SELECTORS["next_step_button"])
                time.sleep(WAIT_TIMES["page_load"])
                print("✓ 已点击下一步，进入详细信息页面")
            
            # 5. 填写详细信息
            print("\n=== 5. 填写详细信息 ===")
            
            # 填写接口名称
            if page.is_visible(SELECTORS["api_name_input"]):
                page.fill(SELECTORS["api_name_input"], "测试接口名称")
                print("✓ 已填写接口名称: 测试接口名称")
            
            # 填写正式接口地址
            if page.is_visible(SELECTORS["access_address_input"]):
                page.fill(SELECTORS["access_address_input"], "http://192.168.0.183:8080/api/v1/test")
                print("✓ 已填写正式接口地址: http://192.168.0.183:8080/api/v1/test")
            
            # 填写测试接口地址
            if page.is_visible(SELECTORS["redirect_address_input"]):
                page.fill(SELECTORS["redirect_address_input"], "http://192.168.0.183:8081/test/v1/test")
                print("✓ 已填写测试接口地址: http://192.168.0.183:8081/test/v1/test")
            
            # 填写入参信息
            print("\n=== 6. 填写入参信息 ===")
            # 假设入参信息有多个字段
            # 第一个入参
            if page.is_visible("input[placeholder='字段名']"):
                page.fill("input[placeholder='字段名']", "user_id")
                print("✓ 已填写入参字段名: user_id")
            
            if page.is_visible("select[placeholder='字段类型']"):
                page.select_option("select[placeholder='字段类型']", "string")
                print("✓ 已选择入参字段类型: string")
            
            if page.is_visible("textarea[placeholder='字段描述']"):
                page.fill("textarea[placeholder='字段描述']", "用户ID")
                print("✓ 已填写入参字段描述: 用户ID")
            
            # 点击添加按钮添加更多入参
            if page.is_visible("button:has-text('+')"):
                page.click("button:has-text('+')")
                time.sleep(0.5)
                print("✓ 已添加新的入参字段")
            
            # 7. 点击下一步
            print("\n=== 7. 点击下一步 ===")
            if page.is_visible(SELECTORS["next_step_button"]):
                page.click(SELECTORS["next_step_button"])
                time.sleep(WAIT_TIMES["page_load"])
                print("✓ 已点击下一步，进入上架信息页面")
            
            # 8. 填写上架信息
            print("\n=== 8. 填写上架信息 ===")
            
            # 填写价格
            if page.is_visible("input[name='price']"):
                page.fill("input[name='price']", "199.00")
                print("✓ 已填写价格: 199.00")
            
            # 选择上架时间
            if page.is_visible("input[name='shelf_time']"):
                page.fill("input[name='shelf_time']", "2024-01-01")
                print("✓ 已选择上架时间: 2024-01-01")
            
            # 9. 点击确定
            print("\n=== 9. 点击确定 ===")
            if page.is_visible(SELECTORS["confirm_button"]):
                page.click(SELECTORS["confirm_button"])
                time.sleep(WAIT_TIMES["page_load"])
                print("✓ 已点击确定，完成数据产品发布")
            
            # 等待查看结果
            print("\n=== 流程完成 ===")
            time.sleep(5)
            
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            try:
                # 保存页面截图便于调试
                page.screenshot(path="debug_error_screenshot.png")
                print("已保存错误截图: debug_error_screenshot.png")
            except:
                print("无法保存页面截图")
            
        finally:
            # 关闭浏览器
            try:
                browser.close()
                print("浏览器已关闭")
            except:
                print("浏览器关闭失败")

if __name__ == "__main__":
    debug_data_product_flow()