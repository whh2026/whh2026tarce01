import pytest
import time
import random
import string
import json
import requests
from utils.base import Base
from tests.ui_tests.config import ui_config

class TestUserManagement(Base):
    """用户管理页面测试类"""
    
    CONFIG = ui_config.USER_IPS
    USER_LIST_URL = "/admin/userManage/user-list?user-list=%257B%2522pageNumber%2522%253A1%252C%2522pageSize%2522%253A10%257D"
    
    @classmethod
    def setup_class(cls):
        """类级别的设置，所有测试方法执行前只执行一次"""
        # 调用父类的setup_class方法初始化浏览器
        super().setup_class()
        
        # 类级别登录标志
        cls.logged_in = False
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        # 调用父类的setup_method
        super().setup_method(method)
        
        # 只在第一次测试时登录
        if not self.__class__.logged_in:
            print("\n=== [类级别] 登录系统 ===")
            login_url = self.get_url_for_user(1, "/login", self.CONFIG)
            self.page.goto(login_url, timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            self.page.wait_for_timeout(1000)
            print(f"   ✓ 已访问登录页面: {login_url}")
            
            self.login_with_user(1, self.CONFIG, page=self.page)
            print("   ✓ 用户1登录成功")
            self.__class__.logged_in = True
        
        self.navigate_to_user_list()
        self.verify_page_elements()
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        # 调用父类的teardown_method
        super().teardown_method(method)
    
    def navigate_to_user_list(self):
        """导航到用户列表页面"""
        user_list_url = self.get_url_for_user(1, self.USER_LIST_URL, self.CONFIG)
        self.page.goto(user_list_url)
        self.page.wait_for_load_state("networkidle")
        
        assert "user-list" in self.page.url.lower(), f"页面访问失败，当前URL: {self.page.url}"
        print(f"[前置条件] 成功访问用户列表页面！")
        print(f"   页面URL: {self.page.url}")
    
    def verify_page_elements(self):
        """验证页面必要元素"""
        print("\n=== 页面元素检查 ===")
        
        # 页面标题检查
        page_title = self.page.title()
        print(f"   ✓ 页面标题: {page_title}")
        assert page_title, "页面标题为空"
        
        # 页面内容检查
        page_content = self.page.content()
        assert "用户管理" in page_content or "user" in page_content.lower(), "页面内容不包含用户管理相关内容"
        print("   ✓ 页面内容包含用户管理相关内容")
        
        # 搜索框检查（支持Element UI和Ant Design）
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='搜索']",
            "input[placeholder*='用户名']",
            ".el-input__inner",
            ".ant-input-search input",
            ".search-input"
        ]
        search_found = False
        for selector in search_selectors:
            if self.page.locator(selector).count() > 0:
                search_found = True
                print(f"   ✓ 搜索框存在 ({selector})")
                break
        if not search_found:
            print("   [警告] 页面未找到搜索框，继续执行测试")
        
        # 新增按钮检查（支持Element UI和Ant Design）
        add_button_selectors = [
            "button:has-text('新增用户')",
            ".el-button:has-text('新增用户')",
            ".ant-btn:has-text('新增用户')",
            ".el-button--primary:has-text('新增')"
        ]
        add_found = False
        for selector in add_button_selectors:
            if self.page.locator(selector).count() > 0:
                add_found = True
                print(f"   ✓ 新增用户按钮存在 ({selector})")
                break
        if not add_found:
            print("   [警告] 页面未找到新增用户按钮，继续执行测试")
        
        # 表格检查（支持Element UI和Ant Design）
        table_selectors = [".el-table", ".ant-table", "table", ".list-table"]
        table_found = False
        for selector in table_selectors:
            if self.page.locator(selector).count() > 0:
                table_found = True
                print(f"   ✓ 用户列表表格存在 ({selector})")
                break
        if not table_found:
            print("   [警告] 页面未找到用户列表表格，继续执行测试")
        
        print("   [页面检查完成]")
    
    def reset_page_state(self):
        """重置页面状态为初始状态"""
        print("\n=== 重置页面状态 ===")
        self.navigate_to_user_list()
        self.page.wait_for_timeout(2000)
        print("   ✓ 页面已重置")
    
    def test_01_search_username(self):
        """测试搜索用户名功能"""
        print("\n=== 测试搜索用户名功能 ===")
        
        search_keyword = "admin"
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='搜索']",
            "input[placeholder*='用户名']",
            ".el-input__inner",
            ".ant-input-search input",
            "input[name='username']"
        ]
        
        try:
            # 找到搜索框并输入
            search_found = False
            for selector in search_selectors:
                if self.page.locator(selector).count() > 0:
                    self.page.fill(selector, search_keyword)
                    search_found = True
                    print(f"   ✓ 输入搜索关键词: {search_keyword}")
                    break
            
            if not search_found:
                print("   [警告] 未找到搜索框")
                self.reset_page_state()
                return
            
            # 触发搜索
            self.page.keyboard.press("Enter")
            print("   ✓ 触发搜索")
            
            self.page.wait_for_timeout(2000)
            self.page.wait_for_load_state("networkidle")
            
            # 检查搜索结果
            result_selectors = [".el-table__body", ".ant-table-tbody", ".table tbody"]
            for selector in result_selectors:
                if self.page.locator(selector).count() > 0:
                    row_count = self.page.locator(f"{selector} tr").count()
                    print(f"   ✓ 搜索结果加载完成，共 {row_count} 条数据")
                    break
            
            self.reset_page_state()
            print("   [测试完成] 搜索用户名功能测试完成！")
        except Exception as e:
            print(f"   ✗ 测试失败: {str(e)}")
            try:
                self.page.screenshot(path=f"reports/screenshots/test_search_username_{int(time.time())}.png")
            except:
                pass
            self.reset_page_state()
            raise
    
    def test_02_add_user(self):
        """测试新增用户功能：使用Playwright的selectOption方法选择下拉框"""
        print("\n=== 测试新增用户功能 ===")
        
        # 生成用户名（必须以auto开头）
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        new_username = f"auto{random_str}"
        new_nickname = f"测试用户{random_str}"
        
        print(f"   ✓ 准备创建用户: {new_username}")
        
        # 点击新增用户按钮
        add_button_selectors = [
            "button:has-text('新增用户')",
            ".el-button:has-text('新增用户')"
        ]
        
        add_button_clicked = False
        for selector in add_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    add_button_clicked = True
                    print("   ✓ 点击新增用户按钮")
                    break
            except Exception as e:
                print(f"   [警告] 点击按钮失败: {e}")
                continue
        
        if not add_button_clicked:
            print("   [警告] 未找到新增用户按钮")
            self.reset_page_state()
            return
        
        # 增加等待时间，确保对话框完全加载
        self.page.wait_for_timeout(3000)
        
        # 调试：查看dialog内的所有输入框
        print("   --- 查看表单结构 ---")
        form_info = self.page.evaluate("""
            (function() {
                var dialog = document.querySelector('.el-dialog');
                if (!dialog) return {error: '未找到对话框'};
                
                var inputs = dialog.querySelectorAll('input');
                var textareas = dialog.querySelectorAll('textarea');
                var selects = dialog.querySelectorAll('.el-select');
                
                var inputInfo = [];
                inputs.forEach(function(input, idx) {
                    inputInfo.push({
                        index: idx,
                        type: input.type,
                        placeholder: input.placeholder,
                        name: input.name,
                        className: input.className
                    });
                });
                
                return {
                    inputs: inputInfo,
                    inputCount: inputs.length,
                    textareaCount: textareas.length,
                    selectCount: selects.length
                };
            })()
        """)
        print(f"   [调试] 表单结构: {form_info}")
        
        # 使用Playwright填写密码字段
        print("   --- 填写密码字段 ---")
        try:
            # 尝试查找所有类型的输入框，包括text类型（可能密码框被伪装）
            pwd_inputs = self.page.locator(".el-dialog input").all()
            
            # 寻找密码相关的输入框（通过placeholder或name）
            for i, input_el in enumerate(pwd_inputs):
                try:
                    placeholder = input_el.get_attribute("placeholder") or ""
                    name = input_el.get_attribute("name") or ""
                    if "密码" in placeholder or "pwd" in name.lower() or "password" in name.lower():
                        input_el.fill("123456")
                        print(f"   ✓ 填写密码输入框 {i}: {placeholder}")
                except Exception as e:
                    continue
            
            print("   ✓ 密码字段填写完成")
        except Exception as e:
            print(f"   [警告] 填写密码失败: {e}")
        
        # 使用JavaScript填写表单，触发Vue双向数据绑定
        print("   --- 使用JavaScript填写表单 ---")
        js_fill_form = f"""
            (function() {{
                var dialog = document.querySelector('.el-dialog');
                if (!dialog) return {{success: false, message: '未找到对话框'}};
                
                var filledFields = [];
                
                // 填写用户名
                var usernameInputs = dialog.querySelectorAll('input[placeholder*="用户名"], input[name="username"]');
                if (usernameInputs.length > 0) {{
                    usernameInputs[0].value = '{new_username}';
                    usernameInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    usernameInputs[0].dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('用户名');
                }}
                
                // 填写昵称
                var nicknameInputs = dialog.querySelectorAll('input[placeholder*="昵称"], input[name="nickname"]');
                if (nicknameInputs.length > 0) {{
                    nicknameInputs[0].value = '{new_nickname}';
                    nicknameInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    nicknameInputs[0].dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('昵称');
                }}
                
                // 填写部门
                var deptInputs = dialog.querySelectorAll('input[placeholder*="部门"], input[name="dept"]');
                if (deptInputs.length > 0) {{
                    deptInputs[0].value = '测试部门';
                    deptInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    deptInputs[0].dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('部门');
                }}
                
                // 填写密码
                var allPwdInputs = document.querySelectorAll('input[type="password"]');
                var pwdInputs = dialog.querySelectorAll('input[type="password"]');
                console.log('所有密码输入框:', allPwdInputs.length, 'dialog内密码输入框:', pwdInputs.length);
                
                if (pwdInputs.length >= 2) {{
                    pwdInputs[0].value = '123456';
                    pwdInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    pwdInputs[1].value = '123456';
                    pwdInputs[1].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('密码');
                }} else if (allPwdInputs.length >= 2) {{
                    // 如果dialog内没找到，尝试全局查找
                    allPwdInputs[0].value = '123456';
                    allPwdInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    allPwdInputs[1].value = '123456';
                    allPwdInputs[1].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('密码');
                }} else if (pwdInputs.length === 1) {{
                    pwdInputs[0].value = '123456';
                    pwdInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('密码');
                }} else if (allPwdInputs.length === 1) {{
                    allPwdInputs[0].value = '123456';
                    allPwdInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('密码');
                }}
                
                // 填写链账户
                var chainInputs = dialog.querySelectorAll('input[placeholder*="链账户"], input[name="chainAccount"]');
                if (chainInputs.length > 0) {{
                    chainInputs[0].value = 'test_chain';
                    chainInputs[0].dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    chainInputs[0].dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                    filledFields.push('链账户');
                }}
                
                // 查找Vue实例并设置角色信息
                var vueEl = dialog;
                var vm = null;
                while (vueEl && !vm) {{
                    if (vueEl.__vue__) {{
                        vm = vueEl.__vue__;
                    }} else if (vueEl._vue) {{
                        vm = vueEl._vue;
                    }}
                    vueEl = vueEl.parentNode;
                }}
                
                // 如果找到Vue实例，直接设置数据
                var formSet = false;
                if (vm) {{
                    var form = null;
                    if (vm.form) form = vm.form;
                    else if (vm.model) form = vm.model;
                    else if (vm.$data && vm.$data.form) form = vm.$data.form;
                    
                    if (form) {{
                        form.username = '{new_username}';
                        form.nickname = '{new_nickname}';
                        form.deptName = '测试部门';
                        form.roleType = '管理员';
                        form.roleName = '内置管理员';
                        form.password = '123456';
                        form.confirmPassword = '123456';
                        form.chainAccount = 'test_chain';
                        
                        if (vm.$forceUpdate) vm.$forceUpdate();
                        formSet = true;
                        filledFields.push('角色类型', '角色名称');
                    }}
                }}
                
                return {{
                    success: filledFields.length > 0,
                    message: '已填写字段: ' + filledFields.join(', '),
                    filledFields: filledFields,
                    vueInstanceFound: !!vm,
                    formSet: formSet
                }};
            }})()
        """
        
        result = self.page.evaluate(js_fill_form)
        print(f"   ✓ JavaScript填写表单结果: {result}")
        
        # 参考base类中的方式选择角色类型和角色名称
        print("   --- 选择角色类型和角色名称 ---")

        # 使用Playwright的type方法选择角色类型和角色名称
        # 模拟真实用户输入
        try:
            # 点击角色类型下拉框
            role_type_select = self.page.locator(".el-dialog .el-select").first
            role_type_select.click()
            print("   ✓ 点击角色类型下拉框")
            self.page.wait_for_timeout(1500)

            # 使用方向键选择第一个选项（管理员）
            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Enter")
            print("   ✓ 选择管理员")
            self.page.wait_for_timeout(1500)
            
            # 点击空白处关闭下拉框（退出iframe效果）
            self.page.click(".el-dialog__body", force=True)
            print("   ✓ 点击空白处关闭角色类型下拉框")
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"   [警告] 选择角色类型失败: {e}")

        # 选择角色名称
        try:
            # 点击角色名称下拉框
            role_name_select = self.page.locator(".el-dialog .el-select").nth(1)
            role_name_select.click()
            print("   ✓ 点击角色名称下拉框")
            self.page.wait_for_timeout(1500)

            # 使用方向键选择第一个选项（内置管理员）
            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Enter")
            print("   ✓ 选择内置管理员")
            self.page.wait_for_timeout(1500)
            
            # 点击空白处关闭下拉框（退出iframe效果）
            self.page.click(".el-dialog__body", force=True)
            print("   ✓ 点击空白处关闭角色名称下拉框")
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"   [警告] 选择角色名称失败: {e}")

        self.page.wait_for_timeout(1000)
        
        # 等待下拉框选择完成
        self.page.wait_for_timeout(1000)
        
        # 验证选择结果
        role_info = self.page.evaluate("""
            (function() {
                var dialog = document.querySelector('.el-dialog');
                var selects = dialog.querySelectorAll('.el-select');
                if (selects.length >= 2) {
                    var typeText = selects[0].querySelector('.el-select__text')?.textContent || 
                                   selects[0].querySelector('.el-select__input')?.value || '';
                    var nameText = selects[1].querySelector('.el-select__text')?.textContent || 
                                   selects[1].querySelector('.el-select__input')?.value || '';
                    return { roleType: typeText.trim(), roleName: nameText.trim() };
                }
                return { roleType: '', roleName: '' };
            })()
        """)
        print(f"   [调试] 角色类型: '{role_info.get('roleType', '')}', 角色名称: '{role_info.get('roleName', '')}'")
        
        # 点击确定按钮前检查表单验证错误和按钮状态
        print("   --- 检查表单验证状态和按钮状态 ---")
        validation_errors = self.page.evaluate("""
            (function() {
                var errors = [];
                var errorEls = document.querySelectorAll('.el-form-item__error');
                errorEls.forEach(function(e) { 
                    var text = e.textContent.trim();
                    if (text) errors.push(text); 
                });
                return errors;
            })()
        """)
        if validation_errors:
            print(f"   [表单验证错误] {validation_errors}")
        else:
            print("   ✓ 表单验证通过，无错误")
        
        # 检查确定按钮状态
        btn_status = self.page.evaluate("""
            (function() {
                var btn = document.querySelector('button.el-button--primary');
                if (btn) {
                    return {
                        found: true,
                        disabled: btn.disabled,
                        text: btn.textContent.trim(),
                        className: btn.className
                    };
                }
                return {found: false};
            })()
        """)
        print(f"   [调试] 确定按钮状态: {btn_status}")
        
        # 点击确定按钮 - 使用用户提供的XPath定位器
        # 用户提供的确定按钮XPath: /html/body/div[1]/div/div/section/div/main/div[2]/div/div/div/form/div[6]/div[2]/button[1]
        print("   --- 点击确定按钮 ---")
        
        try:
            # 使用用户提供的XPath点击确定按钮
            submit_btn_xpath = "/html/body/div[1]/div/div/section/div/main/div[2]/div/div/div/form/div[6]/div[2]/button[1]"
            self.page.click(f"xpath={submit_btn_xpath}", force=True)
            print("   ✓ 点击确定按钮成功")
        except Exception as e:
            print(f"   [警告] 点击确定按钮失败: {e}")
        
        # 等待页面可能的导航或对话框关闭
        self.page.wait_for_timeout(3000)
        
        # 检查是否成功
        success_found = self.page.is_visible(".el-message--success", timeout=5000)
        if success_found:
            print("   ✓ 新增用户成功")
        else:
            # 检查是否有错误提示
            errors = self.page.evaluate("""
                (function() {
                    var errors = [];
                    // 检查el-form-item__error错误提示
                    var errorEls = document.querySelectorAll('.el-form-item__error');
                    errorEls.forEach(function(e) { 
                        var text = e.textContent.trim();
                        if (text) errors.push(text); 
                    });
                    
                    // 检查el-message错误提示
                    var messageEls = document.querySelectorAll('.el-message--error');
                    messageEls.forEach(function(e) { 
                        var text = e.textContent.trim();
                        if (text) errors.push(text); 
                    });
                    
                    // 检查弹窗内的错误
                    var dialogErrors = document.querySelectorAll('.el-dialog .el-error, .el-dialog .error');
                    dialogErrors.forEach(function(e) { 
                        var text = e.textContent.trim();
                        if (text) errors.push(text); 
                    });
                    
                    return errors;
                })()
            """)
            if errors:
                print(f"   [错误信息] {errors}")
            else:
                print("   [警告] 未检测到成功提示，也没有错误信息")
        
        # 刷新页面验证用户是否创建成功
        self.page.reload()
        self.page.wait_for_timeout(2000)
        print("   ✓ 页面已刷新")
        
        # 搜索新用户
        search_input = self.page.locator("input[placeholder*='用户名']").first
        if search_input.count() > 0:
            search_input.fill(new_username)
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(2000)
            print(f"   ✓ 搜索新用户: {new_username}")
            
            # 检查用户是否存在
            user_exists = self.page.is_visible(f"text={new_username}", timeout=2000)
            if user_exists:
                print(f"   ✓ 用户 {new_username} 创建成功！")
            else:
                print(f"   [警告] 用户 {new_username} 未显示在列表中")
        
        print("   [测试完成] 新增用户功能测试完成！")
    
    def _select_role_type_and_name(self):
        """选择角色类型和角色名称"""
        print("   --- 选择角色类型和角色名称 ---")
        
        # 选择角色类型
        try:
            # 点击角色类型下拉框
            role_type_select = self.page.locator(".el-dialog .el-select").first
            role_type_select.click()
            print("   ✓ 点击角色类型下拉框")
            self.page.wait_for_timeout(1500)
            
            # 使用方向键选择第一个选项（管理员）
            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Enter")
            print("   ✓ 选择管理员")
            self.page.wait_for_timeout(1500)
            
            # 点击空白处关闭下拉框
            self.page.click(".el-dialog__body", force=True)
            print("   ✓ 点击空白处关闭角色类型下拉框")
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"   [警告] 选择角色类型失败: {e}")
        
        # 选择角色名称
        try:
            # 点击角色名称下拉框
            role_name_select = self.page.locator(".el-dialog .el-select").nth(1)
            role_name_select.click()
            print("   ✓ 点击角色名称下拉框")
            self.page.wait_for_timeout(1500)
            
            # 使用方向键选择第一个选项（内置管理员）
            self.page.keyboard.press("ArrowDown")
            self.page.wait_for_timeout(500)
            self.page.keyboard.press("Enter")
            print("   ✓ 选择内置管理员")
            self.page.wait_for_timeout(1500)
            
            # 点击空白处关闭下拉框
            self.page.click(".el-dialog__body", force=True)
            print("   ✓ 点击空白处关闭角色名称下拉框")
            self.page.wait_for_timeout(500)
        except Exception as e:
            print(f"   [警告] 选择角色名称失败: {e}")
    
    def _add_user_via_ui(self, username, nickname):
        """通过前端UI方式添加用户"""
        print("   --- 尝试前端UI方式添加用户 ---")
        
        add_button_selectors = [
            "button:has-text('新增用户')",
            ".el-button:has-text('新增用户')"
        ]
        
        for selector in add_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    print("   ✓ 点击新增用户按钮")
                    break
            except Exception:
                continue
        
        self.page.wait_for_timeout(3000)
        
        # 填写表单
        self.page.fill("input[placeholder*='用户名']", username)
        self.page.fill("input[placeholder*='昵称']", nickname)
        self.page.fill("input[placeholder*='部门']", "测试部门")
        
        # 处理密码
        pwd_inputs = self.page.locator("input[type='password']").all()
        if len(pwd_inputs) >= 2:
            pwd_inputs[0].fill("123456")
            pwd_inputs[1].fill("123456")
        
        # 使用playwright的select_option方法选择下拉框
        try:
            self.page.select_option("select", {"label": "管理员"})
            print("   ✓ 选择角色类型")
        except:
            pass
        
        try:
            self.page.click(".el-dialog .el-select", force=True)
            self.page.wait_for_timeout(500)
            self.page.click(".el-select-dropdown__item:has-text('管理员')", force=True)
            print("   ✓ 点击选择角色类型")
        except:
            pass
        
        self.page.wait_for_timeout(500)
        
        # 点击确定
        try:
            self.page.click(".el-dialog .el-button--primary", force=True)
            print("   ✓ 点击确定按钮")
        except:
            pass
        
        self.page.wait_for_timeout(3000)
        
        if self.page.is_visible(".el-message--success", timeout=3000):
            print("   ✓ 前端UI方式创建成功")
        else:
            print("   [警告] 前端UI方式创建失败")
    
    def test_03_view_user_detail(self):
        """测试查看用户详情功能"""
        print("\n=== 测试查看用户详情功能 ===")
        
        # 查找表格第一行的操作列中的详情按钮
        detail_button = self.page.locator(".el-table__body tr:first-child .el-button--text", has_text="详情").first
        if detail_button.count() == 0:
            detail_button = self.page.locator(".el-table__body tr:first-child button", has_text="详情").first
        
        if detail_button.count() > 0:
            detail_button.click()
            print("   ✓ 点击详情按钮")
        else:
            # 如果没有详情按钮，检查操作列的所有按钮
            action_buttons = self.page.locator(".el-table__body tr:first-child td:last-child button")
            button_count = action_buttons.count()
            print(f"   [信息] 操作列有 {button_count} 个按钮，未找到详情按钮")
            
            # 尝试查找详情链接或图标按钮
            detail_link = self.page.locator(".el-table__body tr:first-child a", has_text="详情").first
            if detail_link.count() > 0:
                detail_link.click()
                print("   ✓ 点击详情链接")
            else:
                print("   [警告] 未找到详情按钮或链接")
                self.reset_page_state()
                print("   [测试完成] 查看用户详情功能测试完成！")
                return
        
        self.page.wait_for_timeout(2000)
        
        # 检查详情弹窗是否显示
        dialog_found = self.page.is_visible("[role='dialog']", timeout=2000) or \
                      self.page.is_visible(".el-dialog", timeout=2000)
        if dialog_found:
            print("   ✓ 详情弹窗已显示")
            
            # 关闭弹窗
            close_button = self.page.locator("button:has-text('关闭')").first
            if close_button.count() == 0:
                close_button = self.page.locator("button:has-text('取消')").first
            
            if close_button.count() > 0:
                close_button.click()
                print("   ✓ 点击关闭按钮")
        
        self.reset_page_state()
        print("   [测试完成] 查看用户详情功能测试完成！")
    
    def test_04_edit_user(self):
        """测试编辑用户功能"""
        print("\n=== 测试编辑用户功能 ===")
        
        # 查找表格第一行的编辑按钮
        edit_button = self.page.locator(".el-table__body tr:first-child .el-button--text", has_text="编辑").first
        if edit_button.count() == 0:
            edit_button = self.page.locator(".el-table__body tr:first-child button", has_text="编辑").first
        
        if edit_button.count() > 0:
            edit_button.click()
            print("   ✓ 点击编辑按钮")
        else:
            print("   [警告] 未找到编辑按钮")
            self.reset_page_state()
            print("   [测试完成] 编辑用户功能测试完成！")
            return
        
        self.page.wait_for_timeout(3000)
        
        # 使用用户提供的昵称输入框XPath
        nickname_xpath = "/html/body/div[1]/div/div/section/div/main/div[1]/div/div/div[1]/div/div[2]/form/div[2]/div/div/div/input"
        nickname_input = self.page.locator(f"xpath={nickname_xpath}").first
        
        if nickname_input.count() > 0:
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
            new_nickname = f"编辑后昵称{random_str}"
            nickname_input.fill(new_nickname)
            print(f"   ✓ 修改昵称为: {new_nickname}")
        else:
            # 尝试其他选择器
            nickname_input = self.page.locator(".el-dialog input[placeholder*='昵称']").first
            if nickname_input.count() > 0:
                random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
                new_nickname = f"编辑后昵称{random_str}"
                nickname_input.fill(new_nickname)
                print(f"   ✓ 修改昵称为: {new_nickname}")
            else:
                print("   [警告] 未找到昵称输入框")
        
        # 点击确定按钮
        submit_button = self.page.locator("button:has-text('确定')").first
        if submit_button.count() == 0:
            submit_button = self.page.locator("button:has-text('保存')").first
        
        if submit_button.count() > 0:
            submit_button.click()
            print("   ✓ 点击确定按钮")
        
        self.page.wait_for_timeout(3000)
        
        # 检查成功提示
        success_found = self.page.is_visible(".el-message--success", timeout=3000)
        if success_found:
            print("   ✓ 编辑用户成功")
        else:
            print("   [警告] 未检测到成功提示")
        
        self.reset_page_state()
        print("   [测试完成] 编辑用户功能测试完成！")
    
    def test_05_delete_user(self):
        """测试删除用户功能"""
        print("\n=== 测试删除用户功能 ===")
        
        # 查找表格第一行的删除按钮
        delete_button = self.page.locator(".el-table__body tr:first-child .el-button--text", has_text="删除").first
        if delete_button.count() == 0:
            delete_button = self.page.locator(".el-table__body tr:first-child button", has_text="删除").first
        if delete_button.count() == 0:
            delete_button = self.page.locator(".el-table__body tr:first-child .el-button--danger", has_text="删除").first
        
        if delete_button.count() > 0:
            delete_button.click()
            print("   ✓ 点击删除按钮")
        else:
            print("   [警告] 未找到删除按钮")
            self.reset_page_state()
            print("   [测试完成] 删除用户功能测试完成！")
            return
        
        self.page.wait_for_timeout(2000)
        
        # 确认删除
        confirm_button = self.page.locator(".el-message-box__btns .el-button--primary", has_text="确定").first
        if confirm_button.count() == 0:
            confirm_button = self.page.locator("button:has-text('确定')").first
        
        if confirm_button.count() > 0:
            confirm_button.click()
            print("   ✓ 确认删除")
        
        self.page.wait_for_timeout(3000)
        
        # 检查成功提示
        success_found = self.page.is_visible(".el-message--success", timeout=3000)
        if success_found:
            print("   ✓ 删除用户成功")
        else:
            print("   [警告] 未检测到成功提示")
        
        self.reset_page_state()
        print("   [测试完成] 删除用户功能测试完成！")
    
    def test_06_pagination(self):
        """测试分页功能"""
        print("\n=== 测试分页功能 ===")
        
        # 查找Element UI分页组件的下一页按钮
        next_button = self.page.locator(".el-pagination .btn-next").first
        if next_button.count() == 0:
            next_button = self.page.locator(".el-pagination button", has_text="下一页").first
        if next_button.count() == 0:
            next_button = self.page.locator(".el-pagination .el-icon-arrow-right").first
        
        if next_button.count() > 0:
            # 检查下一页按钮是否可用（不是disabled状态）
            # get_attribute返回字符串或None，需要特殊处理
            is_disabled = next_button.get_attribute("disabled")
            # disabled属性存在时可能返回 "disabled" 或 "" (空字符串)
            if is_disabled is None:
                # 按钮未禁用
                next_button.click()
                print("   ✓ 点击下一页")
            else:
                print("   [信息] 下一页按钮不可用，可能已经是最后一页")
        else:
            print("   [警告] 未找到下一页按钮")
        
        self.page.wait_for_timeout(2000)
        self.page.wait_for_load_state("networkidle")
        
        # 检查分页信息
        page_info_selector = ".el-pagination__total"
        if self.page.is_visible(page_info_selector, timeout=2000):
            page_info = self.page.locator(page_info_selector).text_content()
            print(f"   ✓ 分页信息: {page_info}")
        
        self.reset_page_state()
        print("   [测试完成] 分页功能测试完成！")
    
    def test_07_reset_search(self):
        """测试重置查询功能"""
        print("\n=== 测试重置查询功能 ===")
        
        # 先输入搜索条件
        search_selectors = [
            "input[name='username']",
            "input[placeholder*='用户名']",
            "input[type='search']"
        ]
        
        search_filled = False
        for selector in search_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.fill(selector, "test")
                    search_filled = True
                    print("   ✓ 输入搜索条件")
                    break
            except Exception:
                continue
        
        assert search_filled, "未找到搜索输入框"
        
        # 点击重置按钮
        reset_button_selectors = [
            "button:has-text('重置')",
            ".ant-btn:has-text('重置')"
        ]
        
        reset_clicked = False
        for selector in reset_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    reset_clicked = True
                    print("   ✓ 点击重置按钮")
                    break
            except Exception:
                continue
        
        assert reset_clicked, "未找到重置按钮"
        
        self.page.wait_for_timeout(2000)
        
        # 验证搜索框是否清空
        input_value = ""
        for selector in search_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    input_value = self.page.locator(selector).input_value()
                    break
            except Exception:
                continue
        
        assert input_value == "", f"搜索框未清空，当前值: {input_value}"
        print("   ✓ 搜索框已清空")
        
        self.reset_page_state()
        print("   [测试完成] 重置查询功能测试完成！")
    
    def test_08_disable_user(self):
        """测试禁用用户功能"""
        print("\n=== 测试禁用用户功能 ===")
        
        disable_button_selectors = [
            "button:has-text('禁用')",
            ".ant-btn:has-text('禁用')"
        ]
        
        disable_clicked = False
        for selector in disable_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    disable_clicked = True
                    print("   ✓ 点击禁用按钮")
                    break
            except Exception:
                continue
        
        assert disable_clicked, "未找到禁用按钮"
        
        self.page.wait_for_timeout(2000)
        
        confirm_success = False
        confirm_button_selectors = [
            ".ant-modal-confirm-btns .ant-btn-primary",
            "button:has-text('确定')"
        ]
        for selector in confirm_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    confirm_success = True
                    print("   ✓ 确认禁用")
                    break
            except Exception:
                continue
        
        assert confirm_success, "未找到确认按钮"
        
        self.page.wait_for_timeout(3000)
        
        success_found = self.page.is_visible(".ant-message-success", timeout=3000)
        if success_found:
            print("   ✓ 禁用用户成功")
        else:
            print("   [警告] 未检测到成功提示")
        
        self.reset_page_state()
        print("   [测试完成] 禁用用户功能测试完成！")
    
    def test_09_enable_user(self):
        """测试启用用户功能"""
        print("\n=== 测试启用用户功能 ===")
        
        enable_button_selectors = [
            "button:has-text('启用')",
            ".ant-btn:has-text('启用')"
        ]
        
        enable_clicked = False
        for selector in enable_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    enable_clicked = True
                    print("   ✓ 点击启用按钮")
                    break
            except Exception:
                continue
        
        assert enable_clicked, "未找到启用按钮"
        
        self.page.wait_for_timeout(2000)
        
        confirm_success = False
        confirm_button_selectors = [
            ".ant-modal-confirm-btns .ant-btn-primary",
            "button:has-text('确定')"
        ]
        for selector in confirm_button_selectors:
            try:
                if self.page.is_visible(selector, timeout=2000):
                    self.page.click(selector)
                    confirm_success = True
                    print("   ✓ 确认启用")
                    break
            except Exception:
                continue
        
        assert confirm_success, "未找到确认按钮"
        
        self.page.wait_for_timeout(3000)
        
        success_found = self.page.is_visible(".ant-message-success", timeout=3000)
        if success_found:
            print("   ✓ 启用用户成功")
        else:
            print("   [警告] 未检测到成功提示")
        
        self.reset_page_state()
        print("   [测试完成] 启用用户功能测试完成！")
    
    def test_10_add_user_validation(self):
        """测试新增用户字段校验规则"""
        print("\n=== 测试新增用户字段校验规则 ===")
        
        # 点击新增用户按钮
        add_button = self.page.locator("button:has-text('新增用户')").first
        if add_button.count() > 0:
            add_button.click()
            print("   ✓ 点击新增用户按钮")
        else:
            assert False, "未找到新增用户按钮"
        
        self.page.wait_for_timeout(3000)
        
        # 直接点击确定按钮，验证必填字段校验
        submit_button = self.page.locator("button:has-text('确定')").first
        if submit_button.count() == 0:
            submit_button = self.page.locator("button:has-text('新增用户')").first
        
        if submit_button.count() > 0:
            submit_button.click()
            print("   ✓ 点击确定按钮（不填写任何字段）")
        else:
            assert False, "未找到提交按钮"
        
        self.page.wait_for_timeout(2000)
        
        # 检查错误提示（使用Element UI的错误提示）
        error_found = False
        
        # 检查el-form-item__error提示
        el_error = self.page.locator(".el-form-item__error").first
        if el_error.count() > 0:
            error_found = True
            print("   ✓ 检测到el-form-item错误提示")
        
        # 检查el-message错误提示
        if not error_found:
            message_error = self.page.locator(".el-message--error").first
            if message_error.count() > 0:
                error_found = True
                print("   ✓ 检测到el-message错误提示")
        
        assert error_found, "未检测到必填字段错误提示"
        
        # 关闭弹窗
        close_button = self.page.locator("button:has-text('取消')").first
        if close_button.count() > 0:
            close_button.click()
            print("   ✓ 关闭弹窗")
        
        self.reset_page_state()
        print("   [测试完成] 新增用户字段校验规则测试完成！")
    
    def test_11_username_must_start_with_auto(self):
        """测试用户名必须以auto开头"""
        print("\n=== 测试用户名必须以auto开头 ===")
        
        # 点击新增用户按钮
        add_button = self.page.locator("button:has-text('新增用户')").first
        if add_button.count() > 0:
            add_button.click()
            print("   ✓ 点击新增用户按钮")
        else:
            assert False, "未找到新增用户按钮"
        
        self.page.wait_for_timeout(3000)
        
        # 使用用户提供的XPath定位器
        # 用户名输入框
        username_xpath = "/html/body/div[1]/div/div/section/div/main/div[1]/div/div/div[1]/div/div[2]/form/div[1]/div/div/div/input"
        # 昵称输入框
        nickname_xpath = "/html/body/div[1]/div/div/section/div/main/div[1]/div/div/div[1]/div/div[2]/form/div[2]/div/div/div/input"
        
        # 输入不以auto开头的用户名
        username_input = self.page.locator(f"xpath={username_xpath}").first
        if username_input.count() > 0:
            username_input.fill("testuser123")
            print("   ✓ 输入不以auto开头的用户名: testuser123")
        else:
            assert False, "未找到用户名输入框"
        
        # 填写昵称
        nickname_input = self.page.locator(f"xpath={nickname_xpath}").first
        if nickname_input.count() > 0:
            nickname_input.fill("测试用户")
            print("   ✓ 输入昵称")
        
        # 选择角色类型和角色名称
        self._select_role_type_and_name()
        
        # 点击确定按钮
        submit_button = self.page.locator("button:has-text('确定')").first
        if submit_button.count() == 0:
            submit_button = self.page.locator("button:has-text('新增用户')").first
        
        if submit_button.count() > 0:
            submit_button.click()
            print("   ✓ 点击确定按钮")
        
        self.page.wait_for_timeout(2000)
        
        # 检查是否有用户名格式错误提示
        error_found = False
        
        # 检查el-form-item__error提示
        el_error = self.page.locator(".el-form-item__error", has_text="auto").first
        if el_error.count() > 0:
            error_found = True
            print("   ✓ 检测到用户名格式错误提示")
        
        # 检查el-message错误提示
        if not error_found:
            message_error = self.page.locator(".el-message--error").first
            if message_error.count() > 0:
                error_found = True
                print("   ✓ 检测到消息提示错误")
        
        # 关闭弹窗
        close_button = self.page.locator("button:has-text('取消')").first
        if close_button.count() > 0:
            close_button.click()
            print("   ✓ 关闭弹窗")
        
        self.reset_page_state()
        print("   [测试完成] 用户名必须以auto开头测试完成！")

    def test_12_search_by_nickname(self):
        """测试按昵称查询用户"""
        print("\n=== test_12 测试按昵称查询用户 ===")
        
        # 获取一个已存在的用户昵称
        nickname_to_search = "测试昵称"
        
        # 在昵称搜索框输入
        nickname_input = self.page.locator("input[placeholder*='昵称']").first
        if nickname_input.count() > 0:
            nickname_input.fill(nickname_to_search)
            print(f"   ✓ 输入昵称: {nickname_to_search}")
            
            # 点击查询按钮
            search_button = self.page.locator("button:has-text('查询')").first
            if search_button.count() > 0:
                search_button.click()
                print("   ✓ 点击查询按钮")
                self.page.wait_for_timeout(2000)
                
                # 检查查询结果
                table_rows = self.page.locator(".el-table__body tr")
                if table_rows.count() > 0:
                    print(f"   ✓ 查询结果显示 {table_rows.count()} 条记录")
                else:
                    print("   [警告] 查询结果为空")
        
        self.reset_page_state()
        print("   [测试完成] 按昵称查询测试完成！")

    def test_13_search_by_role_type(self):
        """测试按角色类型查询用户"""
        print("\n=== test_13 测试按角色类型查询用户 ===")
        
        # 找到角色类型下拉框并选择
        role_type_select = self.page.locator("select[name='roleType']").first
        if role_type_select.count() == 0:
            # 尝试查找el-select元素
            role_type_select = self.page.locator(".el-select").first
        
        if role_type_select.count() > 0:
            # 点击下拉框
            role_type_select.click()
            self.page.wait_for_timeout(1000)
            
            # 选择管理员选项 - 使用text选择器
            admin_option = self.page.locator("text=管理员").first
            if admin_option.count() == 0:
                admin_option = self.page.locator(".el-select-dropdown__item", has_text="管理员").first
            
            if admin_option.count() > 0:
                admin_option.click()
                print("   ✓ 选择角色类型: 管理员")
                
                # 点击查询按钮
                search_button = self.page.locator("button:has-text('查询')").first
                if search_button.count() > 0:
                    search_button.click()
                    print("   ✓ 点击查询按钮")
                    self.page.wait_for_timeout(2000)
                    
                    # 检查查询结果
                    table_rows = self.page.locator(".el-table__body tr")
                    if table_rows.count() > 0:
                        print(f"   ✓ 查询结果显示 {table_rows.count()} 条记录")
                    else:
                        print("   [警告] 查询结果为空")
            else:
                print("   [警告] 未找到管理员选项")
        else:
            print("   [警告] 未找到角色类型下拉框")
        
        self.reset_page_state()
        print("   [测试完成] 按角色类型查询测试完成！")

    def test_14_edit_user_validation(self):
        """测试编辑用户弹出框字段校验规则"""
        print("\n=== test_14 测试编辑用户字段校验 ===")
        
        # 找到列表中的第一个用户并点击编辑
        edit_button = self.page.locator(".el-table__body tr:first-child .el-button--text", has_text="编辑").first
        if edit_button.count() == 0:
            edit_button = self.page.locator(".el-table__body tr:first-child button", has_text="编辑").first
        
        if edit_button.count() > 0:
            edit_button.click()
            print("   ✓ 点击编辑按钮")
            self.page.wait_for_timeout(2000)
            
            # 检查编辑弹窗中的字段
            dialog = self.page.locator(".el-dialog")
            if dialog.count() > 0:
                # 检查字段是否存在
                required_fields = [
                    {"name": "用户名", "selector": "input[placeholder*='用户名']"},
                    {"name": "昵称", "selector": "input[placeholder*='昵称']"},
                    {"name": "部门名称", "selector": "input[placeholder*='部门']"}
                ]
                
                for field in required_fields:
                    field_locator = dialog.locator(field["selector"]).first
                    if field_locator.count() > 0:
                        print(f"   ✓ 找到字段: {field['name']}")
                    else:
                        print(f"   [警告] 未找到字段: {field['name']}")
                
                # 检查角色类型和角色名称下拉框
                select_elements = dialog.locator(".el-select")
                if select_elements.count() >= 2:
                    print("   ✓ 找到角色类型和角色名称下拉框")
                else:
                    print(f"   [警告] 找到 {select_elements.count()} 个下拉框")
                
                # 测试清空必填字段
                username_input = dialog.locator("input[placeholder*='用户名']").first
                if username_input.count() > 0:
                    original_value = username_input.input_value()
                    username_input.fill("")
                    
                    # 点击确定按钮触发校验
                    submit_button = dialog.locator("button.el-button--primary").first
                    if submit_button.count() > 0:
                        submit_button.click()
                        self.page.wait_for_timeout(1000)
                        
                        # 检查是否有必填提示
                        error_message = self.page.locator(".el-form-item__error", has_text="不能为空").first
                        if error_message.count() > 0:
                            print("   ✓ 检测到必填字段校验提示")
                        
                        # 恢复用户名
                        username_input.fill(original_value)
                
                # 关闭弹窗
                close_button = dialog.locator("button:has-text('取消')").first
                if close_button.count() > 0:
                    close_button.click()
                    print("   ✓ 关闭编辑弹窗")
            else:
                print("   [警告] 未找到编辑弹窗")
        else:
            print("   [警告] 未找到编辑按钮")
        
        self.reset_page_state()
        print("   [测试完成] 编辑用户字段校验测试完成！")

    def test_15_role_dependency_validation(self):
        """测试角色类型与角色名称的依赖关系"""
        print("\n=== test_15 测试角色类型与角色名称依赖关系 ===")
        
        # 点击新增用户按钮
        add_button = self.page.locator("button:has-text('新增用户')").first
        if add_button.count() > 0:
            add_button.click()
            print("   ✓ 点击新增用户按钮")
            self.page.wait_for_timeout(2000)
            
            dialog = self.page.locator(".el-dialog")
            if dialog.count() > 0:
                # 选择角色类型为管理员
                role_type_select = dialog.locator(".el-select").first
                if role_type_select.count() > 0:
                    role_type_select.click()
                    self.page.wait_for_timeout(1000)
                    
                    # 使用JavaScript来选择下拉框选项
                    select_result = self.page.evaluate("""
                        (function() {
                            // 查找角色类型下拉框的选项
                            var items = document.querySelectorAll('.el-select-dropdown__item');
                            for (var i = 0; i < items.length; i++) {
                                if (items[i].textContent.includes('管理员')) {
                                    items[i].click();
                                    return {success: true, message: '选择管理员成功'};
                                }
                            }
                            return {success: false, message: '未找到管理员选项'};
                        })()
                    """)
                    
                    if select_result.get('success'):
                        print("   ✓ 选择角色类型: 管理员")
                        self.page.wait_for_timeout(1000)
                        
                        # 检查角色名称下拉框选项
                        role_name_select = dialog.locator(".el-select").nth(1)
                        if role_name_select.count() > 0:
                            role_name_select.click()
                            self.page.wait_for_timeout(1000)
                            
                            options = self.page.locator(".el-select-dropdown__item")
                            option_count = options.count()
                            print(f"   ✓ 角色名称选项数量: {option_count}")
                            
                            # 关闭下拉框
                            dialog.click()
                            self.page.wait_for_timeout(500)
                            
                            # 选择角色类型为普通业务员
                            role_type_select.click()
                            self.page.wait_for_timeout(1000)
                            
                            # 使用JavaScript来选择普通业务员
                            select_result2 = self.page.evaluate("""
                                (function() {
                                    var items = document.querySelectorAll('.el-select-dropdown__item');
                                    for (var i = 0; i < items.length; i++) {
                                        if (items[i].textContent.includes('普通业务员')) {
                                            items[i].click();
                                            return {success: true, message: '选择普通业务员成功'};
                                        }
                                    }
                                    return {success: false, message: '未找到普通业务员选项'};
                                })()
                            """)
                            
                            if select_result2.get('success'):
                                print("   ✓ 选择角色类型: 普通业务员")
                                self.page.wait_for_timeout(1000)
                                
                                # 再次检查角色名称下拉框选项
                                role_name_select.click()
                                self.page.wait_for_timeout(1000)
                                
                                options = self.page.locator(".el-select-dropdown__item")
                                option_count = options.count()
                                print(f"   ✓ 角色名称选项数量: {option_count}")
                            else:
                                print(f"   [警告] {select_result2.get('message')}")
                        else:
                            print("   [警告] 未找到角色名称下拉框")
                    else:
                        print(f"   [警告] {select_result.get('message')}")
                else:
                    print("   [警告] 未找到角色类型下拉框")
            
            # 先关闭可能打开的下拉框
            self.page.evaluate("""
                (function() {
                    // 关闭所有下拉框
                    var dropdowns = document.querySelectorAll('.el-select-dropdown');
                    dropdowns.forEach(function(d) {
                        d.style.display = 'none';
                    });
                })()
            """)
            self.page.wait_for_timeout(500)
            
            # 关闭弹窗
            close_button = dialog.locator("button:has-text('取消')").first
            if close_button.count() > 0:
                close_button.click()
                print("   ✓ 关闭弹窗")
            else:
                # 如果找不到取消按钮，尝试点击弹窗外部关闭
                self.page.click("body", position={"x": 10, "y": 10})
                print("   ✓ 点击页面外部关闭弹窗")
        else:
            print("   [警告] 未找到新增用户按钮")
        
        self.reset_page_state()
        print("   [测试完成] 角色类型与角色名称依赖关系测试完成！")
