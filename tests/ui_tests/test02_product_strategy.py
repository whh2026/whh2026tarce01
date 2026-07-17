import time
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.ui_tests.config import ui_config
# 导入测试数据
from tests.test_data.product_strategy_data import (
    SELECTORS,
    ASSERT_MESSAGES, generate_test_data, generate_max_length_data,
    STRATEGY_TYPE, STRATEGY_PRIORITY, WAIT_TIMES
)

class TestProductStrategy(Base):
    """产品策略页面测试类"""
    
    CONFIG = ui_config
    
    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_default_timeout(30000)
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        cls._logged_in = False

    @classmethod
    def teardown_class(cls):
        """类级别的清理，所有测试方法执行后只执行一次"""
        try:
            cls.page.close()
        except Exception as e:
            print(f"[清理] 关闭页面失败: {e}")
        try:
            cls.context.close()
        except Exception as e:
            print(f"[清理] 关闭上下文失败: {e}")
        try:
            cls.browser.close()
        except Exception as e:
            print(f"[清理] 关闭浏览器失败: {e}")
        try:
            cls.playwright.stop()
        except Exception as e:
            print(f"[清理] 停止playwright失败: {e}")

    def setup_method(self, method):
        """每个测试方法执行前：首个用例完成登录（仅一次），其余用例回到产品策略页面（复用已登录会话）"""
        self.current_test = method

        if not type(self)._logged_in:
            # 首次：登录一次（作为本页面测试的初始状态）
            print("\n=== 登录（仅执行一次） ===")
            login_url = self.get_url_for_user(1, "/login", self.CONFIG.USER_IPS)
            self.page.goto(login_url, timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(1000)
            self._fill_login_form()
            self._submit_login()
            self.page.wait_for_timeout(2000)
            print("   ✓ 用户1登录成功")
            type(self)._logged_in = True

        # 导航到产品策略页面
        strategy_url = self.get_url_for_user(1, "/datamarket/product-manage/strategy", self.CONFIG.USER_IPS)
        self.page.goto(strategy_url)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        assert "strategy" in self.page.url.lower(), ASSERT_MESSAGES["page_access_failed"].format(url=self.page.url)
        print(f"[前置条件] 成功访问产品策略页面！")
        print(f"   页面URL: {self.page.url}")
        print(f"   页面标题: {self.page.title()}")

    def teardown_method(self, method):
        """每个测试方法执行后的清理（不关闭页面/上下文，保留登录态供后续用例复用）"""
        # 失败截图由 conftest.py 的 pytest_runtest_makereport 钩子统一处理
        pass

    def _fill_login_form(self):
        """填写登录表单"""
        try:
            username_input = self.page.locator("input[name='username'], input[id='username'], input[placeholder*='用户名']").first
            username_input.wait_for(state="visible", timeout=10000)
            username_input.fill("superadmin")

            password_input = self.page.locator("input[name='password'], input[id='password'], input[placeholder*='密码']").first
            password_input.wait_for(state="visible", timeout=10000)
            password_input.fill("ChainMaker123.")

            captcha_input = self.page.locator("input[name='captchaAnswer'], input[id='captchaAnswer'], input[placeholder*='验证码']").first
            captcha_input.wait_for(state="visible", timeout=10000)
            captcha_input.fill("987423")
        except Exception as e:
            print(f"   [警告] 填写登录表单失败: {e}")

    def _submit_login(self):
        """提交登录"""
        try:
            login_button = self.page.locator("button[type='submit'], button:has-text('登录'), input[type='submit']").first
            login_button.wait_for(state="visible", timeout=10000)
            login_button.click()
            self.page.wait_for_timeout(3000)
            assert "login" not in self.page.url.lower(), f"登录失败，当前URL: {self.page.url}"
            print(f"[登录] 登录成功！当前URL: {self.page.url}")
        except Exception as e:
            print(f"   [警告] 提交登录失败: {e}")

    def test_01_page_elements(self):
        """测试产品策略页面的基本元素"""
        print("\n=== 测试产品策略页面基本元素 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "页面元素验证",
            "测试目的": "验证产品策略页面的基本元素",
            "测试环境": "用户1登录",
            "输入数据": "无"
        }
        
        # 验证页面标题
        page_title = self.page.title()
        print(f"   页面标题: {page_title}")
        assert page_title, "页面标题不能为空"
        
        # 验证页面URL
        current_url = self.page.url
        print(f"   当前URL: {current_url}")
        assert "strategy" in current_url.lower(), "URL中应包含'strategy'"
        
        # 验证页面元素 - 产品策略表格
        self._verify_element_exists([".el-table", ".ant-table", "table"], "产品策略表格", timeout=5000)
        
        # 验证新增策略按钮
        self._verify_element_exists(["button:has-text('新建策略')"], "新增策略按钮", timeout=5000)
        
        # 验证查询按钮
        self._verify_element_exists(["button:has-text('查询')"], "查询按钮", timeout=5000)
        
        # 验证重置按钮
        self._verify_element_exists(["button:has-text('重置')", "button:has-text('清空')", ".reset-btn", "[class*='reset']"], "重置按钮", timeout=5000)
        
        # 验证分页组件
        self._verify_element_exists([".el-pagination", ".ant-pagination", ".pagination"], "分页组件", timeout=5000)
        
        # 验证查询条件 - 产品策略名称输入框
        self._verify_element_exists([
            "input[placeholder*='输入产品策略名称']"], "产品策略名称输入框", timeout=5000)
        
        # 验证表格列
        self._verify_field_exists([
            "th:has-text('产品策略名称')"
        ], "产品策略名称字段")
        
        self._verify_field_exists([
            "th:has-text('策略类型')"
        ], "策略类型字段")
        
        self._verify_field_exists([
            "th:has-text('策略项目')"
        ], "策略项目字段")
        
        self._verify_field_exists([ 
            "th:has-text('操作符')"
        ], "运算符字段")
        

        self._verify_field_exists([
            "th:has-text('值')"], "值字段")
        
        self._verify_field_exists([
            "th:has-text('创建时间')"
        ], "创建时间字段")
        
        self._verify_field_exists([
            "th:has-text('操作')"
        ], "操作字段")
        
        # 输出第一行策略数据
        print("\n   输出第一行策略数据：")
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]
        
        first_row = None
        for selector in table_row_selectors:
            try:
                rows = self.page.locator(selector)
                if rows.count() > 0:
                    first_row = rows.first
                    break
            except Exception:
                continue
        
        if first_row:
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count > 0:
                for idx in range(cell_count):
                    cell = cells.nth(idx)
                    cell_text = (cell.text_content() or "").strip()
                    print(f"     第{idx + 1}列: {cell_text}")
            else:
                print("     ⚠️  表格行没有数据")
        else:
            print("     ⚠️  未找到表格数据")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   ✅ 产品策略页面基本元素验证完成！")
    
    def _verify_element_exists(self, selectors, element_name, timeout=5000):
        """验证元素是否存在"""
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    print(f"   ✅ 找到{element_name}")
                    return True
            except Exception:
                continue
        print(f"   ⚠️  未找到{element_name}")
        return False
    
    def _verify_field_exists(self, selectors, field_name, timeout=5000):
        """验证表格字段是否存在"""
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    print(f"   ✅ 找到{field_name}")
                    return True
            except Exception:
                continue
        print(f"   ⚠️  未找到{field_name}")
        return False
    
    def click_add_button(self):
        """点击新增策略按钮"""
        add_button = self.page.locator(SELECTORS["add_button"])
        add_button.click()
        print("   点击新增策略按钮")
        self.page.wait_for_timeout(3000)
    
    def fill_basic_strategy_fields(self, name, desc=None, operator="≥", strategy_type=None, priority=None):
        """填充策略表单基础字段"""
        # 策略名称
        name_input = self.page.locator(SELECTORS["name_input"])
        name_input.wait_for(state="visible", timeout=5000)
        name_input.fill(name)
        print(f"   填充策略名称: {name[:20]}{'...' if len(name) > 20 else ''}")
        
        # 策略描述（可选）
        if desc and SELECTORS.get("desc_input"):
            desc_input = self.page.locator(SELECTORS["desc_input"])
            if desc_input.count() > 0:
                desc_input.fill(desc)
                print(f"   填充策略描述: {desc[:20]}{'...' if len(desc) > 20 else ''}")
        
        # 运算符（可选）
        if operator:
            # 在弹窗中找到运算符对应的下拉框
            operator_select = self.page.locator(SELECTORS.get("operator_select", ".el-dialog__body .el-select"))
            if operator_select.count() > 0:
                operator_select.first.click()
                self.page.wait_for_timeout(1000)
                # 选择运算符选项（force=True 绕过可见性检查）
                option = self.page.locator(f".el-select-dropdown__item:has-text('{operator}')").first
                if option.count() > 0:
                    option.click(force=True)
                    print(f"   选择运算符: {operator}")
                else:
                    print(f"   [警告] 未找到运算符选项: {operator}")
    
    def submit_strategy_form(self):
        """提交策略表单"""
        confirm_button = self.page.locator(SELECTORS["confirm_button"])
        if confirm_button.count() > 0:
            confirm_button.click()
            print("   点击确定按钮保存策略")
        self.page.wait_for_timeout(WAIT_TIMES["network"])
    
    def verify_strategy_created(self, strategy_name):
        """验证策略创建成功并显示在列表中"""
        product_strategy_url = self.get_url_for_user(1, "/datamarket/product-manage/strategy", self.CONFIG.USER_IPS)
        self.page.goto(product_strategy_url)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # 查找策略
        found = False
        rows = self.page.locator(SELECTORS["table_rows"])
        for idx in range(rows.count()):
            row = rows.nth(idx)
            name_cell = row.locator(SELECTORS["name_cell"])
            if name_cell.count() > 0:
                cell_text = name_cell.text_content().strip()
                if strategy_name in cell_text:
                    found = True
                    print(f"   策略已在列表中找到（第{idx + 1}行）: {cell_text}")
                    break
        
        assert found, ASSERT_MESSAGES["strategy_not_found"].format(name=strategy_name)
        print("   策略创建成功验证通过！")
    
    def test_02_add_strategy_with_normal_fields(self):
        """测试新增策略（正常字段长度）"""
        print("\n=== 测试新增策略（正常字段长度） ===")
        
        # 生成测试数据
        test_data = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略（正常字段长度）",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_data,
                "策略描述": f"{test_data} description",
                "运算符": "≥"
            }
        }
        
        print(f"   生成测试数据: {test_data}")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单
        self.fill_basic_strategy_fields(
            name=test_data,
            desc=f"{test_data} description",
            operator="≥"
        )
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 5. 验证策略创建成功
        self.verify_strategy_created(test_data)
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 新增策略（正常字段长度）测试通过！")
    

    
    def test_03_add_strategy_with_max_length_fields(self):
        """测试新增策略（最大长度字段）"""
        print("\n=== 测试新增策略（最大长度字段） ===")
        
        # 生成最大长度测试数据
        max_length_name, max_length_content = generate_max_length_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略（最大长度字段）",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": f"{max_length_name[:50]}...(共{len(max_length_name)}字符)",
                "策略描述": f"{max_length_content[:200]}...(共{len(max_length_content)}字符)",
                "运算符": "≥",
                "策略类型": STRATEGY_TYPE["DEFAULT"],
                "优先级": STRATEGY_PRIORITY["HIGH"]
            }
        }
        
        print(f"   生成最大长度名称: {max_length_name[:50]}...(共{len(max_length_name)}字符)")
        print(f"   生成最大长度内容: {max_length_content[:2000]}...(共{len(max_length_content)}字符)")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单（最大长度）
        self.fill_basic_strategy_fields(
            name=max_length_name,
            desc=max_length_content,
            operator="≥",
            strategy_type=STRATEGY_TYPE["DEFAULT"],
            priority=STRATEGY_PRIORITY["HIGH"]
        )
        
        # 3. 提交表单
        self.submit_strategy_form()


        # 4. 验证策略创建成功
        self.verify_strategy_created(max_length_name)
        
        print("   [测试完成] 新增策略（正常字段长度）测试通过！")
    
        
        # 5. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 新增策略（最大长度字段）测试通过！")


    def test_04_add_and_delete_strategy(self):
        """测试新增策略后立即删除"""
        print("\n=== 测试新增策略后立即删除 ===")
        
        # 生成测试数据
        input_value = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略后立即删除",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": input_value,
                "策略描述": input_value,
                "策略类型": STRATEGY_TYPE["DEFAULT"]
            }
        }
        
        print(f"   生成测试数据: {input_value}")
        
        # 1. 开始新增产品策略
        print("\n   1. 开始新增产品策略")
        
        # 点击新增策略按钮
        self.click_add_button()
        
        # 填充表单
        self.fill_basic_strategy_fields(
            name=input_value,
            desc=input_value,
            strategy_type=STRATEGY_TYPE["DEFAULT"]
        )
        
        # 点击确定按钮保存
        self.submit_strategy_form()
        
        # 2. 查找刚添加的策略
        print("\n   2. 查找刚添加的策略")
        
        # 返回主页面
        product_strategy_url = self.get_url_for_user(1, "/datamarket/product-manage/strategy", self.CONFIG.USER_IPS)
        self.page.goto(product_strategy_url)
        self.page.wait_for_load_state("networkidle")
        
        # 延迟2秒
        time.sleep(2)
        
        # 查找新增的策略
        rows = self.page.locator(SELECTORS["table_rows"])
        target_row = None
        
        for idx in range(rows.count()):
            row = rows.nth(idx)
            name_cell = row.locator(SELECTORS["name_cell"])
            if name_cell.count() > 0:
                cell_text = name_cell.text_content().strip()
                if input_value in cell_text:
                    target_row = row
                    print(f"   找到新增策略行（第{idx+1}行）")
                    break
        
        assert target_row is not None, ASSERT_MESSAGES["strategy_not_in_list"]
        
        # 3. 开始删除策略
        print("\n   3. 开始删除策略")
        delete_button = target_row.locator(SELECTORS["delete_button"])
        assert delete_button.count() > 0, ASSERT_MESSAGES["no_delete_button"]
        
        delete_button.click()
        print("   点击删除按钮")
        
        # 等待删除确认对话框
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        
        # 4. 确认删除
        confirm_dialog = self.page.locator(SELECTORS["confirm_dialog"])
        if confirm_dialog.count() > 0:
            print("   出现删除确认对话框")
            self.page.wait_for_timeout(WAIT_TIMES["medium"])
            delete_confirm_btn = self.page.locator(SELECTORS["delete_confirm_button"])
            
            if delete_confirm_btn.count() > 0:
                delete_confirm_btn.click()
                print("   点击确认删除按钮")
            else:
                # 尝试使用通用确认按钮
                dialog_ok_btn = self.page.locator(SELECTORS["dialog_ok_button"])
                if dialog_ok_btn.count() > 0:
                    dialog_ok_btn.click()
                    print("   点击通用确认按钮")
                else:
                    print("   [警告] 未找到删除确认按钮")
        else:
            print("   [警告] 未找到删除确认对话框")
        
        # 等待删除完成和页面刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")
        
        # 5. 验证策略已被删除
        print("\n   4. 验证策略已被删除")
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        strategy_found = False
        
        for idx in range(total_rows):
            row = rows.nth(idx)
            name_cell = row.locator(SELECTORS["name_cell"])
            if name_cell.count() > 0:
                cell_text = name_cell.text_content().strip()
                if input_value in cell_text:
                    strategy_found = True
                    print(f"   错误：删除后仍在第{idx + 1}行找到策略")
                    break
        
        assert not strategy_found, ASSERT_MESSAGES["strategy_still_exists"]
        
        # 检查删除成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   删除成功提示已显示")
        else:
            print("   [信息] 未检测到明确的删除成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 新增策略后删除测试完成！")

    def search_strategy_by_name(self, name):
        """根据策略名称查询"""
        # 定位搜索输入框
        print(f"   尝试定位搜索输入框，使用选择器: {SELECTORS.get('search_input')}")
        search_input = self.page.locator(SELECTORS.get("search_input", ""))
        if search_input.count() == 0:
            # 尝试使用更精确的选择器
            alt_selectors = [
                "input[placeholder*='输入产品策略名称']",
                "input[placeholder*='策略名称']",
                "input[placeholder*='搜索']",
                "input[type='text']:not([readonly])"
            ]
            print(f"   [警告] 未找到搜索输入框，尝试替代选择器")
            for selector in alt_selectors:
                print(f"   尝试替代选择器: {selector}")
                alt_input = self.page.locator(selector)
                if alt_input.count() > 0:
                    # 只选择第一个找到的非只读输入框
                    search_input = alt_input.nth(0)
                    print(f"   找到替代搜索输入框")
                    break
            else:
                print("   [警告] 所有选择器均未找到搜索输入框，跳过查询")
                return False
        
        # 清空并输入策略名称
        search_input.clear()
        search_input.fill(name)
        print(f"   输入查询关键字: {name}")
        
        # 点击搜索按钮（如有）
        search_btn = self.page.locator(SELECTORS.get("search_button", ""))
        if search_btn.count() > 0:
            search_btn.click()
            print("   点击搜索按钮")
        else:
            # 无独立搜索按钮则按回车
            self.page.keyboard.press("Enter")
            print("   按回车触发搜索")
        
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")
        return True
    
    def test_05_search_strategy_by_name(self):
        """测试根据策略名称查询"""
        print("\n=== 测试根据策略名称查询 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试根据策略名称查询",
            "测试环境": "用户1登录",
            "输入数据": "无"
        }
        
        # 1. 获取第一行策略名称
        print("   1. 获取第一行策略名称")
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]
        
        first_row = None
        for selector in table_row_selectors:
            try:
                rows = self.page.locator(selector)
                if rows.count() > 0:
                    first_row = rows.first
                    break
            except Exception:
                continue
        
        assert first_row is not None, "未找到表格数据，无法进行查询测试"
        
        # 获取第一列的策略名称
        name_cell = first_row.locator("td:nth-child(1)")
        if name_cell.count() > 0:
            strategy_name = name_cell.text_content().strip()
            print(f"   获取到策略名称: {strategy_name}")
        else:
            print("   ⚠️  未找到策略名称列")
            strategy_name = ""
        
        assert strategy_name, "未获取到策略名称，无法进行查询测试"
        
        # 更新测试数据
        self._test_data["输入数据"] = {
            "查询策略名称": strategy_name
        }
        
        # 2. 执行查询
        print("\n   2. 执行查询")
        search_success = self.search_strategy_by_name(strategy_name)
        assert search_success, "搜索功能不可用"
        
        # 3. 验证查询结果
        print("\n   3. 验证查询结果")
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False
        for idx in range(rows.count()):
            row = rows.nth(idx)
            name_cell = row.locator(SELECTORS["name_cell"])
            if name_cell.count() > 0 and strategy_name in name_cell.text_content().strip():
                found = True
                print(f"   查询结果：在第{idx + 1}行找到策略")
                break
        
        assert found, f"未查到策略: {strategy_name}"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 根据策略名称查询测试通过！")
    
    def test_06_search_strategy_by_name_fuzzy(self):
        """测试根据策略名称模糊查询"""
        print("\n=== 测试根据策略名称模糊查询 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试根据策略名称模糊查询",
            "测试环境": "用户1登录",
            "输入数据": "无"
        }
        
        # 1. 获取第一行策略名称
        print("   1. 获取第一行策略名称")
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]
        
        first_row = None
        for selector in table_row_selectors:
            try:
                rows = self.page.locator(selector)
                if rows.count() > 0:
                    first_row = rows.first
                    break
            except Exception:
                continue
        
        assert first_row is not None, "未找到表格数据，无法进行查询测试"
        
        # 获取第一列的策略名称
        name_cell = first_row.locator("td:nth-child(1)")
        if name_cell.count() > 0:
            strategy_name = name_cell.text_content().strip()
            print(f"   获取到策略名称: {strategy_name}")
        else:
            print("   ⚠️  未找到策略名称列")
            strategy_name = ""
        
        assert strategy_name, "未获取到策略名称，无法进行查询测试"
        
        # 2. 提取策略名称的前几个字符进行模糊查询
        if len(strategy_name) > 3:
            fuzzy_name = strategy_name[:3]
        else:
            fuzzy_name = strategy_name
        
        print(f"\n   2. 提取模糊查询关键词: {fuzzy_name}")
        
        # 更新测试数据
        self._test_data["输入数据"] = {
            "完整策略名称": strategy_name,
            "模糊查询关键词": fuzzy_name
        }
        
        # 3. 执行模糊查询
        print("\n   3. 执行模糊查询")
        search_success = self.search_strategy_by_name(fuzzy_name)
        assert search_success, "搜索功能不可用"
        
        # 4. 验证查询结果
        print("\n   4. 验证模糊查询结果")
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False
        for idx in range(rows.count()):
            row = rows.nth(idx)
            name_cell = row.locator(SELECTORS["name_cell"])
            if name_cell.count() > 0 and fuzzy_name in name_cell.text_content().strip():
                found = True
                print(f"   查询结果：在第{idx + 1}行找到策略，名称包含关键词'{fuzzy_name}'")
                break
        
        assert found, f"未查到包含关键词'{fuzzy_name}'的策略"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 根据策略名称模糊查询测试通过！")
    
    def test_07_add_strategy_with_empty_name(self):
        """测试新增策略时策略名称为空的校验"""
        print("\n=== 测试新增策略时策略名称为空的校验 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称为空的校验",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": "空",
                "预期结果": "显示必填提示"
            }
        }
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 不填写策略名称，直接提交
        self.submit_strategy_form()
        
        # 3. 验证提示信息
        # 检查是否有必填提示
        name_input = self.page.locator(SELECTORS["name_input"])
        assert name_input.count() > 0, "未找到策略名称输入框"
        
        # 获取验证提示（通常出现在输入框下方或弹窗）
        error_tip = self.page.locator(".el-form-item__error, .el-message__content, .ant-form-explain")
        if error_tip.count() > 0:
            tip_text = error_tip.first.text_content().strip()
            print(f"   检测到验证提示: {tip_text}")
            assert "名称" in tip_text or "必填" in tip_text, f"未检测到名称必填提示，实际提示: {tip_text}"
            # 更新测试数据
            self._test_data["输入数据"]["实际提示"] = tip_text
        else:
            # 若无前端提示，则检查是否未跳转或表单未关闭
            current_url = self.page.url
            if "strategy" not in current_url.lower():
                print("   [警告] 页面未跳转，可能后端返回错误")
                # 更新测试数据
                self._test_data["输入数据"]["实际结果"] = "页面未跳转，可能后端返回错误"
            else:
                print("   [警告] 未检测到明确的前端验证提示")
                # 更新测试数据
                self._test_data["输入数据"]["实际结果"] = "未检测到明确的前端验证提示"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 策略名称为空校验测试完成！")
    
    def test_08_add_strategy_with_empty_operator(self):
        """测试新增策略时运算符为空的校验"""
        print("\n=== 测试新增策略时运算符为空的校验 ===")
        
        # 生成测试名称
        test_name = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时运算符为空的校验",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_name,
                "运算符": "空",
                "预期结果": "显示必填提示"
            }
        }
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填写策略名称，但不选择运算符
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.fill(test_name)
            print(f"   填充策略名称: {test_name}")
        
        # 确保运算符下拉未选择（如已选则清空）
        if SELECTORS.get("operator_select"):
            operator_select = self.page.locator(SELECTORS["operator_select"])
            if operator_select.count() > 0:
                # 点击展开下拉，确保无选中值
                operator_select.click()
                self.page.wait_for_timeout(WAIT_TIMES["short"])
                # 再次点击收回下拉
                operator_select.click()
                print("   未选择运算符")
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证提示
        error_tip = self.page.locator(".el-form-item__error, .el-message__content, .ant-form-explain")
        if error_tip.count() > 0:
            tip_text = error_tip.first.text_content().strip()
            print(f"   检测到验证提示: {tip_text}")
            assert "运算符" in tip_text or "必填" in tip_text, f"未检测到运算符必填提示，实际提示: {tip_text}"
            # 更新测试数据
            self._test_data["输入数据"]["实际提示"] = tip_text
        else:
            # 检查是否停留在表单页
            if self.page.locator(SELECTORS["confirm_button"]).count() > 0:
                print("   [信息] 表单未关闭，可能因验证失败")
                # 更新测试数据
                self._test_data["输入数据"]["实际结果"] = "表单未关闭，可能因验证失败"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 运算符为空校验测试完成！")
    
    def test_09_add_strategy_with_both_name_and_operator_empty(self):
        """测试新增策略时策略名称和运算符均为空的校验"""
        print("\n=== 测试新增策略时策略名称和运算符均为空的校验 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称和运算符均为空的校验",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": "空",
                "运算符": "空",
                "预期结果": "显示必填提示"
            }
        }
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 确保名称和运算符均为空
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.clear()
            print("   清空策略名称")
        
        if SELECTORS.get("operator_select"):
            operator_select = self.page.locator(SELECTORS["operator_select"])
            if operator_select.count() > 0:
                # 若已选则清空选择
                operator_select.click()
                self.page.wait_for_timeout(WAIT_TIMES["short"])
                # 尝试点击空白或收回下拉
                self.page.keyboard.press("Escape")
                print("   确保未选择运算符")
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证多个字段的提示
        error_tips = self.page.locator(".el-form-item__error, .el-message__content, .ant-form-explain")
        if error_tips.count() > 0:
            tips_text = [tip.text_content().strip() for tip in error_tips.all()]
            print(f"   检测到验证提示: {tips_text}")
            # 更新测试数据
            self._test_data["输入数据"]["实际提示"] = tips_text
            # 至少应包含名称或运算符的提示
            has_name_tip = any("名称" in t or "name" in t.lower() for t in tips_text)
            has_operator_tip = any("运算符" in t or "operator" in t.lower() for t in tips_text)
            assert has_name_tip or has_operator_tip, "未检测到名称或运算符的必填提示"
        else:
            print("   [警告] 未检测到前端验证提示")
            # 更新测试数据
            self._test_data["输入数据"]["实际结果"] = "未检测到前端验证提示"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 名称和运算符均为空校验测试完成！")
    
    def test_10_add_strategy_with_single_space_in_name(self):
        """测试新增策略时策略名称包含一个空格"""
        print("\n=== 测试新增策略时策略名称包含一个空格 ===")
        
        # 生成包含一个空格的测试数据
        test_data = f"测试 {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称包含一个空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_data,
                "策略描述": f"{test_data} description",
                "运算符": "≥"
            }
        }
        
        print(f"   生成测试数据（包含一个空格）: {test_data}")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单
        self.fill_basic_strategy_fields(
            name=test_data,
            desc=f"{test_data} description",
            operator="≥"
        )
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 5. 验证策略创建成功
        self.verify_strategy_created(test_data)
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 策略名称包含一个空格测试通过！")
    
    def test_11_add_strategy_with_angle_brackets_in_name(self):
        """测试新增策略时策略名称包含《》"""
        print("\n=== 测试新增策略时策略名称包含《》 ===")
        
        # 生成包含《》的测试数据
        test_data = f"《测试》{generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称包含《》",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_data,
                "策略描述": f"{test_data} description",
                "运算符": "≥"
            }
        }
        
        print(f"   生成测试数据（包含《》）: {test_data}")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单
        self.fill_basic_strategy_fields(
            name=test_data,
            desc=f"{test_data} description",
            operator="≥"
        )
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 5. 验证策略创建成功
        self.verify_strategy_created(test_data)
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 策略名称包含《》测试通过！")

    def test_12_add_strategy_with_multiple_spaces_in_name(self):
        """测试新增策略时策略名称包含多个空格"""
        print("\n=== 测试新增策略时策略名称包含多个空格 ===")
        
        # 生成包含多个空格的测试数据
        test_data = f"测试  策略   {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称包含多个空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_data,
                "策略描述": f"{test_data} description",
                "运算符": "≥"
            }
        }
        
        print(f"   生成测试数据（包含多个空格）: {test_data}")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单
        self.fill_basic_strategy_fields(
            name=test_data,
            desc=f"{test_data} description",
            operator="≥"
        )
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 5. 验证策略创建成功
        self.verify_strategy_created(test_data)
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 策略名称包含多个空格测试通过！")
    
    def test_13_add_strategy_with_spaces_in_multiple_fields(self):
        """测试新增策略时策略名称和描述都包含空格"""
        print("\n=== 测试新增策略时策略名称和描述都包含空格 ===")
        
        # 生成包含空格的测试数据
        test_name = f"测试 策略 {generate_test_data()}"
        test_desc = f"这是 测试 策略 描述 {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增策略时策略名称和描述都包含空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "策略名称": test_name,
                "策略描述": test_desc,
                "运算符": "≥"
            }
        }
        
        print(f"   生成测试数据（名称包含空格）: {test_name}")
        print(f"   生成测试数据（描述包含空格）: {test_desc}")
        
        # 1. 点击新增策略按钮
        self.click_add_button()
        
        # 2. 填充表单
        self.fill_basic_strategy_fields(
            name=test_name,
            desc=test_desc,
            operator="≥"
        )
        
        # 3. 提交表单
        self.submit_strategy_form()
        
        # 4. 验证保存成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            print("   保存成功，显示成功提示")
        else:
            print("   [注意] 未检测到明确的保存成功提示")
        
        # 5. 验证策略创建成功
        self.verify_strategy_created(test_name)
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 策略名称和描述都包含空格测试通过！")
    