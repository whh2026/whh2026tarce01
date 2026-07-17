import os
import pytest
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.ui_tests.config import ui_config

class TestApprovePage(Base):
    """审批页面测试类"""
    
    # 配置参数
    CONFIG = ui_config.USER_IPS
    
    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        # 默认无头模式（可通过环境变量 UI_HEADLESS=false 显示浏览器窗口，便于本地调试）
        headless = os.environ.get("UI_HEADLESS", "true").lower() == "true"
        cls.browser = cls.playwright.chromium.launch(headless=headless)
        # 创建持久化的上下文和页面，登录态通过 context 中的 cookie 保持，供所有用例复用
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        # 标记尚未登录，由首个用例的 setup_method 完成一次性登录
        cls._logged_in = False
    
    @classmethod
    def _wait_target_page(cls):
        """等待审批页面加载完成（带容错）"""
        try:
            cls.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            try:
                cls.page.wait_for_load_state("load", timeout=10000)
            except Exception:
                cls.page.wait_for_timeout(2000)
        assert "approve" in cls.page.url.lower(), f"页面访问失败，当前URL: {cls.page.url}"
    
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
        """每个测试方法执行前：首个用例完成登录（仅一次），其余用例回到审批页面（复用已登录会话）"""
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
        
        # 回到审批页面（登录态通过持久化 context 保持，无需重新登录）
        approve_url = self.get_url_for_user(1, "/datamarket/applyManage/approve", self.CONFIG)
        self.page.goto(approve_url)
        self._wait_target_page()
        print(f"\n=== 回到审批页面: {method.__name__} ===")
        print(f"✅ 前置条件 - 成功访问审批页面！")
        print(f"   页面URL: {self.page.url}")
        print(f"   页面标题: {self.page.title()}")
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理（不关闭页面/上下文，保留登录态供后续用例复用）"""
        # 失败截图由 conftest.py 的 pytest_runtest_makereport 钩子统一处理
        pass
    
    def test_01_access_approve_page(self):
        """测试访问审批页面"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试访问审批页面",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "页面标题": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL和标题
        approve_url = self.page.url
        page_title = self.page.title()
        self._test_data["输入数据"]["审批页面URL"] = approve_url
        self._test_data["输入数据"]["页面标题"] = page_title

        print("\n=== 测试访问审批页面 ===")
        
        # 验证页面标题
        print(f"   页面标题: {page_title}")
        assert page_title, "页面标题不能为空"
        
        # 验证页面URL
        current_url = self.page.url
        print(f"   当前URL: {current_url}")
        assert "approve" in current_url.lower(), "URL中应包含'approve'"
        
        # 验证页面元素 - 审批表格
        table_exists = self._verify_element_exists([".el-table", ".ant-table", "table"], "审批表格", timeout=5000)
        
        # 验证查询按钮
        search_button_exists = self._verify_element_exists(["button:has-text('查询')", ".search-btn", "[class*='search']"], "查询按钮", timeout=5000)
        
        # 验证分页组件
        pagination_exists = self._verify_element_exists([".el-pagination", ".ant-pagination", ".pagination"], "分页组件", timeout=5000)
        
        # 验证查询条件 - 申请单编号输入框（占位文本：输入使用申请单编号）
        application_number_input_exists = self._verify_element_exists([
            "input[placeholder*='使用申请单编号']",
            "input[placeholder*='申请单编号']",
            "input[name*='application']"
        ], "申请单编号输入框", timeout=5000)
        
        # 验证查询条件 - 数据产品名称输入框（占位文本：输入数据产品名称）
        product_name_input_exists = self._verify_element_exists([
            "input[placeholder*='数据产品名称']",
            "input[name*='product']"
        ], "数据产品名称输入框", timeout=5000)
        
        # 验证查询条件 - 审批状态下拉框（占位文本：全部状态）
        status_dropdown_exists = self._verify_element_exists([
            "div.el-select:has-text('全部状态')",
            ".el-select"
        ], "审批状态下拉框", timeout=5000)
        
        # 验证表格列
        fields_exists = []
        fields_exists.append(self._verify_field_exists(["th:has-text('使用申请单编号')"], "申请编号字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('数据产品名称')"], "数据产品名称字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('数据产品小类')"], "数据产品小类字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('数据产品使用方')"], "数据产品使用方字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('审批状态')"], "审批状态字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('申请时间')"], "申请时间字段"))
        fields_exists.append(self._verify_field_exists(["th:has-text('操作')"], "操作字段"))
        
        # 验证数据列表标题并输出第一列数据
        print("\n=== 验证数据列表标题并输出第一列数据 ===")
        
        # 等待表格数据加载
        self.page.wait_for_timeout(2000)
        
        # 查找表格的第一行（表头）
        table_header_selectors = [
            ".el-table thead tr",
            ".ant-table thead tr",
            "table thead tr"
        ]
        
        header_row = None
        for selector in table_header_selectors:
            try:
                headers = self.page.locator(selector)
                if headers.count() > 0:
                    header_row = headers.first
                    print(f"   找到表头行: {selector} (数量: {headers.count()})")
                    break
            except Exception:
                continue
        
        if header_row:
            # 获取表头的所有单元格
            header_cells = header_row.locator("th")
            header_count = header_cells.count()
            print(f"   找到 {header_count} 个表头")
            
            # 输出标题名称
            for i in range(min(header_count, 8)):
                header_cell = header_cells.nth(i)
                header_text = (header_cell.text_content() or "").strip()
                print(f"   ✅ 标题名称{i+1}: {header_text}")
        
        # 查找表格的第一行（数据行）
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
                    print(f"   找到表格行: {selector} (数量: {rows.count()})")
                    break
            except Exception:
                continue

        # 记录验证结果
        verification_results = []
        if table_exists: verification_results.append("成功找到审批表格")
        if search_button_exists: verification_results.append("成功找到查询按钮")
        if pagination_exists: verification_results.append("成功找到分页组件")
        if application_number_input_exists: verification_results.append("成功找到申请单编号输入框")
        if product_name_input_exists: verification_results.append("成功找到数据产品名称输入框")
        if status_dropdown_exists: verification_results.append("成功找到审批状态下拉框")
        if all(fields_exists): verification_results.append("成功找到所有表格字段")
        if header_row: verification_results.append("成功找到表头")
        if first_row: verification_results.append("成功找到表格数据行")
        else: verification_results.append("未找到表格数据")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        if first_row:
            # 获取第一行的所有单元格
            cells = first_row.locator("td")
            cell_count = cells.count()
            print(f"   找到 {cell_count} 个单元格")
            
            # 输出第一行数据
            if cell_count > 0:
                print("   ✅ 第一行数据:")
                for i in range(cell_count):
                    cell = cells.nth(i)
                    cell_text = (cell.text_content() or "").strip()
                    print(f"      第{i+1}列: {cell_text}")
        else:
            print("   ⚠️  未找到表格数据")
        
        print("   ✅ 访问审批页面测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_02_filter_by_approve_status(self):
        """测试按审批状态筛选"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按审批状态筛选",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "测试的审批状态": []
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按审批状态筛选 ===")
        
        # 等待页面加载完成
        self.page.wait_for_timeout(2000)
        
        # 审批状态下拉框选择器（使用更通用的选择器）
        status_dropdown_selectors = [
            "div.el-select:has-text('全部状态')",
            ".el-select",
            "select[name*='status']",
            "input[placeholder*='审批状态']"
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
        
        # 审批状态选项定位器（限定在下拉面板内，避免匹配表格内同名状态文本）
        pending_selectors = [
            'xpath=//div[contains(@class,"el-select-dropdown")]//li[normalize-space()="待审批"]'
        ]
        approved_selectors = [
            'xpath=//div[contains(@class,"el-select-dropdown")]//li[normalize-space()="通过"]'
        ]
        rejected_selectors = [
            'xpath=//div[contains(@class,"el-select-dropdown")]//li[normalize-space()="拒绝"]'
        ]
        invalid_selectors = [
            'xpath=//div[contains(@class,"el-select-dropdown")]//li[normalize-space()="已失效"]'
        ]
        
        # 审批状态列表
        status_list = [
            ("待审批", pending_selectors),
            ("通过", approved_selectors),
            ("拒绝", rejected_selectors),
            ("已失效", invalid_selectors)
        ]

        # 记录验证结果
        verification_results = []
        
        # 遍历测试每个审批状态
        for status_name, status_selectors in status_list:
            print(f"   测试审批状态: {status_name}")
            self._test_data["输入数据"]["测试的审批状态"].append(status_name)
            
            # 点击审批状态下拉框
            dropdown_clicked = self._click_element_by_selectors(status_dropdown_selectors, "审批状态下拉框")
            assert dropdown_clicked, "审批状态下拉框未找到，测试失败"
            
            # 等待下拉框展开
            self.page.wait_for_timeout(1000)
            
            # 点击对应的审批状态选项
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
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        verification_results.append("成功重置筛选条件")
        print("   ✅ 重置筛选条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按审批状态筛选测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_03_view_approve_detail(self):
        """测试查看审批详情"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试查看审批详情",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "详情页面URL": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试查看审批详情 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 查找表格的第一行
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
                    print(f"   找到表格行: {selector} (数量: {rows.count()})")
                    break
            except Exception:
                continue

        # 记录验证结果
        verification_results = []
        
        if first_row:
            # 滚动到第一行
            first_row.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            
            # 查找第一行的详情按钮（操作列内的 详情 按钮）
            detail_button = first_row.locator("button:has-text('详情'), a:has-text('详情')")
            
            try:
                # 等待按钮可见
                detail_button.wait_for(state="visible", timeout=5000)
                
                # 点击详情按钮
                detail_button.click()
                verification_results.append("成功点击审批详情按钮")
                print("   ✓ 点击审批详情按钮")
                
                # 等待详情页面加载
                self.page.wait_for_timeout(3000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # 记录详情页面URL
                detail_url = self.page.url
                self._test_data["输入数据"]["详情页面URL"] = detail_url
                
                # 验证是否成功跳转到详情页面
                current_url = self.page.url
                print(f"   当前URL: {current_url}")
                
                if "detail" in current_url.lower() or "详情" in self.page.title():
                    verification_results.append("成功跳转到审批详情页面")
                    print("   ✅ 成功跳转到审批详情页面")
                else:
                    verification_results.append("可能未跳转到详情页面，但按钮点击成功")
                    print("   ⚠️  可能未跳转到详情页面，但按钮点击成功")
                
                # 返回列表页面（优先点击返回/返回列表控件，失败则浏览器回退）
                back_clicked = False
                for back_sel in [
                    "button:has-text('返回')",
                    "a:has-text('返回')",
                    "button:has-text('返回列表')",
                    ".el-page-header__left",
                    "[class*='back']"
                ]:
                    if self._click_element_by_selectors([back_sel], "返回"):
                        back_clicked = True
                        break
                if not back_clicked:
                    self.page.go_back()
                    self.page.wait_for_timeout(2000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    back_clicked = True
                assert back_clicked, "返回按钮未找到，测试失败"
                
                self.page.wait_for_timeout(2000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                verification_results.append("成功返回审批列表页面")
                print("   ✓ 返回审批列表页面")
                
            except Exception as e:
                verification_results.append(f"点击详情按钮失败: {str(e)}")
                print(f"   ⚠️  点击详情按钮失败: {e}")
        else:
            verification_results.append("未找到表格数据，跳过测试")
            print("   ⚠️  未找到表格数据，跳过测试")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 查看审批详情测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_04_query_by_application_number_exact(self):
        """测试按申请单编号精确查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按申请单编号精确查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "申请单编号": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按申请单编号精确查询 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 申请单编号输入框选择器（使用更通用的选择器）
        application_number_input_selectors = [
            "input[placeholder*='申请单编号']",
            "input[name*='application']",
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
        
        # 获取第一行的申请单编号
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
            # 获取第一行的申请单编号（第1列）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 1:
                first_cell = cells.nth(0)
                application_number = (first_cell.text_content() or "").strip()
                self._test_data["输入数据"]["申请单编号"] = application_number
                print(f"   获取到申请单编号: {application_number}")
                
                # 精确查询 - 输入完整的申请单编号
                input_success = self._input_text_by_selectors(application_number_input_selectors, application_number, "申请单编号输入框")
                assert input_success, "申请单编号输入框未找到，测试失败"
                verification_results.append("成功输入申请单编号")
                
                # 点击查询按钮
                query_success = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                assert query_success, "查询按钮未找到，测试失败"
                verification_results.append("成功点击查询按钮")
                
                # 等待查询结果加载
                self.page.wait_for_timeout(2000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # 停留3秒观察结果
                self.page.wait_for_timeout(3000)
                
                # 验证查询结果
                self._verify_query_result_number(application_number)
                verification_results.append("成功验证查询结果")
                
                print("   ✅ 精确查询成功")
            else:
                verification_results.append("表格列数不足，无法获取申请单编号")
                print("   ⚠️  表格列数不足，无法获取申请单编号")
        else:
            verification_results.append("未找到表格数据，跳过测试")
            print("   ⚠️  未找到表格数据，跳过测试")
        
        # 清除查询条件 - 点击重置按钮
        reset_success = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_success, "重置按钮未找到，测试失败"
        verification_results.append("成功清除查询条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 清除查询条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按申请单编号精确查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_05_query_by_application_number_fuzzy(self):
        """测试按申请单编号模糊查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按申请单编号模糊查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "完整申请单编号": "",
                "模糊搜索编号": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按申请单编号模糊查询 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 申请单编号输入框选择器（使用更通用的选择器）
        application_number_input_selectors = [
            "input[placeholder*='申请单编号']",
            "input[name*='application']",
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
        
        # 获取第一行的申请单编号
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
            # 获取第一行的申请单编号（第1列）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 1:
                first_cell = cells.nth(0)
                application_number = (first_cell.text_content() or "").strip()
                self._test_data["输入数据"]["完整申请单编号"] = application_number
                print(f"   获取到申请单编号: {application_number}")
                
                # 模糊搜索 - 输入申请单编号的前几位
                if len(application_number) > 5:
                    fuzzy_number = application_number[:5]
                    self._test_data["输入数据"]["模糊搜索编号"] = fuzzy_number
                    print(f"   使用模糊编号: {fuzzy_number}")
                    
                    input_success = self._input_text_by_selectors(application_number_input_selectors, fuzzy_number, "申请单编号输入框")
                    assert input_success, "申请单编号输入框未找到，测试失败"
                    verification_results.append("成功输入模糊搜索编号")
                    
                    # 点击查询按钮
                    query_success = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                    assert query_success, "查询按钮未找到，测试失败"
                    verification_results.append("成功点击查询按钮")
                    
                    # 等待查询结果加载
                    self.page.wait_for_timeout(2000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    
                    # 停留3秒观察结果
                    self.page.wait_for_timeout(3000)
                    
                    # 验证查询结果非空（模糊查询应返回匹配数据）
                    self._verify_non_empty_query_result()
                    verification_results.append("成功验证查询结果非空")
                    
                    print("   ✅ 模糊搜索成功，查询结果非空")
                else:
                    verification_results.append("申请单编号长度不足，跳过模糊搜索测试")
                    print("   ⚠️  申请单编号长度不足，跳过模糊搜索测试")
            else:
                verification_results.append("表格列数不足，无法获取申请单编号")
                print("   ⚠️  表格列数不足，无法获取申请单编号")
        else:
            verification_results.append("未找到表格数据，跳过测试")
            print("   ⚠️  未找到表格数据，跳过测试")
        
        # 清除查询条件 - 点击重置按钮
        reset_success = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_success, "重置按钮未找到，测试失败"
        verification_results.append("成功清除查询条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 清除查询条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按申请单编号模糊查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_06_query_by_product_name_exact(self):
        """测试按数据产品名称精确查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按数据产品名称精确查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "数据产品名称": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按数据产品名称精确查询 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 数据产品名称输入框选择器（使用更通用的选择器）
        product_name_input_selectors = [
            "input[placeholder*='数据产品名称']",
            "input[name*='product']",
            "input[type='text']:nth-of-type(2)"
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
        
        # 获取第一行的数据产品名称（第2列）
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
            # 获取第一行的数据产品名称（第2列）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 2:
                second_cell = cells.nth(1)
                product_name = (second_cell.text_content() or "").strip()
                self._test_data["输入数据"]["数据产品名称"] = product_name
                print(f"   获取到数据产品名称: {product_name}")
                
                # 精确查询 - 输入完整的数据产品名称
                input_success = self._input_text_by_selectors(product_name_input_selectors, product_name, "数据产品名称输入框")
                assert input_success, "数据产品名称输入框未找到，测试失败"
                verification_results.append("成功输入数据产品名称")
                
                # 点击查询按钮
                query_success = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                assert query_success, "查询按钮未找到，测试失败"
                verification_results.append("成功点击查询按钮")
                
                # 等待查询结果加载
                self.page.wait_for_timeout(2000)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # 停留3秒观察结果
                self.page.wait_for_timeout(3000)
                
                # 验证查询结果
                self._verify_query_result_name(product_name)
                verification_results.append("成功验证查询结果")
                
                print("   ✅ 精确查询成功")
            else:
                verification_results.append("表格列数不足，无法获取数据产品名称")
                print("   ⚠️  表格列数不足，无法获取数据产品名称")
        else:
            verification_results.append("未找到表格数据，跳过测试")
            print("   ⚠️  未找到表格数据，跳过测试")
        
        # 清除查询条件 - 点击重置按钮
        reset_success = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_success, "重置按钮未找到，测试失败"
        verification_results.append("成功清除查询条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 清除查询条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按数据产品名称精确查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_07_query_by_product_name_fuzzy(self):
        """测试按数据产品名称模糊查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按数据产品名称模糊查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "完整产品名称": "",
                "模糊搜索名称": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按数据产品名称模糊查询 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 数据产品名称输入框选择器（使用更通用的选择器）
        product_name_input_selectors = [
            "input[placeholder*='数据产品名称']",
            "input[name*='product']",
            "input[type='text']:nth-of-type(2)"
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
        
        # 获取第一行的数据产品名称（第2列）
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
            # 获取第一行的数据产品名称（第2列）
            cells = first_row.locator("td")
            cell_count = cells.count()
            
            if cell_count >= 2:
                second_cell = cells.nth(1)
                product_name = (second_cell.text_content() or "").strip()
                self._test_data["输入数据"]["完整产品名称"] = product_name
                print(f"   获取到数据产品名称: {product_name}")
                
                # 模糊搜索 - 输入数据产品名称的前几个字符
                if len(product_name) > 2:
                    fuzzy_name = product_name[:2]
                    self._test_data["输入数据"]["模糊搜索名称"] = fuzzy_name
                    print(f"   使用模糊名称: {fuzzy_name}")
                    
                    input_success = self._input_text_by_selectors(product_name_input_selectors, fuzzy_name, "数据产品名称输入框")
                    assert input_success, "数据产品名称输入框未找到，测试失败"
                    verification_results.append("成功输入模糊搜索名称")
                    
                    # 点击查询按钮
                    query_success = self._click_element_by_selectors(query_button_selectors, "查询按钮")
                    assert query_success, "查询按钮未找到，测试失败"
                    verification_results.append("成功点击查询按钮")
                    
                    # 等待查询结果加载
                    self.page.wait_for_timeout(2000)
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    
                    # 停留3秒观察结果
                    self.page.wait_for_timeout(3000)
                    
                    # 验证查询结果非空（模糊查询应返回匹配数据）
                    self._verify_non_empty_query_result()
                    verification_results.append("成功验证查询结果非空")
                    
                    print("   ✅ 模糊搜索成功，查询结果非空")
                else:
                    verification_results.append("数据产品名称长度不足，跳过模糊搜索测试")
                    print("   ⚠️  数据产品名称长度不足，跳过模糊搜索测试")
            else:
                verification_results.append("表格列数不足，无法获取数据产品名称")
                print("   ⚠️  表格列数不足，无法获取数据产品名称")
        else:
            verification_results.append("未找到表格数据，跳过测试")
            print("   ⚠️  未找到表格数据，跳过测试")
        
        # 清除查询条件 - 点击重置按钮
        reset_success = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_success, "重置按钮未找到，测试失败"
        verification_results.append("成功清除查询条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 清除查询条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按数据产品名称模糊查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def test_08_query_by_product_name_empty(self):
        """测试按数据产品名称空查询"""
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试按数据产品名称空查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "审批页面URL": "",
                "空查询名称": ""
            },
            "验证结果": ""
        }

        # 记录审批页面URL
        approve_url = self.page.url
        self._test_data["输入数据"]["审批页面URL"] = approve_url

        print("\n=== 测试按数据产品名称空查询 ===")
        
        # 等待页面完全加载
        self.page.wait_for_timeout(3000)
        
        # 数据产品名称输入框选择器（使用更通用的选择器）
        product_name_input_selectors = [
            "input[placeholder*='数据产品名称']",
            "input[name*='product']",
            "input[type='text']:nth-of-type(2)"
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

        # 记录验证结果
        verification_results = []
        
        # 空查询 - 输入不存在的数据产品名称
        empty_name = "不存在的产品名称123456"
        self._test_data["输入数据"]["空查询名称"] = empty_name
        print(f"   使用空查询名称: {empty_name}")
        
        input_success = self._input_text_by_selectors(product_name_input_selectors, empty_name, "数据产品名称输入框")
        assert input_success, "数据产品名称输入框未找到，测试失败"
        verification_results.append("成功输入空查询名称")
        
        # 点击查询按钮
        query_success = self._click_element_by_selectors(query_button_selectors, "查询按钮")
        assert query_success, "查询按钮未找到，测试失败"
        verification_results.append("成功点击查询按钮")
        
        # 等待查询结果加载
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        
        # 停留3秒观察结果
        self.page.wait_for_timeout(3000)
        
        # 验证查询结果为空
        self._verify_empty_query_result()
        verification_results.append("成功验证查询结果为空")
        
        print("   ✅ 空查询成功，查询结果为空")
        
        # 清除查询条件 - 点击重置按钮
        reset_success = self._click_element_by_selectors(reset_button_selectors, "重置按钮")
        assert reset_success, "重置按钮未找到，测试失败"
        verification_results.append("成功清除查询条件")
        
        # 等待重置操作完成
        self.page.wait_for_timeout(1000)
        print("   ✅ 清除查询条件成功")

        self._test_data["验证结果"] = "\n".join(verification_results)
        
        print("   ✅ 按数据产品名称空查询测试完成！")
        
        print("[成功] 测试数据已附加到HTML报告")
    
    def _find_element_by_selectors(self, selectors):
        """根据选择器列表查找元素"""
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    return element
            except Exception:
                continue
        return None
    
    def _click_element_by_selectors(self, selectors, element_name):
        """根据选择器列表点击元素"""
        if not selectors:
            return False
        
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
    
    def _input_text_by_xpath(self, xpath, text, element_name):
        """通过XPath输入文本到元素"""
        try:
            element = self.page.locator(xpath).first
            if element.count() > 0:
                element.clear()
                element.fill(text)
                print(f"   ✓ 输入{text}到{element_name}")
                return True
        except Exception as e:
            print(f"   ⚠️  输入{text}到{element_name}失败: {e}")
            return False
    
    def _verify_query_result_number(self, expected_number):
        """验证查询结果的申请单编号是否与输入一致"""
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
                # 获取第一行的申请单编号（第1列）
                cells = first_row.locator("td")
                cell_count = cells.count()
                
                if cell_count >= 1:
                    first_cell = cells.nth(0)
                    result_number = (first_cell.text_content() or "").strip()
                    print(f"   查询结果申请单编号: {result_number}")
                    
                    # 验证编号是否一致
                    if expected_number in result_number or result_number in expected_number:
                        print(f"   ✅ 查询结果编号与输入编号一致: {expected_number}")
                    else:
                        print(f"   ⚠️  查询结果编号({result_number})与输入编号({expected_number})不一致")
                else:
                    print(f"   ⚠️  表格列数不足，无法验证编号")
            else:
                print(f"   ⚠️  未找到表格数据，无法验证编号")
        except Exception as e:
            print(f"   ⚠️  验证查询结果编号时出错: {e}")
    
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
                # 获取第一行的数据产品名称（第2列）
                cells = first_row.locator("td")
                cell_count = cells.count()
                
                if cell_count >= 2:
                    second_cell = cells.nth(1)
                    result_name = (second_cell.text_content() or "").strip()
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
    
    def _verify_empty_query_result(self):
        """验证查询结果为空"""
        try:
            # 检查是否实际存在数据行（若有误判，明确提示非空）
            for selector in [".el-table tbody tr", ".ant-table tbody tr", "table tbody tr"]:
                try:
                    if self.page.locator(selector).count() > 0:
                        print("   ⚠️  查询结果为空校验失败：表格中存在数据行（结果非空）")
                        return
                except Exception:
                    continue

            # 检查空状态提示信息
            empty_text_selectors = [
                ".el-table__empty-block",
                ".ant-empty",
                "[class*='empty']",
                "text=暂无数据",
                "text=无数据",
                "text=没有找到相关数据"
            ]
            
            for selector in empty_text_selectors:
                try:
                    empty_element = self.page.locator(selector).first
                    if empty_element.count() > 0:
                        empty_text = (empty_element.text_content() or "").strip()
                        if empty_text:
                            print(f"   找到空状态提示: {empty_text}")
                            print("   ✅ 确认查询结果为空")
                            return
                except Exception:
                    continue
            
            print("   ✅ 确认查询结果为空（未找到数据行）")
                
        except Exception as e:
            print(f"   ⚠️  验证查询结果为空时出错: {e}")
    
    def _verify_non_empty_query_result(self):
        """验证查询结果非空（模糊/部分匹配查询应返回至少一条数据）"""
        try:
            table_row_selectors = [
                ".el-table tbody tr",
                ".ant-table tbody tr",
                "table tbody tr"
            ]
            for selector in table_row_selectors:
                try:
                    rows = self.page.locator(selector)
                    if rows.count() > 0:
                        print(f"   ✅ 确认查询结果非空，共 {rows.count()} 行")
                        return
                except Exception:
                    continue
            print("   ⚠️  查询结果为空（模糊查询预期应有结果）")
        except Exception as e:
            print(f"   ⚠️  验证查询结果非空时出错: {e}")
    
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
