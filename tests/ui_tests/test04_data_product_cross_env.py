import pytest
import random
import time
from playwright.sync_api import sync_playwright
from utils.base import Base

class TestDataProductCrossEnv(Base):
    """数据产品跨环境测试类"""
    
    CONFIG = {
        1: "192.168.0.183:30001",
        2: "192.168.0.185:30001"
    }
    
    @classmethod
    def setup_class(cls):
        """类级别的设置"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
    
    @classmethod
    def teardown_class(cls):
        """类级别的清理"""
        cls.browser.close()
        cls.playwright.stop()
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.context = self.browser.new_context(viewport={"width": 1900, "height": 950})
        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1900, "height": 950})
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        self.page.close()
        self.context.close()
    
    def debug_interface_page(self):
        """在接口调试页面进行操作"""
        print("\n   === 在接口调试页面进行操作 ===")
        time.sleep(2)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        
        # 下拉接口地址，选择第一个
        print("   正在下拉接口地址...")
        interface_address_selectors = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/form/div[1]/div/div/div",
            "div[role='combobox']",
            ".el-select",
            "[class*='select']"
        ]
        
        for address_selector in interface_address_selectors:
            address_element = self.page.locator(address_selector).first
            if address_element.count() > 0:
                print(f"   ✓ 找到接口地址下拉框: {address_selector}")
                address_element.click()
                time.sleep(1)
                print("   ✓ 已点击接口地址下拉框")
                
                first_option_selectors = [
                    "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/form/div[1]/div/div/div/div[1]",
                    ".el-select-dropdown__item:first-child",
                    "[class*='select-dropdown'] [class*='item']:first-child"
                ]
                
                for option_selector in first_option_selectors:
                    first_option = self.page.locator(option_selector).first
                    if first_option.count() > 0:
                        print(f"   ✓ 找到第一个选项: {option_selector}")
                        first_option.click()
                        time.sleep(1)
                        print("   ✓ 已选择第一个接口地址")
                        break
                break
        
        # 输入入参信息
        print("   正在输入入参信息...")
        param_input_selectors = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/form/div[5]/div/div/div/div[3]/div/input",
            "input[type='text']",
            "textarea",
            "[class*='input']"
        ]
        
        param_data = "20260426"
        
        for param_selector in param_input_selectors:
            param_input = self.page.locator(param_selector).first
            if param_input.count() > 0:
                print(f"   ✓ 找到入参输入框: {param_selector}")
                param_input.fill(param_data)
                time.sleep(1)
                print(f"   ✓ 已输入入参信息: {param_data}")
                
                # 点击发起请求按钮
                print("   正在点击发起请求按钮...")
                request_button_selectors = [
                    "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/form/div[7]/div/button",
                    "button:has-text('发起请求')",
                    "button:has-text('请求')"
                ]
                
                for request_selector in request_button_selectors:
                    request_button = self.page.locator(request_selector).first
                    if request_button.count() > 0:
                        print(f"   ✓ 找到发起请求按钮: {request_selector}")
                        request_button.click()
                        time.sleep(2)
                        print("   ✓ 已点击发起请求按钮")
                        print("   ✓ 接口调试操作完成")
                        return True
                break
    
    def test_01_cross_env_sync_and_api_test(self):
        """测试跨环境同步和API调用"""
        print("\n=== 开始执行 test_01_cross_env_sync_and_api_test ===")
        
        # 步骤 1: 用户1在183环境创建产品
        print("\n=== 1. 用户1在183环境创建产品 ===")
        self.login_with_user(user_id=1, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        product_data = self.create_data_product(need_apply=False, need_auth=False)
        print(f"   ✓ 产品创建成功: {product_data['name']}")
        
        # 步骤 2: 用户2在185环境登录并等待同步
        print("\n=== 2. 用户2在185环境登录并等待同步 ===")
        self.login_with_user(user_id=2, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        
        product_list_url = "http://192.168.0.185:30001/datamarket/product/product-list"
        self.page.goto(product_list_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(2)
        
        # 步骤 3: 多次尝试搜索，等待产品同步
        print("\n=== 3. 等待产品同步 ===")
        max_retries = 5
        retry_delay = 5
        product_found = False
        
        for retry in range(max_retries):
            print(f"   [第 {retry + 1}/{max_retries} 次尝试] 搜索产品...")
            
            # 使用指定XPath定位搜索框和查询按钮
            search_input_xpath = "/html/body/div[1]/div/div/section/div/main/div/div/div[1]/div/div/form/div[1]/div/div/div/input"
            search_button_xpath = "/html/body/div[1]/div/div/section/div/main/div/div/div[1]/div/div/form/div[3]/div/button"
            
            search_input = self.page.locator(f"xpath={search_input_xpath}").first
            if search_input.count() > 0:
                search_input.fill(product_data["name"])
                time.sleep(2)
                print(f"   ✓ 已在搜索框输入产品名称: {product_data['name']}")
                
                search_button = self.page.locator(f"xpath={search_button_xpath}").first
                if search_button.count() > 0:
                    search_button.click()
                    time.sleep(2)
                    print("   ✓ 已点击查询按钮")
            
            # 使用指定XPath验证产品名称
            name_verify_xpath = "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div/div/div/div[1]/div/div[1]/div[2]/div[1]/div[1]/div"
            name_element = self.page.locator(f"xpath={name_verify_xpath}").first
            
            if name_element.count() > 0:
                actual_name = name_element.text_content()
                if actual_name and product_data["name"] in actual_name:
                    print(f"   ✓ 产品名称验证通过: {actual_name}")
                    product_found = True
                    break
                else:
                    print(f"   ⚠️  产品名称不匹配: 期望包含'{product_data['name']}'，实际为'{actual_name}'")
            else:
                product_cell = self.page.locator(f"td:has-text('{product_data['name']}')").first
                if product_cell.count() > 0:
                    print(f"   ✓ 产品已同步，共重试 {retry + 1} 次")
                    product_found = True
                    break
            
            print(f"   [等待同步] 第 {retry + 1}/{max_retries} 次尝试...")
            time.sleep(retry_delay)
        
        if not product_found:
            print("   ⚠️  产品同步超时")
        
        print("\n=== test_01_cross_env_sync_and_api_test 执行完成 ===")
    
    def test_02_cross_env_no_apply_test(self):
        """跨环境测试：用户1创建不需要审批的产品，用户2申请并调用接口调试"""
        print("\n=== 开始执行 test_02_cross_env_no_apply_test ===")
        
        # 步骤 1: 用户1在183环境创建数据产品
        print("\n=== 1. 用户1在183环境创建数据产品 ===")
        self.login_with_user(user_id=1, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        product_data = self.create_data_product(need_apply=False, need_auth=False)
        print(f"   ✓ 产品创建成功: {product_data['name']}")
        
        # 步骤 2: 用户2在185环境登录
        print("\n=== 2. 用户2在185环境登录 ===")
        self.login_with_user(user_id=2, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        
 
        self.search_product_and_apply(user_id=2, product_name=product_data["name"])
        self.submit_application()
        time.sleep(2)
        self.search_in_received_list(product_data["name"])
        self.debug_interface()
        self.verify_product_status_in_received_list(product_data["name"], "待交付", 2, self.CONFIG)
        print("   ✓ 产品状态验证成功")
 

        
        print("\n=== test_02_cross_env_no_apply_test 执行完成 ===")
    
    def test_03_authorized_product_application_flow(self):
        """跨环境测试：用户1创建需要审批的授权产品，用户2审批并验证流程"""
        print("\n=== 开始执行 test_03_authorized_product_application_flow ===")
        
        # 步骤 1: 用户1在183环境创建需要审批的授权产品
        print("\n=== 1. 用户1在183环境创建需要审批的授权产品 ===")
        self.login_with_user(user_id=1, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        product_data = self.create_data_product(need_apply=True, need_auth=True)
        print(f"   ✓ 产品创建成功: {product_data['name']}")
        
        # 步骤 2: 用户2在185环境登录并搜索产品申请（精准授权）
        print("\n=== 2. 用户2在185环境登录并申请产品（精准授权） ===")
        self.login_with_user(user_id=2, user_ips=self.CONFIG, page=self.page)
        time.sleep(2)
        
        # 搜索产品并点击立即申请
        print("\n   --- 搜索产品并申请 ---")
        self.search_product_and_apply(user_id=2, product_name=product_data["name"])
        time.sleep(3)
        
        # 精准授权申请：输入业务场景
        print("\n   --- 输入业务场景 ---")
        business_scene_inputs = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[3]/div/div/div[1]/div/input",
            "input[placeholder*='业务场景']",
            "input[placeholder*='业务']",
            "input[name*='business']"
        ]
        
        for selector in business_scene_inputs:
            try:
                scene_input = self.page.locator(selector).first
                if scene_input.count() > 0:
                    scene_input.wait_for(state="visible", timeout=5000)
                    scene_input.fill("测试业务场景")
                    time.sleep(1)
                    print("   ✓ 已输入业务场景")
                    break
            except Exception as e:
                print(f"   ⚠️  输入业务场景失败: {str(e)[:30]}")
                continue
        
        # 精准授权申请：输入具体用途
        print("\n   --- 输入具体用途 ---")
        purpose_inputs = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[4]/div/div/div[1]/div/input",
            "input[placeholder*='具体用途']",
            "input[placeholder*='用途']",
            "input[name*='purpose']"
        ]
        
        for selector in purpose_inputs:
            try:
                purpose_input = self.page.locator(selector).first
                if purpose_input.count() > 0:
                    purpose_input.wait_for(state="visible", timeout=5000)
                    purpose_input.fill("测试具体用途")
                    time.sleep(1)
                    print("   ✓ 已输入具体用途")
                    break
            except Exception as e:
                print(f"   ⚠️  输入具体用途失败: {str(e)[:30]}")
                continue
        
        # 输入申请理由
        print("\n   --- 输入申请理由 ---")
        reason_textarea = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[5]/div/div/textarea").first
        if reason_textarea.count() > 0:
            reason_textarea.wait_for(state="visible", timeout=5000)
            reason_textarea.fill("测试精准授权申请")
            time.sleep(1)
            print("   ✓ 已输入申请理由")
        
        # 勾选我已阅读并同意
        print("\n   --- 勾选同意协议 ---")
        checkbox_found = False
        
        # 尝试多种方式定位并点击勾选框
        checkbox_selectors = [
            # 点击label标签（Element UI常见方式）
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[4]/div/div/label",
            # 点击可见的span（样式化的checkbox）
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[4]/div/div/label/span[2]",
            # 通过文本内容定位label
            "label:has-text('我已阅读')",
            "label:has-text('同意')",
            ".el-checkbox",
            "[class*='checkbox']"
        ]
        
        for selector in checkbox_selectors:
            try:
                checkbox_element = self.page.locator(selector).first
                if checkbox_element.count() > 0:
                    checkbox_element.wait_for(state="visible", timeout=5000)
                    checkbox_element.click()
                    time.sleep(1)
                    print(f"   ✓ 使用选择器 '{selector}' 勾选同意协议成功")
                    checkbox_found = True
                    break
            except Exception as e:
                print(f"   ⚠️  选择器 '{selector}' 点击失败: {str(e)[:30]}")
                continue
        
        # 如果以上方式都失败，尝试JavaScript强制点击隐藏的input
        if not checkbox_found:
            try:
                hidden_checkbox = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[6]/div/div[1]/label/span[1]/span").first
                if hidden_checkbox.count() > 0:
                    self.page.evaluate("(el) => el.click()", hidden_checkbox)
                    time.sleep(1)
                    print("   ✓ 使用JavaScript强制点击勾选框成功")
                    checkbox_found = True
            except Exception as e:
                print(f"   ⚠️  JavaScript点击失败: {str(e)[:30]}")
        
        if not checkbox_found:
            print("   ⚠️  未能勾选同意协议")
        
        # 点击确定按钮提交申请
        print("\n   --- 提交申请 ---")
        submit_button = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[7]/div/button[1]").first
        if submit_button.count() > 0:
            submit_button.wait_for(state="visible", timeout=5000)
            submit_button.click()
            time.sleep(3)
            print("   ✓ 已提交申请")
        
        # 步骤 3: 用户1重新登录并进入数据提供审批页面
        print("\n=== 3. 用户1重新登录并进入数据提供审批页面 ===")
        # 先清除cookies并重置页面状态
        self.page.context.clear_cookies()
        self.page.goto("about:blank")
        time.sleep(2)

        # 先导航到183环境的登录页面，确保页面状态正确
        login_url = "http://192.168.0.183:30001/login"
        self.page.goto(login_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)

        # 调试信息：检查页面状态
        print(f"   [调试] 登录页面URL: {self.page.url}")
        print(f"   [调试] 登录页面标题: {self.page.title()}")

        # 输入用户名、密码、验证码进行登录
        print("   [调试] 正在查找用户名输入框...")
        username_input = self.page.locator("input[name='username'], input[id='username'], input[placeholder*='用户名']").first
        username_input.wait_for(state="visible", timeout=30000)
        username_input.fill("admin")
        print("   ✓ 已输入用户名")

        print("   [调试] 正在查找密码输入框...")
        password_input = self.page.locator("input[name='password'], input[id='password'], input[placeholder*='密码']").first
        password_input.wait_for(state="visible", timeout=30000)
        password_input.fill("admin123")
        print("   ✓ 已输入密码")

        print("   [调试] 正在查找验证码输入框...")
        captcha_input = self.page.locator("input[name='captchaAnswer'], input[id='captchaAnswer'], input[placeholder*='验证码']").first
        captcha_input.wait_for(state="visible", timeout=30000)
        captcha_input.fill("987423")
        print("   ✓ 已输入验证码")

        print("   [调试] 正在查找登录按钮...")
        login_button = self.page.locator("button[type='submit'], button:has-text('登录'), input[type='submit']").first
        login_button.wait_for(state="visible", timeout=30000)
        login_button.click()
        time.sleep(3)
        print("   ✓ 已点击登录按钮")

        # 进入数据提供审批页面
        approval_url = "http://192.168.0.183:30001/datamarket/applyManage/application-approval"
        self.page.goto(approval_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        print(f"   ✓ 已进入数据提供审批页面: {approval_url}")
        
        # 步骤 4: 搜索产品
        print("\n=== 4. 搜索产品 ===")
        search_input_selectors = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div/div[1]/div/div[2]/form/div[2]/div/div/div/input",
            "input[placeholder*='产品名称']",
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div[1]/div/div[2]/form/div[1]/div/div/div/input",
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/div[2]/form/div[1]/div/div/div/input",
            "input[name*='productName']",
            "input[name*='dataProductName']",
            ".el-form-item:nth-child(1) .el-input__inner",
            ".el-form-item:has(label:has-text('数据产品名称')) .el-input__inner"
        ]
        
        search_input_found = False
        for selector in search_input_selectors:
            search_input = self.page.locator(selector).first
            if search_input.count() > 0:
                try:
                    search_input.wait_for(state="visible", timeout=5000)
                    search_input.fill(product_data["name"])
                    time.sleep(2)
                    print(f"   ✓ 使用选择器 '{selector}' 输入产品名称: {product_data['name']}")
                    search_input_found = True
                    break
                except Exception as e:
                    print(f"   ⚠️  选择器 '{selector}' 输入失败: {str(e)[:30]}")
                    continue
        
        if search_input_found:
            search_button = self.page.locator("button:has-text('查询')").first
            if search_button.count() > 0:
                search_button.click()
                time.sleep(2)
                print("   ✓ 已点击查询按钮")
        
        # 步骤 5: 校验产品名称并点击去审批按钮
        print("\n=== 5. 校验产品名称并点击去审批按钮 ===")
        product_name_xpaths = [
            "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr[1]/td[2]/div",
            "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr/td[2]/div"
        ]
        
        for xpath in product_name_xpaths:
            product_name_element = self.page.locator(f"xpath={xpath}").first
            if product_name_element.count() > 0:
                actual_name = product_name_element.text_content()
                if actual_name and product_data["name"] in actual_name:
                    print(f"   ✓ 产品名称校验成功: {actual_name}")
                    
                    approve_button = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr/td[7]/div/button/span").first
                    if approve_button.count() > 0:
                        approve_button.click()
                        time.sleep(2)
                        print("   ✓ 已点击去审批按钮")
                    break
        
        # 步骤 6: 在审批页面点击通过按钮
        print("\n=== 6. 在审批页面点击通过按钮 ===")
        pass_button = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/button[1]/span").first
        if pass_button.count() > 0:
            pass_button.click()
            time.sleep(2)
            print("   ✓ 已点击通过按钮")
        
        # 步骤 7: 处理审批通过提示框
        print("\n=== 7. 处理审批通过提示框 ===")
        
        # 选择第一个下拉框选项
        first_dropdown = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[1]/div/div[1]/div/div[1]/div[2]").first
        if first_dropdown.count() > 0:
            first_dropdown.click()
            time.sleep(1)
            first_option = self.page.locator(".el-select-dropdown__item:first-child").first
            if first_option.count() > 0:
                first_option.click()
                time.sleep(1)
                print("   ✓ 已选择第一个下拉框选项")
        
        # 授权书模板下拉框
        template_dropdown = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[2]/div/div[1]/div/div[1]/div[2]").first
        if template_dropdown.count() > 0:
            template_dropdown.click()
            time.sleep(1)
            template_option = self.page.locator(".el-select-dropdown__item:first-child").first
            if template_option.count() > 0:
                template_option.click()
                time.sleep(1)
                print("   ✓ 已选择授权书模板")
        
        # 数据边界配置输入
        boundary_input = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[3]/div/div[1]/div[1]/div/input").first
        if boundary_input.count() > 0:
            boundary_input.fill("test123456")
            time.sleep(1)
            print("   ✓ 已输入数据边界配置")
        
        # 点击确定按钮
        confirm_button = self.page.locator("button:has-text('确定')").first
        if confirm_button.count() > 0:
            confirm_button.click()
            time.sleep(2)
            print("   ✓ 已点击确定按钮")
        
        # 步骤 8: 回到审批页面查看详情
        print("\n=== 8. 回到审批页面查看详情 ===")
        self.page.goto(approval_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        # 搜索产品
        search_input_selectors = [
            "input[placeholder*='搜索']",
            "input[type='text']",
            "input[placeholder*='名称']"
        ]
        
        search_input_found = False
        for selector in search_input_selectors:
            search_input = self.page.locator(selector).first
            if search_input.count() > 0:
                try:
                    search_input.wait_for(state="visible", timeout=5000)
                    search_input.fill(product_data["name"])
                    time.sleep(2)
                    print(f"   ✓ 使用选择器 '{selector}' 输入产品名称: {product_data['name']}")
                    search_input_found = True
                    break
                except Exception as e:
                    print(f"   ⚠️  选择器 '{selector}' 输入失败: {str(e)[:30]}")
                    continue
        
        if search_input_found:
            search_button = self.page.locator("button:has-text('查询')").first
            if search_button.count() > 0:
                search_button.click()
                time.sleep(2)
                print("   ✓ 已点击查询按钮")
        
        # 步骤 7: 校验产品名称并点击去审批按钮
        print("\n=== 7. 校验产品名称并点击去审批按钮 ===")
        product_name_xpaths = [
            "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr[1]/td[2]/div",
            "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr/td[2]/div"
        ]
        
        for xpath in product_name_xpaths:
            product_name_element = self.page.locator(f"xpath={xpath}").first
            if product_name_element.count() > 0:
                actual_name = product_name_element.text_content()
                if actual_name and product_data["name"] in actual_name:
                    print(f"   ✓ 产品名称校验成功: {actual_name}")
                    
                    approve_button = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div/table/tbody/tr/td[7]/div/button/span").first
                    if approve_button.count() > 0:
                        approve_button.click()
                        time.sleep(2)
                        print("   ✓ 已点击去审批按钮")
                    break
        
        # 步骤 8: 在审批页面点击通过按钮
        print("\n=== 8. 在审批页面点击通过按钮 ===")
        pass_button = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/button[1]/span").first
        if pass_button.count() > 0:
            pass_button.click()
            time.sleep(2)
            print("   ✓ 已点击通过按钮")
        
        # 步骤 9: 处理审批通过提示框
        print("\n=== 9. 处理审批通过提示框 ===")
        
        # 选择第一个下拉框选项
        first_dropdown = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[1]/div/div[1]/div/div[1]/div[2]").first
        if first_dropdown.count() > 0:
            first_dropdown.click()
            time.sleep(1)
            first_option = self.page.locator(".el-select-dropdown__item:first-child").first
            if first_option.count() > 0:
                first_option.click()
                time.sleep(1)
                print("   ✓ 已选择第一个下拉框选项")
        
        # 授权书模板下拉框
        template_dropdown = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[2]/div/div[1]/div/div[1]/div[2]").first
        if template_dropdown.count() > 0:
            template_dropdown.click()
            time.sleep(1)
            template_option = self.page.locator(".el-select-dropdown__item:first-child").first
            if template_option.count() > 0:
                template_option.click()
                time.sleep(1)
                print("   ✓ 已选择授权书模板")
        
        # 数据边界配置输入
        boundary_input = self.page.locator("xpath=/html/body/div[1]/div/div/section/div/main/div/div[5]/div/div/div/form/div[3]/div/div[1]/div[1]/div/input").first
        if boundary_input.count() > 0:
            boundary_input.fill("test123456")
            time.sleep(1)
            print("   ✓ 已输入数据边界配置")
        
        # 点击确定按钮
        confirm_button = self.page.locator("button:has-text('确定')").first
        if confirm_button.count() > 0:
            confirm_button.click()
            time.sleep(2)
            print("   ✓ 已点击确定按钮")
        
        # 步骤 10: 回到审批页面查看详情
        print("\n=== 10. 回到审批页面查看详情 ===")
        self.page.goto(approval_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        # 搜索产品
        search_input_selectors = [
            "input[placeholder*='搜索']",
            "input[type='text']",
            "input[placeholder*='名称']"
        ]
        
        search_input_found = False
        for selector in search_input_selectors:
            search_input = self.page.locator(selector).first
            if search_input.count() > 0:
                try:
                    search_input.wait_for(state="visible", timeout=5000)
                    search_input.fill(product_data["name"])
                    print(f"   ✓ 使用选择器 '{selector}' 输入产品名称")
                    search_input_found = True
                    break
                except Exception as e:
                    print(f"   ⚠️  选择器 '{selector}' 输入失败: {str(e)[:30]}")
                    continue
        
        if search_input_found:
            time.sleep(2)
            
            # 点击查询按钮
            search_button_selectors = [
                "button:has-text('查询')",
                "button.el-button.el-button--primary:has-text('查询')",
                ".search-btn"
            ]
            
            for selector in search_button_selectors:
                search_button = self.page.locator(selector).first
                if search_button.count() > 0:
                    try:
                        search_button.wait_for(state="visible", timeout=5000)
                        search_button.click()
                        print(f"   ✓ 使用选择器 '{selector}' 点击查询按钮")
                        break
                    except Exception as e:
                        print(f"   ⚠️  选择器 '{selector}' 点击失败: {str(e)[:30]}")
                        continue
        
        time.sleep(3)
        
        # 查找详情按钮
        detail_button_selectors = [
            "button:has-text('详情')",
            "button.el-button.el-button--primary.is-link",
            "button[class*='is-link']"
        ]
        
        detail_button_found = False
        for selector in detail_button_selectors:
            detail_button = self.page.locator(selector).first
            if detail_button.count() > 0:
                try:
                    # 等待按钮可见
                    detail_button.wait_for(state="visible", timeout=10000)
                    # 尝试滚动到按钮位置
                    self.page.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", detail_button)
                    time.sleep(1)
                    detail_button.click()
                    print(f"   ✓ 使用选择器 '{selector}' 点击详情按钮成功")
                    detail_button_found = True
                    break
                except Exception as e:
                    print(f"   ⚠️  选择器 '{selector}' 点击失败: {str(e)[:30]}")
                    continue
        
        if not detail_button_found:
            # 尝试使用JavaScript强制点击
            try:
                detail_button = self.page.locator("button:has-text('详情')").first
                if detail_button.count() > 0:
                    self.page.evaluate("(el) => el.click()", detail_button)
                    print("   ✓ 使用JavaScript强制点击详情按钮成功")
                    detail_button_found = True
            except Exception as e:
                print(f"   ⚠️  JavaScript点击失败: {str(e)[:30]}")
        
        if detail_button_found:
            time.sleep(2)
            print("   ✓ 已点击查看详情按钮")
        
        # 步骤 11: 去下单流程
        print("\n=== 11. 去下单流程 ===")
        
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
        
        print("\n=== test_03_authorized_product_application_flow 执行完成 ===")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])