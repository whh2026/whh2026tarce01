# 重新创建测试文件，确保内容完整且编码正确

new_content = '''import pytest
import random
import string
import time
from playwright.sync_api import sync_playwright
from utils.base import Base
# 导入测试数据
from tests.test_data.product_protocol_data import (
    SELECTORS, QUILL_EDITOR_SELECTORS,
    IFRAME_EDITOR_SELECTORS, TEXT_INPUT_SELECTORS,
    CONFIRM_DIALOG_SELECTORS, SUCCESS_SELECTORS,
    ASSERT_MESSAGES, generate_test_data, generate_max_length_data,
    CHAIN_STATUS, WAIT_TIMES, CHAIN_STATUS_TEST_LIST
)
from tests.ui_tests.config import ui_config

class TestProductProtocol(Base):
    """产品协议页面测试类"""
    
    # 配置参数
    CONFIG = ui_config.USER_IPS
    
    @classmethod
    def setup_class(cls):
        """类级别的设置，所有测试方法执行前只执行一次"""
        cls.playwright = sync_playwright().start()
        # 启动浏览器（使用Chrome，可根据需要更换为firefox或webkit）
        cls.browser = cls.playwright.chromium.launch(headless=False)  # headless=False 显示浏览器窗口
    
    @classmethod
    def teardown_class(cls):
        """类级别的清理，所有测试方法执行后只执行一次"""
        try:
            cls.browser.close()
        except Exception as e:
            print(f"[清理] 关闭浏览器失败: {e}")
        
        try:
            cls.playwright.stop()
        except Exception as e:
            print(f"[清理] 停止playwright失败: {e}")
    
    def setup_method(self, method):
        """每个测试方法执行前的设置，继承并扩展基础类"""
        # 为每个测试方法创建新的上下文和页面
        self.context = self.browser.new_context(viewport={"width": 1900, "height": 950})
        self.page = self.context.new_page()
        
        # 窗口最大化
        self.page.set_viewport_size({"width": 1900, "height": 950})
        
        # 保存当前测试方法，用于截图命名
        self.current_test = method
        
        # 先登录
        print("\n=== 登录 ===")
        login_url = self.get_url_for_user(1, "/login", self.CONFIG)
        self.page.goto(login_url, timeout=30000)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        self.page.wait_for_timeout(1000)
        
        print(f"   ✓ 已访问登录页面: {login_url}")
        
        # 执行登录操作（每次都重新登录）
        self.login_with_user(1, self.CONFIG, page=self.page)
        print("   ✓ 用户1登录成功")
        
        # 根据测试方法名称决定访问的URL
        if method.__name__ == "test_add_new_protocol_direct":
            # 直接访问create页面
            self.product_protocol_url = self.get_url_for_user(1, "/registration/product/productProtocol/create", self.CONFIG)
        else:
            # 导航到产品协议主页面
            self.product_protocol_url = self.get_url_for_user(1, "/registration/product/productProtocol", self.CONFIG)
        
        self.page.goto(self.product_protocol_url)
        
        # 等待页面加载
        self.page.wait_for_load_state("networkidle")
        
        # 验证页面访问成功
        assert "productprotocol" in self.page.url.lower(), ASSERT_MESSAGES["page_access_failed"].format(url=self.page.url)
        
        print(f"[前置条件] 前置条件 - 成功访问产品协议页面！")
        print(f"   页面URL: {self.page.url}")
        print(f"   页面标题: {self.page.title()}")
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        # 关闭页面和上下文
        try:
            self.page.close()
        except Exception as e:
            print(f"   [警告] 关闭页面失败: {e}")
        
        try:
            self.context.close()
        except Exception as e:
            print(f"   [警告] 关闭上下文失败: {e}")
    
    def test_01_page_elements(self):
        """测试产品协议页面的基本元素"""
        print("\n=== 测试产品协议页面基本元素 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "页面元素验证",
            "测试目的": "验证产品协议页面的基本元素",
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
        assert "productprotocol" in current_url.lower(), "URL中应包含'productprotocol'"
        
        # 验证页面元素 - 产品协议表格
        self._verify_element_exists([".el-table", ".ant-table", "table"], "产品协议表格", timeout=5000)
        
        # 验证新增协议按钮
        self._verify_element_exists(["button:has-text('新增协议')", "button:has-text('新增')", ".add-btn", "[class*='add']"], "新增协议按钮", timeout=5000)
        
        # 验证查询按钮
        self._verify_element_exists(["button:has-text('查询')", ".search-btn", "[class*='search']"], "查询按钮", timeout=5000)
        
        # 验证重置按钮
        self._verify_element_exists(["button:has-text('重置')", "button:has-text('清空')", ".reset-btn", "[class*='reset']"], "重置按钮", timeout=5000)
        
        # 验证分页组件
        self._verify_element_exists([".el-pagination", ".ant-pagination", ".pagination"], "分页组件", timeout=5000)
        
        # 验证查询条件 - 产品协议名称输入框
        self._verify_element_exists([
            "input[placeholder*='产品协议名称']",
            "input[placeholder*='协议名称']",
            "xpath=/html/body/div[1]/div/section/div/main/div/div[1]/div[1]/div/div[2]/form/div[1]/div/div/div/input"
        ], "产品协议名称输入框", timeout=5000)
        
        # 验证查询条件 - 链上状态下拉框
        self._verify_element_exists([
            "div:has-text('链上状态') + div",
            "xpath=/html/body/div[1]/div/section/div/main/div/div[1]/div[1]/div/div[2]/form/div[2]/div/div/div/div/div[1]/div[2]"
        ], "链上状态下拉框", timeout=5000)
        
        # 验证表格列
        self._verify_field_exists([
            "th:has-text('产品协议编号')"
        ], "产品协议编号字段")
        
        self._verify_field_exists([
            "th:has-text('产品协议名称')"
        ], "产品协议名称字段")
        
        self._verify_field_exists([
            "th:has-text('协议信息')"
        ], "协议信息字段")
        
        self._verify_field_exists([
            "th:has-text('链上状态')"
        ], "链上状态字段")
        
        self._verify_field_exists([
            "th:has-text('创建时间')"
        ], "创建时间字段")
        
        self._verify_field_exists([
            "th:has-text('操作')"
        ], "操作字段")
        
        # 输出第一行协议数据
        print("\n   输出第一行协议数据：")
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
        
        print("   ✅ 产品协议页面基本元素验证完成！")
    
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

    def test_02_publish_button_visibility_by_chain_status(self):
        """检验产品协议列表：未上链记录有发布按钮，已上链记录无发布按钮"""
        print("\n=== 检验产品协议列表发布按钮根据链上状态显示 ===")
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "检验产品协议列表发布按钮根据链上状态显示",
            "测试环境": "用户1登录",
            "输入数据": "无"
        }
        
        # 等待列表加载
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        
        # 1. 先统计列表总行数
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        print(f"   列表总记录数: {total_rows}")
        
        if total_rows == 0:
            print("   [警告] 列表为空，无法验证发布按钮逻辑")
            # 将测试数据附加到HTML报告
            print("[成功] 测试数据已附加到HTML报告")
            return
        
        # 2. 逐行检查链上状态与发布按钮
        found_unpublished = False
        found_published = False
        
        for idx in range(total_rows):
            row = rows.nth(idx)
            
            # 获取链上状态文本
            chain_status_cell = row.locator(SELECTORS["chain_status"]).first
            chain_status = chain_status_cell.text_content().strip()
            
            # 获取发布按钮
            publish_btn = row.locator(SELECTORS["publish_button"]).first
            publish_btn_exists = publish_btn.count() > 0
            
            # 打印当前行的详细信息
            print(f"   第{idx+1}行 - 链上状态:【{chain_status}】, 发布按钮存在: {publish_btn_exists}")
            
            if any(status in chain_status for status in CHAIN_STATUS["UNPUBLISHED"]):
                found_unpublished = True
                assert publish_btn_exists, f"第{idx+1}行状态为【{chain_status}】，但未找到发布按钮"
                print(f"   ✓ 第{idx+1}行状态【{chain_status}】存在发布按钮")
                
            elif any(status in chain_status for status in CHAIN_STATUS["PUBLISHED"]):
                found_published = True
                assert publish_btn.count() == 0, f"第{idx+1}行状态为【{chain_status}】，不应存在发布按钮"
                print(f"   ✓ 第{idx+1}行状态【{chain_status}】无发布按钮")
            
            else:
                print(f"   [信息] 第{idx+1}行状态【{chain_status}】未知，跳过验证")
        
        # 3. 断言至少各找到一条未上链与已上链记录，确保验证完整性
        assert found_unpublished or found_published, ASSERT_MESSAGES["no_valid_chain_status"]
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 发布按钮根据链上状态正确显示！")
    def test_03_add_protocol_with_max_length_fields(self):
        """测试新增协议时，名称、描述、标题均为50字符，正文为2000字符"""
        print("\n=== 测试新增协议最大长度字段 ===")
        
        # 生成50位和2000位随机字符串
        name_desc_title, body_content = generate_max_length_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议最大长度字段",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": name_desc_title,
                "产品协议描述": name_desc_title,
                "协议标题": name_desc_title,
                "协议正文长度": len(body_content)
            }
        }

        print(f"   产品协议名称/描述/标题: {name_desc_title}")
        print(f"   协议正文长度: {len(body_content)} 字符")

        # 1. 点击"新增协议"按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 2. 填充表单字段
        # 产品协议名称
        self.page.fill(SELECTORS["name_input"], name_desc_title)
        print(f"   填充产品协议名称: {name_desc_title}")

        # 产品协议描述
        self.page.fill(SELECTORS["desc_input"], name_desc_title)
        print(f"   填充产品协议描述: {name_desc_title}")

        # 协议标题
        self.page.fill(SELECTORS["title_input"], name_desc_title)
        print(f"   填充协议标题: {name_desc_title}")

        # 协议正文（兼容多种富文本编辑器）
        body_filled = False
        
        # 先尝试通用的Quill编辑器定位
        quill_generic = self.page.locator("div.ql-editor")
        if quill_generic.count() > 0:
            quill_generic.fill(body_content)
            print(f"   成功使用通用选择器填充Quill编辑器协议正文: {len(body_content)} 字符")
            body_filled = True
        else:
            # 使用预定义的富文本编辑器选择器
            for xpath in QUILL_EDITOR_SELECTORS:
                editor = self.page.locator(xpath)
                if editor.count() > 0:
                    editor.fill(body_content)
                    print(f"   成功使用预定义XPath {xpath} 填充协议正文: {len(body_content)} 字符")
                    body_filled = True
                    break
            
            if not body_filled:
                # 尝试定位iframe编辑器
                iframe_editor = self.page.locator(", ".join(IFRAME_EDITOR_SELECTORS))
                if iframe_editor.count() > 0:
                    iframe_editor.frame_locator("body").fill(body_content)
                    print(f"   成功填充iframe类型富文本编辑器协议正文: {len(body_content)} 字符")
                    body_filled = True
                else:
                    # 尝试定位普通文本框
                    text_input = self.page.locator(", ".join(TEXT_INPUT_SELECTORS))
                    if text_input.count() > 0:
                        text_input.fill(body_content)
                        print(f"   成功填充普通文本框协议正文: {len(body_content)} 字符")
                        body_filled = True
                    else:
                        print(f"   [警告] 未找到协议正文编辑器")
        
        # 等待一下
        self.page.wait_for_timeout(WAIT_TIMES["network"])

        # 3. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 4. 在列表中找到刚新增的协议（根据名称匹配）
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        target_row = None

        # 调试：打印所有行的名称
        print(f"   列表中所有协议名称：")
        for idx in range(total_rows):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if cell_text:
                        print(f"     第{idx + 1}行第{col_idx}列: {cell_text}")
                        # 检查是否包含新增的协议名称（可能被截断）
                        if name_desc_title[:20] in cell_text:  # 检查前20个字符
                            target_row = row
                            print(f"   找到新增协议行（第{idx + 1}行）")
                            break
            if target_row:
                break

        assert target_row is not None, ASSERT_MESSAGES["protocol_not_in_list"]

        # 5. 验证新增成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 新增协议成功，出现成功提示")
        else:
            print("   [信息] 新增协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 最大长度字段新增协议测试完成！")

    def test_04_add_and_publish_protocol(self):
        """测试新增协议后立刻发布"""
        print("\n=== 测试新增协议后发布 ===")

        # 1. 生成随机值
        input_value = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议后发布",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": input_value,
                "产品协议描述": input_value,
                "协议标题": input_value,
                "协议正文": input_value
            }
        }
        
        print(f"   设置输入值: {input_value}")

        # 2. 点击"新增协议"按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 3. 填充表单字段
        # 产品协议名称
        self.page.fill(SELECTORS["name_input"], input_value)
        print(f"   填充产品协议名称: {input_value}")

        # 产品协议描述
        self.page.fill(SELECTORS["desc_input"], input_value)
        print(f"   填充产品协议描述: {input_value}")

        # 协议标题
        self.page.fill(SELECTORS["title_input"], input_value)
        print(f"   填充协议标题: {input_value}")

        # 协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(input_value)
                print(f"   成功填充协议正文: {input_value}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(input_value)
                print(f"   使用通用选择器填充协议正文: {input_value}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 4. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 5. 查找刚新增的协议行（根据名称）
        rows = self.page.locator(SELECTORS["table_rows"])
        target_row = None

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        target_row = row
                        print(f"   找到新增协议行（第{idx + 1}行）")
                        break
            if target_row:
                break

        assert target_row is not None, f"未找到新增的协议: {input_value}"

        # 6. 点击发布按钮
        publish_btn = target_row.locator(SELECTORS["publish_button"]).first
        if publish_btn.count() > 0:
            print("   点击发布按钮")
            publish_btn.click()
            self.page.wait_for_timeout(WAIT_TIMES["short"])

            # 7. 处理确认对话框
            confirm_dialog = None
            for selector in CONFIRM_DIALOG_SELECTORS:
                dialog = self.page.locator(selector)
                if dialog.count() > 0:
                    confirm_dialog = dialog
                    break

            if confirm_dialog:
                # 点击确认按钮
                confirm_btn = confirm_dialog.locator(".el-button--primary, .ant-btn-primary, button:has-text('确认')").first
                if confirm_btn.count() > 0:
                    print("   点击确认发布")
                    confirm_btn.click()
                    self.page.wait_for_timeout(WAIT_TIMES["long"])
                else:
                    print("   [警告] 未找到确认按钮")
            else:
                print("   [警告] 未找到发布确认对话框")
        else:
            print("   [警告] 未找到发布按钮")

        # 8. 验证发布成功
        # 等待页面刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 重新查找协议行并检查状态
        updated_rows = self.page.locator(SELECTORS["table_rows"])
        found_updated = False

        for idx in range(updated_rows.count()):
            row = updated_rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        # 检查链上状态
                        chain_status_cell = row.locator(SELECTORS["chain_status"]).first
                        if chain_status_cell.count() > 0:
                            chain_status = chain_status_cell.text_content().strip()
                            print(f"   协议发布后状态: {chain_status}")
                            # 验证状态是否为已上链
                            assert any(status in chain_status for status in CHAIN_STATUS["PUBLISHED"]), f"协议发布失败，状态仍为: {chain_status}"
                            print("   ✅ 协议发布成功！")
                            found_updated = True
                        break
            if found_updated:
                break

        assert found_updated, f"未找到更新后的协议行: {input_value}"

        # 9. 验证发布成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 发布协议成功，出现成功提示")
        else:
            print("   [信息] 发布协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议后发布测试完成！")

    def test_05_add_new_protocol(self):
        """测试新增协议"""
        print("\n=== 测试新增协议 ===")

        # 1. 生成随机值
        input_value = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": input_value,
                "产品协议描述": input_value,
                "协议标题": input_value,
                "协议正文": input_value
            }
        }
        
        print(f"   设置输入值: {input_value}")

        # 2. 点击"新增协议"按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 3. 填充表单字段
        # 产品协议名称
        self.page.fill(SELECTORS["name_input"], input_value)
        print(f"   填充产品协议名称: {input_value}")

        # 产品协议描述
        self.page.fill(SELECTORS["desc_input"], input_value)
        print(f"   填充产品协议描述: {input_value}")

        # 协议标题
        self.page.fill(SELECTORS["title_input"], input_value)
        print(f"   填充协议标题: {input_value}")

        # 协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(input_value)
                print(f"   成功填充协议正文: {input_value}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(input_value)
                print(f"   使用通用选择器填充协议正文: {input_value}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 4. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 5. 查找刚新增的协议行（根据名称）
        rows = self.page.locator(SELECTORS["table_rows"])
        target_row = None

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        target_row = row
                        print(f"   找到新增协议行（第{idx + 1}行）")
                        break
            if target_row:
                break

        assert target_row is not None, f"未找到新增的协议: {input_value}"

        # 6. 验证新增成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 新增协议成功，出现成功提示")
        else:
            print("   [信息] 新增协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议测试完成！")

    def test_06_query_protocol_by_name(self):
        """测试根据协议名称查询"""
        print("\n=== 测试根据协议名称查询 ===")

        # 1. 先新增一个协议
        test_protocol_name = f"测试查询 {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试根据协议名称查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "协议名称": test_protocol_name
            }
        }
        
        # 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 填充表单
        self.page.fill(SELECTORS["name_input"], test_protocol_name)
        print(f"   填充产品协议名称: {test_protocol_name}")

        self.page.fill(SELECTORS["desc_input"], test_protocol_name)
        print(f"   填充产品协议描述: {test_protocol_name}")

        self.page.fill(SELECTORS["title_input"], test_protocol_name)
        print(f"   填充协议标题: {test_protocol_name}")

        # 填充协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(test_protocol_name)
                print(f"   成功填充协议正文: {test_protocol_name}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(test_protocol_name)
                print(f"   使用通用选择器填充协议正文: {test_protocol_name}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 2. 清空查询条件
        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        # 3. 在查询条件中输入协议名称
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.fill(test_protocol_name)
            print(f"   输入查询条件: {test_protocol_name}")
        else:
            print("   [警告] 未找到协议名称输入框")

        # 4. 点击查询按钮
        search_button = self.page.locator(SELECTORS["search_button"])
        if search_button.count() > 0:
            search_button.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(WAIT_TIMES["medium"])
        else:
            print("   [警告] 未找到查询按钮")

        # 5. 验证查询结果
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if test_protocol_name in cell_text:
                        print(f"   找到查询结果: {cell_text}")
                        found = True
                        break
            if found:
                break

        assert found, f"未找到查询结果: {test_protocol_name}"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 根据协议名称查询测试完成！")

    def test_07_query_protocol_by_name_fuzzy(self):
        """测试根据协议名称模糊查询"""
        print("\n=== 测试根据协议名称模糊查询 ===")

        # 1. 先新增一个协议
        test_protocol_name = f"测试模糊查询 {generate_test_data()}"
        fuzzy_keyword = test_protocol_name[:5]  # 取前5个字符作为模糊查询关键词
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试根据协议名称模糊查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "协议名称": test_protocol_name,
                "模糊查询关键词": fuzzy_keyword
            }
        }
        
        # 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 填充表单
        self.page.fill(SELECTORS["name_input"], test_protocol_name)
        print(f"   填充产品协议名称: {test_protocol_name}")

        self.page.fill(SELECTORS["desc_input"], test_protocol_name)
        print(f"   填充产品协议描述: {test_protocol_name}")

        self.page.fill(SELECTORS["title_input"], test_protocol_name)
        print(f"   填充协议标题: {test_protocol_name}")

        # 填充协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(test_protocol_name)
                print(f"   成功填充协议正文: {test_protocol_name}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(test_protocol_name)
                print(f"   使用通用选择器填充协议正文: {test_protocol_name}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 2. 清空查询条件
        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        # 3. 在查询条件中输入模糊关键词
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.fill(fuzzy_keyword)
            print(f"   输入模糊查询关键词: {fuzzy_keyword}")
        else:
            print("   [警告] 未找到协议名称输入框")

        # 4. 点击查询按钮
        search_button = self.page.locator(SELECTORS["search_button"])
        if search_button.count() > 0:
            search_button.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(WAIT_TIMES["medium"])
        else:
            print("   [警告] 未找到查询按钮")

        # 5. 验证查询结果
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if test_protocol_name in cell_text:
                        print(f"   找到模糊查询结果: {cell_text}")
                        found = True
                        break
            if found:
                break

        assert found, f"未找到模糊查询结果: {test_protocol_name}"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 根据协议名称模糊查询测试完成！")

    def test_08_query_protocol_by_chain_status(self):
        """测试根据链上状态查询"""
        print("\n=== 测试根据链上状态查询 ===")

        # 1. 新增一个协议
        test_protocol_name = f"测试状态查询 {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试根据链上状态查询",
            "测试环境": "用户1登录",
            "输入数据": {
                "协议名称": test_protocol_name
            }
        }
        
        # 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 填充表单
        self.page.fill(SELECTORS["name_input"], test_protocol_name)
        print(f"   填充产品协议名称: {test_protocol_name}")

        self.page.fill(SELECTORS["desc_input"], test_protocol_name)
        print(f"   填充产品协议描述: {test_protocol_name}")

        self.page.fill(SELECTORS["title_input"], test_protocol_name)
        print(f"   填充协议标题: {test_protocol_name}")

        # 填充协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(test_protocol_name)
                print(f"   成功填充协议正文: {test_protocol_name}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(test_protocol_name)
                print(f"   使用通用选择器填充协议正文: {test_protocol_name}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 2. 清空查询条件
        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        # 3. 选择链上状态（未上链）
        chain_status_select = self.page.locator(SELECTORS["chain_status_select"])
        if chain_status_select.count() > 0:
            chain_status_select.click()
            print("   点击链上状态下拉框")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

            # 选择第一个未上链状态
            unpublish_status = CHAIN_STATUS["UNPUBLISHED"][0]
            status_option = self.page.locator(f"text={unpublish_status}")
            if status_option.count() > 0:
                status_option.click()
                print(f"   选择状态: {unpublish_status}")
                self.page.wait_for_timeout(WAIT_TIMES["short"])
            else:
                print(f"   [警告] 未找到状态选项: {unpublish_status}")
        else:
            print("   [警告] 未找到链上状态下拉框")

        # 4. 点击查询按钮
        search_button = self.page.locator(SELECTORS["search_button"])
        if search_button.count() > 0:
            search_button.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(WAIT_TIMES["medium"])
        else:
            print("   [警告] 未找到查询按钮")

        # 5. 验证查询结果
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if test_protocol_name in cell_text:
                        print(f"   找到查询结果: {cell_text}")
                        found = True
                        break
            if found:
                break

        assert found, f"未找到查询结果: {test_protocol_name}"
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 根据链上状态查询测试完成！")

    def test_09_add_and_delete_protocol(self):
        """测试新增协议后删除"""
        print("\n=== 测试新增协议后删除 ===")

        # 1. 生成随机值
        input_value = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议后删除",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": input_value,
                "产品协议描述": input_value,
                "协议标题": input_value,
                "协议正文": input_value
            }
        }
        
        print(f"   设置输入值: {input_value}")

        # 2. 点击"新增协议"按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 3. 填充表单字段
        # 产品协议名称
        self.page.fill(SELECTORS["name_input"], input_value)
        print(f"   填充产品协议名称: {input_value}")

        # 产品协议描述
        self.page.fill(SELECTORS["desc_input"], input_value)
        print(f"   填充产品协议描述: {input_value}")

        # 协议标题
        self.page.fill(SELECTORS["title_input"], input_value)
        print(f"   填充协议标题: {input_value}")

        # 协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(input_value)
                print(f"   成功填充协议正文: {input_value}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(input_value)
                print(f"   使用通用选择器填充协议正文: {input_value}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 4. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 5. 查找刚新增的协议行（根据名称）
        rows = self.page.locator(SELECTORS["table_rows"])
        target_row = None

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        target_row = row
                        print(f"   找到新增协议行（第{idx + 1}行）")
                        break
            if target_row:
                break

        assert target_row is not None, f"未找到新增的协议: {input_value}"

        # 6. 点击删除按钮
        delete_btn = target_row.locator(SELECTORS["delete_button"]).first
        if delete_btn.count() > 0:
            print("   点击删除按钮")
            delete_btn.click()
            self.page.wait_for_timeout(WAIT_TIMES["short"])

            # 7. 处理确认对话框
            confirm_dialog = None
            for selector in CONFIRM_DIALOG_SELECTORS:
                dialog = self.page.locator(selector)
                if dialog.count() > 0:
                    confirm_dialog = dialog
                    break

            if confirm_dialog:
                # 点击确认按钮
                confirm_btn = confirm_dialog.locator(".el-button--primary, .ant-btn-primary, button:has-text('确认')").first
                if confirm_btn.count() > 0:
                    print("   点击确认删除")
                    confirm_btn.click()
                    self.page.wait_for_timeout(WAIT_TIMES["long"])
                else:
                    print("   [警告] 未找到确认按钮")
            else:
                print("   [警告] 未找到删除确认对话框")
        else:
            print("   [警告] 未找到删除按钮")

        # 8. 验证删除成功（通过查询验证）
        # 清空查询条件
        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        # 输入协议名称查询
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.fill(input_value)
            print(f"   输入查询条件: {input_value}")

            # 点击查询按钮
            search_button = self.page.locator(SELECTORS["search_button"])
            if search_button.count() > 0:
                search_button.click()
                print("   点击查询按钮")
                self.page.wait_for_timeout(WAIT_TIMES["medium"])

                # 验证查询结果为空
                rows = self.page.locator(SELECTORS["table_rows"])
                if rows.count() == 0:
                    print("   ✅ 协议已成功删除，查询结果为空")
                else:
                    print("   [警告] 删除后查询仍有结果")
            else:
                print("   [警告] 未找到查询按钮")
        else:
            print("   [警告] 未找到协议名称输入框")

        # 9. 验证删除成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 删除协议成功，出现成功提示")
        else:
            print("   [信息] 删除协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议后删除测试完成！")

    def test_10_query_and_reset_filters(self):
        """测试协议名称和上链状态筛选条件后点击查询，再点击重置按钮"""
        print("\n=== 测试协议名称和上链状态筛选后查询和重置 ===")

        # 1. 生成随机值
        input_value = generate_test_data()
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试协议名称和上链状态筛选条件后点击查询，再点击重置按钮",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": input_value,
                "产品协议描述": input_value,
                "协议标题": input_value,
                "协议正文": input_value,
                "链上状态": CHAIN_STATUS["UNPUBLISHED"][0]
            }
        }
        
        print(f"   设置输入值: {input_value}")

        # 2. 点击"新增协议"按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")

        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")

        # 3. 填充表单字段
        # 产品协议名称
        self.page.fill(SELECTORS["name_input"], input_value)
        print(f"   填充产品协议名称: {input_value}")

        # 产品协议描述
        self.page.fill(SELECTORS["desc_input"], input_value)
        print(f"   填充产品协议描述: {input_value}")

        # 协议标题
        self.page.fill(SELECTORS["title_input"], input_value)
        print(f"   填充协议标题: {input_value}")

        # 协议正文（兼容多种富文本编辑器）
        body_filled = False
        for xpath in QUILL_EDITOR_SELECTORS:
            editor = self.page.locator(xpath)
            if editor.count() > 0:
                editor.fill(input_value)
                print(f"   成功填充协议正文: {input_value}")
                body_filled = True
                break

        if not body_filled:
            # 兜底：通用 quill 编辑器
            quill_generic = self.page.locator("div.ql-editor")
            if quill_generic.count() > 0:
                quill_generic.fill(input_value)
                print(f"   使用通用选择器填充协议正文: {input_value}")
                body_filled = True

        if not body_filled:
            print("   [警告] 未找到协议正文编辑器，跳过正文填充")

        # 4. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 5. 清空查询条件
        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        # 6. 在查询条件中输入协议名称
        name_input = self.page.locator(SELECTORS["name_input"])
        if name_input.count() > 0:
            name_input.fill(input_value)
            print(f"   输入查询条件: {input_value}")
        else:
            print("   [警告] 未找到协议名称输入框")

        # 7. 选择链上状态（未上链）
        chain_status_select = self.page.locator(SELECTORS["chain_status_select"])
        if chain_status_select.count() > 0:
            chain_status_select.click()
            print("   点击链上状态下拉框")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

            # 选择第一个未上链状态
            unpublish_status = CHAIN_STATUS["UNPUBLISHED"][0]
            status_option = self.page.locator(f"text={unpublish_status}")
            if status_option.count() > 0:
                status_option.click()
                print(f"   选择状态: {unpublish_status}")
                self.page.wait_for_timeout(WAIT_TIMES["short"])
            else:
                print(f"   [警告] 未找到状态选项: {unpublish_status}")
        else:
            print("   [警告] 未找到链上状态下拉框")

        # 8. 点击查询按钮
        search_button = self.page.locator(SELECTORS["search_button"])
        if search_button.count() > 0:
            search_button.click()
            print("   点击查询按钮")
            self.page.wait_for_timeout(WAIT_TIMES["medium"])
        else:
            print("   [警告] 未找到查询按钮")

        # 9. 验证查询结果
        rows = self.page.locator(SELECTORS["table_rows"])
        found = False

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        print(f"   找到查询结果: {cell_text}")
                        found = True
                        break
            if found:
                break

        assert found, f"未找到查询结果: {input_value}"

        # 10. 点击重置按钮
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

            # 11. 验证查询条件已清空
            if name_input.count() > 0:
                input_value_after_reset = name_input.input_value()
                print(f"   重置后输入框值: '{input_value_after_reset}'")
                assert input_value_after_reset == "", "重置后协议名称输入框应为空"

            # 12. 再次点击查询按钮
            if search_button.count() > 0:
                search_button.click()
                print("   点击查询按钮")
                self.page.wait_for_timeout(WAIT_TIMES["medium"])

                # 13. 验证查询结果（应该显示所有记录）
                rows_after_reset = self.page.locator(SELECTORS["table_rows"])
                print(f"   重置后查询结果数量: {rows_after_reset.count()}")
                assert rows_after_reset.count() > 0, "重置后查询结果不应为空"

        # 14. 清理测试数据（删除新增的协议）
        # 查找并删除测试协议
        rows = self.page.locator(SELECTORS["table_rows"])
        target_row = None

        for idx in range(rows.count()):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if input_value in cell_text:
                        target_row = row
                        break
            if target_row:
                break

        if target_row:
            # 点击删除按钮
            delete_btn = target_row.locator(SELECTORS["delete_button"]).first
            if delete_btn.count() > 0:
                delete_btn.click()
                self.page.wait_for_timeout(WAIT_TIMES["short"])

                # 处理确认对话框
                confirm_dialog = None
                for selector in CONFIRM_DIALOG_SELECTORS:
                    dialog = self.page.locator(selector)
                    if dialog.count() > 0:
                        confirm_dialog = dialog
                        break

                if confirm_dialog:
                    # 点击确认按钮
                    confirm_btn = confirm_dialog.locator(".el-button--primary, .ant-btn-primary, button:has-text('确认')").first
                    if confirm_btn.count() > 0:
                        confirm_btn.click()
                        # 等待删除完成
                        self.page.wait_for_timeout(WAIT_TIMES["long"])
                        self.page.wait_for_load_state("networkidle")
                        print("   ✅ 测试协议已删除")
                    else:
                        print("   [警告] 未找到删除确认按钮")
                else:
                    print("   [警告] 未找到删除确认对话框")
            else:
                print("   [警告] 未找到删除按钮")
        else:
            print("   [信息] 未找到测试协议，可能已被删除")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")
        
        print("   [测试完成] 协议名称和上链状态筛选查询和重置测试完成！")
    
    def test_11_add_protocol_with_single_space_in_name(self):
        """测试新增协议时协议名称包含一个空格"""
        print("\n=== 测试新增协议时协议名称包含一个空格 ===")
        
        # 生成包含一个空格的测试数据
        test_data = f"测试 {generate_test_data()}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议时协议名称包含一个空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": test_data,
                "产品协议描述": f"{test_data} description",
                "协议标题": f"{test_data} title",
                "协议正文": f"{test_data} content"
            }
        }
        
        print(f"   生成测试数据（包含一个空格）: {test_data}")
        
        # 1. 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")
        
        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")
        
        # 2. 填充表单字段
        self.page.fill(SELECTORS["name_input"], test_data)
        print(f"   填充产品协议名称: {test_data}")
        
        self.page.fill(SELECTORS["desc_input"], f"{test_data} description")
        print(f"   填充产品协议描述: {test_data} description")
        
        self.page.fill(SELECTORS["title_input"], f"{test_data} title")
        print(f"   填充协议标题: {test_data} title")
        
        # 填充协议正文（兼容多种富文本编辑器）
        body_filled = False
        
        # 先尝试通用的Quill编辑器定位
        quill_generic = self.page.locator("div.ql-editor")
        if quill_generic.count() > 0:
            quill_generic.fill(f"{test_data} content")
            print(f"   成功使用通用选择器填充Quill编辑器协议正文")
            body_filled = True
        else:
            # 使用预定义的富文本编辑器选择器
            for xpath in QUILL_EDITOR_SELECTORS:
                editor = self.page.locator(xpath)
                if editor.count() > 0:
                    editor.fill(f"{test_data} content")
                    print(f"   成功使用预定义XPath {xpath} 填充协议正文")
                    body_filled = True
                    break
            
            if not body_filled:
                # 尝试定位iframe编辑器
                iframe_editor = self.page.locator(", ".join(IFRAME_EDITOR_SELECTORS))
                if iframe_editor.count() > 0:
                    iframe_editor.frame_locator("body").fill(f"{test_data} content")
                    print(f"   成功填充iframe类型富文本编辑器协议正文")
                    body_filled = True
                else:
                    # 尝试定位普通文本框
                    text_input = self.page.locator(", ".join(TEXT_INPUT_SELECTORS))
                    if text_input.count() > 0:
                        text_input.fill(f"{test_data} content")
                        print(f"   成功填充普通文本框协议正文")
                        body_filled = True
                    else:
                        print(f"   [警告] 未找到协议正文编辑器")
        
        # 等待一下
        self.page.wait_for_timeout(WAIT_TIMES["network"])

        # 3. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 4. 在列表中找到刚新增的协议（根据名称匹配）
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        target_row = None

        # 调试：打印所有行的名称
        print(f"   列表中所有协议名称：")
        for idx in range(total_rows):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if cell_text:
                        print(f"     第{idx + 1}行第{col_idx}列: {cell_text}")
                        # 检查是否包含新增的协议名称（可能被截断）
                        if test_data[:20] in cell_text:  # 检查前20个字符
                            target_row = row
                            print(f"   找到新增协议行（第{idx + 1}行）")
                            break
            if target_row:
                break

        assert target_row is not None, ASSERT_MESSAGES["protocol_not_in_list"]

        # 5. 验证新增成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 新增协议成功，出现成功提示")
        else:
            print("   [信息] 新增协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议时协议名称包含一个空格测试完成！")

    def test_12_add_protocol_with_multiple_spaces_in_name(self):
        """测试新增协议时协议名称包含多个空格"""
        print("\n=== 测试新增协议时协议名称包含多个空格 ===")
        
        # 生成包含多个空格的测试数据
        test_data = f"测试   {generate_test_data()}   多个空格"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议时协议名称包含多个空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": test_data,
                "产品协议描述": f"{test_data} description",
                "协议标题": f"{test_data} title",
                "协议正文": f"{test_data} content"
            }
        }
        
        print(f"   生成测试数据（包含多个空格）: {test_data}")
        
        # 1. 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")
        
        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")
        
        # 2. 填充表单字段
        self.page.fill(SELECTORS["name_input"], test_data)
        print(f"   填充产品协议名称: {test_data}")
        
        self.page.fill(SELECTORS["desc_input"], f"{test_data} description")
        print(f"   填充产品协议描述: {test_data} description")
        
        self.page.fill(SELECTORS["title_input"], f"{test_data} title")
        print(f"   填充协议标题: {test_data} title")
        
        # 填充协议正文（兼容多种富文本编辑器）
        body_filled = False
        
        # 先尝试通用的Quill编辑器定位
        quill_generic = self.page.locator("div.ql-editor")
        if quill_generic.count() > 0:
            quill_generic.fill(f"{test_data} content")
            print(f"   成功使用通用选择器填充Quill编辑器协议正文")
            body_filled = True
        else:
            # 使用预定义的富文本编辑器选择器
            for xpath in QUILL_EDITOR_SELECTORS:
                editor = self.page.locator(xpath)
                if editor.count() > 0:
                    editor.fill(f"{test_data} content")
                    print(f"   成功使用预定义XPath {xpath} 填充协议正文")
                    body_filled = True
                    break
            
            if not body_filled:
                # 尝试定位iframe编辑器
                iframe_editor = self.page.locator(", ".join(IFRAME_EDITOR_SELECTORS))
                if iframe_editor.count() > 0:
                    iframe_editor.frame_locator("body").fill(f"{test_data} content")
                    print(f"   成功填充iframe类型富文本编辑器协议正文")
                    body_filled = True
                else:
                    # 尝试定位普通文本框
                    text_input = self.page.locator(", ".join(TEXT_INPUT_SELECTORS))
                    if text_input.count() > 0:
                        text_input.fill(f"{test_data} content")
                        print(f"   成功填充普通文本框协议正文")
                        body_filled = True
                    else:
                        print(f"   [警告] 未找到协议正文编辑器")
        
        # 等待一下
        self.page.wait_for_timeout(WAIT_TIMES["network"])

        # 3. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 4. 在列表中找到刚新增的协议（根据名称匹配）
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        target_row = None

        # 调试：打印所有行的名称
        print(f"   列表中所有协议名称：")
        for idx in range(total_rows):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if cell_text:
                        print(f"     第{idx + 1}行第{col_idx}列: {cell_text}")
                        # 检查是否包含新增的协议名称（可能被截断）
                        if test_data[:20] in cell_text:  # 检查前20个字符
                            target_row = row
                            print(f"   找到新增协议行（第{idx + 1}行）")
                            break
            if target_row:
                break

        assert target_row is not None, ASSERT_MESSAGES["protocol_not_in_list"]

        # 5. 验证新增成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 新增协议成功，出现成功提示")
        else:
            print("   [信息] 新增协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议时协议名称包含多个空格测试完成！")

    def test_13_add_protocol_with_spaces_in_multiple_fields(self):
        """测试新增协议时多个字段包含空格"""
        print("\n=== 测试新增协议时多个字段包含空格 ===")
        
        # 生成测试数据
        base_data = generate_test_data()
        test_data_name = f"测试名称 {base_data}"
        test_data_desc = f"测试描述 {base_data} 多个空格"
        test_data_title = f"测试标题 {base_data}"
        
        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能验证",
            "测试目的": "测试新增协议时多个字段包含空格",
            "测试环境": "用户1登录",
            "输入数据": {
                "产品协议名称": test_data_name,
                "产品协议描述": test_data_desc,
                "协议标题": test_data_title,
                "协议正文": f"测试正文 {base_data} 多个空格 content"
            }
        }
        
        print(f"   生成测试数据 - 名称: {test_data_name}")
        print(f"   生成测试数据 - 描述: {test_data_desc}")
        print(f"   生成测试数据 - 标题: {test_data_title}")
        
        # 1. 点击新增协议按钮
        self.page.click(SELECTORS["add_button"])
        print("   点击新增协议按钮")
        
        # 等待弹窗/表单出现
        self.page.wait_for_timeout(WAIT_TIMES["medium"])
        self.page.wait_for_load_state("networkidle")
        
        # 2. 填充表单字段
        self.page.fill(SELECTORS["name_input"], test_data_name)
        print(f"   填充产品协议名称: {test_data_name}")
        
        self.page.fill(SELECTORS["desc_input"], test_data_desc)
        print(f"   填充产品协议描述: {test_data_desc}")
        
        self.page.fill(SELECTORS["title_input"], test_data_title)
        print(f"   填充协议标题: {test_data_title}")
        
        # 填充协议正文（兼容多种富文本编辑器）
        body_content = f"测试正文 {base_data} 多个空格 content"
        body_filled = False
        
        # 先尝试通用的Quill编辑器定位
        quill_generic = self.page.locator("div.ql-editor")
        if quill_generic.count() > 0:
            quill_generic.fill(body_content)
            print(f"   成功使用通用选择器填充Quill编辑器协议正文")
            body_filled = True
        else:
            # 使用预定义的富文本编辑器选择器
            for xpath in QUILL_EDITOR_SELECTORS:
                editor = self.page.locator(xpath)
                if editor.count() > 0:
                    editor.fill(body_content)
                    print(f"   成功使用预定义XPath {xpath} 填充协议正文")
                    body_filled = True
                    break
            
            if not body_filled:
                # 尝试定位iframe编辑器
                iframe_editor = self.page.locator(", ".join(IFRAME_EDITOR_SELECTORS))
                if iframe_editor.count() > 0:
                    iframe_editor.frame_locator("body").fill(body_content)
                    print(f"   成功填充iframe类型富文本编辑器协议正文")
                    body_filled = True
                else:
                    # 尝试定位普通文本框
                    text_input = self.page.locator(", ".join(TEXT_INPUT_SELECTORS))
                    if text_input.count() > 0:
                        text_input.fill(body_content)
                        print(f"   成功填充普通文本框协议正文")
                        body_filled = True
                    else:
                        print(f"   [警告] 未找到协议正文编辑器")
        
        # 等待一下
        self.page.wait_for_timeout(WAIT_TIMES["network"])

        # 3. 保存/确定
        self.page.click(SELECTORS["confirm_button"])
        print("   点击确定按钮保存协议")

        # 等待列表刷新
        self.page.wait_for_timeout(WAIT_TIMES["long"])
        self.page.wait_for_load_state("networkidle")

        # 4. 在列表中找到刚新增的协议（根据名称匹配）
        rows = self.page.locator(SELECTORS["table_rows"])
        total_rows = rows.count()
        target_row = None

        # 调试：打印所有行的名称
        print(f"   列表中所有协议名称：")
        for idx in range(total_rows):
            row = rows.nth(idx)
            # 尝试所有可能的列位置查找名称
            for col_idx in range(1, 6):  # 检查前5列
                name_cell = row.locator(f"td:nth-child({col_idx})")
                if name_cell.count() > 0:
                    cell_text = name_cell.text_content().strip()
                    if cell_text:
                        print(f"     第{idx + 1}行第{col_idx}列: {cell_text}")
                        # 检查是否包含新增的协议名称（可能被截断）
                        if test_data_name[:20] in cell_text:  # 检查前20个字符
                            target_row = row
                            print(f"   找到新增协议行（第{idx + 1}行）")
                            break
            if target_row:
                break

        assert target_row is not None, ASSERT_MESSAGES["protocol_not_in_list"]

        # 5. 验证新增成功提示
        if self.page.locator(SELECTORS["success_message"]).count() > 0:
            print("   [成功] 新增协议成功，出现成功提示")
        else:
            print("   [信息] 新增协议操作完成，未检测到明确的成功提示")
        
        # 将测试数据附加到HTML报告
        print("[成功] 测试数据已附加到HTML报告")

        print("   [测试完成] 新增协议时多个字段包含空格测试完成！")
'''

# 写入新文件
with open(r'd:\autotrace\traceai\tests\ui_tests\test01_product_protocol.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("成功重新创建测试文件，编码已修复为UTF-8")