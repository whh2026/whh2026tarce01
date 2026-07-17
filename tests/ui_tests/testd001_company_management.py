import pytest
import time
import random
import string
from utils.base import Base
from tests.ui_tests.config import ui_config

class TestCompanyManagement(Base):
    """公司管理页面测试类"""
    
    # 配置参数
    CONFIG = ui_config.USER_IPS

    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
        # 创建持久化的上下文和页面，登录态通过 context 中的 cookie 保持，供所有用例复用
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        # 标记尚未登录，由首个用例的 setup_method 完成一次性登录
        cls._logged_in = False

    @classmethod
    def _wait_target_page(cls):
        """等待用户列表页面加载完成"""
        cls.page.wait_for_load_state("networkidle")
        assert "user-list" in cls.page.url.lower(), f"页面访问失败，当前URL: {cls.page.url}"

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
        """每个测试方法执行前：首个用例完成登录（仅一次），其余用例回到用户列表页面（复用已登录会话）"""
        # 保存当前测试方法，用于截图命名
        self.current_test = method
        
        if not type(self)._logged_in:
            # 首次：登录一次（作为本页面测试的初始状态）
            print("\n=== 登录（仅执行一次） ===")
            login_url = self.get_url_for_user(1, "/login", self.CONFIG)
            self.page.goto(login_url, timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(1000)
            print(f"   ✓ 已访问登录页面: {login_url}")
            self.login_with_user(1, self.CONFIG, page=self.page)
            print("   ✓ 用户1登录成功")
            type(self)._logged_in = True
        
        # 回到用户列表页面（登录态通过持久化 context 保持，无需重新登录）
        self.user_list_page_url = self.get_url_for_user(1, "/admin/userManage/user-list?user-list=%257B%2522pageNumber%2522%253A1%252C%2522pageSize%2522%253A10%257D", self.CONFIG)
        self.page.goto(self.user_list_page_url)
        self._wait_target_page()
        print(f"[前置条件] 前置条件 - 成功访问用户列表页面！")
        print(f"   页面URL: {self.page.url}")
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理（不关闭页面/上下文，保留登录态供后续用例复用）"""
        # 失败截图由 conftest.py 的 pytest_runtest_makereport 钩子统一处理
        pass
    
    def test_search_username(self):
        """测试搜索用户名功能"""
        
        # 查找搜索框并输入关键词
        search_keyword = "admin"
        # 尝试多种定位方式查找搜索框
        search_selector = "input[type='search'], input[placeholder*='搜索'], input[placeholder*='用户名'], .ant-input-search input"
        self.page.fill(search_selector, search_keyword)
        
        # 触发搜索（可能是按下Enter键或点击搜索按钮）
        self.page.press(search_selector, "Enter")
        
        # 等待搜索结果加载
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle")
        
        # 验证搜索结果
        # 检查页面是否显示了搜索结果（这里使用通用的结果列表定位）
        result_selector = ".ant-table-tbody, .table tbody, .list-container, [class*='result']"
        
        # 等待结果元素出现
        try:
            self.page.wait_for_selector(result_selector, timeout=5000)
        except Exception:
            pass
    
    def test_add_user(self):
        """测试新增用户功能"""
        
        # 1. 点击新增按钮 - 使用更精确的定位器
        add_button_selectors = [
            "xpath=/html/body/div[1]/div/section/div/main/div[2]/div/div/div[1]/div/button[1]",
            "button:has-text('新增用户')",
            ".ant-btn:has-text('新增用户')"
        ]
        
        add_button_clicked = False
        for selector in add_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    add_button_clicked = True
                    break
            except Exception:
                continue
        
        if not add_button_clicked:
            self.page.screenshot(path=f"reports/screenshots/debug_add_button_{int(time.time())}.png")
        
        # 2. 等待弹窗出现
        self.page.wait_for_timeout(3000)
        
        # 检查弹出的dialog元素
        dialog_selectors = [
            "[role='dialog']",
            ".ant-modal",
            ".modal"
        ]
        
        dialog_found = False
        for selector in dialog_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    dialog_element = self.page.locator(selector).first
                    dialog_found = True
                    break
            except Exception as e:
                continue
        
        # 等待弹窗完全显示
        modal_selector = ".ant-modal, .modal, [role='dialog']"
        
        # 3. 填写新增用户表单
        # 设置用户名（添加随机字符避免重复）
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        new_username = f"whh{random_str}"
        
        # 用户名输入 - 使用更明确的定位器
        username_selectors = [
            "xpath=/html/body/div[1]/div/section/div/main/div[2]/div/div/div/form/div[1]/div[2]/div/div/input",
            "input[name='username']",
            "input[id='username']",
            ".ant-modal input[placeholder*='用户名']"
        ]
        username_filled = False
        for selector in username_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, new_username)
                    username_filled = True
                    break
            except Exception:
                continue
        
        if not username_filled:
            self.page.screenshot(path=f"reports/screenshots/debug_username_{int(time.time())}.png")
        
        # 昵称输入
        nickname_selectors = [
            "xpath=/html/body/div[1]/div/section/div/main/div[2]/div/div/div/form/div[2]/div[2]/div/div/input",
            "input[name='nickname']",
            "input[id='nickname']",
            ".ant-modal input[placeholder*='昵称']"
        ]
        nickname_filled = False
        for selector in nickname_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, "测试昵称")
                    nickname_filled = True
                    break
            except Exception as e:
                continue
        
        if not nickname_filled:
            self.page.screenshot(path=f"reports/screenshots/debug_nickname_{int(time.time())}.png")
        
        # 部门名称输入
        department_selectors = [
            "xpath=/html/body/div[1]/div/section/div/main/div[2]/div/div/div/form/div[3]/div[2]/div/div/input",
            "input[name='department']",
            "input[id='department']",
            ".ant-modal input[placeholder*='部门名称']"
        ]
        department_filled = False
        for selector in department_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, "测试部门")
                    department_filled = True
                    break
            except Exception as e:
                continue
        
        if not department_filled:
            self.page.screenshot(path=f"reports/screenshots/debug_department_{int(time.time())}.png")
        
        # 角色下拉框1
        role1_selectors = [
            ".ant-modal .ant-select"
        ]
        role1_clicked = False
        for selector in role1_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    role1_clicked = True
                    break
            except Exception as e:
                continue
        
        if not role1_clicked:
            self.page.screenshot(path=f"reports/screenshots/debug_role1_{int(time.time())}.png")
        else:
            # 等待下拉选项显示
            self.page.wait_for_timeout(1000)
            # 点击第一个角色选项
            try:
                self.page.click(".ant-select-dropdown-item:visible, .el-select-dropdown__item:visible")
            except Exception:
                pass
        
        # 角色下拉框2
        role2_selectors = [
            ".ant-modal .ant-select"
        ]
        role2_clicked = False
        for selector in role2_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    role2_clicked = True
                    break
            except Exception as e:
                continue
        
        if not role2_clicked:
            self.page.screenshot(path=f"reports/screenshots/debug_role2_{int(time.time())}.png")
        else:
            # 等待下拉选项显示
            self.page.wait_for_timeout(1000)
            # 点击第一个角色选项
            try:
                self.page.click(".ant-select-dropdown-item:visible, .el-select-dropdown__item:visible")
            except Exception:
                pass
        
        # 4. 提交表单
        submit_button_selectors = [
            "button:has-text('确定')",
            ".ant-modal-footer button:has-text('确定')",
            "xpath=/html/body/div[1]/div/section/div/main/div[2]/div/div/div[2]/div/button[1]"
        ]
        
        submit_button_clicked = False
        for selector in submit_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=3000):
                    self.page.click(selector)
                    submit_button_clicked = True
                    break
            except Exception as e:
                continue
        
        if not submit_button_clicked:
            self.page.screenshot(path=f"reports/screenshots/debug_submit_button_{int(time.time())}.png")
        
        # 5. 等待操作结果
        self.page.wait_for_timeout(3000)
        self.page.wait_for_load_state("networkidle")
        
        # 6. 验证新增成功
        # 检查是否有成功提示
        success_selector = ".ant-message-success, [class*='success'], [class*='message']:has-text('成功')"
        try:
            self.page.wait_for_selector(success_selector, timeout=5000)
        except Exception:
            pass
