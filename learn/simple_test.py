#!/usr/bin/env python3
"""
简化版数据产品测试脚本
专注于关键步骤：基础配置→详细信息→上架信息
"""

import time
import re
from playwright.sync_api import sync_playwright, expect
import random, string

def test_data_product_flow():
    """测试数据产品完整流程"""
    with sync_playwright() as playwright:
        # 启动浏览器（非无头模式，便于查看）
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 登录系统
                print("=== 1. 登录系统 ===")
                page.goto("http://192.168.0.183:30001/login")
                time.sleep(3)  # 等待页面加载
                print(f"已访问登录页面: {page.url}")
                
                # 输入用户名和密码
                print("输入用户名和密码...")
                # 使用更通用的选择器
                if page.is_visible("input[type='text']"):
                    page.fill("input[type='text']", "admin")
                    print("✓ 已输入用户名: admin")
                
                if page.is_visible("input[type='password']"):
                    page.fill("input[type='password']", "ChainMaker123.")
                    print("✓ 已输入密码: ChainMaker123.")
                
                # 输入验证码
                if page.is_visible("input[type='text'][placeholder*='验证码']"):
                    page.fill("input[type='text'][placeholder*='验证码']", "987423")
                    print("✓ 已输入验证码: 987423")
                
                # 点击登录按钮
                # 尝试多种选择器
                login_clicked = False
                if page.is_visible("button:has-text('登录')"):
                    page.click("button:has-text('登录')")
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击登录按钮")
                    login_clicked = True
                elif page.is_visible("button[type='button']"):
                    page.click("button[type='button']")
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击登录按钮")
                    login_clicked = True
                elif page.is_visible("#loginBtn"):
                    page.click("#loginBtn")
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击登录按钮")
                    login_clicked = True
                else:
                    print("✗ 未找到登录按钮")
                
                # 2. 访问数据产品发布页面
                print("\n=== 2. 访问数据产品发布页面 ===")

                if page.is_visible("li.route-item:has-text('产品管理')"):
                    page.click("li.route-item:has-text('产品管理')")
                    time.sleep(3)  # 等待页面加载
                    print("进入产品管理页面")

                if page.is_visible("//span[text()='数据产品发布']"):
                    page.click("//span[text()='数据产品发布']")
                    time.sleep(3)  # 等待页面加载
                    print("进入产品发布页面")

                if page.is_visible("//span[text()='数据产品登记']"):
                    page.click("//span[text()='数据产品登记']")
                    time.sleep(3)  # 等待页面加载
                    print("进入产品登记页面")
                
                # 3. 填写基础配置
                print("\n=== 3. 填写基础配置 ===")
                
                
                # 生成8位随机字符串
                rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # 填写中文名称
                print("填写中文名称...")
                cn_name = f"测aa试数据产品_{rand_str}"
                if page.is_visible("label:has-text('数据产品名称') ~ div .el-input__inner"):
                    page.fill("label:has-text('数据产品名称') ~ div .el-input__inner", cn_name)
                    print(f"✓ 已填写中文名称: {cn_name}")
                
                # 填写英文名称
                print("填写英文名称...")
                en_name = f"TestDataProduc111t_{rand_str}"
                if page.is_visible("label:has-text('数据产品英文名称') ~ div .el-input__inner"):
                    page.fill("label:has-text('数据产品英文名称') ~ div .el-input__inner", en_name)
                    print(f"✓ 已填写英文名称: {en_name}")

                # 填写数据产品标签
                print("填写数据产品标签签...")
                if page.is_visible("label:has-text('数据产品标签') + div >> input"):
                    page.fill("label:has-text('数据产品标签') + div >> input", "TestDataProduct_2024111")
                    print("✓ 已填写数据产品标签: TestDataProduct_2024111")

                # 填写产品介绍
                print("填写产品介绍...")
                if page.is_visible("textarea[placeholder*='说明数据产品的基本信息']"):
                    page.fill("textarea[placeholder*='说明数据产品的基本信息']", "这是一个用于自动化测试的数据产品")
                    print("✓ 已填写产品介绍")


                # 填写产品介绍
                print("填写使用限制...")
                if page.is_visible("textarea[placeholder*='说明数据产品在使用过程中的任何限制或条件']"):
                    page.fill("textarea[placeholder*='说明数据产品在使用过程中的任何限制或条件']", "这是一个用于自动化测试的数据产品")
                    print("✓ 已填写产品介绍")


                # 选择行业分类
                print("选择行业分类...")
                if page.is_visible("label:has-text('行业分类') + div"):
                    page.click("label:has-text('行业分类') + div")
                    time.sleep(1)
                    page.get_by_text("采矿业").click()
                    time.sleep(1)
                    print("✓ 已选择行业分类: 采矿业")
                
                # # 选择产品类型
                # print("选择产品类型...")
                # if page.is_visible("label:has-text('产品类型') + div"):
                #     page.click("label:has-text('产品类型') + div")
                #     time.sleep(1)
                #     page.get_by_text("数据接口").click()
                #     time.sleep(1)
                #     print("✓ 已选择产品类型: 数据接口")
                
                # 选择产品小类
                print("选择产品小类...")
                if page.is_visible("label:has-text('产品小类') + div"):
                    page.click("label:has-text('产品小类') + div")
                    time.sleep(1)
                    # 使用更具体的选择器
                    page.get_by_role("option", name="API接口").click()
                    time.sleep(1)
                    print("✓ 已选择产品小类: API接口")

                # 选择地域分类
                print("选择地域分类...")
                if page.is_visible("label:has-text('地域分类') + div"):
                    page.click("label:has-text('地域分类') + div")
                    time.sleep(0.5)
                    page.locator("div").filter(has_text=re.compile(r"^北京市$")).locator("span").nth(1).click()
                    print("✓ 已选择地域分类: 北京市")


                # 4. 点击下一步
                print("\n=== 4. 点击下一步 ===")
                if page.is_visible("button:has-text('下一步')"):
                    page.click("button:has-text('下一步')")
                    
                    # 页面跳转/刷新处理 - 使用更可靠的等待方式
                    try:
                        # 等待页面加载完成（网络请求完成）
                        page.wait_for_load_state("networkidle", timeout=30000)
                        
                        # 等待旧页面元素消失
                        page.wait_for_selector("button:has-text('下一步')", state="hidden", timeout=15000)
                        
                        # 等待新页面的关键元素出现（这里假设新页面有"接口名称"标签）
                        new_page_indicator = "label:has-text('接口名称')"
                        page.wait_for_selector(new_page_indicator, state="visible", timeout=20000)
                        
                        print("✓ 已点击下一步，页面已刷新并加载完成，进入详细信息页面")
                        print(f"✓ 新页面关键元素 '{new_page_indicator}' 已可见")
                        
                    except Exception as e:
                        print(f"✗ 页面跳转或加载失败: {str(e)}")
                        # 尝试获取当前页面的URL和标题，以便调试
                        print(f"   当前页面URL: {page.url}")
                        print(f"   当前页面标题: {page.title()}")
                        # 可以选择截图保存以便进一步分析
                        # page.screenshot(path="page_load_failure.png")
                
                # 5. 填写详细信息
                print("\n=== 5. 填写详细信息 ===")
                
                # 填写接口名称
                print("填写接口名称...")
                
                # 由于页面已刷新，使用更可靠的选择器列表
                api_name_selectors = [
                    "label:has-text('接口名称') + * input",
                    "//label[contains(text(), '接口名称')]/following-sibling::*//input",
                    "//label[contains(text(), '接口名称')]/parent::*//input",
                    "//*[text()='接口名称']/following::input[1]",
                    "//input[contains(@placeholder, '接口名称')]",
                    "//input[@name='apiName' or @id='apiName' or @data-field='apiName']"
                ]
                
                api_name_filled = False
                for selector in api_name_selectors:
                    try:
                        # 由于前面已经等待了"接口名称"标签出现，这里可以直接检查输入框
                        if page.is_visible(selector, timeout=3000):
                            page.wait_for_selector(selector, state="visible", timeout=5000)
                            page.fill(selector, "测试接口")
                            print(f"✓ 已填写接口名称: 测试接口")
                            print(f"  使用选择器: {selector}")
                            api_name_filled = True
                            break
                    except Exception as e:
                        print(f"  尝试选择器 {selector} 失败: {str(e)}")
                        continue
                
                if not api_name_filled:
                    print("✗ 未找到接口名称输入框")
                    # 打印页面信息以便调试
                    print(f"  当前页面URL: {page.url}")
                    print(f"  当前页面标题: {page.title()}")
                
                # 填写正式接口地址
                print("填写正式接口地址...")
                formal_api_selectors = [
                    "label:has-text('正式接口地址') + * input",
                    "//label[contains(text(), '正式接口地址')]/following-sibling::*//input",
                    "//label[contains(text(), '正式接口地址')]/parent::*//input",
                    "//input[contains(@placeholder, '正式接口地址')]"
                ]
                
                formal_api_filled = False
                for selector in formal_api_selectors:
                    try:
                        if page.is_visible(selector, timeout=3000):
                            page.wait_for_selector(selector, state="visible", timeout=5000)
                            page.fill(selector, "http://192.168.0.183:8081/api/v1/test")
                            print(f"✓ 已填写正式接口地址: http://192.168.0.183:8081/api/v1/test")
                            print(f"  使用选择器: {selector}")
                            formal_api_filled = True
                            break
                    except Exception as e:
                        print(f"  尝试选择器 {selector} 失败: {str(e)}")
                        continue
                
                if not formal_api_filled:
                    print("✗ 未找到正式接口地址输入框")
                
                # 填写测试接口地址
                print("填写测试接口地址...")
                test_api_selectors = [
                    "label:has-text('测试接口地址') + * input",
                    "//label[contains(text(), '测试接口地址')]/following-sibling::*//input",
                    "//label[contains(text(), '测试接口地址')]/parent::*//input",
                    "//input[contains(@placeholder, '测试接口地址')]"
                ]
                
                test_api_filled = False
                for selector in test_api_selectors:
                    try:
                        if page.is_visible(selector, timeout=3000):
                            page.wait_for_selector(selector, state="visible", timeout=5000)
                            page.fill(selector, "http://192.168.0.183:8082/api/v1/test")
                            print(f"✓ 已填写测试接口地址: http://192.168.0.183:8082/api/v1/test")
                            print(f"  使用选择器: {selector}")
                            test_api_filled = True
                            break
                    except Exception as e:
                        print(f"  尝试选择器 {selector} 失败: {str(e)}")
                        continue
                
                if not test_api_filled:
                    print("✗ 未找到测试接口地址输入框")
                  
                # 6. 填写入参信息
                print("\n=== 6. 填写入参信息 ===")
                # 等待入参区域加载完成
                time.sleep(2)
                
     
                
                # 第一个入参
                # 尝试使用更通用的选择器
                if page.is_visible("input[type='text']"):
                    # 获取所有文本输入框
                    inputs = page.query_selector_all("input[type='text']")
                    if inputs:
                        # 找到第一个可用的输入框
                        for input_el in inputs:
                            if input_el.is_enabled():
                                input_el.fill("user_id")
                                print("✓ 已填写入参字段名: user_id")
                                break
                
                
                # 7. 点击下一步
                print("\n=== 7. 点击下一步 ===")
                if page.is_visible("button:has-text('下一步')"):
                    page.click("button:has-text('下一步')")
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击下一步，进入上架信息页面")
                
                # 8. 填写上架信息
                print("\n=== 8. 填写上架信息 ===")
                # 等待页面加载完成
                time.sleep(5)
                
                # 是否需要申请使用 - 选择是
                print("选择是否需要申请使用: 是...")
                
                # 使用更精确的选择器：先找到问题容器，再找选项
                apply_selectors = [
                    "label:has-text('是否需要申请使用') + * span:has-text('是')",
                    "label:has-text('是否需要申请使用') ~ div span:has-text('是')",
                    "label:has-text('是否需要申请使用')/parent::*//span:has-text('是')",
                    "//label[contains(text(), '是否需要申请使用')]/following-sibling::*//span[contains(text(), '是')]",
                    "//label[contains(text(), '是否需要申请使用')]/parent::*/descendant::span[contains(text(), '是')]",
                    "//label[contains(text(), '是否需要申请使用')]/following-sibling::*//span[@class='el-radio__inner']"
                ]
                
                selected = False
                for selector in apply_selectors:
                    try:
                        if page.is_visible(selector):
                            page.wait_for_selector(selector, state="visible", timeout=3000)
                            page.click(selector)
                            print("✓ 已选择是否需要申请使用: 是")
                            selected = True
                            break
                    except Exception as e:
                        print(f"尝试选择器 {selector} 失败: {str(e)}")
                        continue
                
                if not selected:
                    print("✗ 未找到是否需要申请使用的'是'选项")
                
                # 服务协议下拉框选择第一个
                print("选择服务协议: 第一个选项...")
                service_agreement_selected = False
                # 查找包含'服务协议'的标签
                if page.is_visible("label:has-text('服务协议')"):
                    # 找到服务协议标签的父元素
                    label = page.query_selector("label:has-text('服务协议')")
                    if label:
                        # 找到相邻的下拉框容器
                        next_element = label.query_selector("+ *")
                        if next_element:
                            # 查找包含SVG图标的Element UI下拉框
                            el_select = next_element.query_selector(".el-select")
                            if el_select:
                                el_select.click()
                                time.sleep(1)
                                # 等待下拉选项出现
                                if page.wait_for_selector(".el-select-dropdown__item", state="visible", timeout=5000):
                                    # 选择第一个选项
                                    options = page.query_selector_all(".el-select-dropdown__item")
                                    if options:
                                        options[0].click()
                                        print("✓ 已选择服务协议: 第一个选项")
                                        service_agreement_selected = True

                
                # 产品授权范围 - 选择允许第三方授权使用
                print("选择产品授权范围: 允许第三方授权使用...")
                # 使用用户提供的.el-checkbox__inner选择器
                if page.is_visible("label:has-text('允许第三方授权使用')"):
                    # 找到包含'允许第三方授权使用'的标签
                    label = page.query_selector("label:has-text('允许第三方授权使用')")
                    if label:
                        # 获取包含该标签的复选框组
                        checkbox_group = label.query_selector("..")
                        if checkbox_group:
                            # 找到复选框内部元素
                            checkbox_inner = checkbox_group.query_selector(".el-checkbox__inner")
                            if checkbox_inner:
                                checkbox_inner.click()
                                print("✓ 已选择产品授权范围: 允许第三方授权使用")
                elif page.is_visible(".el-checkbox__inner"):
                    # 尝试第一个复选框
                    checkboxes = page.query_selector_all(".el-checkbox__inner")
                    if checkboxes:
                        checkboxes[0].click()
                        print("✓ 已选择产品授权范围: 第一个选项")
                
                # 产品交付策略 - 点击选择第一个
                print("选择产品交付策略: 第一个选项...")
                delivery_strategy_selected = False
                
                # 使用用户提供的具体选择按钮选择器
                select_button = page.query_selector("button[data-v-6ae8c76f]")
                if select_button and page.is_visible("button[data-v-6ae8c76f]"):
                    select_button.click()
                    time.sleep(2)
                    print("✓ 已点击产品交付策略选择按钮")
                    
                    # 等待表格加载完成
                    if page.wait_for_selector(".el-table", state="visible", timeout=5000):
                        # 查找表格中的第一个复选框（用户提供的.el-checkbox__inner）
                        first_checkbox = page.query_selector(".el-table__row:first-child .el-checkbox__inner")
                        if first_checkbox:
                            # 使用force=True强制点击
                            first_checkbox.click(force=True)
                            print("✓ 已选择产品交付策略的第一个选项")
                            
                            # 等待选择状态变化
                            time.sleep(1)
                            
                            # 使用用户提供的确定按钮选择器
                            confirm_button = page.query_selector("button[data-v-fa68e069]")
                            if confirm_button and page.is_visible("button[data-v-fa68e069]"):
                                confirm_button.click()
                                print("✓ 已确认产品交付策略选择")
                                delivery_strategy_selected = True
                            else:
                                # 备选：查找包含'确定'的按钮
                                confirm_button = page.query_selector("button:has-text('确定')")
                                if confirm_button:
                                    confirm_button.click()
                                    print("✓ 已确认产品交付策略选择")
                                    delivery_strategy_selected = True
                
                if not delivery_strategy_selected:
                    print("⚠ 跳过产品交付策略选择，继续流程")
 
                # 9. 点击确定
                print("\n=== 9. 点击确定 ===")
                if page.is_visible("button:has-text('确定')"):
                    page.click("button:has-text('确定')")
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击确定，完成数据产品发布")
                
                # 10. 点击数据产品名称查询
                print("\n=== 输入数据产品名称查询 ===")
                if page.is_visible("input[placeholder='输入数据产品名称']"):
                    page.fill("input[placeholder='输入数据产品名称']", cn_name)
                    time.sleep(3)  # 等待页面加载
                    print("✓ 已点击确定，完成数据产品发布")
                
                # 11. 点击查询
                print("\n=== 9. 点击查询 ===")
                if page.is_visible("//span[text()='查询']"):
                    page.click("//span[text()='查询']")
                    time.sleep(3)  # 等待页面加载
                    print("点击查询")

                # 12. 点击发布
                print("\n=== 9. 点击发布 ===")
                if page.is_visible("span.el-button__text:has-text('发布')"):
                    page.click("span.el-button__text:has-text('发布')")
                    time.sleep(3)  # 等待页面加载
                    print("✓点击发布已点击确定，完成数据产品发布")




                
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            try:
                # 保存页面截图便于调试
                page.screenshot(path="test_error_screenshot.png")
                print("已保存错误截图: test_error_screenshot.png")
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
    test_data_product_flow()