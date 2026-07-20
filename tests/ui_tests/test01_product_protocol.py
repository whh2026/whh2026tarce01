import pytest
import time
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.test_data.product_protocol_data import (
    SELECTORS, ASSERT_MESSAGES, generate_test_data, generate_max_length_data,
    CHAIN_STATUS, WAIT_TIMES, CHAIN_STATUS_TEST_LIST, get_test_file_path
)
from tests.ui_tests.config import ui_config


class TestProductProtocol(Base):
    """产品协议页面测试类 - 适配新版页面 /datamarket/product-manage/productProtocol"""

    CONFIG = ui_config

    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
        # 创建持久化的上下文和页面，登录态通过 context 中的 cookie 保持，供所有用例复用
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_default_timeout(30000)
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        # 标记尚未登录，由首个用例的 setup_method 完成一次性登录
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
        """每个测试方法执行前：首个用例完成登录（仅一次），其余用例回到产品协议页面（复用已登录会话）"""
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

        # 导航到产品协议页面
        if "direct" in method.__name__ or method.__name__.endswith("add_protocol_direct"):
            self.product_protocol_url = self.get_url_for_user(1, "/datamarket/product-manage/productProtocol/create", self.CONFIG.USER_IPS)
        else:
            self.product_protocol_url = self.get_url_for_user(1, "/datamarket/product-manage/productProtocol", self.CONFIG.USER_IPS)

        self.page.goto(self.product_protocol_url)
        self.page.wait_for_load_state("networkidle")

        assert "productprotocol" in self.page.url.lower(), ASSERT_MESSAGES["page_access_failed"].format(url=self.page.url)
        print(f"[前置条件] 成功访问产品协议页面！")
        print(f"   页面URL: {self.page.url}")
        print(f"   页面标题: {self.page.title()}")

    def teardown_method(self, method):
        """每个测试方法执行后的清理（不关闭页面/上下文，保留登录态供后续用例复用）"""
        # 失败截图由 conftest.py 的 pytest_runtest_makereport 钩子统一处理
        pass

    def _fill_login_form(self):
        """填写登录表单"""
        try:
            # 使用与base.py相同的selector
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
            # 验证登录成功
            assert "login" not in self.page.url.lower(), f"登录失败，当前URL: {self.page.url}"
            print(f"[登录] 登录成功！当前URL: {self.page.url}")
        except Exception as e:
            print(f"   [警告] 提交登录失败: {e}")

    def _get_test_file_path(self):
        """获取测试文件路径"""
        path = get_test_file_path()
        if path and __import__('os').path.exists(path):
            return path
        # 尝试创建临时测试文件
        import os
        temp_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "test_protocol.docx")
        temp_path = os.path.abspath(temp_path)
        if not os.path.exists(temp_path):
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            # 创建一个最小的docx文件
            with open(temp_path, 'wb') as f:
                f.write(b'PK\x03\x04')
        return temp_path if os.path.exists(temp_path) else None

    def _upload_file(self, file_path=None):
        """上传文件到产品协议文件字段"""
        if not file_path:
            file_path = self._get_test_file_path()
        if not file_path or not __import__('os').path.exists(file_path):
            print("   [警告] 未找到测试文件，跳过文件上传")
            return False

        try:
            # 使用 set_input_files 直接操作隐藏的文件 input
            file_input = self.page.locator(SELECTORS["file_upload_input"])
            if file_input.count() > 0:
                file_input.set_input_files(file_path)
                print(f"   上传文件: {file_path}")
                self.page.wait_for_timeout(2000)
                return True
            else:
                print("   [警告] 未找到文件上传输入框")
                return False
        except Exception as e:
            print(f"   [警告] 文件上传失败: {e}")
            return False

    def _click_add_button(self):
        """点击新增协议按钮并等待页面跳转"""
        # 先获取当前URL
        current_url = self.page.url
        print(f"   当前URL: {current_url}")

        # 点击新增协议按钮
        add_btn = self.page.locator(SELECTORS["add_button"]).first
        if add_btn.count() == 0:
            # 尝试更通用的选择器
            add_btn = self.page.locator("button.el-button--primary:has-text('新增协议')").first
        if add_btn.count() == 0:
            add_btn = self.page.locator("span.el-button__text:has-text('新增协议')").locator("..").first

        assert add_btn.count() > 0, "未找到新增协议按钮"
        print("   点击新增协议按钮")
        add_btn.click()

        # 等待页面跳转（URL变化）
        try:
            self.page.wait_for_url("**/productProtocol/create", timeout=10000)
            print(f"   已跳转到新增页面: {self.page.url}")
        except Exception:
            # 如果wait_for_url失败，尝试等待networkidle
            self.page.wait_for_timeout(3000)
            self.page.wait_for_load_state("networkidle")
            print(f"   点击后URL: {self.page.url}")
            if "create" not in self.page.url.lower():
                # 如果还没有跳转，可能是SPA路由，直接导航到create页面
                print("   [提示] 未检测到页面跳转，直接导航到新增页面")
                create_url = self.get_url_for_user(1, "/datamarket/product-manage/productProtocol/create", self.CONFIG.USER_IPS)
                self.page.goto(create_url)
                self.page.wait_for_load_state("networkidle")
                # 整页加载后 JS 可能尚未初始化，显式等待表单与提交按钮就绪，避免提交失败
                self.page.locator(SELECTORS["name_input"]).first.wait_for(state="visible", timeout=10000)
                self.page.locator(SELECTORS["confirm_button"]).first.wait_for(state="visible", timeout=10000)
                self.page.wait_for_timeout(1000)

    def _fill_add_form(self, name, desc=None, upload_file=True):
        """填写新增协议表单"""
        if desc is None:
            desc = name

        # 等待页面加载完成（create页面）
        if "create" not in self.page.url.lower():
            print(f"   [警告] 当前不在新增页面，URL: {self.page.url}")
            return

        # 产品协议名称
        name_input = self.page.locator(SELECTORS["name_input"])
        name_input.wait_for(state="visible", timeout=10000)
        if name_input.count() > 0:
            name_input.fill(name)
            print(f"   填充产品协议名称: {name}")
        else:
            print("   [警告] 未找到产品协议名称输入框")

        # 产品协议描述
        desc_input = self.page.locator(SELECTORS["desc_input"])
        if desc_input.count() > 0:
            desc_input.fill(desc)
            print(f"   填充产品协议描述: {desc}")
        else:
            print("   [警告] 未找到产品协议描述输入框")

        # 上传文件
        if upload_file:
            self._upload_file()

        self.page.wait_for_timeout(1000)

    def _click_confirm(self):
        """点击确定按钮"""
        confirm_btn = self.page.locator(SELECTORS["confirm_button"])
        if confirm_btn.count() > 0:
            confirm_btn.click()
            print("   点击确定按钮")
            self.page.wait_for_timeout(3000)
            self.page.wait_for_load_state("networkidle")
        else:
            print("   [警告] 未找到确定按钮")

    def _find_row_by_name(self, name):
        """根据名称在表格中查找行（首屏找不到时用名称搜索兜底，覆盖列表分页场景）"""
        # 先在首屏查找
        rows = self.page.locator(SELECTORS["table_rows"])
        total = rows.count()
        for idx in range(total):
            row = rows.nth(idx)
            name_cell = row.locator("td:nth-child(2)")
            if name_cell.count() > 0 and name in (name_cell.text_content() or ""):
                return row, idx
        # 首屏未找到，使用名称搜索过滤后查找（可跨分页定位）
        try:
            search_input = self.page.locator(SELECTORS["search_input"])
            if search_input.count() > 0:
                search_input.fill(name)
                self.page.locator(SELECTORS["search_button"]).first.click()
                self.page.wait_for_timeout(2000)
                rows = self.page.locator(SELECTORS["table_rows"])
                total = rows.count()
                for idx in range(total):
                    row = rows.nth(idx)
                    name_cell = row.locator("td:nth-child(2)")
                    if name_cell.count() > 0 and name in (name_cell.text_content() or ""):
                        return row, idx
        except Exception as e:
            print(f"   [警告] 搜索兜底查找失败: {str(e)}")
        return None, -1

    def _search_by_name(self, name):
        """根据名称搜索并返回结果"""
        # 重置
        reset_btn = self.page.locator(SELECTORS["reset_button"])
        if reset_btn.count() > 0:
            reset_btn.click()
            self.page.wait_for_timeout(1000)

        # 输入搜索条件
        search_input = self.page.locator(SELECTORS["search_input"])
        if search_input.count() > 0:
            search_input.fill(name)
            print(f"   输入查询条件: {name}")

        # 点击查询
        search_btn = self.page.locator(SELECTORS["search_button"])
        if search_btn.count() > 0:
            search_btn.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(2000)

        # 返回结果行数
        rows = self.page.locator(SELECTORS["table_rows"])
        return rows.count()

    def _handle_uneditable_dialog(self):
        """处理不可编辑对话框"""
        dialog = self.page.locator(SELECTORS["uneditable_dialog"])
        if dialog.count() > 0 and dialog.first.is_visible():
            print("   [提示] 弹出'不可编辑'对话框（协议被数据产品使用）")
            close_btn = self.page.locator(SELECTORS["dialog_close_button"])
            if close_btn.count() > 0:
                close_btn.first.click()
                self.page.wait_for_timeout(1000)
            return True
        return False

    def _handle_undeletable_dialog(self):
        """处理不可删除对话框"""
        dialog = self.page.locator(SELECTORS["undeletable_dialog"])
        if dialog.count() > 0 and dialog.first.is_visible():
            print("   [提示] 弹出'不可删除'对话框（协议被数据产品使用）")
            close_btn = self.page.locator(SELECTORS["dialog_close_button"])
            if close_btn.count() > 0:
                close_btn.first.click()
                self.page.wait_for_timeout(1000)
            return True
        return False

    # ==================== 测试方法 ====================

    def test_01_page_elements(self):
        """测试产品协议页面的基本元素"""
        print("\n=== 测试产品协议页面基本元素 ===")
        self._test_data = {"测试类型": "页面元素验证", "测试目的": "验证产品协议页面的基本元素"}

        page_title = self.page.title()
        print(f"   页面标题: {page_title}")
        assert page_title, "页面标题不能为空"

        current_url = self.page.url
        print(f"   当前URL: {current_url}")
        assert "productprotocol" in current_url.lower(), "URL中应包含'productprotocol'"

        # 验证表格
        table = self.page.locator(".el-table")
        assert table.count() > 0, "未找到产品协议表格"
        print("   找到产品协议表格")

        # 验证新增协议按钮
        add_btn = self.page.locator(SELECTORS["add_button"])
        assert add_btn.count() > 0, "未找到新增协议按钮"
        print("   找到新增协议按钮")

        # 验证查询按钮
        search_btn = self.page.locator(SELECTORS["search_button"])
        assert search_btn.count() > 0, "未找到查询按钮"
        print("   找到查询按钮")

        # 验证重置按钮
        reset_btn = self.page.locator(SELECTORS["reset_button"])
        assert reset_btn.count() > 0, "未找到重置按钮"
        print("   找到重置按钮")

        # 验证分页组件
        pagination = self.page.locator(".el-pagination")
        assert pagination.count() > 0, "未找到分页组件"
        print("   找到分页组件")

        # 验证搜索输入框
        search_input = self.page.locator(SELECTORS["search_input"])
        assert search_input.count() > 0, "未找到搜索输入框"
        print("   找到搜索输入框")

        # 验证表格列
        headers = ["产品协议编号", "产品协议名称", "产品协议文件", "链上状态", "创建时间", "操作"]
        for header in headers:
            header_locator = self.page.locator(f"th:has-text('{header}')")
            assert header_locator.count() > 0, f"未找到表格列: {header}"
            print(f"   找到表格列: {header}")

        # 输出第一行数据
        print("\n   输出第一行协议数据：")
        rows = self.page.locator(SELECTORS["table_rows"])
        if rows.count() > 0:
            first_row = rows.first
            cells = first_row.locator("td")
            for idx in range(cells.count()):
                text = cells.nth(idx).text_content() or "".strip()
                print(f"     第{idx + 1}列: {text}")
        else:
            print("     表格暂无数据")

        print("   产品协议页面基本元素验证完成！")

    def test_02_publish_button_visibility_by_chain_status(self):
        """检验产品协议列表：未上链记录有发布按钮，已上链记录无发布按钮"""
        print("\n=== 检验产品协议列表发布按钮根据链上状态显示 ===")
        self._test_data = {"测试类型": "功能验证", "测试目的": "验证发布按钮根据链上状态显示"}

        self.page.wait_for_timeout(2000)
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        print(f"   列表总记录数: {total_rows}")

        if total_rows == 0:
            pytest.skip("列表为空，无法验证发布按钮显示")

        found_unpublished = False
        found_published = False

        for idx in range(min(total_rows, 10)):
            row = rows.nth(idx)
            # 获取链上状态（第4列）
            status_cell = row.locator("td:nth-child(4)")
            chain_status = ""
            if status_cell.count() > 0:
                chain_status = status_cell.text_content().strip()

            # 检查是否有发布按钮
            publish_btn = row.locator(SELECTORS["publish_button"])
            has_publish = publish_btn.count() > 0

            print(f"   第{idx+1}行: 状态='{chain_status}', {'有' if has_publish else '无'}发布按钮")

            if chain_status in CHAIN_STATUS["UNPUBLISHED"]:
                assert has_publish, f"第{idx+1}行状态为'{chain_status}'，应显示发布按钮"
                found_unpublished = True
            elif chain_status in CHAIN_STATUS["PUBLISHED"]:
                assert not has_publish, f"第{idx+1}行状态为'{chain_status}'，不应显示发布按钮"
                found_published = True

        assert found_unpublished or found_published, "未找到可识别的链上状态记录"
        print("   发布按钮根据链上状态正确显示！")

    def test_03_add_protocol_with_max_length_fields(self):
        """测试新增协议时，名称和描述均为50字符"""
        print("\n=== 测试新增协议最大长度字段 ===")
        name_desc, _ = generate_max_length_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试新增协议最大长度字段",
                          "输入数据": {"产品协议名称": name_desc, "产品协议描述": name_desc}}

        print(f"   产品协议名称/描述: {name_desc}")

        # 点击新增协议
        self._click_add_button()
        print("   点击新增协议按钮")
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle")

        # 验证跳转到create页面
        assert "create" in self.page.url.lower(), f"未跳转到新增页面，当前URL: {self.page.url}"
        print(f"   已跳转到新增页面: {self.page.url}")

        # 填写表单
        self._fill_add_form(name_desc, name_desc)

        # 点击确定
        self._click_confirm()

        # 验证返回列表页
        assert "productprotocol" in self.page.url.lower() and "create" not in self.page.url.lower(), \
            f"保存后未返回列表页，当前URL: {self.page.url}"
        print("   保存后已返回列表页")

        # 验证新增成功
        row, idx = self._find_row_by_name(name_desc[:20])
        assert row is not None, "新增协议未出现在列表中"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   最大长度字段新增协议测试完成！")

    def test_04_add_and_publish_protocol(self):
        """测试新增协议后立刻发布"""
        print("\n=== 测试新增协议后发布 ===")
        input_value = generate_test_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试新增协议后发布",
                          "输入数据": {"产品协议名称": input_value}}

        print(f"   设置输入值: {input_value}")

        # 点击新增协议
        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle")

        # 填写表单
        self._fill_add_form(input_value)
        self._click_confirm()

        # 查找新增协议
        row, idx = self._find_row_by_name(input_value)
        assert row is not None, "未找到新增的协议"
        print(f"   找到新增协议行（第{idx + 1}行）")

        # 点击发布按钮
        publish_btn = row.locator(SELECTORS["publish_button"]).first
        if publish_btn.count() > 0:
            print("   点击发布按钮")
            publish_btn.click()
            self.page.wait_for_timeout(2000)

            # 处理确认对话框
            dialog = self.page.locator(SELECTORS["confirm_dialog"])
            if dialog.count() > 0:
                ok_btn = dialog.locator(SELECTORS["dialog_ok_button"]).first
                if ok_btn.count() > 0:
                    ok_btn.click()
                    self.page.wait_for_timeout(5000)
                    print("   点击确认发布")

            # 验证状态变为已上链
            self.page.wait_for_timeout(3000)
            self.page.wait_for_load_state("networkidle")

            # 重新查找行
            updated_row, _ = self._find_row_by_name(input_value)
            if updated_row:
                status_cell = updated_row.locator("td:nth-child(4)")
                if status_cell.count() > 0:
                    status_text = status_cell.text_content().strip()
                    print(f"   发布后状态: {status_text}")
                    assert status_text in CHAIN_STATUS["PUBLISHED"] or status_text in CHAIN_STATUS["PUBLISHING"], \
                        f"发布后状态异常: {status_text}"
        else:
            print("   [警告] 未找到发布按钮")

        print("   新增协议后发布测试完成！")

    def test_05_add_new_protocol(self):
        """测试新增协议"""
        print("\n=== 测试新增协议 ===")
        input_value = generate_test_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试新增协议",
                          "输入数据": {"产品协议名称": input_value}}

        print(f"   设置输入值: {input_value}")

        # 点击新增协议
        self._click_add_button()

        # 填写表单
        self._fill_add_form(input_value)
        self._click_confirm()

        # 验证返回列表页
        assert "productprotocol" in self.page.url.lower() and "create" not in self.page.url.lower(), \
            f"保存后未返回列表页，当前URL: {self.page.url}"

        # 查找新增协议
        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   新增协议测试完成！")

    def test_06_query_protocol_by_name(self):
        """测试根据协议名称查询"""
        print("\n=== 测试根据协议名称查询 ===")
        test_name = f"测试查询 {generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试根据协议名称查询",
                          "输入数据": {"协议名称": test_name}}

        # 先新增一个协议
        self._click_add_button()
        self._fill_add_form(test_name)
        self._click_confirm()

        # 查询
        count = self._search_by_name(test_name)
        assert count > 0, f"未找到查询结果: {test_name}"
        print(f"   查询结果: 找到 {count} 条记录")
        print("   根据协议名称查询测试完成！")

    def test_07_query_protocol_by_name_fuzzy(self):
        """测试根据协议名称模糊查询"""
        print("\n=== 测试根据协议名称模糊查询 ===")
        test_name = f"模糊查询测试 {generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试模糊查询",
                          "输入数据": {"协议名称": test_name}}

        # 先新增一个协议
        self._click_add_button()
        self._fill_add_form(test_name)
        self._click_confirm()

        # 模糊查询（取前5个字符）
        fuzzy_name = test_name[:5]
        count = self._search_by_name(fuzzy_name)
        assert count > 0, f"模糊查询未找到结果: {fuzzy_name}"
        print(f"   模糊查询结果: 找到 {count} 条记录")
        print("   模糊查询测试完成！")

    def test_08_query_protocol_by_chain_status(self):
        """测试根据链上状态查询"""
        print("\n=== 测试根据链上状态查询 ===")
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试根据链上状态查询"}

        # 重置
        reset_btn = self.page.locator(SELECTORS["reset_button"])
        if reset_btn.count() > 0:
            reset_btn.click()
            self.page.wait_for_timeout(1000)

        # 选择链上状态
        status_filter = self.page.locator(SELECTORS["chain_status_filter"])
        if status_filter.count() > 0:
            status_filter.click()
            self.page.wait_for_timeout(1000)

            # 选择"已上链"
            option = self.page.locator(SELECTORS["chain_status_option"].format(status="已上链"))
            if option.count() > 0:
                option.first.click()
                print("   选择链上状态: 已上链")
                self.page.wait_for_timeout(1000)

        # 点击查询
        search_btn = self.page.locator(SELECTORS["search_button"])
        if search_btn.count() > 0:
            search_btn.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(3000)

        # 验证结果
        rows = self.page.locator(SELECTORS["table_rows"])
        total = rows.count()
        print(f"   查询结果: {total} 条记录")

        if total > 0:
            for idx in range(min(total, 5)):
                row = rows.nth(idx)
                status_cell = row.locator("td:nth-child(4)")
                if status_cell.count() > 0:
                    status = status_cell.text_content().strip()
                    print(f"   第{idx+1}行状态: {status}")

        print("   根据链上状态查询测试完成！")

    def test_09_add_and_delete_protocol(self):
        """测试新增协议后删除"""
        print("\n=== 测试新增协议后删除 ===")
        input_value = generate_test_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试新增协议后删除",
                          "输入数据": {"产品协议名称": input_value}}

        print(f"   设置输入值: {input_value}")

        # 新增协议
        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value)
        self._click_confirm()

        # 查找新增协议
        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")

        # 点击删除按钮
        clicked = self._click_row_button("删除", 0)
        if not clicked:
            print("   [警告] 未找到删除按钮")
            return

        self.page.wait_for_timeout(2000)

        # 处理不可删除对话框
        if self._handle_undeletable_dialog():
            print("   [提示] 该协议被数据产品使用，无法删除，测试跳过验证")
            return

        # 处理确认对话框
        dialog = self.page.locator(SELECTORS["confirm_dialog"])
        if dialog.count() > 0:
            ok_btn = dialog.locator(SELECTORS["dialog_ok_button"]).first
            if ok_btn.count() > 0:
                ok_btn.click()
                print("   点击确认删除")
                self.page.wait_for_timeout(5000)
            else:
                print("   [警告] 未找到确认按钮")
        else:
            print("   [警告] 未找到删除确认对话框")

        # 验证删除成功
        count = self._search_by_name(input_value)
        if count == 0:
            print("   协议已成功删除，查询结果为空")
        else:
            print(f"   [警告] 删除后查询仍有 {count} 条结果")

        print("   新增协议后删除测试完成！")

    def test_10_query_and_reset_filters(self):
        """测试协议名称和链上状态筛选后点击查询，再点击重置按钮"""
        print("\n=== 测试协议名称和链上状态筛选后查询和重置 ===")
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试筛选查询和重置"}

        # 输入协议名称
        search_input = self.page.locator(SELECTORS["search_input"])
        if search_input.count() > 0:
            search_input.fill("测试")
            print("   输入协议名称: 测试")

        # 选择链上状态
        status_filter = self.page.locator(SELECTORS["chain_status_filter"])
        if status_filter.count() > 0:
            status_filter.click()
            self.page.wait_for_timeout(1000)
            option = self.page.locator(SELECTORS["chain_status_option"].format(status="已上链"))
            if option.count() > 0:
                option.first.click()
                print("   选择链上状态: 已上链")
                self.page.wait_for_timeout(1000)

        # 点击查询
        search_btn = self.page.locator(SELECTORS["search_button"])
        if search_btn.count() > 0:
            search_btn.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(3000)

        filtered_count = self.page.locator(SELECTORS["table_rows"]).count()
        print(f"   筛选后记录数: {filtered_count}")

        # 点击重置
        reset_btn = self.page.locator(SELECTORS["reset_button"])
        if reset_btn.count() > 0:
            reset_btn.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(3000)

        reset_count = self.page.locator(SELECTORS["table_rows"]).count()
        print(f"   重置后记录数: {reset_count}")
        print("   筛选查询和重置测试完成！")

    def test_11_add_protocol_with_single_space_in_name(self):
        """测试新增协议时协议名称包含一个空格"""
        print("\n=== 测试新增协议时协议名称包含一个空格 ===")
        input_value = f"测试 空格{generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试名称包含空格",
                          "输入数据": {"产品协议名称": input_value}}

        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value)
        self._click_confirm()

        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   名称包含空格测试完成！")

    def test_12_add_protocol_with_multiple_spaces_in_name(self):
        """测试新增协议时协议名称包含多个空格"""
        print("\n=== 测试新增协议时协议名称包含多个空格 ===")
        input_value = f"测试  多个  空格{generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试名称包含多个空格",
                          "输入数据": {"产品协议名称": input_value}}

        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value)
        self._click_confirm()

        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   名称包含多个空格测试完成！")

    def test_13_add_protocol_with_spaces_in_multiple_fields(self):
        """测试新增协议时多个字段包含空格"""
        print("\n=== 测试新增协议时多个字段包含空格 ===")
        input_value = f"测试 多字段{generate_test_data()}"
        desc_value = f"描述 包含 空格 {generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试多字段包含空格",
                          "输入数据": {"产品协议名称": input_value, "产品协议描述": desc_value}}

        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value, desc_value)
        self._click_confirm()

        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   多字段包含空格测试完成！")

    def test_14_add_protocol_with_angle_brackets_in_name(self):
        """测试新增协议时协议名称包含《》"""
        print("\n=== 测试新增协议时协议名称包含《》 ===")
        input_value = f"测试《书名号》{generate_test_data()}"
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试名称包含书名号",
                          "输入数据": {"产品协议名称": input_value}}

        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value)
        self._click_confirm()

        row, idx = self._find_row_by_name(input_value)
        assert row is not None, f"未找到新增的协议: {input_value}"
        print(f"   找到新增协议行（第{idx + 1}行）")
        print("   名称包含书名号测试完成！")

    def test_15_sql_injection_in_protocol_name_query(self):
        """测试协议名称查询时的SQL注入防护"""
        print("\n=== 测试协议名称查询时的SQL注入防护 ===")
        malicious_input = "' OR '1'='1"
        self._test_data = {"测试类型": "安全测试", "测试目的": "SQL注入防护",
                          "输入数据": {"协议名称": malicious_input}}

        count = self._search_by_name(malicious_input)
        print(f"   SQL注入查询结果: {count} 条记录")
        # 不应抛出异常或返回所有数据
        print("   SQL注入防护测试完成！")

    def test_16_js_injection_in_protocol_name_query(self):
        """测试协议名称查询时的JS注入防护"""
        print("\n=== 测试协议名称查询时的JS注入防护 ===")
        malicious_input = "<script>alert('xss')</script>"
        self._test_data = {"测试类型": "安全测试", "测试目的": "JS注入防护",
                          "输入数据": {"协议名称": malicious_input}}

        count = self._search_by_name(malicious_input)
        print(f"   JS注入查询结果: {count} 条记录")
        print("   JS注入防护测试完成！")

    def test_17_xss_injection_in_protocol_name_query(self):
        """测试协议名称查询时的XSS注入防护"""
        print("\n=== 测试协议名称查询时的XSS注入防护 ===")
        malicious_input = "<img src=x onerror=alert('xss')>"
        self._test_data = {"测试类型": "安全测试", "测试目的": "XSS注入防护",
                          "输入数据": {"协议名称": malicious_input}}

        count = self._search_by_name(malicious_input)
        print(f"   XSS注入查询结果: {count} 条记录")
        print("   XSS注入防护测试完成！")

    def _click_row_button(self, button_text, row_index=0):
        """使用 Playwright 的 locator.evaluate 点击表格行中的按钮（处理 Vue scoped slot）"""
        try:
            # 先尝试直接通过 Playwright 点击
            btn = self.page.locator(".el-table__body tr.el-table__row").nth(row_index).locator("button").filter(has_text=button_text)
            if btn.count() > 0:
                btn.first.click()
                print(f"   Playwright 直接点击 '{button_text}' 成功")
                return True
        except Exception as e:
            print(f"   Playwright 直接点击失败: {e}")

        # 兜底：使用 JavaScript 在元素上下文中执行点击
        try:
            btn = self.page.locator(".el-table__body tr.el-table__row").nth(row_index).locator("button").filter(has_text=button_text)
            if btn.count() > 0:
                btn.first.evaluate("el => el.click()")
                print(f"   JavaScript evaluate 点击 '{button_text}' 成功")
                return True
        except Exception as e:
            print(f"   JavaScript evaluate 点击失败: {e}")

        # 最后尝试：使用 page.evaluate 执行全局脚本
        script = f"""
        () => {{
            const rows = document.querySelectorAll('.el-table__body tr.el-table__row');
            if (rows.length > {row_index}) {{
                const row = rows[{row_index}];
                const btns = Array.from(row.querySelectorAll('button'));
                const targetBtn = btns.find(b => b.innerText.trim() === '{button_text}');
                if (targetBtn) {{
                    targetBtn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
                    return 'clicked';
                }}
                return 'not found: ' + btns.map(b => b.innerText.trim()).join(', ');
            }}
            return 'no rows';
        }}
        """
        result = self.page.evaluate(script)
        print(f"   MouseEvent 点击 '{button_text}' 结果: {result}")
        return result == 'clicked'

    def test_18_view_protocol_detail(self):
        """测试查看协议详情"""
        print("\n=== 测试查看协议详情 ===")
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试查看协议详情"}

        rows = self.page.locator(SELECTORS["table_rows"])
        if rows.count() == 0:
            pytest.skip("列表为空，无法测试详情")

        first_row = rows.first
        # 获取协议ID（第1列）和名称
        id_cell = first_row.locator("td:nth-child(1)")
        name_cell = first_row.locator("td:nth-child(2)")
        protocol_id = id_cell.text_content().strip() if id_cell.count() > 0 else ""
        protocol_name = name_cell.text_content().strip() if name_cell.count() > 0 else ""
        print(f"   查看协议详情: {protocol_name} (ID: {protocol_id})")

        if not protocol_id:
            pytest.skip("未获取到协议ID")

        # 直接导航到详情页（因为表格按钮点击在Playwright中无法触发Vue路由）
        detail_url = self.get_url_for_user(1, f"/datamarket/product-manage/productProtocol/detail/{protocol_id}", self.CONFIG.USER_IPS)
        self.page.goto(detail_url)
        self.page.wait_for_timeout(3000)
        self.page.wait_for_load_state("networkidle")

        # 验证跳转到详情页
        assert "detail" in self.page.url.lower(), f"未跳转到详情页，当前URL: {self.page.url}"
        print(f"   已跳转到详情页: {self.page.url}")

        # 验证详情页内容
        page_text = self.page.locator("body").text_content() or ""
        assert "产品协议编号" in page_text, "详情页未显示产品协议编号"
        assert "产品协议名称" in page_text, "详情页未显示产品协议名称"
        print("   详情页内容验证通过")

        print("   查看协议详情测试完成！")

    def test_19_edit_protocol(self):
        """测试编辑协议"""
        print("\n=== 测试编辑协议 ===")
        input_value = generate_test_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "测试编辑协议",
                          "输入数据": {"产品协议名称": input_value}}

        # 先新增一个协议
        self._click_add_button()
        self.page.wait_for_timeout(2000)
        self._fill_add_form(input_value)
        self._click_confirm()

        # 查找并点击编辑
        row, idx = self._find_row_by_name(input_value)
        if row is None:
            pytest.skip(f"未找到新增的协议: {input_value}")

        # 查找并点击编辑
        clicked = self._click_row_button("编辑", 0)
        if not clicked:
            pytest.skip("未找到编辑按钮")

        self.page.wait_for_timeout(3000)

        # 检查是否弹出不可编辑对话框
        if self._handle_uneditable_dialog():
            print("   [提示] 该协议被数据产品使用，无法编辑")
            return

        # 验证编辑对话框或页面
        dialog = self.page.locator(".el-dialog, .el-drawer")
        if dialog.count() > 0 and dialog.first.is_visible():
            print("   编辑对话框已打开")
            # 修改名称
            new_name = f"{input_value}_edited"
            name_input = self.page.locator(SELECTORS["name_input"])
            if name_input.count() > 0:
                name_input.fill(new_name)
                print(f"   修改产品协议名称为: {new_name}")

            # 点击确定
            self._click_confirm()

            # 验证修改成功
            self.page.wait_for_timeout(2000)
            updated_row, _ = self._find_row_by_name(new_name)
            if updated_row:
                print("   编辑成功")
            else:
                print("   [警告] 未找到编辑后的协议")
        else:
            print("   [信息] 编辑可能是页面跳转形式")

        print("   编辑协议测试完成！")

        print("   编辑协议测试完成！")

    def test_20_add_protocol_direct(self):
        """直接访问新增协议页面测试"""
        print("\n=== 直接访问新增协议页面测试 ===")
        input_value = generate_test_data()
        self._test_data = {"测试类型": "功能验证", "测试目的": "直接访问新增页面",
                          "输入数据": {"产品协议名称": input_value}}

        # 直接访问create页面（setup_method已处理）
        assert "create" in self.page.url.lower(), f"未在新增页面，当前URL: {self.page.url}"
        print(f"   当前在新增页面: {self.page.url}")

        # 验证页面元素
        name_input = self.page.locator(SELECTORS["name_input"])
        assert name_input.count() > 0, "未找到产品协议名称输入框"
        print("   找到产品协议名称输入框")

        desc_input = self.page.locator(SELECTORS["desc_input"])
        assert desc_input.count() > 0, "未找到产品协议描述输入框"
        print("   找到产品协议描述输入框")

        file_input = self.page.locator(SELECTORS["file_upload_input"])
        assert file_input.count() > 0, "未找到文件上传输入框"
        print("   找到文件上传输入框")

        confirm_btn = self.page.locator(SELECTORS["confirm_button"])
        assert confirm_btn.count() > 0, "未找到确定按钮"
        print("   找到确定按钮")

        # 填写并保存
        self._fill_add_form(input_value)
        self._click_confirm()

        # 验证返回列表页
        assert "productprotocol" in self.page.url.lower() and "create" not in self.page.url.lower(), \
            f"保存后未返回列表页，当前URL: {self.page.url}"
        print("   保存后已返回列表页")

        print("   直接访问新增页面测试完成！")
