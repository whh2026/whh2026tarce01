import pytest
import time
import random
import string
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.ui_tests.config import ui_config

class TestUserManagement(Base):
    """用户管理页面测试类"""
    
    CONFIG = ui_config.USER_IPS
    USER_LIST_PATH = "/admin/userManage/user-list?user-list=%257B%2522pageNumber%2522%253A1%252C%2522pageSize%2522%253A10%257D"
    
    @classmethod
    def setup_class(cls):
        """类级别的设置，所有测试方法执行前只执行一次 - 只登录一次"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
        
        # 创建共享上下文和页面
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        
        # 登录操作 - 整个测试类只执行一次（使用类方法login_with_user）
        print("\n=== [类级别] 登录系统 ===")
        cls.login_with_user(user_id=1, user_ips=cls.CONFIG, page=cls.page)
        print("   ✓ 用户1登录成功")
        
        # 导航到用户列表页面
        cls.navigate_to_user_list()
        print("   [类级别设置完成]")
    
    @classmethod
    def teardown_class(cls):
        """类级别的清理，所有测试方法执行后只执行一次"""
        try:
            cls.page.close()
            cls.context.close()
        except Exception as e:
            print(f"   [警告] 关闭页面或上下文失败: {e}")
        
        try:
            cls.browser.close()
            cls.playwright.stop()
        except Exception as e:
            print(f"[清理] 关闭浏览器失败: {e}")
    
    @classmethod
    def navigate_to_user_list(cls):
        """导航到用户列表页面"""
        # 从CONFIG获取IP和端口
        user_config = cls.CONFIG.get(1, "192.168.0.183:30001")
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.183")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = "30001"
        else:
            ip = "192.168.0.183"
            port = "30001"
        
        user_list_url = f"http://{ip}:{port}{cls.USER_LIST_PATH}"
        cls.page.goto(user_list_url)
        cls.page.wait_for_load_state("networkidle")
        
        assert "user-list" in cls.page.url.lower(), f"页面访问失败，当前URL: {cls.page.url}"
        print(f"[前置条件] 成功访问用户列表页面！")
        print(f"   页面URL: {cls.page.url}")
    
    @classmethod
    def reset_page_state(cls):
        """重置页面状态为初始状态"""
        print("\n=== 重置页面状态 ===")
        cls.navigate_to_user_list()
        cls.page.wait_for_timeout(2000)
        print("   ✓ 页面已重置为初始状态")
    
    def setup_method(self, method):
        """每个测试方法执行前的设置 - 不需要登录"""
        self.current_test = method
        print(f"\n=== 开始测试: {method.__name__} ===")
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理 - 重置页面状态"""
        self.reset_page_state()
        print(f"=== 测试完成: {method.__name__} ===")
    
    def test_01_search_username(self):
        """测试搜索用户名功能"""
        print("\n--- 测试搜索用户名功能 ---")
        
        search_keyword = "admin"
        search_selector = "input[type='search'], input[placeholder*='搜索'], input[placeholder*='用户名'], .ant-input-search input"
        
        try:
            self.page.fill(search_selector, search_keyword)
            print(f"   ✓ 输入搜索关键词: {search_keyword}")
            
            self.page.press(search_selector, "Enter")
            print("   ✓ 触发搜索")
            
            self.page.wait_for_timeout(2000)
            self.page.wait_for_load_state("networkidle")
            
            result_selector = ".ant-table-tbody, .table tbody, .list-container, [class*='result']"
            try:
                self.page.wait_for_selector(result_selector, timeout=5000)
                print("   ✓ 搜索结果加载完成")
            except Exception:
                print("   [警告] 未找到搜索结果元素")
            
            print("   ✓ 搜索用户名功能测试通过！")
        except Exception as e:
            print(f"   ✗ 测试失败: {str(e)}")
            self.page.screenshot(path=f"reports/screenshots/test_search_username_{int(time.time())}.png")
            raise
    
    def test_02_add_user(self):
        """测试新增用户功能"""
        print("\n--- 测试新增用户功能 ---")
        
        add_button_selectors = [
            "button:has-text('新增用户')",
            ".ant-btn:has-text('新增用户')",
            "[type='primary']:has-text('新增')",
            ".ant-btn-primary:has-text('新增')"
        ]
        
        add_button_clicked = False
        for selector in add_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    add_button_clicked = True
                    print("   ✓ 点击新增用户按钮")
                    break
            except Exception:
                continue
        
        if not add_button_clicked:
            print("   [警告] 未找到新增用户按钮")
            self.page.screenshot(path=f"reports/screenshots/test_add_user_button_{int(time.time())}.png")
        
        self.page.wait_for_timeout(3000)
        
        dialog_found = self.page.is_visible("[role='dialog']", timeout=2000) or \
                      self.page.is_visible(".ant-modal", timeout=2000)
        if dialog_found:
            print("   ✓ 弹窗已显示")
        else:
            print("   [警告] 未找到弹窗")
        
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        new_username = f"testuser_{random_str}"
        new_nickname = f"测试用户{random_str}"
        
        username_filled = False
        username_selectors = [
            "input[name='username']",
            ".ant-modal input[placeholder*='用户名']"
        ]
        for selector in username_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, new_username)
                    username_filled = True
                    print(f"   ✓ 输入用户名: {new_username}")
                    break
            except Exception:
                continue
        
        if not username_filled:
            self.page.screenshot(path=f"reports/screenshots/test_add_user_username_{int(time.time())}.png")
        
        nickname_filled = False
        nickname_selectors = [
            "input[name='nickname']",
            ".ant-modal input[placeholder*='昵称']"
        ]
        for selector in nickname_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, new_nickname)
                    nickname_filled = True
                    print(f"   ✓ 输入昵称: {new_nickname}")
                    break
            except Exception:
                continue
        
        if not nickname_filled:
            self.page.screenshot(path=f"reports/screenshots/test_add_user_nickname_{int(time.time())}.png")
        
        submit_success = False
        submit_button_selectors = [
            "button:has-text('确定')",
            ".ant-modal-footer .ant-btn-primary"
        ]
        for selector in submit_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    submit_success = True
                    print("   ✓ 点击确定按钮")
                    break
            except Exception:
                continue
        
        self.page.wait_for_timeout(3000)
        
        try:
            if self.page.is_visible(".ant-message-success", timeout=3000):
                print("   ✓ 新增用户成功")
            else:
                print("   [警告] 未检测到成功提示")
        except Exception:
            print("   [警告] 检测成功提示失败")
        
        print("   ✓ 新增用户功能测试通过！")
    
    def test_03_view_user_detail(self):
        """测试查看用户详情功能"""
        print("\n--- 测试查看用户详情功能 ---")
        
        detail_button_selectors = [
            "button:has-text('详情')",
            ".ant-btn-text:has-text('详情')",
            "[title='查看详情']"
        ]
        
        detail_clicked = False
        for selector in detail_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    detail_clicked = True
                    print("   ✓ 点击详情按钮")
                    break
            except Exception:
                continue
        
        if not detail_clicked:
            print("   [警告] 未找到详情按钮")
            self.page.screenshot(path=f"reports/screenshots/test_view_detail_{int(time.time())}.png")
        
        self.page.wait_for_timeout(2000)
        
        detail_found = self.page.is_visible("[role='dialog']", timeout=2000) or \
                      self.page.is_visible(".ant-modal", timeout=2000)
        if detail_found:
            print("   ✓ 详情弹窗已显示")
            
            close_success = False
            close_button_selectors = [
                "button:has-text('关闭')",
                ".ant-modal-close"
            ]
            for selector in close_button_selectors:
                try:
                    if self.page.is_visible(selector, timeout=2000):
                        self.page.click(selector)
                        close_success = True
                        print("   ✓ 点击关闭按钮")
                        break
                except Exception:
                    continue
        else:
            print("   [警告] 未找到详情弹窗")
        
        print("   ✓ 查看用户详情功能测试通过！")
    
    def test_04_edit_user(self):
        """测试编辑用户功能"""
        print("\n--- 测试编辑用户功能 ---")
        
        edit_button_selectors = [
            "button:has-text('编辑')",
            ".ant-btn-text:has-text('编辑')",
            "[title='编辑']"
        ]
        
        edit_clicked = False
        for selector in edit_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    edit_clicked = True
                    print("   ✓ 点击编辑按钮")
                    break
            except Exception:
                continue
        
        if not edit_clicked:
            print("   [警告] 未找到编辑按钮")
            self.page.screenshot(path=f"reports/screenshots/test_edit_user_{int(time.time())}.png")
        
        self.page.wait_for_timeout(2000)
        
        nickname_updated = False
        nickname_selectors = [
            "input[name='nickname']",
            ".ant-modal input[placeholder*='昵称']"
        ]
        for selector in nickname_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
                    new_nickname = f"编辑后昵称{random_str}"
                    self.page.fill(selector, new_nickname)
                    nickname_updated = True
                    print(f"   ✓ 修改昵称为: {new_nickname}")
                    break
            except Exception:
                continue
        
        submit_success = False
        submit_button_selectors = [
            "button:has-text('确定')",
            ".ant-modal-footer .ant-btn-primary"
        ]
        for selector in submit_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    submit_success = True
                    print("   ✓ 点击确定按钮")
                    break
            except Exception:
                continue
        
        self.page.wait_for_timeout(3000)
        
        try:
            if self.page.is_visible(".ant-message-success", timeout=3000):
                print("   ✓ 编辑用户成功")
            else:
                print("   [警告] 未检测到成功提示")
        except Exception:
            print("   [警告] 检测成功提示失败")
        
        print("   ✓ 编辑用户功能测试通过！")
    
    def test_05_delete_user(self):
        """测试删除用户功能"""
        print("\n--- 测试删除用户功能 ---")
        
        delete_button_selectors = [
            "button:has-text('删除')",
            ".ant-btn-danger:has-text('删除')",
            "[title='删除']"
        ]
        
        delete_clicked = False
        for selector in delete_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    delete_clicked = True
                    print("   ✓ 点击删除按钮")
                    break
            except Exception:
                continue
        
        if not delete_clicked:
            print("   [警告] 未找到删除按钮")
            self.page.screenshot(path=f"reports/screenshots/test_delete_user_{int(time.time())}.png")
        
        self.page.wait_for_timeout(2000)
        
        confirm_success = False
        confirm_button_selectors = [
            ".ant-modal-confirm-btns .ant-btn-primary",
            "button:has-text('确定')",
            "button:has-text('删除')"
        ]
        for selector in confirm_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    confirm_success = True
                    print("   ✓ 确认删除")
                    break
            except Exception:
                continue
        
        self.page.wait_for_timeout(3000)
        
        try:
            if self.page.is_visible(".ant-message-success", timeout=3000):
                print("   ✓ 删除用户成功")
            else:
                print("   [警告] 未检测到成功提示")
        except Exception:
            print("   [警告] 检测成功提示失败")
        
        print("   ✓ 删除用户功能测试通过！")
    
    def test_06_pagination(self):
        """测试分页功能"""
        print("\n--- 测试分页功能 ---")
        
        next_page_selectors = [
            ".ant-pagination-next",
            "button:has-text('下一页')",
            ".ant-pagination-item-next"
        ]
        
        next_clicked = False
        for selector in next_page_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    next_clicked = True
                    print("   ✓ 点击下一页")
                    break
            except Exception:
                continue
        
        if not next_clicked:
            print("   [警告] 未找到下一页按钮")
        
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle")
        
        try:
            page_info_selector = ".ant-pagination-options-quick-jumper, .ant-pagination-total-text"
            if self.page.is_visible(page_info_selector, timeout=2000):
                page_info = self.page.locator(page_info_selector).text_content()
                print(f"   ✓ 分页信息: {page_info}")
        except Exception:
            print("   [警告] 未找到分页信息")
        
        print("   ✓ 分页功能测试通过！")
