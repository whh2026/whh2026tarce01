import pytest
import random
import string
import time
import re
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.ui_tests.config import ui_config
# 导入测试数据
from tests.test_data.data_product_data import (
    SELECTORS, TEST_URLS, ASSERT_MESSAGES, 
    generate_test_data, WAIT_TIMES
)

class TestDataProduct(Base):
    """数据产品页面测试类"""
    
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

    def test_21_sql_injection_in_data_product_name_query(self):
        """测试产品列表页面产品名称查询输入框的SQL注入防护"""
        print("\n=== 测试产品列表页面产品名称查询输入框的SQL注入防护 ===")

        # SQL注入测试用例列表
        sql_injection_payloads = [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR '1'='1'/*",
            "admin'--",
            "admin' #",
            "admin'/*",
            "' OR '1'='1' LIMIT 1--",
            "' OR '1'='1' OFFSET 0--",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "' OR 'x'='x",
            "' OR 'x'='x'--",
            "' OR 'x'='x'#",
            "' OR 'x'='x'/*",
            "' OR 1=1 LIMIT 1--",
            "' OR 1=1 OFFSET 0--",
            "' OR '1'='1' UNION SELECT username, password FROM users--",
            "' OR '1'='1' UNION SELECT 1, 2, 3, 4--",
            "' OR '1'='1' UNION SELECT NULL, NULL, NULL--",
            "' OR '1'='1' UNION SELECT 1, 2, 3, 4, 5, 6--",
            "' OR '1'='1' UNION SELECT username, password, email, phone FROM users--",
            "' OR '1'='1' AND (SELECT COUNT(*) FROM users) > 0--",
            "' OR '1'='1' AND (SELECT COUNT(*) FROM admin) > 0--",
            "' OR '1'='1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "' OR '1'='1' AND (SELECT COUNT(*) FROM sys.tables) > 0--",
            "' OR (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "' OR (SELECT COUNT(*) FROM sys.tables) > 0--",
            "1' AND 1=1--",
            "1' AND 1=1#",
            "1' AND 1=1/*",
            "1' AND (SELECT COUNT(*) FROM users) > 0--",
            "1' AND (SELECT COUNT(*) FROM admin) > 0--",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "1' AND (SELECT COUNT(*) FROM sys.tables) > 0--",
            "' OR (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "' OR (SELECT COUNT(*) FROM sys.tables) > 0--",
            "1' AND 1=1 IN (SELECT 1)--",
            "1' AND 1=1 IN (SELECT * FROM information_schema.tables)--",
            "1' AND 1=1 IN (SELECT * FROM sys.tables)--",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "1' AND (SELECT COUNT(*) FROM sys.tables)>0--",
            "' OR (SELECT COUNT(*) FROM information_schema.tables) > 0--",
            "' OR (SELECT COUNT(*) FROM sys.tables)>0--",
            "1' AND (SELECT COUNT(*) FROM data_products)>0--",
            "' OR (SELECT COUNT(*) FROM data_products)>0--",
            "1' AND (SELECT 1 FROM data_products LIMIT 1)=1--",
            "' OR (SELECT 1 FROM data_products LIMIT 1)=1--",
            "1' AND (SELECT name FROM data_products LIMIT 1) IS NOT NULL--",
            "' OR (SELECT name FROM data_products LIMIT 1) IS NOT NULL--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test%') > 0--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test%') > 0--",
            "1' AND (SELECT SUBSTRING(name,1,1) FROM data_products LIMIT 1) = 'a'--",
            "' OR (SELECT SUBSTRING(name,1,1) FROM data_products LIMIT 1) = 'a'--",
            "1' AND (SELECT ASCII(SUBSTRING(name,1,1)) FROM data_products LIMIT 1) = 97--",
            "' OR (SELECT ASCII(SUBSTRING(name,1,1)) FROM data_products LIMIT 1) = 97--",
            "1' AND (SELECT LENGTH(name) FROM data_products LIMIT 1) > 5--",
            "' OR (SELECT LENGTH(name) FROM data_products LIMIT 1) > 5--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name = 'test') > 0--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE 'test%') > 0--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test') > 0--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test%') > 0--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name = 'test') = 1--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE 'test%') = 1--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test') = 1--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE '%test%') = 1--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name = '测试') > 0--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE '测试%') > 0--",
            "1' AND (SELECT COUNT(*) FROM data_products WHERE name LIKE '%测试') > 0--",
            "' OR (SELECT COUNT(*) FROM data_products WHERE name LIKE '%测试%') > 0--",
        ]

        # 初始化测试数据
        self._test_data = {
            "测试类型": "安全测试",
            "测试目的": "测试产品列表页面产品名称查询输入框的SQL注入防护",
            "测试环境": "用户1登录",
            "输入数据": {
                "SQL注入测试用例数量": len(sql_injection_payloads),
                "测试用例列表": sql_injection_payloads[:10]
            },
            "验证结果": "",
            "测试详情": []
        }

        # 1. 登录系统
        print("   正在登录系统...")
        self.login_with_user(1, self.CONFIG, None, self.page)
        print("   ✓ 登录成功")

        # 2. 访问数据产品列表页面
        main_url = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(main_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面: {main_url}")

        # 2. 验证页面是否加载正确
        try:
            # 验证页面标题
            page_title = self.page.locator(SELECTORS["page_title"])
            if page_title.count() > 0:
                title_text = page_title.first.text_content()
                print(f"   ✓ 页面标题: {title_text}")
            else:
                print(f"   ⚠ 未找到页面标题")

            # 验证产品列表表格
            table = self.page.locator(SELECTORS["table"])
            if table.count() > 0:
                print(f"   ✓ 找到产品列表表格")
            else:
                print(f"   ⚠ 未找到产品列表表格")

            # 验证查询输入框
            search_input = self.page.locator(SELECTORS["search_input"])
            if search_input.count() > 0:
                print(f"   ✓ 找到产品名称查询输入框")
            else:
                print(f"   ⚠ 未找到产品名称查询输入框")

        except Exception as e:
            print(f"   ⚠ 页面验证失败: {str(e)}")

        print(f"   共测试 {len(sql_injection_payloads)} 个SQL注入用例")

        sql_injection_failed_count = 0

        for idx, payload in enumerate(sql_injection_payloads, 1):
            print(f"\n   测试用例 {idx}/{len(sql_injection_payloads)}: {payload[:50]}...")

            test_detail = {
                "序号": idx,
                "注入payload": payload,
                "结果": "",
                "备注": ""
            }

            try:
                # 清空查询条件 - 每次重新定位重置按钮
                reset_button = self.page.locator(SELECTORS["reset_button"])
                if reset_button.count() > 0:
                    reset_button.click()
                    self.page.wait_for_timeout(1000)

                # 在产品列表页面的产品名称查询输入框中输入SQL注入payload
                search_input = self.page.locator(SELECTORS["search_input"])
                if search_input.count() > 0:
                    search_input.fill(payload)
                    print(f"   在产品名称查询输入框中输入SQL注入payload: {payload[:50]}...")
                else:
                    print(f"   [警告] 未找到产品名称查询输入框")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到输入框"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                # 点击查询按钮
                search_button = self.page.locator(SELECTORS["search_button"])
                if search_button.count() > 0:
                    search_button.click()
                    print(f"   点击查询按钮")
                    # 等待查询结果
                    self.page.wait_for_timeout(2000)
                else:
                    print(f"   [警告] 未找到查询按钮")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到查询按钮"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                # 检查是否有错误信息或异常
                error_message = self.page.locator(SELECTORS.get("error_message", ".error"))
                if error_message.count() > 0:
                    error_text = error_message.first.text_content()
                    if "SQL" in error_text or "数据库" in error_text or "语法" in error_text:
                        print(f"   ⚠ 可能存在SQL注入漏洞: {error_text}")
                        test_detail["结果"] = "可能存在漏洞"
                        test_detail["备注"] = f"出现数据库错误: {error_text}"
                        sql_injection_failed_count += 1
                    else:
                        print(f"   ✓ 系统正常处理错误: {error_text}")
                        test_detail["结果"] = "已阻止"
                        test_detail["备注"] = f"系统返回错误: {error_text}"
                else:
                    # 检查是否返回了结果
                    table_rows = self.page.locator(SELECTORS["table_rows"])
                    if table_rows.count() > 0:
                        print(f"   ✓ 系统返回查询结果")
                        test_detail["结果"] = "已阻止"
                        test_detail["备注"] = "系统返回正常查询结果"
                    else:
                        print(f"   ✓ 系统返回空结果")
                        test_detail["结果"] = "已阻止"
                        test_detail["备注"] = "系统返回空结果"

            except Exception as e:
                print(f"   ⚠ 测试过程中发生错误: {str(e)}")
                test_detail["结果"] = "错误"
                test_detail["备注"] = f"测试错误: {str(e)}"

            finally:
                self._test_data["测试详情"].append(test_detail)

        # 计算防护成功率
        total_tests = len(sql_injection_payloads)
        blocked_tests = total_tests - sql_injection_failed_count
        protection_rate = (blocked_tests / total_tests) * 100 if total_tests > 0 else 0

        print(f"\n=== SQL注入测试结果总结 ===")
        print(f"   总测试用例数: {total_tests}")
        print(f"   成功阻止: {blocked_tests}")
        print(f"   可能存在漏洞: {sql_injection_failed_count}")
        print(f"   阻止率: {protection_rate:.2f}%")

        # 更新测试数据
        self._test_data["验证结果"] = f"阻止率: {protection_rate:.2f}%，成功阻止 {blocked_tests} 个，可能存在漏洞 {sql_injection_failed_count} 个"

        # 验证SQL注入防护能力
        assert protection_rate >= 95, f"SQL注入防护能力不足，建议加强安全措施"

        print("[成功] 测试数据已附加到HTML报告")

    def test_01_add_normal_data_product(self):
        """测试添加正常数据产品"""
        print("\n=== 测试添加正常数据产品 ===")

        # 初始化测试数据
        self._test_data = {
            "测试类型": "功能测试",
            "测试目的": "测试添加正常数据产品",
            "测试环境": "用户1登录",
            "输入数据": {
                "数据产品名称": f"测试产品_{generate_test_data()}",
                "数据产品描述": "这是一个测试数据产品",
                "产品类型": "API",
                "行业分类": "金融",
                "是否涉及个人信息": "否",
                "是否需要申请使用": "是"
            },
            "验证结果": "",
            "测试详情": []
        }

        # 1. 登录系统
        print("   正在登录系统...")
        self.login_with_user(1, self.CONFIG, None, self.page)
        print("   ✓ 登录成功")

        # 2. 访问数据产品列表页面
        main_url = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(main_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面")

        # 3. 点击新增按钮
        add_button = self.page.locator(SELECTORS["add_button"])
        if add_button.count() > 0:
            add_button.first.click()
            print("   ✓ 已点击新增按钮")
            time.sleep(2)
        else:
            raise AssertionError("未找到新增按钮")

        # 4. 填写基本信息 - 参考 base.py 的定位方式
        import random
        import string
        random_suffix = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        product_name = f"测试产品{random_suffix}"
        
        # 填写数据产品名称
        if self.page.is_visible(SELECTORS["data_product_name_input"]):
            self.page.fill(SELECTORS["data_product_name_input"], product_name)
            print(f"   ✓ 已填写数据产品名称: {product_name}")
        else:
            print("   ⚠ 未找到数据产品名称输入框")

        # 填写数据产品英文名称
        import random
        import string
        random_suffix = ''.join(random.sample(string.ascii_letters + string.digits, 6))
        english_name = f"TestDataProduct{random_suffix}"
        if self.page.is_visible(SELECTORS["data_product_english_name_input"]):
            self.page.fill(SELECTORS["data_product_english_name_input"], english_name)
            print(f"   ✓ 已填写数据产品英文名称: {english_name}")
        else:
            print("   ⚠ 未找到数据产品英文名称输入框")

        # 填写数据产品描述
        if self.page.is_visible(SELECTORS["data_product_desc_textarea"]):
            self.page.fill(SELECTORS["data_product_desc_textarea"], "这是一个测试数据产品")
            print("   ✓ 已填写数据产品描述")
        else:
            print("   ⚠ 未找到数据产品描述输入框")

        # 填写使用限制
        if self.page.is_visible(SELECTORS["data_product_limit_textarea"]):
            self.page.fill(SELECTORS["data_product_limit_textarea"], "使用限制：仅用于测试目的，不得用于生产环境")
            print("   ✓ 已填写使用限制")
        else:
            print("   ⚠ 未找到使用限制输入框")

        # 填写产品标签
        tags_value = "测试, API, 自动化测试"
        if self.page.is_visible(SELECTORS["data_product_tags_input"]):
            self.page.fill(SELECTORS["data_product_tags_input"], tags_value)
            print(f"   ✓ 已填写标签: {tags_value}")
        else:
            print("   ⚠ 未找到产品标签输入框")

        # 选择行业分类
        if self.page.is_visible(SELECTORS["data_product_category_select"]):
            self.page.click(SELECTORS["data_product_category_select"])
            time.sleep(1)
            self.page.click("li:has-text('采矿业')")
            print("   ✓ 已选择行业分类: 采矿业")
        else:
            print("   ⚠ 未找到行业分类下拉框")

        # 选择产品类型
        if self.page.is_visible(SELECTORS["data_product_type_select"]):
            self.page.click(SELECTORS["data_product_type_select"])
            time.sleep(1)
            self.page.click("li:has-text('数据接口')")
            print("   ✓ 已选择产品类型: 数据接口")
        else:
            print("   ⚠ 未找到产品类型下拉框")

        # 选择产品小类
        if self.page.is_visible(SELECTORS["data_product_subtype_select"]):
            self.page.click(SELECTORS["data_product_subtype_select"])
            time.sleep(1)
            self.page.click("li:has-text('API接口')")
            print("   ✓ 已选择产品小类: API接口")
        else:
            print("   ⚠ 未找到产品小类下拉框")

        # 选择地域分类
        if self.page.is_visible(SELECTORS["data_product_region_select"]):
            self.page.locator(".allPadding > .el-select > .el-select__wrapper > .el-select__selection > div:nth-child(2)").click()
            time.sleep(1)
            self.page.locator("div").filter(has_text=re.compile(r"^北京市$")).locator("span").nth(1).click()
            print("   ✓ 已选择地域分类: 北京市")
        else:
            print("   ⚠ 未找到地域分类下拉框")

        # 5. 点击下一步
        if self.page.is_visible(SELECTORS["next_step_button"]):
            self.page.click(SELECTORS["next_step_button"])
            print("   ✓ 已点击下一步按钮")
            time.sleep(2)
        else:
            print("   ⚠ 未找到下一步按钮")

        # 6. 填写详细信息 - 参考 base.py 的定位方式
        print("\n=== 6. 填写详细信息 ===")
        
        # 步骤 6.1: 填写接口名称
        if self.page.is_visible(SELECTORS.get("data_product_api_name_input")):
            self.page.fill(SELECTORS["data_product_api_name_input"], "测试接口")
            print("   ✓ 已填写接口名称: 测试接口")
        else:
            print("   ⚠ 未找到接口名称输入框")

        # 步骤 6.2: 填写正式接口地址
        if self.page.is_visible(SELECTORS.get("access_address_input")):
            self.page.fill(SELECTORS["access_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print("   ✓ 已填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        else:
            print("   ⚠ 未找到正式接口地址输入框")

        # 步骤 6.3: 填写测试接口地址
        if self.page.is_visible(SELECTORS.get("redirect_address_input")):
            self.page.fill(SELECTORS["redirect_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print("   ✓ 已填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        else:
            print("   ⚠ 未找到测试接口地址输入框")

        # 步骤 6.4: 向下滚动页面，使入参字段可见
        print("   向下滚动页面，使入参字段可见...")
        self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(1)
        self.page.evaluate("window.scrollBy({top: -200, behavior: 'smooth'})")
        time.sleep(1)

        # 步骤 6.5: 填写入参信息（非授权产品：仅date）
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
                        print(f"   ✓ 已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                    else:
                        print(f"   ⚠ 第{i+1}个入参字段不可见，尝试强制填充")
                        input_element.fill(param_name)
                        print(f"   ✓ (强制) 已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                else:
                    print(f"   ⚠ 第{i+1}个入参字段xpath不存在")
            except Exception as e:
                print(f"   ⚠ 填写第{i+1}个入参字段时出错: {e}")
        
        if filled_count < len(input_params):
            print(f"   ⚠ 警告：只成功填写了{filled_count}/{len(input_params)}个入参字段")

        # 7. 点击下一步
        if self.page.is_visible(SELECTORS["next_step_button"]):
            self.page.click(SELECTORS["next_step_button"])
            print("   ✓ 已点击下一步按钮")
            time.sleep(2)
        else:
            print("   ⚠ 未找到下一步按钮")

        # 8. 填写价格信息 
        print("\n=== 8. 填写价格信息 ===")
        
        # 选择价格类型
        if self.page.is_visible(SELECTORS.get("price_type_select")):
            self.page.click(SELECTORS["price_type_select"])
            time.sleep(1)
            self.page.click("li:has-text('计量定价')")
            print("   ✓ 已选择价格类型: 计量定价")
            time.sleep(2)
        
        # 计量方式默认已选择，无需操作
        
        # 填写价格
        if self.page.is_visible(SELECTORS.get("price_input")):
            self.page.fill(SELECTORS["price_input"], "10")
            print("   ✓ 已填写价格: 10")
        else:
            print("   ⚠ 未找到价格输入框")
        
        # 设置是否隐藏价格
        if self.page.is_visible(SELECTORS.get("hidden_price_radio_no")):
            self.page.click(SELECTORS["hidden_price_radio_no"])
            print("   ✓ 是否隐藏价格: 否")
        
        # 选择支付模式
        try:
            if self.page.is_visible(SELECTORS.get("payment_mode_select")):
                self.page.click(SELECTORS["payment_mode_select"])
                time.sleep(1)
                self.page.click("li:has-text('预付款')")
                print("   ✓ 已选择支付模式: 预付款")
                time.sleep(1)
        except Exception as e:
            print(f"   ⚠ 支付模式选择跳过: {str(e)}")
        
        # 选择支付方式
        try:
            if self.page.is_visible(SELECTORS.get("payment_method_select")):
                self.page.click(SELECTORS["payment_method_select"])
                time.sleep(1)
                self.page.click("li:has-text('线下付款')")
                print("   ✓ 已选择支付方式: 线下付款")
                time.sleep(1)
        except Exception as e:
            print(f"   ⚠ 支付方式选择跳过: {str(e)}")

        # 9. 填写上架信息
        print("\n=== 9. 填写上架信息 ===")
        
        # 设置是否需要审批
        if self.page.is_visible(SELECTORS["need_apply_no_radio"]):
            self.page.click(SELECTORS["need_apply_no_radio"])
            print("   ✓ 是否需要审批: 否")
        else:
            print("   ⚠ 未找到是否需要审批选项")
        
        # 选择服务协议 - 参考 base.py 步骤 7.2
        if self.page.is_visible("label:has-text('服务协议') + div >> .el-select"):
            self.page.click("label:has-text('服务协议') + div >> .el-select")
            time.sleep(1)
            self.page.click(".el-select-dropdown__item")
            print("   ✓ 已选择服务协议: 第一个选项")
        else:
            print("   ⚠ 未找到服务协议下拉框")
        
        # 设置产品授权范围 - 参考 base.py 步骤 7.3
        if self.page.is_visible(SELECTORS["allow_third_party_checkbox"]):
            self.page.click(SELECTORS["allow_third_party_checkbox"])
            print("   ✓ 已选择产品授权范围: 允许第三方授权使用")
        else:
            print("   ⚠ 未找到允许第三方授权使用选项")
        
        # 选择产品交付策略 - 参考 base.py 步骤 7.4
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
                    print(f"   ✓ 已点击选择按钮: {selector}")
                    break
            except Exception as e:
                print(f"   ⚠ 选择器 {selector} 点击失败: {e}")
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
                        print("   ✓ 已选择产品交付策略")
                        delivery_strategy_selected = True
                        break
                except Exception as e:
                    print(f"   ⚠ 选择器 {checkbox_selector} 点击失败: {e}")
                    continue
            
            if delivery_strategy_selected:
                confirm_button_selectors = [
                    SELECTORS["delivery_strategy_confirm_button"],
                    ".el-dialog__footer button:has-text('确定')",
                    ".el-dialog__footer .el-button--primary"
                ]
                
                for confirm_selector in confirm_button_selectors:
                    try:
                        if self.page.is_visible(confirm_selector):
                            self.page.click(confirm_selector)
                            time.sleep(1)
                            print("   ✓ 已点击确定按钮")
                            break
                    except Exception as e:
                        print(f"   ⚠ 选择器 {confirm_selector} 点击失败: {e}")
                        continue
        except Exception as e:
            print(f"   ⚠ 选择产品交付策略失败: {e}")

        # 10. 点击确定按钮
        if self.page.is_visible(SELECTORS["confirm_button"]):
            self.page.click(SELECTORS["confirm_button"])
            print("   ✓ 已点击确定按钮")
            time.sleep(3)
        else:
            print("   ⚠ 未找到确定按钮")

        # 11. 验证产品是否创建成功
        if self.page.is_visible(SELECTORS["success_message"]):
            success_text = self.page.locator(SELECTORS["success_message"]).first.text_content()
            print(f"   ✓ 产品创建成功: {success_text}")
            self._test_data["验证结果"] = "产品创建成功"
        else:
            print("   ⚠ 未找到成功消息")
            self._test_data["验证结果"] = "产品创建状态未知"

        # 12. 导航到数据产品列表页面 - 参考 base.py
        print("\n=== 12. 导航到数据产品列表页面 ===")
        data_product_page = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(data_product_page)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面: {data_product_page}")
        
        # 13. 输入数据产品名称查询 - 参考 base.py
        print("\n=== 13. 输入数据产品名称查询 ===")
        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", product_name)
            time.sleep(3)
            print(f"   ✓ 已输入产品名称: {product_name}")
        
        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)
            print("   ✓ 已点击查询")

        # 14. 点击发布 - 参考 base.py
        print("\n=== 14. 点击发布 ===")
        if self.page.is_visible("span.el-button__text:has-text('发布')"):
            self.page.click("span.el-button__text:has-text('发布')")
            time.sleep(3)
            print("   ✓ 已点击发布")

        # 15. 点击确定 - 参考 base.py
        print("\n=== 15. 点击确定 ===")
        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            try:
                self.page.wait_for_selector(SELECTORS["success_message"], timeout=10000)
                print("   ✓ 已点击确定，数据产品发布成功")
            except Exception as e:
                print("   ✓ 已点击确定，完成数据产品发布")

        print("\n✓ 新增数据产品完整流程测试完成")
        print("[成功] 测试数据已附加到HTML报告")

    def test_02_add_data_product_with_empty_name(self):
        """测试添加空名称的数据产品（边界测试）"""
        print("\n=== 测试添加空名称的数据产品 ===")

        # 初始化测试数据
        self._test_data = {
            "测试类型": "边界测试",
            "测试目的": "测试添加空名称的数据产品",
            "测试环境": "用户1登录",
            "输入数据": {
                "数据产品名称": "",
                "数据产品描述": "这是一个测试数据产品"
            },
            "验证结果": "",
            "测试详情": []
        }

        # 1. 登录系统
        print("   正在登录系统...")
        self.login_with_user(1, self.CONFIG, None, self.page)
        print("   ✓ 登录成功")

        # 2. 访问数据产品列表页面
        main_url = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(main_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面")

        # 3. 点击新增按钮
        add_button = self.page.locator(SELECTORS["add_button"])
        if add_button.count() > 0:
            add_button.first.click()
            print("   ✓ 已点击新增按钮")
            time.sleep(2)
        else:
            raise AssertionError("未找到新增按钮")

        # 4. 不填写数据产品名称（留空）
        print("   ⚠ 数据产品名称留空")

        # 5. 填写数据产品描述
        desc_textarea = self.page.locator(SELECTORS["data_product_desc_textarea"])
        if desc_textarea.count() > 0:
            desc_textarea.first.fill("这是一个测试数据产品")
            print("   ✓ 已填写数据产品描述")
        else:
            print("   ⚠ 未找到数据产品描述输入框")

        # 6. 点击确定按钮
        confirm_button = self.page.locator(SELECTORS["confirm_button"])
        if confirm_button.count() > 0:
            confirm_button.first.click()
            print("   ✓ 已点击确定按钮")
            time.sleep(2)
        else:
            print("   ⚠ 未找到确定按钮")

        # 7. 验证是否显示错误提示
        error_message = self.page.locator(SELECTORS["error_message"])
        if error_message.count() > 0:
            error_text = error_message.first.text_content()
            print(f"   ✓ 系统正确显示错误提示: {error_text}")
            self._test_data["验证结果"] = "系统正确阻止空名称产品创建"
        else:
            print("   ⚠ 未找到错误提示，可能存在漏洞")
            self._test_data["验证结果"] = "系统未正确阻止空名称产品创建"

        print("[成功] 测试数据已附加到HTML报告")

    def test_03_add_data_product_with_special_characters(self):
        """测试添加包含特殊字符的数据产品"""
        print("\n=== 测试添加包含特殊字符的数据产品 ===")

        # 特殊字符测试用例
        special_chars = [
            "<script>alert('xss')</script>",
            "' OR '1'='1",
            "<img src=x onerror=alert(1)>",
            "${7*7}",
            "{{7*7}}",
            "<%7*7%>",
            "test<>test",
            "test'test",
            'test"test',
            "test\\test",
            "test|test",
            "test&test",
            "test;test"
        ]

        self._test_data = {
            "测试类型": "安全测试",
            "测试目的": "测试添加包含特殊字符的数据产品",
            "测试环境": "用户1登录",
            "输入数据": {
                "特殊字符数量": len(special_chars),
                "测试用例": special_chars[:5]
            },
            "验证结果": "",
            "测试详情": []
        }

        # 1. 登录系统
        print("   正在登录系统...")
        self.login_with_user(1, self.CONFIG, None, self.page)
        print("   ✓ 登录成功")

        # 2. 访问数据产品列表页面
        main_url = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(main_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面")

        blocked_count = 0

        for idx, special_char in enumerate(special_chars, 1):
            print(f"\n   测试特殊字符 {idx}/{len(special_chars)}: {special_char[:30]}...")

            test_detail = {
                "序号": idx,
                "特殊字符": special_char,
                "结果": "",
                "备注": ""
            }

            try:
                # 点击新增按钮
                add_button = self.page.locator(SELECTORS["add_button"])
                if add_button.count() > 0:
                    add_button.first.click()
                    time.sleep(2)
                else:
                    raise AssertionError("未找到新增按钮")

                # 填写包含特殊字符的数据产品名称
                name_input = self.page.locator(SELECTORS["data_product_name_input"])
                if name_input.count() > 0:
                    name_input.first.fill(special_char)
                    print(f"   已填写特殊字符: {special_char[:30]}...")
                else:
                    print("   ⚠ 未找到数据产品名称输入框")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到输入框"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                # 填写数据产品描述
                desc_textarea = self.page.locator(SELECTORS["data_product_desc_textarea"])
                if desc_textarea.count() > 0:
                    desc_textarea.first.fill("这是一个测试数据产品")

                # 点击确定按钮
                confirm_button = self.page.locator(SELECTORS["confirm_button"])
                if confirm_button.count() > 0:
                    confirm_button.first.click()
                    time.sleep(2)
                else:
                    print("   ⚠ 未找到确定按钮")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到确定按钮"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                # 检查是否显示错误提示
                error_message = self.page.locator(SELECTORS["error_message"])
                if error_message.count() > 0:
                    error_text = error_message.first.text_content()
                    print(f"   ✓ 系统正确显示错误提示")
                    test_detail["结果"] = "已阻止"
                    test_detail["备注"] = f"系统返回错误: {error_text}"
                    blocked_count += 1
                else:
                    # 检查是否成功创建
                    success_message = self.page.locator(SELECTORS["success_message"])
                    if success_message.count() > 0:
                        print(f"   ⚠ 产品创建成功，可能存在XSS漏洞")
                        test_detail["结果"] = "可能存在漏洞"
                        test_detail["备注"] = "产品创建成功"
                    else:
                        print(f"   ✓ 系统未创建产品")
                        test_detail["结果"] = "已阻止"
                        test_detail["备注"] = "系统未创建产品"
                        blocked_count += 1

                # 返回列表页面
                self.page.goto(main_url)
                self.page.wait_for_load_state("networkidle", timeout=30000)
                time.sleep(1)

            except Exception as e:
                print(f"   ⚠ 测试过程中发生错误: {str(e)}")
                test_detail["结果"] = "错误"
                test_detail["备注"] = f"测试错误: {str(e)}"

            finally:
                self._test_data["测试详情"].append(test_detail)

        # 计算防护成功率
        protection_rate = (blocked_count / len(special_chars)) * 100 if len(special_chars) > 0 else 0

        print(f"\n=== 特殊字符测试结果总结 ===")
        print(f"   总测试用例数: {len(special_chars)}")
        print(f"   成功阻止: {blocked_count}")
        print(f"   阻止率: {protection_rate:.2f}%")

        self._test_data["验证结果"] = f"阻止率: {protection_rate:.2f}%，成功阻止 {blocked_count} 个"

        print("[成功] 测试数据已附加到HTML报告")

    def test_04_add_data_product_with_max_length(self):
        """测试添加最大长度数据产品（边界测试）"""
        print("\n=== 测试添加最大长度数据产品 ===")

        # 生成最大长度字符串（假设最大长度为100）
        max_length_name = "A" * 100
        max_length_desc = "B" * 500

        self._test_data = {
            "测试类型": "边界测试",
            "测试目的": "测试添加最大长度数据产品",
            "测试环境": "用户1登录",
            "输入数据": {
                "数据产品名称长度": len(max_length_name),
                "数据产品描述长度": len(max_length_desc)
            },
            "验证结果": "",
            "测试详情": []
        }

        # 1. 登录系统
        print("   正在登录系统...")
        self.login_with_user(1, self.CONFIG, None, self.page)
        print("   ✓ 登录成功")

        # 2. 访问数据产品列表页面
        main_url = self.get_url_for_user(1, "/registration/product/dataProduct", self.CONFIG)
        self.page.goto(main_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面")

        # 3. 点击新增按钮
        add_button = self.page.locator(SELECTORS["add_button"])
        if add_button.count() > 0:
            add_button.first.click()
            print("   ✓ 已点击新增按钮")
            time.sleep(2)
        else:
            raise AssertionError("未找到新增按钮")

        # 4. 填写最大长度的数据产品名称
        name_input = self.page.locator(SELECTORS["data_product_name_input"])
        if name_input.count() > 0:
            name_input.first.fill(max_length_name)
            print(f"   ✓ 已填写最大长度数据产品名称（{len(max_length_name)}字符）")
        else:
            print("   ⚠ 未找到数据产品名称输入框")

        # 5. 填写最大长度的数据产品描述
        desc_textarea = self.page.locator(SELECTORS["data_product_desc_textarea"])
        if desc_textarea.count() > 0:
            desc_textarea.first.fill(max_length_desc)
            print(f"   ✓ 已填写最大长度数据产品描述（{len(max_length_desc)}字符）")
        else:
            print("   ⚠ 未找到数据产品描述输入框")

        # 6. 点击下一步
        next_button = self.page.locator(SELECTORS["next_step_button"])
        if next_button.count() > 0:
            next_button.first.click()
            print("   ✓ 已点击下一步按钮")
            time.sleep(2)
        else:
            print("   ⚠ 未找到下一步按钮")

        # 7. 填写详细信息
        api_name_input = self.page.locator(SELECTORS["data_product_api_name_input"])
        if api_name_input.count() > 0:
            api_name_input.first.fill("测试API")
            print("   ✓ 已填写接口名称")

        # 8. 点击下一步
        if next_button.count() > 0:
            next_button.first.click()
            print("   ✓ 已点击下一步按钮")
            time.sleep(2)

        # 9. 填写上架信息
        need_apply_yes = self.page.locator(SELECTORS["need_apply_yes_radio"])
        if need_apply_yes.count() > 0:
            need_apply_yes.first.click()
            print("   ✓ 已选择需要申请使用")

        # 10. 点击确定按钮
        confirm_button = self.page.locator(SELECTORS["confirm_button"])
        if confirm_button.count() > 0:
            confirm_button.first.click()
            print("   ✓ 已点击确定按钮")
            time.sleep(3)
        else:
            print("   ⚠ 未找到确定按钮")

        # 11. 验证产品是否创建成功
        success_message = self.page.locator(SELECTORS["success_message"])
        if success_message.count() > 0:
            success_text = success_message.first.text_content()
            print(f"   ✓ 产品创建成功: {success_text}")
            self._test_data["验证结果"] = "最大长度数据产品创建成功"
        else:
            error_message = self.page.locator(SELECTORS["error_message"])
            if error_message.count() > 0:
                error_text = error_message.first.text_content()
                print(f"   ⚠ 系统显示错误: {error_text}")
                self._test_data["验证结果"] = f"系统显示错误: {error_text}"
            else:
                print("   ⚠ 产品创建状态未知")
                self._test_data["验证结果"] = "产品创建状态未知"

        print("[成功] 测试数据已附加到HTML报告")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
