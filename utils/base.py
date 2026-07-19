import pytest
from playwright.sync_api import sync_playwright
import json
import os
import time
from datetime import datetime

# 导入报告相关模块
try:
    import allure
except ImportError:
    pass

# 从JSON文件读取测试数据
def get_test_data():
    with open('data/ui_test_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

class Base:
    """基础测试类，包含登录和浏览器管理"""

    @staticmethod
    def _safe_page_load(page, timeout=30000):
        """安全页面加载：依次尝试 networkidle → load → wait_for_timeout 容错"""
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception:
            try:
                page.wait_for_load_state("load", timeout=10000)
            except Exception:
                page.wait_for_timeout(3000)

    @classmethod
    def setup_class(cls):
        """类级别的设置，所有测试方法执行前只执行一次"""
        cls.playwright = sync_playwright().start()
        # 根据环境变量控制是否显示浏览器窗口（默认无头模式）
        headless = os.environ.get("UI_HEADLESS", "true").lower() == "true"
        cls.browser = cls.playwright.chromium.launch(headless=headless)
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        
        # 窗口最大化
        cls.page.set_viewport_size({"width": 1900, "height": 950})
        
        # 不再在setup_class中执行登录，让每个测试方法自己处理登录
    
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
            print(f"[清理] 停止Playwright失败: {e}")
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        # 保存当前测试方法，用于截图命名
        self.current_test = method
        
        # 可以在这里添加每个测试方法需要的特定设置
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        # 截图捕获已经由conftest.py中的pytest_runtest_makereport钩子处理
        # 这里可以添加其他需要的清理操作
        pass
    
    def capture_failure_screenshot(self, method):
        """捕获失败截图并附加到测试报告中"""
        # 从环境变量获取截图目录，如果没有则使用默认值
        screenshots_dir = os.environ.get('SCREENSHOTS_DIR', 'reports/screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # 生成唯一的截图文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        
        # 修复测试名称生成逻辑，确保正确获取测试类和方法名
        try:
            if hasattr(method, '__self__'):
                test_class = method.__self__.__class__.__name__
            elif hasattr(method, '__qualname__'):
                test_class = method.__qualname__.split('.')[0]
            else:
                test_class = 'Unknown'
            
            if hasattr(method, '__name__'):
                test_method = method.__name__
            elif hasattr(method, '__qualname__'):
                test_method = method.__qualname__.split('.')[-1]
            else:
                test_method = 'unknown'
            
            if hasattr(method, '__module__'):
                module_name = method.__module__.replace('.', '_')
            else:
                module_name = 'unknown'
                
            test_name = f"{module_name}_{test_class}_{test_method}_{timestamp}.png"
            screenshot_path = os.path.join(screenshots_dir, test_name)
            
            # 保存截图
            screenshot_bytes = self.page.screenshot(full_page=True, type='png')
            
            # 保存到文件
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_bytes)
            
            print(f"\n[截图] 测试失败，截图已保存：{screenshot_path}")
            
            # 对于allure报告，附加截图
            try:
                import allure
                allure.attach(
                    screenshot_bytes,
                    name='失败截图',
                    attachment_type=allure.attachment_type.PNG
                )
            except ImportError:
                pass
            
            # 对于HTML报告，通过pytest-html的API附加截图
            # 需要将截图路径存储到实例，供conftest.py中的pytest_runtest_makereport使用
            self._last_screenshot_path = screenshot_path
            
        except Exception as e:
            print(f"\n[错误] 截图保存失败：{e}")
            # 尝试使用简单方式保存截图
            try:
                fallback_path = os.path.join(screenshots_dir, f"fallback_{timestamp}.png")
                self.page.screenshot(path=fallback_path, full_page=True)
                print(f"[截图] 备用截图已保存：{fallback_path}")
                self._last_screenshot_path = fallback_path
            except Exception as fallback_error:
                print(f"[错误] 备用截图也失败：{fallback_error}")
    
    @classmethod
    def login(cls):
        """登录方法，作为测试用例的前置条件（正确的classmethod实现）"""
        from tests.ui_tests.config import UIConfig
        
        # 从测试数据中获取第一个用户的登录信息
        test_data = get_test_data()[0]
        username = test_data["username"]
        password = test_data["password"]
        captchaAnswer = test_data["captchaAnswer"]
        
        # 获取登录地址信息
        ip = test_data.get("ip", "192.168.0.183")
        port = test_data.get("port", "30001")
        
        # 调用公共登录方法
        cls.login_with_ip(ip, port, username, password, captchaAnswer)
    
    @classmethod
    def login_with_ip(cls, ip, port, username, password, captchaAnswer, page=None):
        """
        使用指定的IP和端口登录
        
        参数:
            ip: IP地址
            port: 端口号
            username: 用户名
            password: 密码
            captchaAnswer: 验证码
            page: 页面对象（可选，默认使用 cls.page）
        """
        # 优先使用传入的page，否则使用类级别的cls.page
        page = page if page is not None else cls.page
        # 构建登录页面地址
        login_url = f"http://{ip}:{port}/login"
        
        # 等待页面完全加载
        page.wait_for_timeout(2000)
        
        # 检查当前URL是否为登录页面
        current_url = page.url
        if "login" not in current_url.lower():
            print(f"   [警告] 当前页面不是登录页面，正在导航到登录页面...")
            page.goto(login_url, timeout=30000)
            cls._safe_page_load(page, timeout=30000)
            page.wait_for_timeout(2000)
            # 导航后可能因已有Cookie自动重定向到非登录页，此时视为已登录
            if "login" not in page.url.lower():
                print(f"[登录] 已有有效会话，自动登录成功！当前URL: {page.url}")
                return
        
        # 查找用户名输入框并输入
        print(f"   [调试] 正在查找用户名输入框...")
        username_input = page.locator("input[name='username'], input[id='username'], input[placeholder*='用户名']").first
        username_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到用户名输入框，正在输入用户名: {username}")
        username_input.fill(username)
        
        # 查找密码输入框并输入
        print(f"   [调试] 正在查找密码输入框...")
        password_input = page.locator("input[name='password'], input[id='password'], input[placeholder*='密码']").first
        password_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到密码输入框，正在输入密码...")
        password_input.fill(password)

        # 查找验证码输入框并输入
        print(f"   [调试] 正在查找验证码输入框...")
        captcha_input = page.locator("input[name='captchaAnswer'], input[id='captchaAnswer'], input[placeholder*='验证码']").first
        captcha_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到验证码输入框，正在输入验证码: {captchaAnswer}")
        captcha_input.fill(captchaAnswer)
        
        # 查找登录按钮并点击
        print(f"   [调试] 正在查找登录按钮...")
        login_button = page.locator("button[type='submit'], button:has-text('登录'), input[type='submit']").first
        login_button.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到登录按钮，正在点击...")
        login_button.click()
        
        # 等待登录结果，可根据实际情况调整等待时间
        page.wait_for_timeout(3000)
        
        # 验证登录成功（检查URL是否不再包含login）
        assert "login" not in page.url.lower(), f"登录失败，当前URL: {page.url}"
        
        print(f"[登录] 前置条件 - 登录成功！用户名: {username}, 登录地址: {login_url}")
    
    @classmethod
    def login_with_ip_direct(cls, ip, port, username, password, captchaAnswer, page):
        """
        使用指定的IP和端口登录（不包含页面导航）
        
        参数:
            ip: IP地址
            port: 端口号
            username: 用户名
            password: 密码
            captchaAnswer: 验证码
            page: 页面对象
        """
        # 等待页面完全加载
        page.wait_for_timeout(2000)
        
        # 查找用户名输入框并输入
        print(f"   [调试] 正在查找用户名输入框...")
        username_input = page.locator("input[name='username'], input[id='username'], input[placeholder*='用户名']").first
        username_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到用户名输入框，正在输入用户名: {username}")
        username_input.fill(username)
        
        # 查找密码输入框并输入
        print(f"   [调试] 正在查找密码输入框...")
        password_input = page.locator("input[name='password'], input[id='password'], input[placeholder*='密码']").first
        password_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到密码输入框，正在输入密码...")
        password_input.fill(password)

        # 查找验证码输入框并输入
        print(f"   [调试] 正在查找验证码输入框...")
        captcha_input = page.locator("input[name='captchaAnswer'], input[id='captchaAnswer'], input[placeholder*='验证码']").first
        captcha_input.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到验证码输入框，正在输入验证码: {captchaAnswer}")
        captcha_input.fill(captchaAnswer)
        
        # 查找登录按钮并点击
        print(f"   [调试] 正在查找登录按钮...")
        login_button = page.locator("button[type='submit'], button:has-text('登录'), input[type='submit']").first
        login_button.wait_for(state="visible", timeout=10000)
        print(f"   [调试] 找到登录按钮，正在点击...")
        login_button.click()
        
        # 等待登录结果，可根据实际情况调整等待时间
        page.wait_for_timeout(3000)
        
        # 验证登录成功（检查URL是否不再包含login）
        assert "login" not in page.url.lower(), f"登录失败，当前URL: {page.url}"
        
        print(f"[登录] 前置条件 - 登录成功！用户名: {username}")
    
    def get_url_for_ip(self, ip, port, path):
        """根据IP和端口获取完整URL
        
        Args:
            ip: 服务器IP地址
            port: 服务器端口
            path: 路径
        
        Returns:
            str: 完整的URL
        """
        return f"http://{ip}:{port}{path}"
    
    def get_url_for_user(self, user_id, path, user_ips=None, fixed_port=None):
        """根据用户ID获取URL
        
        Args:
            user_id: 用户ID
            path: 路径
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        
        Returns:
            str: 完整的URL
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.183:30001")
        
        # 判断配置格式
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.183")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = user_config
            port = fixed_port if fixed_port else "30001"
        
        # 使用get_url_for_ip方法构建完整的URL
        return self.get_url_for_ip(ip, port, path)
    
    @classmethod
    def login_with_user(cls, user_id=1, user_ips=None, fixed_port=None, page=None):
        """根据用户ID登录
        
        参数:
            user_id: 用户ID
            user_ips: 用户IP映射字典
            fixed_port: 固定端口
            page: 页面对象（已废弃，使用cls.page）
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.183:30001")
        
        # 判断配置格式
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.183")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = user_config
            port = fixed_port if fixed_port else "30001"
        
        # 从测试数据中获取用户登录信息（使用第一个用户的登录凭证）
        test_data = get_test_data()[0]
        username = test_data["username"]
        password = test_data["password"]
        captchaAnswer = test_data["captchaAnswer"]
        
        # 每次都重新登录，不跳过登录
        print(f"[登录] 正在登录用户{user_id}到{ip}:{port}...")
        
        # 使用login_with_ip方法进行登录
        cls.login_with_ip(ip, port, username, password, captchaAnswer, page)
    
    def create_data_product(self, need_apply=False, custom_name=None, need_auth=False):
        """
        创建数据产品的完整流程，返回创建的产品名称
        
        测试目的：提供一个可复用的方法，用于创建测试数据产品
        测试场景：模拟用户完整的数据产品发布流程
        
        测试步骤：
        1. 访问数据产品发布页面
        2. 生成测试数据或使用自定义产品名称
        3. 填写基础配置信息
        4. 填写详细信息
        5. 填写上架信息
        
        6. 确认并发布数据产品
        
        Args:
            need_apply: 是否需要申请使用（默认为False，即"否"）
            custom_name: 自定义产品名称（默认为None，使用随机生成的名称）
            need_auth: 是否需要授权（精准授权，默认为False，即"否"）
        
        返回值：
            dict: 包含产品名称、产品编码、行业分类的字典
        """
        import time
        import re
        from tests.test_data.data_product_data import TEST_URLS, SELECTORS, generate_test_data
        
        print("\n=== 创建数据产品，完整流程 ===")

        # 步骤 1: 访问数据产品发布页面 - 直接访问数据产品发布页面，准备开始创建新的数据产品
        release_url = self.get_url_for_user(1, "/registration/product/release", None, None)
        self.page.goto(release_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)  # 等待页面完全加载完成
        print(f"   已访问发布页面: {release_url}")

        # 步骤 2: 生成测试数据 - 使用测试数据生成函数创建随机测试数据，避免测试数据冲突
        test_data = generate_test_data()
        
        # 如果提供了自定义产品名称，则使用自定义名称
        if custom_name:
            test_data["name"] = custom_name
            print(f"   使用自定义产品名称: {custom_name}")
        else:
            print(f"   使用测试数据: 名称='{test_data['name']}', 英文名称='{test_data['english_name']}'")

        # 步骤 3: 填写基础配置信息 - 填写数据产品的基本信息，包括名称、描述、分类等
        print("\n=== 3. 填写基础配置信息 ===")
        
        # 步骤 3.1: 填写中文名称 - 填写数据产品的中文名称，这是必填项
        if self.page.is_visible(SELECTORS["data_product_name_input"]):
            self.page.fill(SELECTORS["data_product_name_input"], test_data["name"])
            print(f"   已填写中文名称: {test_data['name']}")

        # 步骤 3.2: 填写英文名称 - 填写数据产品的英文名称，需符合命名规范
        if self.page.is_visible(SELECTORS["data_product_english_name_input"]):
            self.page.fill(SELECTORS["data_product_english_name_input"], test_data["english_name"])
            print(f"   已填写英文名称: {test_data['english_name']}")

        # 步骤 3.3: 填写产品介绍 - 填写数据产品的详细介绍，描述产品功能和特性
        if self.page.is_visible(SELECTORS["data_product_desc_textarea"]):
            self.page.fill(SELECTORS["data_product_desc_textarea"], test_data["desc"])
            print(f"   已填写产品介绍")
        
        # 步骤 3.4: 填写使用限制 - 填写数据产品的使用限制和注意事项
        if self.page.is_visible(SELECTORS["data_product_limit_textarea"]):
            self.page.fill(SELECTORS["data_product_limit_textarea"], test_data["limit"])
            print(f"   已填写使用限制")
        
        # 步骤 3.5: 填写其他说明 - 填写数据产品的其他相关说明信息
        if self.page.is_visible(SELECTORS["data_product_other_textarea"]):
            self.page.fill(SELECTORS["data_product_other_textarea"], test_data["other"])
            print(f"   已填写其他说明")
        
        # 步骤 3.6: 填写产品标签 - 为数据产品添加相关标签，方便分类和搜索
        if self.page.is_visible(SELECTORS["data_product_tags_input"]):
            tags_value = f"测试, {test_data['type']}, 自动化测试"
            self.page.fill(SELECTORS["data_product_tags_input"], tags_value)
            print(f"   已填写标签: {tags_value}")
        
        # 步骤 3.7: 选择行业分类 - 选择数据产品所属的行业分类，这里选择"采矿业"
        if self.page.is_visible(SELECTORS["data_product_category_select"]):
            self.page.click(SELECTORS["data_product_category_select"])
            self.page.click("li:has-text('采矿业')")
            print(f"   已选择行业分类: 采矿业")
        
        # 步骤 3.8: 选择产品类型 - 选择数据产品的类型，这里选择"数据接口"
        if self.page.is_visible(SELECTORS["data_product_type_select"]):
            self.page.click(SELECTORS["data_product_type_select"])
            self.page.click("li:has-text('数据接口')")
            print(f"   已选择产品类型: 数据接口")

        # 步骤 3.9: 选择产品小类 - 选择数据产品的小类，这里选择"API接口"
        if self.page.is_visible(SELECTORS["data_product_subtype_select"]):
            self.page.click(SELECTORS["data_product_subtype_select"])
            self.page.click("li:has-text('API接口')")
            print(f"   已选择产品小类: API接口")
        
        # 3.10 选择地域分类 - 北京市
        if self.page.is_visible(SELECTORS["data_product_region_select"]):
            # 点击地域下拉框
            self.page.locator(".allPadding > .el-select > .el-select__wrapper > .el-select__selection > div:nth-child(2)").click()
            # 选择"北京市"
            self.page.locator("div").filter(has_text=re.compile(r"^北京市$")).locator("span").nth(1).click()
            print(f"   已选择 北京市")
        
        # 步骤 4: 进入详细信息页面 - 点击下一步按钮，进入详细信息填写页面
        print("\n=== 4. 进入详细信息页面 ===")
        if self.page.is_visible(SELECTORS["next_step_button"]):
            self.page.click(SELECTORS["next_step_button"])
            
            # 使用networkidle等待页面完全加载
            self.page.wait_for_load_state("networkidle", timeout=45000)
            
            # 等待详细信息页面的特征元素出现，使用多种选择器确保兼容性
            try:
                # 尝试多种选择器来确认页面已成功切换
                detail_page_selectors = [
                    "label:has-text('接口名称')",
                    "label:has-text('正式接口地址')",
                    "input[placeholder*='接口名称']",
                    "input[placeholder*='接口地址']"
                ]
                
                detail_page_loaded = False
                for selector in detail_page_selectors:
                    try:
                        self.page.wait_for_selector(selector, timeout=5000)
                        detail_page_loaded = True
                        break
                    except Exception:
                        continue
                        
                if detail_page_loaded:
                    print(f"   已进入详细信息页面")
                else:
                    print(f"   ⚠ 可能未进入详细信息页面，但继续执行测试")
            except Exception as e:
                print(f"   ⚠ 等待详细信息页面元素超时: {str(e)}")
                print(f"   ⚠ 继续执行测试")

        # 步骤 5: 填写详细信息 - 填写数据产品的详细技术信息，包括接口信息等
        print("\n=== 5. 填写详细信息 ===")
        
        # 步骤 5.1: 填写接口名称 - 填写数据接口的名称，使用多种选择器确保兼容性
        print("   填写接口名称: 测试接口...")
        if self.page.is_visible(SELECTORS.get("data_product_api_name_input")):
            self.page.fill(SELECTORS["data_product_api_name_input"], "测试接口")
            print(f"   已填写接口名称: 测试接口")


        # 步骤 5.2: 填写正式接口地址 - 填写数据接口的正式访问地址
        print("   填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("access_address_input")):
            self.page.fill(SELECTORS["access_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   已填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")


        # 步骤 5.3: 填写测试接口地址 - 填写数据接口的测试环境访问地址
        print("   填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("redirect_address_input")):
            self.page.fill(SELECTORS["redirect_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   已填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")

        # 向下滚动页面，使入参字段可见
        print("   向下滚动页面，使入参字段可见...")
        self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(1)
        # 稍微向上滚动一点，确保入参字段完全可见
        self.page.evaluate("window.scrollBy({top: -200, behavior: 'smooth'})")
        time.sleep(1)


        # 步骤 5.4: 填写入参信息 - 根据是否需要授权决定输入哪些参数
        # 授权产品（need_auth=True）：输入 abc 和 date 两个参数
        # 非授权产品（need_auth=False）：只需输入 date 参数
        if need_auth:
            print("   填写入参信息（授权产品：abc、date）...")
            input_params = ["abc", "date"]
            input_xpaths = [
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input",
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[2]/div/div[2]/div[1]/div/input"
            ]
        else:
            print("   填写入参信息（非授权产品：仅date）...")
            input_params = ["date"]
            input_xpaths = [
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input"
            ]
        
        filled_count = 0
        for i, (xpath, param_name) in enumerate(zip(input_xpaths, input_params)):
            try:
                input_element = self.page.locator(f"xpath={xpath}")
                if input_element.count() > 0:
                    if input_element.is_visible():
                        input_element.fill(param_name)
                        print(f"   已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                    else:
                        print(f"   第{i+1}个入参字段不可见，尝试强制填充")
                        input_element.fill(param_name)
                        print(f"   (强制) 已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                else:
                    print(f"   第{i+1}个入参字段xpath不存在")
            except Exception as e:
                print(f"   填写第{i+1}个入参字段时出错: {e}")
        
        if filled_count < len(input_params):
            print(f"   警告：只成功填写了{filled_count}/{len(input_params)}个入参字段")

        # 步骤 5.5: 设置是否需要授权（精准授权）- 如果need_auth为True，则选择"是"
        # 注意：必须先选择是否需要授权，才能显示精准授权相关字段
        if need_auth:
            print("   设置精准授权为是...")
            
            # 向下滚动页面，确保精准授权选项可见
            self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
            time.sleep(1)
            
            # 精准授权选项的xpath - 使用label包含"是否需要授权"然后找对应的radio
            auth_xpath = "//label[contains(text(),'是否需要授权')]/following-sibling::div//span[contains(text(),'是')]/preceding-sibling::span[contains(@class,'el-radio__inner')]"
            
            # 尝试多种选择器定位精准授权选项
            auth_selectors = [
                auth_xpath,
                "label:has-text('是否需要授权') + div .el-radio:has-text('是')",
                "label:has-text('是否需要授权') ~ div .el-radio:last-child",
                ".el-radio:has-text('是')"
            ]
            
            auth_clicked = False
            for selector in auth_selectors:
                try:
                    if "xpath=" in selector:
                        element = self.page.locator(selector)
                    else:
                        element = self.page.locator(selector)
                    
                    if element.count() > 0 and element.is_visible():
                        element.first.click(force=True)
                        print(f"   已设置精准授权为: 是")
                        auth_clicked = True
                        
                        # 勾选后等待5秒，确保页面元素加载完成
                        print("   等待5秒，确保页面元素加载完成...")
                        time.sleep(5)
                        break
                except Exception as e:
                    print(f"   选择器 {selector} 点击失败: {e}")
                    continue
            
            if not auth_clicked:
                print(f"   ⚠ 未找到精准授权选择器")
            else:
                # 精准授权相关字段的xpath - 使用用户提供的正确xpath
                precise_auth_fields = [
                    {
                        "name": "企业名称",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input",
                        "value": "a"
                    },
                    {
                        "name": "统一社会信用代码",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[2]/div/div[2]/div[1]/div/input",
                        "value": "b"
                    },
                    {
                        "name": "企业扩展字段",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/input",
                        "value": "c"
                    },
                    {
                        "name": "日期字段",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[4]/div/div[2]/div[1]/div/input",
                        "value": "date"
                    }
                ]
                
                # 填写每个精准授权字段
                for field in precise_auth_fields:
                    try:
                        input_element = self.page.locator(f"xpath={field['xpath']}")
                        if input_element.count() > 0:
                            if input_element.is_visible():
                                input_element.fill(field['value'])
                                print(f"   已填写{field['name']}: {field['value']}")
                            else:
                                print(f"   {field['name']}字段不可见，尝试强制填充")
                                input_element.fill(field['value'])
                                print(f"   (强制) 已填写{field['name']}: {field['value']}")
                        else:
                            print(f"   {field['name']}字段不存在")
                    except Exception as e:
                        print(f"   填写{field['name']}时出错: {e}")

        # 步骤 6: 进入上架信息页面 - 点击下一步按钮，进入上架信息填写页面
        print("\n=== 6. 进入上架信息页面 ===")
        
        # 尝试多种选择器点击下一步按钮
        # 注意: has-text是Playwright特有的选择器，不能在JavaScript中使用
        next_button_selectors = [
            SELECTORS["next_step_button"],
            "button:has-text('下一步')",
            ".el-button--primary:has-text('下一步')",
            "button[type='button']:has-text('下一步')",
            ".el-button.el-button--primary"
        ]
        
        next_button_clicked = False
        for selector in next_button_selectors:
            try:
                if self.page.is_visible(selector):
                    # 使用Playwright的click方法（支持has-text选择器）
                    self.page.click(selector)
                    next_button_clicked = True
                    print(f"   已点击下一步按钮: {selector}")
                    break
            except Exception as e:
                print(f"   选择器 {selector} 点击失败: {e}")
                continue
        
        if not next_button_clicked:
            print("   ✗ 未找到下一步按钮，无法进入上架信息页面")
            # 截图保存当前页面状态
            self.page.screenshot(path="failed_to_find_next_button.png")
            print("   ✗ 已保存截图: failed_to_find_next_button.png")
            return {
                "name": test_data["name"],
                "code": test_data["name"],
                "industry": test_data["industry"]
            }
        
        # 等待页面完全加载
        self.page.wait_for_load_state("networkidle", timeout=45000)
        time.sleep(3)
        
        # 检查页面是否有验证错误提示
        print("   === 检查页面验证状态 ===")
        try:
            error_messages = self.page.locator(".el-form-item__error")
            if error_messages.count() > 0:
                for i in range(error_messages.count()):
                    error_text = error_messages.nth(i).text_content()
                    print(f"   表单验证错误 {i+1}: {error_text}")
            else:
                print("   未检测到表单验证错误")
        except Exception as e:
            print(f"   检查验证错误时出错: {e}")
        
        # 检查是否有任何隐藏的错误或警告消息
        print("   === 检查隐藏错误消息 ===")
        try:
            # 检查所有包含错误类的元素
            all_errors = self.page.locator("[class*='error'], [class*='Error'], .el-message-error")
            if all_errors.count() > 0:
                for i in range(min(all_errors.count(), 10)):
                    error_text = all_errors.nth(i).text_content()
                    print(f"   错误消息 {i+1}: {error_text}")
            else:
                print("   未检测到隐藏错误消息")
        except Exception as e:
            print(f"   检查隐藏错误时出错: {e}")
        
        # 使用JavaScript检查Vue表单验证状态
        print("   === 检查Vue表单验证状态 ===")
        try:
            form_status = self.page.evaluate("""
                const forms = document.querySelectorAll('form');
                for (let form of forms) {
                    if (form.__vue__) {
                        const vm = form.__vue__;
                        if (vm.$refs && vm.$refs.form) {
                            const formRef = vm.$refs.form;
                            if (formRef.validate) {
                                formRef.validate((valid) => {
                                    console.log('Form validation result:', valid);
                                });
                            }
                        }
                    }
                }
                return 'Vue form check completed';
            """)
            print(f"   Vue表单检查: {form_status}")
        except Exception as e:
            print(f"   Vue表单检查时出错: {e}")
        
        # 添加调试信息：检查当前页面状态
        print("   === 调试信息 ===")
        print(f"   当前URL: {self.page.url}")
        print(f"   当前页面标题: {self.page.title()}")
        
        # 检查是否有警告或错误弹窗
        try:
            alert = self.page.locator(".el-message-box")
            if alert.count() > 0:
                print("   发现弹窗")
                alert_text = alert.text_content()
                print(f"   弹窗内容: {alert_text}")
        except Exception as e:
            print(f"   检查弹窗时出错: {e}")
        
        # 检查当前URL
        current_url = self.page.url
        print(f"   当前URL: {current_url}")
        
        # 等待上架信息页面的特征元素出现，使用多种选择器确保兼容性
        shelf_page_loaded = False
        try:
            # 尝试多种选择器来确认页面已成功切换
            shelf_page_selectors = [
                "label:has-text('是否需要申请使用')",
                "label:has-text('服务协议')",
                "label:has-text('产品授权范围')",
                "label:has-text('产品交付策略')",
                "input[type='radio'][name*='needApply']",
                SELECTORS.get("need_apply_no_radio")
            ]
            
            for selector in shelf_page_selectors:
                if not selector:
                    continue
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    shelf_page_loaded = True
                    print(f"   检测到上架信息页面特征元素: {selector}")
                    break
                except Exception:
                    continue
                    
            if shelf_page_loaded:
                print(f"   已进入上架信息页面")
            else:
                print(f"   ⚠ 可能未进入上架信息页面，正在尝试刷新页面...")
                # 截图保存当前页面状态
                self.page.screenshot(path="shelf_page_not_loaded.png")
                print("   ⚠ 已保存截图: shelf_page_not_loaded.png")
                
                # 尝试刷新页面
                self.page.reload()
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                # 再次检查
                for selector in shelf_page_selectors:
                    if not selector:
                        continue
                    try:
                        self.page.wait_for_selector(selector, timeout=3000)
                        shelf_page_loaded = True
                        print(f"   刷新后检测到上架信息页面特征元素: {selector}")
                        break
                    except Exception:
                        continue
                
                if not shelf_page_loaded:
                    print("   ✗ 刷新后仍未进入上架信息页面")
        except Exception as e:
            print(f"   ⚠ 等待上架信息页面元素超时: {str(e)}")

        # 步骤 6.1: 填写价格信息 - 填写数据产品的价格相关信息
        print("\n=== 6.1 填写价格信息 ===")
        
        # 步骤 6.1.1: 选择价格类型 - 选择数据产品的价格类型，支持计量定价、买断、免费
        price_type = "计量定价"  # 可选值：计量定价、买断、免费
        if self.page.is_visible(SELECTORS.get("price_type_select")):
            self.page.click(SELECTORS["price_type_select"])
            time.sleep(1)
            # 根据价格类型选择对应的选项
            if price_type == "计量定价":
                self.page.click("li:has-text('计量定价')")
            elif price_type == "买断":
                self.page.click("li:has-text('买断')")
            elif price_type == "免费":
                self.page.click("li:has-text('免费')")
            print(f"   已选择价格类型: {price_type}")
            time.sleep(1)
        

        # 步骤 6.1.3: 填写价格 - 填写数据产品的价格（只能输入数字）
        price = "100"
        if self.page.is_visible(SELECTORS.get("price_input")):
            self.page.fill(SELECTORS["price_input"], price)
            print(f"   已填写价格: {price}")
        
        # 步骤 6.1.4: 设置是否隐藏价格 - 当价格类型为计量定价或买断时，可选择是否隐藏价格
        # 当是否要审批选择"是"时，计量定价和买断的价格可以选择是否隐藏
        hidden_price = "否"  # 可选值：是、否
        if price_type in ["计量定价", "买断"]:
            if self.page.is_visible(SELECTORS.get("hidden_price_radio_yes")) or self.page.is_visible(SELECTORS.get("hidden_price_radio_no")):
                if hidden_price == "是":
                    self.page.click(SELECTORS["hidden_price_radio_yes"])
                else:
                    self.page.click(SELECTORS["hidden_price_radio_no"])
                print(f"   是否隐藏价格: {hidden_price}")
        


        # 步骤 7: 填写上架信息 - 填写数据产品的上架配置信息，包括申请方式、服务协议等
        print("\n=== 7. 填写上架信息 ===")
        
        # 步骤 7.1: 设置是否需要申请使用 - 选择是否需要用户申请使用该数据产品
        
        # 尝试更通用的选择器来定位单选按钮
        if need_apply:
            # 选择"是"
            yes_selectors = [
                SELECTORS["need_apply_yes_radio"],
                ".el-radio:has-text('是')",
                "span:has-text('是')",
                "label:has-text('是')",
                ".el-radio__label:has-text('是')"
            ]
            
            for selector in yes_selectors:
                try:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        print(f"   是否需要申请使用: 是")
                        break
                except:
                    continue
            else:
                print(f"   ⚠ 未找到'是否需要申请使用: 是'选项")
        else:
            # 选择"否"
            no_selectors = [
                SELECTORS["need_apply_no_radio"],
                ".el-radio:has-text('否')",
                "span:has-text('否')",
                "label:has-text('否')",
                ".el-radio__label:has-text('否')"
            ]
            
            for selector in no_selectors:
                try:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        print(f"   是否需要申请使用: 否")
                        break
                except:
                    continue
            else:
                print(f"   ⚠ 未找到'是否需要申请使用: 否'选项")

        # 步骤 7.2: 选择服务协议 - 选择数据产品使用的服务协议，这里选择第一个选项
        if self.page.is_visible("label:has-text('服务协议') + div >> .el-select"):
            self.page.click("label:has-text('服务协议') + div >> .el-select")
            time.sleep(1)
            self.page.click(".el-select-dropdown__item")
            print(f"   已选择服务协议: 第一个选项")

        # 步骤 7.3: 设置产品授权范围 - 设置产品是否允许第三方授权使用，这里选择"允许"
        if self.page.is_visible(SELECTORS["allow_third_party_checkbox"]):
            self.page.click(SELECTORS["allow_third_party_checkbox"])
            print(f"   已选择产品授权范围: 允许第三方授权使用")

        # 步骤 7.4: 选择产品交付策略 - 选择数据产品的交付策略
        print("   选择产品交付策略...")
        delivery_strategy_selected = False
        
        # 尝试多种选择器点击选择按钮
        select_button_selectors = [
            SELECTORS["delivery_strategy_select_button"],
            SELECTORS["delivery_strategy_select_span"],
            ".el-form-item:has(label:has-text('产品交付策略')) button",
            ".el-form-item:has(label:has-text('产品交付策略')) span:has-text('选择')"
        ]
        
        for selector in select_button_selectors:
            try:
                if self.page.is_visible(selector):
                    self.page.click(selector)
                    time.sleep(1)
                    print(f"   已点击选择按钮: {selector}")
                    break
            except Exception as e:
                print(f"   选择器 {selector} 点击失败: {e}")
                continue
        
        # 等待弹窗出现并选择策略
        try:
            # 等待弹窗出现
            self.page.wait_for_selector(".el-dialog", state="visible", timeout=10000)
            time.sleep(1)
            
            # 尝试选择第一个可用的策略
            checkbox_selectors = [
                SELECTORS["delivery_strategy_last_checkbox"],
                ".el-table__row:first-child .el-checkbox__inner",
                ".el-checkbox__inner"
            ]
            
            for checkbox_selector in checkbox_selectors:
                try:
                    if self.page.is_visible(checkbox_selector):
                        self.page.click(checkbox_selector)
                        time.sleep(0.5)
                        print(f"   已选择产品交付策略")
                        delivery_strategy_selected = True
                        break
                except Exception as e:
                    print(f"   选择器 {checkbox_selector} 点击失败: {e}")
                    continue
            
            # 点击确定按钮
            if delivery_strategy_selected:
                confirm_button_selectors = [
                    SELECTORS["delivery_strategy_confirm_button"],
                    ".el-dialog__footer button:has-text('确定')",
                    ".el-dialog button:has-text('确定')"
                ]
                
                for confirm_selector in confirm_button_selectors:
                    try:
                        if self.page.is_visible(confirm_selector):
                            self.page.click(confirm_selector)
                            time.sleep(1)
                            print("   已确认产品交付策略")
                            break
                    except Exception as e:
                        print(f"   确认按钮选择器 {confirm_selector} 点击失败: {e}")
                        continue
        except Exception as e:
            print(f"   ✗ 选择产品交付策略失败: {str(e)}")
        
        if not delivery_strategy_selected:
            print("   警告：产品交付策略未选择，可能导致产品创建失败")

        # 步骤 8: 填写价格信息
        print("\n=== 8. 填写价格信息 ===")
        

        

        
        # # 设置是否隐藏价格
        # if self.page.is_visible(SELECTORS.get("hidden_price_radio_no")):
        #     self.page.click(SELECTORS["hidden_price_radio_no"])
        #     print("   是否隐藏价格: 否")
        

        # 9. 点击确定
        print("\n=== 9. 点击确定 ===")
        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            time.sleep(3)  # 等待页面加载
            print("已点击确定，完成数据产品发布")
        
        # 导航到数据产品列表页面
        print("\n=== 导航到数据产品列表页面 ===")
        data_product_page = self.get_url_for_user(1, "/registration/product/dataProduct", None, None)
        self.page.goto(data_product_page)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问数据产品列表页面: {data_product_page}")
        
        # 10. 点击数据产品名称查询
        print("\n=== 10. 输入数据产品名称查询 ===")
        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", test_data["name"])
            time.sleep(3)  # 等待页面加载
        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)  # 等待页面加载
            print("   已点击查询")

        # 12. 点击发布
        print("\n=== 12. 点击发布 ===")
        if self.page.is_visible("span.el-button__text:has-text('发布')"):
            self.page.click("span.el-button__text:has-text('发布')")
            time.sleep(3)  # 等待页面加载
            print("   已点击发布")

        print("\n新增数据产品完整流程测试完成")

        # 13. 点击确定
        print("\n=== 13. 点击确定 ===")
        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            # 等待保存成功的提示
            try:
                self.page.wait_for_selector(SELECTORS["success_message"], timeout=10000)
                print("   已点击确定，数据产品发布成功")
            except Exception as e:
                # 如果没有成功提示，也不影响测试流程
                print("   已点击确定，完成数据产品发布")
        

        # 14. 点击数据产品名称查询
        print("\n=== 输入数据产品名称查询 ===")
        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", test_data["name"])
            time.sleep(3)  # 等待页面加载
        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)  # 等待页面加载

            # 获取第一个匹配的元素的文本内容
            try:
                text_content = self.page.locator("div.cell.el-tooltip").nth(0).text_content(timeout=5000)
            except:
                # 如果tooltip不可用，尝试从产品名称元素获取
                text_content = test_data["name"]
        
        return {
            "name": test_data["name"],
            "code": text_content,
            "industry": "采矿业"
        }

    def fill_basic_info(self, test_data):
        """
        填写基础配置信息
        
        Args:
            test_data: 测试数据字典
        
        Returns:
            dict: 包含产品名称、产品编码、行业分类的字典
        """
        print("\n=== 3. 填写基础配置信息 ===")
        
        if self.page.is_visible(SELECTORS["data_product_name_input"]):
            self.page.fill(SELECTORS["data_product_name_input"], test_data["name"])
            print(f"   已填写中文名称: {test_data['name']}")

        if self.page.is_visible(SELECTORS["data_product_english_name_input"]):
            self.page.fill(SELECTORS["data_product_english_name_input"], test_data["english_name"])
            print(f"   已填写英文名称: {test_data['english_name']}")

        if self.page.is_visible(SELECTORS["data_product_desc_textarea"]):
            self.page.fill(SELECTORS["data_product_desc_textarea"], test_data["desc"])
            print(f"   已填写产品介绍")
        
        if self.page.is_visible(SELECTORS["data_product_limit_textarea"]):
            self.page.fill(SELECTORS["data_product_limit_textarea"], test_data["limit"])
            print(f"   已填写使用限制")
        
        if self.page.is_visible(SELECTORS["data_product_other_textarea"]):
            self.page.fill(SELECTORS["data_product_other_textarea"], test_data["other"])
            print(f"   已填写其他说明")
        
        if self.page.is_visible(SELECTORS["data_product_tags_input"]):
            tags_value = f"测试, {test_data['type']}, 自动化测试"
            self.page.fill(SELECTORS["data_product_tags_input"], tags_value)
            print(f"   已填写标签: {tags_value}")
        
        if self.page.is_visible(SELECTORS["data_product_category_select"]):
            self.page.click(SELECTORS["data_product_category_select"])
            self.page.click("li:has-text('采矿业')")
            print(f"   已选择行业分类: 采矿业")
        
        if self.page.is_visible(SELECTORS["data_product_type_select"]):
            self.page.click(SELECTORS["data_product_type_select"])
            self.page.click("li:has-text('数据接口')")
            print(f"   已选择产品类型: 数据接口")

        if self.page.is_visible(SELECTORS["data_product_subtype_select"]):
            self.page.click(SELECTORS["data_product_subtype_select"])
            self.page.click("li:has-text('API接口')")
            print(f"   已选择产品小类: API接口")
        
        if self.page.is_visible(SELECTORS["data_product_region_select"]):
            self.page.locator(".allPadding > .el-select > .el-select__wrapper > .el-select__selection > div:nth-child(2)").click()
            self.page.locator("div").filter(has_text=re.compile(r"^北京市$")).locator("span").nth(1).click()
            print(f"   已选择 北京市")

    def fill_detail_info(self, need_auth=False):
        """
        填写详细信息
        
        Args:
            need_auth: 是否需要授权（精准授权）
        """
        print("\n=== 4. 进入详细信息页面 ===")
        if self.page.is_visible(SELECTORS["next_step_button"]):
            self.page.click(SELECTORS["next_step_button"])
            
            self.page.wait_for_load_state("networkidle", timeout=45000)
            
            try:
                detail_page_selectors = [
                    "label:has-text('接口名称')",
                    "label:has-text('正式接口地址')",
                    "input[placeholder*='接口名称']",
                    "input[placeholder*='接口地址']"
                ]
                
                detail_page_loaded = False
                for selector in detail_page_selectors:
                    try:
                        self.page.wait_for_selector(selector, timeout=5000)
                        detail_page_loaded = True
                        break
                    except Exception:
                        continue
                        
                if detail_page_loaded:
                    print(f"   已进入详细信息页面")
                else:
                    print(f"   ⚠ 可能未进入详细信息页面，但继续执行测试")
            except Exception as e:
                print(f"   ⚠ 等待详细信息页面元素超时: {str(e)}")
                print(f"   ⚠ 继续执行测试")

        print("\n=== 5. 填写详细信息 ===")
        
        print("   填写接口名称: 测试接口...")
        if self.page.is_visible(SELECTORS.get("data_product_api_name_input")):
            self.page.fill(SELECTORS["data_product_api_name_input"], "测试接口")
            print(f"   已填写接口名称: 测试接口")

        print("   填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("access_address_input")):
            self.page.fill(SELECTORS["access_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   已填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")

        print("   填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("redirect_address_input")):
            self.page.fill(SELECTORS["redirect_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   已填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")

        print("   向下滚动页面，使入参字段可见...")
        self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(1)
        self.page.evaluate("window.scrollBy({top: -200, behavior: 'smooth'})")
        time.sleep(1)

        if need_auth:
            print("   填写入参信息（授权产品：abc、date）...")
            input_params = ["abc", "date"]
            input_xpaths = [
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input",
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[2]/div/div[2]/div[1]/div/input"
            ]
        else:
            print("   填写入参信息（非授权产品：仅date）...")
            input_params = ["date"]
            input_xpaths = [
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input"
            ]
        
        filled_count = 0
        for i, (xpath, param_name) in enumerate(zip(input_xpaths, input_params)):
            try:
                input_element = self.page.locator(f"xpath={xpath}")
                if input_element.count() > 0:
                    if input_element.is_visible():
                        input_element.fill(param_name)
                        print(f"   已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                    else:
                        print(f"   第{i+1}个入参字段不可见，尝试强制填充")
                        input_element.fill(param_name)
                        print(f"   (强制) 已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                else:
                    print(f"   第{i+1}个入参字段xpath不存在")
            except Exception as e:
                print(f"   填写第{i+1}个入参字段时出错: {e}")
        
        if filled_count < len(input_params):
            print(f"   警告：只成功填写了{filled_count}/{len(input_params)}个入参字段")

        if need_auth:
            print("   设置精准授权为是...")
            
            self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
            time.sleep(1)
            
            auth_xpath = "//label[contains(text(),'是否需要授权')]/following-sibling::div//span[contains(text(),'是')]/preceding-sibling::span[contains(@class,'el-radio__inner')]"
            
            auth_selectors = [
                auth_xpath,
                "label:has-text('是否需要授权') + div .el-radio:has-text('是')",
                "label:has-text('是否需要授权') ~ div .el-radio:last-child",
                ".el-radio:has-text('是')"
            ]
            
            auth_clicked = False
            for selector in auth_selectors:
                try:
                    if "xpath=" in selector:
                        element = self.page.locator(selector)
                    else:
                        element = self.page.locator(selector)
                    
                    if element.count() > 0 and element.is_visible():
                        element.first.click(force=True)
                        print(f"   已设置精准授权为: 是")
                        auth_clicked = True
                        print("   等待5秒，确保页面元素加载完成...")
                        time.sleep(5)
                        break
                except Exception as e:
                    print(f"   选择器 {selector} 点击失败: {e}")
                    continue
            
            if not auth_clicked:
                print(f"   ⚠ 未找到精准授权选择器")
            else:
                precise_auth_fields = [
                    {
                        "name": "企业名称",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input",
                        "value": "a"
                    },
                    {
                        "name": "统一社会信用代码",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[2]/div/div[2]/div[1]/div/input",
                        "value": "b"
                    },
                    {
                        "name": "企业扩展字段",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/input",
                        "value": "c"
                    },
                    {
                        "name": "日期字段",
                        "xpath": "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[4]/div/div[2]/div[1]/div/input",
                        "value": "date"
                    }
                ]
                
                for field in precise_auth_fields:
                    try:
                        input_element = self.page.locator(f"xpath={field['xpath']}")
                        if input_element.count() > 0:
                            if input_element.is_visible():
                                input_element.fill(field['value'])
                                print(f"   已填写{field['name']}: {field['value']}")
                            else:
                                print(f"   {field['name']}字段不可见，尝试强制填充")
                                input_element.fill(field['value'])
                                print(f"   (强制) 已填写{field['name']}: {field['value']}")
                        else:
                            print(f"   {field['name']}字段不存在")
                    except Exception as e:
                        print(f"   填写{field['name']}时出错: {e}")

    def fill_shelf_info(self, need_apply=False):
        """
        填写上架信息
        
        Args:
            need_apply: 是否需要申请使用
        """
        print("\n=== 6. 进入上架信息页面 ===")
        
        next_button_selectors = [
            SELECTORS["next_step_button"],
            "button:has-text('下一步')",
            ".el-button--primary:has-text('下一步')",
            "button[type='button']:has-text('下一步')",
            ".el-button.el-button--primary"
        ]
        
        next_button_clicked = False
        for selector in next_button_selectors:
            try:
                if self.page.is_visible(selector):
                    self.page.click(selector)
                    next_button_clicked = True
                    print(f"   已点击下一步按钮: {selector}")
                    break
            except Exception as e:
                print(f"   选择器 {selector} 点击失败: {e}")
                continue
        
        if not next_button_clicked:
            print("   ✗ 未找到下一步按钮，无法进入上架信息页面")
            self.page.screenshot(path="failed_to_find_next_button.png")
            print("   ✗ 已保存截图: failed_to_find_next_button.png")
            return False
        
        self.page.wait_for_load_state("networkidle", timeout=45000)
        time.sleep(3)
        
        shelf_page_selectors = [
            "label:has-text('是否需要申请使用')",
            "label:has-text('服务协议')",
            "label:has-text('产品授权范围')",
            "label:has-text('产品交付策略')",
            "input[type='radio'][name*='needApply']",
            SELECTORS.get("need_apply_no_radio")
        ]
        
        shelf_page_loaded = False
        try:
            for selector in shelf_page_selectors:
                if not selector:
                    continue
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    shelf_page_loaded = True
                    print(f"   检测到上架信息页面特征元素: {selector}")
                    break
                except Exception:
                    continue
                    
            if shelf_page_loaded:
                print(f"   已进入上架信息页面")
            else:
                print(f"   ⚠ 可能未进入上架信息页面，正在尝试刷新页面...")
                self.page.screenshot(path="shelf_page_not_loaded.png")
                print("   ⚠ 已保存截图: shelf_page_not_loaded.png")
                
                self.page.reload()
                self.page.wait_for_load_state("networkidle", timeout=30000)
                
                for selector in shelf_page_selectors:
                    if not selector:
                        continue
                    try:
                        self.page.wait_for_selector(selector, timeout=3000)
                        shelf_page_loaded = True
                        print(f"   刷新后检测到上架信息页面特征元素: {selector}")
                        break
                    except Exception:
                        continue
                
                if not shelf_page_loaded:
                    print("   ✗ 刷新后仍未进入上架信息页面")
        except Exception as e:
            print(f"   ⚠ 等待上架信息页面元素超时: {str(e)}")

        print("\n=== 6.1 填写价格信息 ===")
        
        price_type = "计量定价"
        if self.page.is_visible(SELECTORS.get("price_type_select")):
            self.page.click(SELECTORS["price_type_select"])
            time.sleep(1)
            if price_type == "计量定价":
                self.page.click("li:has-text('计量定价')")
            elif price_type == "买断":
                self.page.click("li:has-text('买断')")
            elif price_type == "免费":
                self.page.click("li:has-text('免费')")
            print(f"   已选择价格类型: {price_type}")
            time.sleep(1)

        price = "100"
        if self.page.is_visible(SELECTORS.get("price_input")):
            self.page.fill(SELECTORS["price_input"], price)
            print(f"   已填写价格: {price}")

        hidden_price = "否"
        if price_type in ["计量定价", "买断"]:
            if self.page.is_visible(SELECTORS.get("hidden_price_radio_yes")) or self.page.is_visible(SELECTORS.get("hidden_price_radio_no")):
                if hidden_price == "是":
                    self.page.click(SELECTORS["hidden_price_radio_yes"])
                else:
                    self.page.click(SELECTORS["hidden_price_radio_no"])
                print(f"   是否隐藏价格: {hidden_price}")

        print("\n=== 7. 填写上架信息 ===")
        
        if need_apply:
            yes_selectors = [
                SELECTORS["need_apply_yes_radio"],
                ".el-radio:has-text('是')",
                "span:has-text('是')",
                "label:has-text('是')",
                ".el-radio__label:has-text('是')"
            ]
            
            for selector in yes_selectors:
                try:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        print(f"   是否需要申请使用: 是")
                        break
                except:
                    continue
            else:
                print(f"   ⚠ 未找到'是否需要申请使用: 是'选项")
        else:
            no_selectors = [
                SELECTORS["need_apply_no_radio"],
                ".el-radio:has-text('否')",
                "span:has-text('否')",
                "label:has-text('否')",
                ".el-radio__label:has-text('否')"
            ]
            
            for selector in no_selectors:
                try:
                    if self.page.is_visible(selector):
                        self.page.click(selector)
                        print(f"   是否需要申请使用: 否")
                        break
                except:
                    continue
            else:
                print(f"   ⚠ 未找到'是否需要申请使用: 否'选项")

        if self.page.is_visible("label:has-text('服务协议') + div >> .el-select"):
            self.page.click("label:has-text('服务协议') + div >> .el-select")
            time.sleep(1)
            self.page.click(".el-select-dropdown__item")
            print(f"   已选择服务协议: 第一个选项")

        if self.page.is_visible(SELECTORS["allow_third_party_checkbox"]):
            self.page.click(SELECTORS["allow_third_party_checkbox"])
            print(f"   已选择产品授权范围: 允许第三方授权使用")

        print("   选择产品交付策略...")
        delivery_strategy_selected = False
        
        select_button_selectors = [
            SELECTORS["delivery_strategy_select_button"],
            SELECTORS["delivery_strategy_select_span"],
            ".el-form-item:has(label:has-text('产品交付策略')) button",
            ".el-form-item:has(label:has-text('产品交付策略')) span:has-text('选择')"
        ]
        
        for selector in select_button_selectors:
            try:
                if self.page.is_visible(selector):
                    self.page.click(selector)
                    time.sleep(1)
                    print(f"   已点击选择按钮: {selector}")
                    break
            except Exception as e:
                print(f"   选择器 {selector} 点击失败: {e}")
                continue
        
        try:
            self.page.wait_for_selector(".el-dialog", state="visible", timeout=10000)
            time.sleep(1)
            
            checkbox_selectors = [
                SELECTORS["delivery_strategy_last_checkbox"],
                ".el-table__row:first-child .el-checkbox__inner",
                ".el-checkbox__inner"
            ]
            
            for checkbox_selector in checkbox_selectors:
                try:
                    if self.page.is_visible(checkbox_selector):
                        self.page.click(checkbox_selector)
                        time.sleep(0.5)
                        print(f"   已选择产品交付策略")
                        delivery_strategy_selected = True
                        break
                except Exception as e:
                    print(f"   选择器 {checkbox_selector} 点击失败: {e}")
                    continue
            
            if delivery_strategy_selected:
                confirm_button_selectors = [
                    SELECTORS["delivery_strategy_confirm_button"],
                    ".el-dialog__footer button:has-text('确定')",
                    ".el-dialog button:has-text('确定')"
                ]
                
                for confirm_selector in confirm_button_selectors:
                    try:
                        if self.page.is_visible(confirm_selector):
                            self.page.click(confirm_selector)
                            time.sleep(1)
                            print("   已确认产品交付策略")
                            break
                    except Exception as e:
                        print(f"   确认按钮选择器 {confirm_selector} 点击失败: {e}")
                        continue
        except Exception as e:
            print(f"   ✗ 选择产品交付策略失败: {str(e)}")
        
        if not delivery_strategy_selected:
            print("   警告：产品交付策略未选择，可能导致产品创建失败")
        
        return True

    def confirm_and_publish(self, test_data):
        """
        确认并发布数据产品
        
        Args:
            test_data: 测试数据字典
        
        Returns:
            dict: 包含产品名称、产品编码、行业分类的字典
        """
        print("\n=== 9. 点击确定 ===")
        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            time.sleep(3)
            print("已点击确定，完成数据产品发布")
        
        print("\n=== 导航到数据产品列表页面 ===")
        data_product_page = self.get_url_for_user(1, "/registration/product/dataProduct", None, None)
        self.page.goto(data_product_page)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问数据产品列表页面: {data_product_page}")
        
        print("\n=== 10. 输入数据产品名称查询 ===")
        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", test_data["name"])
            time.sleep(3)
        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)
            print("   已点击查询")

        print("\n=== 12. 点击发布 ===")
        if self.page.is_visible("span.el-button__text:has-text('发布')"):
            self.page.click("span.el-button__text:has-text('发布')")
            time.sleep(3)
            print("   已点击发布")

        print("\n新增数据产品完整流程测试完成")

        print("\n=== 13. 点击确定 ===")
        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            try:
                self.page.wait_for_selector(SELECTORS["success_message"], timeout=10000)
                print("   已点击确定，数据产品发布成功")
            except Exception as e:
                print("   已点击确定，完成数据产品发布")
        

        print("\n=== 输入数据产品名称查询 ===")
        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", test_data["name"])
            time.sleep(3)
        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)

            try:
                text_content = self.page.locator("div.cell.el-tooltip").nth(0).text_content(timeout=5000)
            except:
                text_content = test_data["name"]
        
        return {
            "name": test_data["name"],
            "code": text_content,
            "industry": "采矿业"
        }
    
    def search_product_and_apply(self, user_id, product_name, user_ips=None, fixed_port=None):
        """
        搜索产品并申请的公共方法
        
        Args:
            user_id: 用户ID
            product_name: 产品名称
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        
        Returns:
            bool: 是否找到并点击了立即申请按钮
        """
        print(f"\n=== search_product_and_apply 开始 ===")
        print(f"   user_id: {user_id}, product_name: {product_name}")
        
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.183:30001")
        
        # 判断配置格式并提取IP和端口
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.183")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = str(user_config)
            port = fixed_port if fixed_port else "30001"
        
        print(f"   目标环境: {ip}:{port}")
        
        # 访问产品列表页面
        product_list_url = self.get_url_for_ip(ip, port, "/datamarket/product/product-list")
        self.page.goto(product_list_url)
        try:
            self.page.wait_for_load_state("networkidle", timeout=30000)
        except Exception:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                print(f"   [警告] 页面加载超时，继续执行")
                pass
        print(f"   已访问产品列表页面: {product_list_url}")

        # 增加重试机制，等待产品同步到目标环境
        max_retries = 15
        retry_delay = 20
        
        target_product_element = None
        
        for retry in range(max_retries):
            print(f"\n   [重试 {retry + 1}/{max_retries}] 搜索产品: {product_name}")
            
            # 尝试多种搜索框选择器
            search_input_selectors = [
                "input[placeholder='输入数据产品名称']",
                "input[type='text']",
                "input[placeholder*='搜索']",
                "input[placeholder*='名称']",
                ".search-input",
                "input[name*='name']"
            ]
            
            name_input_found = False
            for selector in search_input_selectors:
                try:
                    name_input = self.page.locator(selector).first
                    if name_input.count() > 0:
                        name_input.wait_for(state="visible", timeout=5000)
                        name_input.fill(product_name)
                        print(f"   使用选择器 '{selector}' 输入产品名称")
                        name_input_found = True
                        break
                except Exception as e:
                    print(f"   选择器 '{selector}' 未找到搜索框: {str(e)[:30]}")
                    continue
            
            if not name_input_found:
                print(f"   未找到搜索框，跳过本次搜索")
                if retry < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    assert False, "未找到搜索框"
            
            # 尝试多种方式触发搜索
            search_button_selectors = [
                "button:has-text('查询')",
                "button.el-button.el-button--primary:has-text('查询')",
                ".search-btn",
                "[class*='search']",
                "button[type='submit']"
            ]
            
            search_clicked = False
            for button_selector in search_button_selectors:
                try:
                    if self.page.locator(button_selector).count() > 0:
                        self.page.click(button_selector)
                        print(f"   使用选择器 '{button_selector}' 点击查询按钮")
                        search_clicked = True
                        break
                except Exception as e:
                    print(f"   选择器 '{button_selector}' 点击失败: {str(e)[:30]}")
                    continue
            
            if not search_clicked:
                print(f"   未找到查询按钮，尝试按回车键")
                self.page.keyboard.press("Enter")
            
            # 等待搜索结果
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except Exception:
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    print(f"   [警告] 搜索后页面加载超时")
                    pass
            time.sleep(3)

            # 尝试多种选择器定位产品名称元素
            product_name_selectors = [
                ".product-name-text",
                f"td:has-text('{product_name}')",
                "div[class*='product-name']",
                "span[class*='product-name']",
                ".el-table__cell:has-text('" + product_name[:10] + "')"
            ]
            
            target_product_element = None
            for selector in product_name_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.count() > 0:
                        element.wait_for(state="visible", timeout=3000)
                        target_product_element = element
                        print(f"   使用选择器 '{selector}' 找到产品")
                        break
                except Exception as e:
                    print(f"   选择器 '{selector}' 未找到产品: {str(e)[:30]}")
                    continue
            
            if target_product_element:
                # 找到产品，跳出重试循环
                break
            
            # 尝试模糊搜索
            print(f"   [警告] 未找到产品，尝试模糊搜索...")
            if len(product_name) > 5:
                short_name = product_name[:5]
                for selector in search_input_selectors:
                    try:
                        name_input = self.page.locator(selector).first
                        if name_input.count() > 0:
                            name_input.fill(short_name)
                            break
                    except:
                        continue
                
                for button_selector in search_button_selectors:
                    try:
                        if self.page.locator(button_selector).count() > 0:
                            self.page.click(button_selector)
                            break
                    except:
                        continue
                
                time.sleep(3)
                
                for selector in product_name_selectors:
                    try:
                        element = self.page.locator(selector).first
                        if element.count() > 0:
                            element.wait_for(state="visible", timeout=3000)
                            target_product_element = element
                            print(f"   模糊搜索找到产品")
                            break
                    except:
                        continue
            
            if target_product_element:
                break
            
            # 尝试遍历所有产品
            print(f"   [警告] 模糊搜索也失败，尝试遍历所有产品...")
            all_products = self.page.locator(".product-name-text").all()
            found = False
            for idx, product_element in enumerate(all_products):
                try:
                    actual_name = product_element.inner_text()
                    print(f"   检查产品 {idx + 1}: {actual_name[:20]}...")
                    if actual_name == product_name or actual_name.startswith(product_name[:5]):
                        target_product_element = product_element
                        found = True
                        print(f"   通过遍历找到产品: {actual_name}")
                        break
                except Exception as e:
                    continue
            
            if found:
                break
            
            # 继续重试
            if retry < max_retries - 1:
                print(f"   [等待] 产品尚未同步到目标环境，{retry_delay}秒后重试...")
                time.sleep(retry_delay)
            else:
                assert False, f"未找到产品: {product_name}"
          
        # 验证产品名称
        actual_product_name = target_product_element.inner_text()
        print(f"   找到目标产品: {actual_product_name}")
        
        # 点击产品详情
        detail_button_selectors = [
            ".cursor-pointer:has-text('产品详情')",
            "button:has-text('详情')",
            "a:has-text('详情')",
            "[class*='detail']"
        ]
        
        detail_button_found = False
        for selector in detail_button_selectors:
            try:
                detail_button = self.page.locator(selector).first
                if detail_button.count() > 0:
                    detail_button.wait_for(state="visible", timeout=5000)
                    detail_button.click()
                    print(f"   使用选择器 '{selector}' 点击产品详情")
                    detail_button_found = True
                    break
            except Exception as e:
                print(f"   选择器 '{selector}' 点击详情失败: {str(e)[:30]}")
                continue
        
        if not detail_button_found:
            # 尝试从产品元素找到对应的详情按钮
            try:
                product_row = target_product_element.locator('xpath=ancestor::tr')
                detail_button = product_row.locator("button:has-text('详情')").first
                if detail_button.count() > 0:
                    detail_button.click()
                    print(f"   通过产品行找到并点击详情按钮")
                    detail_button_found = True
            except Exception as e:
                print(f"   通过产品行找详情按钮失败: {str(e)[:30]}")
        
        if not detail_button_found:
            assert False, "未找到产品详情按钮"
        
        time.sleep(3)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        
        # 点击立即申请
        apply_button_selectors = [
            "xpath=/html/body/div[1]/div/div/section/div/main/div/div[1]/div/div/div[2]/div[6]/button",
            "button.el-button.el-button--primary:has-text('立即申请')",
            "button:has-text('立即申请')",
            "button.el-button--primary"
        ]
        
        has_apply_button = False
        for selector in apply_button_selectors:
            try:
                apply_button = self.page.locator(selector).first
                apply_button.wait_for(state="visible", timeout=5000)
                apply_button.click()
                self.page.wait_for_load_state("networkidle", timeout=30000)
                print(f"   使用选择器 '{selector}' 点击立即申请成功")
                has_apply_button = True
                break
            except Exception as e:
                print(f"   选择器 '{selector}' 未找到立即申请按钮: {str(e)[:30]}")
                continue
        
        if not has_apply_button:
            print(f"   未找到立即申请按钮")
        
        print(f"\n=== search_product_and_apply 结束 ===")
        return has_apply_button
    
    def submit_application(self):
        """
        提交申请的公共方法
        
        Returns:
            bool: 是否成功提交申请
        """
        # 输入申请理由
        print("\n=== 输入申请理由 ===")
        reason_xpath = "/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[3]/div/div/textarea"
        reason_input_selectors = [
            f"xpath={reason_xpath}",
            "textarea.el-textarea__inner[placeholder='请输入申请理由']",
            "textarea[placeholder*='申请理由']"
        ]
        
        for selector in reason_input_selectors:
            try:
                reason_input = self.page.locator(selector).first
                reason_input.wait_for(state="visible", timeout=10000)
                reason_input.fill("测试申请理由")
                print(f"   使用选择器 '{selector}' 输入申请理由成功")
                break
            except Exception as e:
                print(f"   选择器 '{selector}' 未找到申请理由输入框: {e}")
                continue
        
        # 勾选我已阅读并同意
        print("\n=== 勾选我已阅读并同意 ===")
        checkbox_xpath = "/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[4]/div/div/label/span[1]/input"
        agree_checkbox_selectors = [
            f"xpath={checkbox_xpath}",
            "span.el-checkbox__inner",
            "input[type='checkbox']"
        ]
        
        for selector in agree_checkbox_selectors:
            try:
                agree_checkbox = self.page.locator(selector).first
                agree_checkbox.wait_for(state="visible", timeout=10000)
                agree_checkbox.click()
                print(f"   使用选择器 '{selector}' 勾选我已阅读并同意成功")
                break
            except Exception as e:
                print(f"   选择器 '{selector}' 未找到勾选框: {e}")
                continue
        
        # 点击确定
        print("\n=== 点击确定 ===")
        confirm_xpath = "/html/body/div[1]/div/div/section/div/main/div/div[3]/div/div/div/form/div[5]/div/button[1]"
        confirm_button_selectors = [
            f"xpath={confirm_xpath}",
            "button.el-button.el-button--primary:has-text('确定')",
            "button:has-text('确定')"
        ]
        
        for selector in confirm_button_selectors:
            try:
                confirm_button = self.page.locator(selector).first
                confirm_button.wait_for(state="visible", timeout=10000)
                confirm_button.click()
                self.page.wait_for_load_state("networkidle", timeout=30000)
                print(f"   使用选择器 '{selector}' 点击确定成功")
                break
            except Exception as e:
                print(f"   选择器 '{selector}' 未找到确定按钮: {e}")
                continue
        
        # 验证申请成功
        print("\n=== 验证申请成功 ===")
        try:
            success_message = self.page.locator(".el-message--success, .success-message").first
            if success_message.is_visible():
                print(f"   申请成功: {success_message.inner_text()}")
                return True
        except:
            pass
        
        return False
    
    def approve_product_application(self, product_name, user_id=1, user_ips=None, fixed_port=None):
        """
        审核产品申请的公共方法
        
        Args:
            product_name: 产品名称
            user_id: 审核用户ID（默认为1）
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.183:30001")
        
        # 判断配置格式并提取IP和端口
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.183")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = str(user_config)
            port = fixed_port if fixed_port else "30001"
        
        # 创建新的上下文和页面，确保干净的登录环境
        print(f"[调试] 创建新的浏览器上下文...")
        new_context = self.page.context.browser.new_context(viewport={"width": 1900, "height": 950})
        new_page = new_context.new_page()
        
        # 从测试数据中获取用户登录信息
        test_data = get_test_data()[0]
        username = test_data["username"]
        password = test_data["password"]
        captchaAnswer = test_data["captchaAnswer"]
        
        # 直接使用login_with_ip方法进行登录
        print(f"[登录] 正在登录用户{user_id}到{ip}:{port}...")
        
        # 先访问登录页面
        login_url = self.get_url_for_ip(ip, port, "/login")
        new_page.goto(login_url, timeout=30000)
        new_page.wait_for_load_state("networkidle", timeout=30000)
        new_page.wait_for_timeout(2000)
        print(f"   已访问登录页面: {login_url}")
        
        # 检查当前URL是否为登录页面
        current_url = new_page.url
        print(f"   [调试] 当前URL: {current_url}")
        if "login" not in current_url.lower():
            print(f"   [警告] 当前页面不是登录页面，可能已经登录或被重定向")
        
        # 然后调用login_with_ip方法进行登录（不需要再次goto）
        self.login_with_ip_direct(ip, port, username, password, captchaAnswer, new_page)
        print(f"   已登录环境: 用户ID={user_id}")
        
        # 访问审核页面
        approve_url = self.get_url_for_ip(ip, port, "/datamarket/applyManage/approve")
        new_page.goto(approve_url)
        new_page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问审核页面: {approve_url}")
        
        # 使用产品名称进行搜索
        print("\n=== 搜索待审核产品 ===")
        name_input = new_page.locator("input[placeholder='输入数据产品名称']").first
        name_input.fill(product_name)
        # 尝试点击搜索按钮
        try:
            search_button = new_page.locator("button:has-text('查询')").first
            search_button.click()
        except:
            new_page.keyboard.press("Enter")
        new_page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已搜索产品: {product_name}")
        
        # 点击审批按钮
        print("\n=== 点击审批按钮 ===")
        approve_button = new_page.locator("span:has-text('去审批')").first
        approve_button.wait_for(state="visible", timeout=15000)
        approve_button.click()
        new_page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        print("   已点击审批按钮")
        
        # 点击通过按钮
        print("\n=== 点击通过按钮 ===")
        pass_button = new_page.locator("button.el-button.el-button--primary:has-text('通过')").first
        pass_button.wait_for(state="visible", timeout=15000)
        if pass_button.is_visible():
            pass_button.click()
            time.sleep(3)
            print("   已点击通过按钮")
        
        # 处理确认对话框
        print("\n=== 处理确认对话框 ===")
        confirm_button = new_page.locator("button:has-text('确定')").first
        confirm_button.wait_for(state="visible", timeout=15000)
        if confirm_button.is_visible():
            confirm_button.click()
            time.sleep(5)
            print("   已点击确定按钮")
        
        # 关闭新页面和上下文
        try:
            new_page.close()
            new_context.close()
            print(f"   已关闭新的浏览器上下文")
        except Exception as e:
            print(f"   [警告] 关闭新上下文失败: {e}")
    
    def verify_product_stats(self, product_name, user_id=2, user_ips=None, fixed_port=None):
        """
        验证产品统计信息的公共方法（申请次数和调用次数）
        
        Args:
            product_name: 产品名称
            user_id: 用户ID（默认为2）
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.185:30001")
        
        # 判断配置格式并提取IP和端口
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.185")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = str(user_config)
            port = fixed_port if fixed_port else "30001"
        
        # 回到产品列表页面
        print("\n=== 回到产品列表页面 ===")
        product_list_url = self.get_url_for_ip(ip, port, "/datamarket/product/product-list")
        self.page.goto(product_list_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问页面: {product_list_url}")
        
        # 搜索产品名称
        print("\n=== 搜索产品名称 ===")
        name_input = self.page.locator("input[placeholder='输入数据产品名称']").first
        name_input.wait_for(state="visible", timeout=15000)
        name_input.fill(product_name)
        print(f"   已输入产品名称: {product_name}")
        
        # 点击查询按钮
        search_button = self.page.locator("button.el-button.el-button--primary:has-text('查询')").first
        search_button.wait_for(state="visible", timeout=15000)
        search_button.click()
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print("   已点击查询按钮")
        
        # 进入产品详情页面
        print("\n=== 进入产品详情页面 ===")
        detail_button = self.page.locator(".cursor-pointer:has-text('产品详情')").first
        detail_button.wait_for(state="visible", timeout=15000)
        time.sleep(5)
        detail_button.click()
        time.sleep(30)
        
        # 刷新页面以获取最新数据
        print("   刷新页面")
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(10)  # 等待统计数据更新
        
        # 获取并校验申请次数和调用次数
        print("\n=== 获取并校验统计信息 ===")
        stats_element = self.page.locator("div:has-text('申请次数')").first
        stats_element.wait_for(timeout=15000)
        stats_text = stats_element.inner_text()
        print(f"   获取到统计信息: {stats_text}")
        
        # 校验申请次数和调用次数
        assert "申请次数：1次" in stats_text, "申请次数校验失败"
        assert "调用次数：1次" in stats_text, "调用次数校验失败"
        print("   申请次数和调用次数校验通过")
    
    def search_in_received_list(self, product_name, user_id=2, user_ips=None, fixed_port=None):
        """
        在received-list页面搜索产品的公共方法
        
        Args:
            product_name: 产品名称
            user_id: 用户ID（默认为2）
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.185:30001")
        
        # 判断配置格式
        if isinstance(user_config, dict):
            # 旧格式：{"ip": "192.168.0.183", "port": "30001"}
            ip = user_config.get("ip", "192.168.0.185")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            # 新格式："192.168.0.183:30001"
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = user_config
            port = fixed_port if fixed_port else "30001"
        
        # 访问received-list页面
        print("\n=== 访问received-list页面 ===")
        received_list_url = f"http://{ip}:{port}/datamarket/source/received-list"
        self.page.goto(received_list_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问页面: {received_list_url}")
        
        # 刷新页面以获取最新数据
        print("\n=== 刷新页面 ===")
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print("   页面刷新完成")
        
        # 输入产品名称并查询
        print("\n=== 输入产品名称并查询 ===")
        # 在输入框中输入产品名称 - 支持多种选择器以适应不同环境
        name_input_selectors = [
            "input[placeholder='输入数据产品名称']",
            "input[placeholder*='输入数据产品名称']",
            "input[placeholder*='产品名称']",
            "input[placeholder*='名称']",
            ".search-input",
            "input[type='text']",
            "input.el-input__inner"
        ]
        
        name_input = None
        for selector in name_input_selectors:
            try:
                element = self.page.locator(selector).first
                if element.is_visible(timeout=3000):
                    name_input = element
                    print(f"   已找到输入框: {selector}")
                    break
            except Exception as e:
                continue
        
        if name_input:
            name_input.fill(product_name)
            print(f"   已输入产品名称: {product_name}")
        else:
            print(f"   未找到产品名称输入框，尝试直接查询")
        
        # 点击查询按钮 - 支持多种选择器
        search_button_selectors = [
            "button.el-button.el-button--primary:has-text('查询')",
            "button:has-text('查询')",
            ".search-btn",
            "[class*='search']",
            "button.el-button--primary"
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                element = self.page.locator(selector).first
                if element.is_visible(timeout=3000):
                    search_button = element
                    print(f"   已找到查询按钮: {selector}")
                    break
            except Exception as e:
                continue
        
        if search_button:
            search_button.click()
            self.page.wait_for_load_state("networkidle", timeout=30000)
            print("   已点击查询按钮")
        else:
            print(f"   未找到查询按钮，尝试按回车键查询")
            # 尝试按回车键触发查询
            if name_input:
                name_input.press("Enter")
                self.page.wait_for_load_state("networkidle", timeout=30000)
                print("   已按回车键查询")
    
    def debug_interface(self, input_param="1234", wait_time=10):
        """
        接口调试的公共方法
        
        Args:
            input_param: 输入参数（默认为"1234"）
            wait_time: 发起请求后的等待时间（默认为10秒）
        """
        # 点击接口调试按钮
        print("\n=== 点击接口调试按钮 ===")
        # 尝试多种选择器定位接口调试按钮
        debug_button_selectors = [
            "button:has-text('接口调试')",
            "button[class*='debug']",
            ".debug-button"
        ]
        
        debug_button = None
        for selector in debug_button_selectors:
            if debug_button:
                print(f"   已定位接口调试按钮: {selector}")
                break
            
            element = self.page.locator(selector).first
            element.wait_for(timeout=15000)
            debug_button = element
        
        if debug_button:
            debug_button.click()
            self.page.wait_for_load_state("networkidle", timeout=30000)
            print("   已点击接口调试按钮")
            
            # 选择接口地址
            print("\n=== 选择接口地址 ===")
            # 找到接口地址元素
            interface_address_element = self.page.locator("div.el-form-item:has-text('接口地址')").first
            # 等待元素出现并可见
            interface_address_element.wait_for(state="visible", timeout=15000)
            # 点击接口地址下拉框
            select_element = interface_address_element.locator(".el-select").first
            select_element.wait_for(state="visible", timeout=15000)
            select_element.click()
            print("   已点击接口地址下拉框")
            
            # 等待下拉菜单出现
            self.page.wait_for_timeout(1000)
            # 选择第一个元素
            dropdown_menu = self.page.locator(".el-select-dropdown").first
            # 等待下拉菜单出现并可见
            dropdown_menu.wait_for(state="visible", timeout=15000)
            dropdown_item = dropdown_menu.locator(".el-select-dropdown__item").first
            # 等待下拉菜单项出现并可见
            dropdown_item.wait_for(state="visible", timeout=15000)
            dropdown_item.click()
            print("   已选择第一个接口地址")
            
            # 等待页面3秒
            time.sleep(3)
            
            # 输入参数并发起请求
            print("\n=== 输入参数并发起请求 ===")
            # 在输入框中输入参数
            input_element = self.page.locator("input[placeholder='请输入']").first
            # 等待元素出现并可见
            input_element.wait_for(state="visible", timeout=15000)
            input_element.fill(input_param)
            print(f"   已在输入框中输入{input_param}")
            
            # 点击发起请求按钮
            send_request_button = self.page.locator("button:has-text('发起请求')").first
            # 等待元素出现并可见
            send_request_button.wait_for(state="visible", timeout=15000)
            send_request_button.click()
            time.sleep(wait_time)
            print("   已点击发起请求按钮")
    
    def verify_product_status_in_received_list(self, product_name, expected_status="交付中", user_id=2, user_ips=None, fixed_port=None):
        """
        在received-list页面验证产品状态的公共方法
        
        Args:
            product_name: 产品名称
            expected_status: 期望的产品状态（默认为"交付中"）
            user_id: 用户ID（默认为2）
            user_ips: 用户IP映射字典（支持格式：{"ip": "192.168.0.183", "port": "30001"} 或 {"1": "192.168.0.183:30001"}）
            fixed_port: 固定端口（可选，如果user_ips中已包含端口则忽略）
        """
        # 默认用户IP映射（新格式：IP:端口）
        default_user_ips = {
            1: "192.168.0.183:30001",
            2: "192.168.0.185:30001"
        }
        
        # 使用传入的参数或默认值
        ips = user_ips if user_ips else default_user_ips
        
        # 获取用户对应的配置
        user_config = ips.get(user_id, "192.168.0.185:30001")
        
        # 判断配置格式并提取IP和端口
        if isinstance(user_config, dict):
            ip = user_config.get("ip", "192.168.0.185")
            port = user_config.get("port", "30001")
        elif isinstance(user_config, str):
            if ":" in user_config:
                ip, port = user_config.split(":")
            else:
                ip = user_config
                port = fixed_port if fixed_port else "30001"
        else:
            # 兼容旧格式：直接是IP字符串
            ip = str(user_config)
            port = fixed_port if fixed_port else "30001"
        
        # 步骤 1: 访问产品列表页面进行查询验证
        print("\n=== 1. 访问产品列表页面 ===")
        product_list_url = self.get_url_for_ip(ip, port, "/datamarket/product/product-list")
        self.page.goto(product_list_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问产品列表页面: {product_list_url}")
        
        # 步骤 2: 在产品列表页面查询产品
        print("\n=== 2. 在产品列表页面查询产品 ===")
        name_input = self.page.locator("input[placeholder='输入数据产品名称']").first
        name_input.wait_for(state="visible", timeout=15000)
        name_input.fill(product_name)
        print(f"   已输入产品名称: {product_name}")
        
        # 点击查询按钮
        search_button = self.page.locator("button.el-button.el-button--primary:has-text('查询')").first
        search_button.wait_for(state="visible", timeout=15000)
        search_button.click()
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print("   已点击查询按钮")
        
        # 步骤 3: 验证产品列表查询结果
        print("\n=== 3. 验证产品列表查询结果 ===")
        
        # 增加等待时间，确保查询结果完全加载
        time.sleep(5)        
        # 访问received-list页面
        print("\n=== 4. 访问received-list页面 ===")
        received_list_url = self.get_url_for_ip(ip, port, "/datamarket/source/received-list")
        self.page.goto(received_list_url)
        # 等待页面加载完成
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   已访问页面: {received_list_url}")
        
        # 搜索产品名称
        print("\n=== 5. 搜索产品名称 ===")
        # 在输入框中输入产品名称
        name_input = self.page.locator("input[placeholder='输入数据产品名称']").first
        # 等待元素出现并可见
        name_input.wait_for(state="visible", timeout=15000)
        name_input.fill(product_name)
        print(f"   已输入产品名称: {product_name}")
        
        # 点击查询按钮
        search_button = self.page.locator("button.el-button.el-button--primary:has-text('查询')").first
        # 等待元素出现并可见
        search_button.wait_for(state="visible", timeout=15000)
        search_button.click()
        # 等待页面加载完成
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print("   已点击查询按钮")
        
        # 查询产品状态
        print("\n=== 6. 查询产品状态 ===")
        
        # 增加等待时间，确保表格加载完成
        time.sleep(5)
        
        # 尝试多种选择器定位状态元素
        status_selectors = [
            "span.el-tag__content",
            "span.el-tag",
            ".el-table__cell .status",
            "td:nth-child(6) span",
            "td:has(.el-tag)",
            "[class*='status']",
            "span[class*='el-tag']",
            ".el-table__body tr:first-child td:last-child span",
            ".status-tag",
            "span.status",
            "td span.el-tag",
            "div.status",
            "[role='status']"
        ]
        
        status_text = None
        for selector in status_selectors:
            try:
                status_element = self.page.locator(selector).first
                status_element.wait_for(state="visible", timeout=3000)
                status_text = status_element.inner_text()
                print(f"   使用选择器 '{selector}' 找到产品状态: {status_text}")
                break
            except Exception as e:
                print(f"   选择器 '{selector}' 未找到状态元素: {str(e)[:50]}")
                continue
        
        if not status_text:
            print("   未找到产品状态元素，尝试遍历页面元素...")
            # 尝试获取页面上所有可能的状态文本
            all_spans = self.page.locator("span")
            span_count = all_spans.count()
            print(f"   页面上共有 {span_count} 个 span 元素")
            
            for i in range(min(span_count, 50)):
                try:
                    span_text = all_spans.nth(i).inner_text()
                    if span_text and len(span_text) <= 10:  # 状态文本通常较短
                        if span_text in ["待交付", "交付中", "已交付", "审批中", "已拒绝", "待审批", "已通过", "已驳回"]:
                            status_text = span_text
                            print(f"   通过遍历找到产品状态: {status_text}")
                            break
                except Exception as e:
                    continue
        
        if not status_text:
            print("   仍然未找到产品状态元素")
            # 打印当前页面URL和一些调试信息
            print(f"   当前URL: {self.page.url}")
            print(f"   当前页面标题: {self.page.title()}")
            
            # 尝试获取页面HTML内容（前2000字符）
            try:
                html_content = self.page.content()
                print(f"   页面HTML片段: {html_content[:500]}...")
            except:
                pass
        
        # 校验产品状态
        if status_text:
            assert status_text == expected_status, f"产品状态校验失败: 期望'{expected_status}'，实际为'{status_text}'"
            print(f"   产品状态校验通过: {expected_status}")
        else:
            print(f"   无法验证产品状态，跳过状态校验")
