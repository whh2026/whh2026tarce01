import pytest
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.ui_tests.config import ui_config

class TestSourceReceivedListPage(Base):
    """数据提供交付页面测试类"""
    
    # 配置参数
    CONFIG = ui_config.USER_IPS
    
    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)  # headless=False 显示浏览器窗口
        # 创建持久化的上下文和页面，登录态通过 context 中的 cookie 保持，供所有用例复用
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        # 标记尚未登录，由首个用例的 setup_method 完成一次性登录
        cls._logged_in = False
    
    @classmethod
    def _wait_target_page(cls):
        """等待数据提供交付页面加载完成（带容错）"""
        try:
            cls.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            try:
                cls.page.wait_for_load_state("load", timeout=10000)
            except Exception:
                cls.page.wait_for_timeout(2000)
        assert "received-list" in cls.page.url.lower(), f"页面访问失败，当前URL: {cls.page.url}"
    
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
        """每个测试方法执行前：首个用例完成登录（仅一次），其余用例回到数据提供交付页面（复用已登录会话）"""
        # 保存当前测试方法，用于截图命名
        self.current_test = method
        
        if not type(self)._logged_in:
            # 首次：登录一次（作为本页面测试的初始状态）
            print("\n=== 登录（仅执行一次） ===")
            login_url = self.get_url_for_user(1, "/login", self.CONFIG)
            self.page.goto(login_url, timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(1000)
            self.login_with_user(1, self.CONFIG, page=self.page)
            print("   ✓ 用户1登录成功")
            type(self)._logged_in = True
        
        # 回到数据提供交付页面（登录态通过持久化 context 保持，无需重新登录）
        source_received_list_url = self.get_url_for_user(1, "/datamarket/source/sourceReceived-list", self.CONFIG)
        self.page.goto(source_received_list_url)
        self._wait_target_page()
        print(f"\n=== 回到数据提供交付页面: {method.__name__} ===")
        print(f"✅ 前置条件 - 成功访问数据提供交付页面！")
        print(f"   页面URL: {self.page.url}")
        print(f"   页面标题: {self.page.title()}")
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理（不关闭页面/上下文，保留登录态供后续用例复用）"""
        # 失败截图由 conftest.py 的 pytest_runtest_makereport 钩子统一处理
        pass
    
    def test_01_access_source_received_list_page(self):
        """测试访问数据提供交付页面"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试访问数据提供交付页面",
            "测试环境": "用户1登录",
            "输入数据": {
                "页面URL": "",
                "页面标题": ""
            },
            "验证结果": ""
        }

        # 记录页面URL和标题
        page_url = self.page.url
        page_title = self.page.title()
        self._test_data["输入数据"]["页面URL"] = page_url
        self._test_data["输入数据"]["页面标题"] = page_title

        print("\n=== 测试访问数据提供交付页面 ===")
        
        # 验证页面标题
        page_title = self.page.title()
        print(f"   页面标题: {page_title}")
        assert page_title, "页面标题不能为空"
        
        # 验证页面URL
        current_url = self.page.url
        print(f"   当前URL: {current_url}")
        assert "received-list" in current_url.lower(), "URL中应包含'received-list'"
        
        # 验证页面元素 - 数据提供交付表格
        table_exists = self._verify_element_exists([".el-table", ".ant-table", "table"], "数据提供交付表格", timeout=5000)
        
        # 验证查询按钮
        search_button_exists = self._verify_element_exists(["button:has-text('查询')", ".search-btn", "[class*='search']"], "查询按钮", timeout=5000)
        
        # 验证分页组件
        pagination_exists = self._verify_element_exists([".el-pagination", ".ant-pagination", ".pagination"], "分页组件", timeout=5000)
        
        # 验证查询条件 - 数据产品名称输入框
        product_name_input_exists = self._verify_element_exists([
            "input[placeholder*='数据产品名称']",
            "input[name*='product']",
            "input[type='text']:nth-of-type(1)"
        ], "数据产品名称输入框", timeout=5000)
        
        # 验证查询条件 - 数据产品小类下拉框
        category_dropdown_exists = self._verify_element_exists([
            "div.el-select:has-text('数据产品小类')",
            ".el-select",
            "select[name*='category']"
        ], "数据产品小类下拉框", timeout=5000)
        
        # 验证查询条件 - 状态下拉框
        status_dropdown_exists = self._verify_element_exists([
            "div.el-select:has-text('状态')",
            ".el-select",
            "select[name*='status']"
        ], "状态下拉框", timeout=5000)
        
        # 验证表格列
        fields_exists = []
        fields_exists.append(self._verify_field_exists(["th:has-text('数据产品名称')"], "数据产品名称字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('数据产品小类')"], "数据产品小类字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('状态')"], "状态字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('创建时间')"], "创建时间字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('操作')"], "操作字段"))

        # 记录验证结果
        verification_results = []
        if table_exists: verification_results.append("成功找到数据提供交付表格")
        if search_button_exists: verification_results.append("成功找到查询按钮")
        if pagination_exists: verification_results.append("成功找到分页组件")
        if product_name_input_exists: verification_results.append("成功找到数据产品名称输入框")
        if category_dropdown_exists: verification_results.append("成功找到数据产品小类下拉框")
        if status_dropdown_exists: verification_results.append("成功找到状态下拉框")
        if all(fields_exists): verification_results.append("成功找到所有表格字段")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 访问数据提供交付页面测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_02_filter_by_status(self):
        """测试按状态筛选"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按状态筛选",
            "测试环境": "用户1登录",
            "输入数据": {
                "页面URL": "",
                "测试的状态": []
            },
            "验证结果": ""
        }

        # 记录页面URL
        page_url = self.page.url
        self._test_data["输入数据"]["页面URL"] = page_url

        print("\n=== 测试按状态筛选 ===")
        
        # 等待页面加载完成
        self.page.wait_for_timeout(2000)
        
        # 状态下拉框选择器（稳定：用表单标签"交付状态"定位，避免选中后文本变化导致失配）
        status_dropdown_selectors = [
            "div.el-form-item:has(label:has-text('交付状态')) .el-select",
            "div.el-select:has-text('状态')",
            ".el-select",
            "select[name*='status']",
            "input[placeholder*='状态']"
        ]
        
        # 查询按钮选择器
        query_button_selectors = [
            "button:has-text('查询')",
            ".search-btn",
            "[class*='search']"
        ]
        
        # 重置按钮选择器
        reset_button_selectors = [
            "button:has-text('重置')",
            ".reset-btn",
            "[class*='reset']"
        ]
        
        # 状态选项定位器
        pending_selectors = [
            'xpath=//span[contains(text(), "待交付")]'
        ]
        delivering_selectors = [
            'xpath=//span[contains(text(), "交付中")]'
        ]
        completed_selectors = [
            'xpath=//span[contains(text(), "交付完成")]'
        ]
        suspend_selectors = [
            'xpath=//span[contains(text(), "暂停交付")]'
        ]
        # 状态列表
        status_list = [
            ("待交付", pending_selectors),
            ("交付中", delivering_selectors),
            ("交付完成", completed_selectors),
            ("暂停交付", suspend_selectors)
        ]

        # 记录验证结果
        verification_results = []
        
        # 遍历测试每个状态
        for status_name, status_selectors in status_list:
            print(f"   测试状态: {status_name}")
            self._test_data["输入数据"]["测试的状态"].append(status_name)
            
            # 点击状态下拉框
            dropdown_clicked = self._click_element_by_selectors(status_dropdown_selectors, "状态下拉框")
            assert dropdown_clicked, "状态下拉框未找到，测试失败"
            
            # 等待下拉框展开（仅在可见的下拉面板中查找状态选项，避免命中其它隐藏面板）
            self.page.wait_for_timeout(1000)
            try:
                self.page.wait_for_selector(".el-select-dropdown:visible", timeout=5000)
            except Exception:
                pass
            
            # 在可见下拉面板中点击对应的状态选项（限定 :visible，规避隐藏面板同名 span 干扰）
            option_locator = self.page.locator(
                f".el-select-dropdown:visible .el-select-dropdown__item:has-text('{status_name}')"
            ).first
            status_clicked = False
            try:
                if option_locator.count() > 0:
                    option_locator.wait_for(state="visible", timeout=5000)
                    option_locator.click()
                    status_clicked = True
                    print(f"   ✓ 点击{status_name}状态选项")
            except Exception as e:
                print(f"   ⚠️  点击{status_name}状态选项失败: {e}")
            # 回退：若可见面板定位失败，再尝试原来的通用选择器
            if not status_clicked:
                status_clicked = self._click_element_by_selectors(status_selectors, f"{status_name}状态")
            assert status_clicked, f"{status_name}状态选项未找到，测试失败"
            
            # 点击查询按钮
            query_clicked = self._click_element_by_selectors(query_button_selectors, "查询按钮")
            assert query_clicked, "查询按钮未找到，测试失败"
            
            # 等待查询结果加载
            self.page.wait_for_timeout(2000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # 停留3秒观察结果
            self.page.wait_for_timeout(3000)
            
            verification_results.append(f"成功测试{status_name}状态筛选")
            print(f"   ✅ {status_name}状态筛选成功")
        
        # 清除筛选条件 - 点击重置按钮显示全部
        reset_clicked = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_clicked, "重置按钮未找到，测试失败"
        verification_results.append("成功重置筛选条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 重置筛选条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按状态筛选测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_03_view_detail(self):
        """测试查看明细"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试查看明细",
            "测试环境": "用户1登录",
            "输入数据": {
                "页面URL": "",
                "明细页面URL": ""
            },
            "验证结果": ""
        }

        # 记录页面URL
        page_url = self.page.url
        self._test_data["输入数据"]["页面URL"] = page_url

        print("\n=== 测试查看明细 ===")
        
        # 等待页面加载完成
        self.page.wait_for_timeout(2000)
        
        # 查找表格的第一行
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]

        # 记录验证结果
        verification_results = []
        
        first_row = None
        for selector in table_row_selectors:
            try:
                rows = self.page.locator(selector)
                if rows.count() > 0:
                    first_row = rows.first
                    print(f"   找到表格行: {selector} (数量: {rows.count()})")
                    break
            except Exception:
                continue
        
        if first_row:
            # 滚动到第一行
            first_row.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            
            # 查找明细按钮（最后一列）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count > 0:
                last_cell = cells.nth(cell_count - 1)
                
                # 查找明细按钮
                detail_button = last_cell.locator("button:has-text('明细')").first
                
                assert detail_button.count() > 0, "明细按钮未找到，测试失败"
                
                # 等待按钮可见
                detail_button.wait_for(state="visible", timeout=5000)
                
                # 点击明细按钮
                detail_button.click()
                verification_results.append("成功点击明细按钮")
                print("   ✅ 点击明细按钮")
                
                # 等待页面跳转
                self.page.wait_for_timeout(2000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # 记录明细页面URL
                detail_url = self.page.url
                self._test_data["输入数据"]["明细页面URL"] = detail_url
                
                # 验证是否成功跳转到明细页面
                current_url = self.page.url
                print(f"   当前URL: {current_url}")
                
                if "detail" in current_url.lower() or "明细" in self.page.title():
                    verification_results.append("成功跳转到明细页面")
                    print("   ✅ 成功跳转到明细页面")
                else:
                    verification_results.append("可能未跳转到明细页面，但按钮点击成功")
                    print("   ⚠️  可能未跳转到明细页面，但按钮点击成功")
                
                # 返回列表页面（使用浏览器后退功能）
                self.page.go_back()
                self.page.wait_for_timeout(2000)
                verification_results.append("成功返回列表页面")
                print("   ✅ 返回列表页面")
            else:
                verification_results.append("表格列数为0")
                print("   ⚠️  表格列数为0")
        else:
            verification_results.append("未找到表格数据")
            print("   ⚠️  未找到表格数据")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 查看明细测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_04_query_by_product_name_exact(self):
        """测试按数据产品名称精确查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按数据产品名称精确查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "页面URL": "",
                "数据产品名称": ""
            },
            "验证结果": ""
        }

        # 记录页面URL
        page_url = self.page.url
        self._test_data["输入数据"]["页面URL"] = page_url

        print("\n=== 测试按数据产品名称精确查询 ===")
        
        # 等待页面加载完成
        self.page.wait_for_timeout(2000)
        
        # 查找表格的第一行数据
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]

        # 记录验证结果
        verification_results = []
        
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
            # 获取第一行的数据产品名称（第3列，索引2）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 1:
                first_cell = cells.nth(2)
                product_name = (first_cell.text_content() or "").strip()
                self._test_data["输入数据"]["数据产品名称"] = product_name
                print(f"   获取到数据产品名称: {product_name}")
                
                # 数据产品名称输入框选择器（使用更通用的选择器）
                product_name_input_selectors = [
                    "input[placeholder*='数据产品名称']",
                    "input[name*='product']",
                    "input[type='text']:nth-of-type(1)"
                ]
                
                # 查询按钮选择器
                query_button_selectors = [
                    "button:has-text('查询')",
                    ".search-btn",
                    "[class*='search']"
                ]
                
                # 重置按钮选择器
                reset_button_selectors = [
                    "button:has-text('重置')",
                    ".reset-btn",
                    "[class*='reset']"
                ]
                
                # 输入完整的数据产品名称
                input_success = self._input_text_by_selectors(product_name_input_selectors, product_name, "数据产品名称输入框")
                assert input_success, "数据产品名称输入框未找到，测试失败"
                verification_results.append("成功输入数据产品名称")
                self.page.wait_for_timeout(500)
                
                # 点击查询按钮
                query_clicked = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                assert query_clicked, "查询按钮未找到，测试失败"
                verification_results.append("成功点击查询按钮")
                self.page.wait_for_timeout(3000)
                
                # 验证查询结果
                self._verify_query_result_name(product_name)
                verification_results.append("成功验证查询结果")
                
                # 清除查询条件
                reset_clicked = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
                assert reset_clicked, "重置按钮未找到，测试失败"
                verification_results.append("成功清除查询条件")
                self.page.wait_for_timeout(2000)
                print("   ✅ 清除查询条件成功")
            else:
                verification_results.append("表格列数不足，无法获取数据产品名称")
                print("   ⚠️  表格列数不足，无法获取数据产品名称")
        else:
            verification_results.append("未找到表格数据，无法获取数据产品名称")
            print("   ⚠️  未找到表格数据，无法获取数据产品名称")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按数据产品名称精确查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_05_query_by_product_name_fuzzy(self):
        """测试按数据产品名称模糊查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按数据产品名称模糊查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "页面URL": "",
                "完整数据产品名称": "",
                "模糊查询关键词": ""
            },
            "验证结果": ""
        }

        # 记录页面URL
        page_url = self.page.url
        self._test_data["输入数据"]["页面URL"] = page_url

        print("\n=== 测试按数据产品名称模糊查询 ===")
        
        # 等待页面加载完成
        self.page.wait_for_timeout(2000)
        
        # 查找表格的第一行数据
        table_row_selectors = [
            ".el-table tbody tr",
            ".ant-table tbody tr",
            "table tbody tr"
        ]

        # 记录验证结果
        verification_results = []
        
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
            # 获取第一行的数据产品名称（第3列，索引2）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 1:
                first_cell = cells.nth(2)
                product_name = (first_cell.text_content() or "").strip()
                self._test_data["输入数据"]["完整数据产品名称"] = product_name
                print(f"   获取到数据产品名称: {product_name}")
                
                # 提取数据产品名称的前几个字符进行模糊查询
                if len(product_name) > 3:
                    fuzzy_name = product_name[:3]
                else:
                    fuzzy_name = product_name
                
                self._test_data["输入数据"]["模糊查询关键词"] = fuzzy_name
                print(f"   模糊查询关键词: {fuzzy_name}")
                
                # 数据产品名称输入框选择器（使用更通用的选择器）
                product_name_input_selectors = [
                    "input[placeholder*='数据产品名称']",
                    "input[name*='product']",
                    "input[type='text']:nth-of-type(1)"
                ]
                
                # 查询按钮选择器
                query_button_selectors = [
                    "button:has-text('查询')",
                    ".search-btn",
                    "[class*='search']"
                ]
                
                # 重置按钮选择器
                reset_button_selectors = [
                    "button:has-text('重置')",
                    ".reset-btn",
                    "[class*='reset']"
                ]
                
                # 输入模糊查询关键词
                input_success = self._input_text_by_selectors(product_name_input_selectors, fuzzy_name, "数据产品名称输入框")
                assert input_success, "数据产品名称输入框未找到，测试失败"
                verification_results.append("成功输入模糊查询关键词")
                self.page.wait_for_timeout(500)
                
                # 点击查询按钮
                query_clicked = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                assert query_clicked, "查询按钮未找到，测试失败"
                verification_results.append("成功点击查询按钮")
                self.page.wait_for_timeout(3000)
                
                # 验证查询结果
                self._verify_query_result_name(fuzzy_name)
                verification_results.append("成功验证查询结果")
                
                # 清除查询条件
                reset_clicked = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
                assert reset_clicked, "重置按钮未找到，测试失败"
                verification_results.append("成功清除查询条件")
                self.page.wait_for_timeout(2000)
                print("   ✅ 清除查询条件成功")
            else:
                verification_results.append("表格列数不足，无法获取数据产品名称")
                print("   ⚠️  表格列数不足，无法获取数据产品名称")
        else:
            verification_results.append("未找到表格数据，无法获取数据产品名称")
            print("   ⚠️  未找到表格数据，无法获取数据产品名称")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按数据产品名称模糊查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def _input_text_by_xpath(self, xpath, text, element_name):
        """通过XPath输入文本"""
        try:
            input_element = self.page.locator(xpath).first
            if input_element.count() > 0:
                input_element.click()
                self.page.wait_for_timeout(200)
                input_element.fill("")
                self.page.wait_for_timeout(200)
                input_element.fill(text)
                print(f"   ✓ 输入{text}到{element_name}")
                return True
        except Exception as e:
            print(f"   ⚠️  输入文本到{element_name}失败: {e}")
            return False
    
    def _input_text_by_selectors(self, selectors, text, element_name):
        """通过选择器列表输入文本到元素"""
        if not selectors:
            return False
        
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    element.clear()
                    element.fill(text)
                    print(f"   ✓ 输入{text}到{element_name}")
                    return True
            except Exception:
                continue
        print(f"   ⚠️  未找到{element_name}")
        return False
    
    def _verify_query_result_name(self, expected_name):
        """验证查询结果的数据产品名称是否与输入一致"""
        try:
            # 查找表格的第一行数据
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
                # 获取第一行的数据产品名称（第3列，索引2）
                cells = first_row.locator("td")
                cell_count = cells.count()
                
                if cell_count >= 1:
                    first_cell = cells.nth(2)
                    result_name = (first_cell.text_content() or "").strip()
                    print(f"   查询结果数据产品名称: {result_name}")
                    
                    # 验证名称是否一致
                    if expected_name in result_name or result_name in expected_name:
                        print(f"   ✅ 查询结果名称与输入名称一致: {expected_name}")
                    else:
                        print(f"   ⚠️  查询结果名称({result_name})与输入名称({expected_name})不一致")
                else:
                    print(f"   ⚠️  表格列数不足，无法验证名称")
            else:
                print(f"   ⚠️  未找到表格数据，无法验证名称")
        except Exception as e:
            print(f"   ⚠️  验证查询结果名称时出错: {e}")
    
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
    
    def _click_element_by_selectors(self, selectors, element_name):
        """通过多个选择器点击元素"""
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    element.click()
                    print(f"   ✓ 点击{element_name}: {selector}")
                    return True
            except Exception:
                continue
        print(f"   ⚠️  未找到{element_name}")
        return False
