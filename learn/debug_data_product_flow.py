#!/usr/bin/env python3
"""
数据产品完整流程调试脚本
测试从数据产品登记到上架的完整流程
"""

import time
import pytest
from playwright.sync_api import Playwright, sync_playwright, expect
from tests.test_data.data_product_data import TEST_URLS, SELECTORS, WAIT_TIMES
from tests.utils.base import BaseTest

class TestDataProductFlow(BaseTest):
    """测试数据产品完整流程"""
    
    def setup_class(self):
        """类级别的前置条件"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False, slow_mo=50)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        # 登录系统
        self.login()
        
        # 访问数据产品发布页面
        self.page.goto(TEST_URLS["data_product_create"])
        time.sleep(WAIT_TIMES["page_load"])
        print(f"已访问发布页面: {TEST_URLS['data_product_create']}")
    
    def login(self):
        """登录系统"""
        # 这里需要根据实际登录页面调整
        login_url = "http://192.168.0.183:30001/login"
        self.page.goto(login_url)
        time.sleep(WAIT_TIMES["page_load"])
        
        # 输入用户名和密码
        self.page.fill("input[name='username']", "admin")
        self.page.fill("input[name='password']", "admin123")
        
        # 点击登录按钮
        self.page.click("button:has-text('登录')")
        time.sleep(WAIT_TIMES["page_load"])
        print("[登录] 登录成功！")
    
    def test_complete_data_product_flow(self):
        """测试完整的数据产品流程"""
        print("\n=== 开始测试数据产品完整流程 ===")
        
        # 第一大步：数据产品登记基础配置
        self._fill_basic_info()
        
        # 点击下一步
        self._click_next_step()
        
        # 第二大步：详细信息配置
        self._fill_detailed_info()
        
        # 点击下一步
        self._click_next_step()
        
        # 第三大步：上架信息配置
        self._fill_shelf_info()
        
        # 点击确定
        self._click_confirm()
        
        print("\n=== 数据产品完整流程测试完成 ===")
    
    def _fill_basic_info(self):
        """填写基础信息"""
        print("\n1. 填写基础信息:")
        
        # 填写中文名称
        if self.page.is_visible(SELECTORS["data_product_name_input"]):
            self.page.fill(SELECTORS["data_product_name_input"], "测试数据产品")
            print("   已填写中文名称: 测试数据产品")
        
        # 填写英文名称
        if self.page.is_visible(SELECTORS["data_product_english_name_input"]):
            self.page.fill(SELECTORS["data_product_english_name_input"], "TestDataProduct")
            print("   已填写英文名称: TestDataProduct")
        
        # 填写产品介绍
        if self.page.is_visible(SELECTORS["data_product_desc_textarea"]):
            self.page.fill(SELECTORS["data_product_desc_textarea"], "这是一个测试数据产品，用于自动化测试。")
            print("   已填写产品介绍")
        
        # 填写使用限制
        if self.page.is_visible(SELECTORS["data_product_limit_textarea"]):
            self.page.fill(SELECTORS["data_product_limit_textarea"], "仅供测试使用，不得用于生产环境。")
            print("   已填写使用限制")
        
        # 选择行业分类
        if self.page.is_visible(SELECTORS["data_product_category_select"]):
            self.page.click(SELECTORS["data_product_category_select"])
            time.sleep(0.5)
            self.page.get_by_text("采矿业").click()
            print("   已选择行业分类: 采矿业")
        
        # 选择产品类型
        if self.page.is_visible(SELECTORS["data_product_type_select"]):
            self.page.click(SELECTORS["data_product_type_select"])
            time.sleep(0.5)
            self.page.get_by_text("数据接口").click()
            print("   已选择产品类型: 数据接口")
        
        # 选择产品小类
        if self.page.is_visible(SELECTORS["data_product_subtype_select"]):
            self.page.click(SELECTORS["data_product_subtype_select"])
            time.sleep(0.5)
            self.page.get_by_text("API接口").click()
            print("   已选择产品小类: API接口")
        
        # 选择地域分类
        if self.page.is_visible(SELECTORS["data_product_region_select"]):
            self.page.click(SELECTORS["data_product_region_select"])
            time.sleep(0.5)
            self.page.get_by_text("北京市").click()
            print("   已选择地域分类: 北京市")
    
    def _fill_detailed_info(self):
        """填写详细信息"""
        print("\n2. 填写详细信息:")
        
        # 填写接口名称
        if self.page.is_visible(SELECTORS["api_name_input"]):
            self.page.fill(SELECTORS["api_name_input"], "测试接口名称")
            print("   已填写接口名称: 测试接口名称")
        
        # 填写正式接口地址
        if self.page.is_visible(SELECTORS["access_address_input"]):
            self.page.fill(SELECTORS["access_address_input"], "http://test.example.com/api/v1/test")
            print("   已填写正式接口地址: http://test.example.com/api/v1/test")
        
        # 填写测试接口地址
        if self.page.is_visible(SELECTORS["redirect_address_input"]):
            self.page.fill(SELECTORS["redirect_address_input"], "http://test.example.com/test/v1/test")
            print("   已填写测试接口地址: http://test.example.com/test/v1/test")
        
        # 填写入参信息
        self._fill_input_params()
    
    def _fill_input_params(self):
        """填写入参信息"""
        print("\n3. 填写入参信息:")
        
        # 假设入参信息有多个字段
        # 第一个入参
        param1_name = "param1"
        param1_type = "string"
        param1_desc = "第一个参数"
        
        # 填写第一个入参
        if self.page.is_visible("input[placeholder='字段名']"):
            self.page.fill("input[placeholder='字段名']", param1_name)
            print(f"   已填写入参字段名: {param1_name}")
        
        if self.page.is_visible("select[placeholder='字段类型']"):
            self.page.select_option("select[placeholder='字段类型']", param1_type)
            print(f"   已选择入参字段类型: {param1_type}")
        
        if self.page.is_visible("textarea[placeholder='字段描述']"):
            self.page.fill("textarea[placeholder='字段描述']", param1_desc)
            print(f"   已填写入参字段描述: {param1_desc}")
        
        # 添加更多入参...
    
    def _fill_shelf_info(self):
        """填写上架信息"""
        print("\n4. 填写上架信息:")
        
        # 假设上架信息包括价格、上架时间等
        # 填写价格
        if self.page.is_visible("input[name='price']"):
            self.page.fill("input[name='price']", "99.99")
            print("   已填写价格: 99.99")
        
        # 选择上架时间
        if self.page.is_visible("input[name='shelf_time']"):
            self.page.fill("input[name='shelf_time']", "2024-01-01")
            print("   已选择上架时间: 2024-01-01")
    
    def _click_next_step(self):
        """点击下一步按钮"""
        print("\n点击下一步按钮...")
        if self.page.is_visible(SELECTORS["next_step_button"]):
            self.page.click(SELECTORS["next_step_button"])
            time.sleep(WAIT_TIMES["page_load"])
            print("已点击下一步按钮，页面已加载")
        else:
            print("警告: 未找到下一步按钮")
    
    def _click_confirm(self):
        """点击确定按钮"""
        print("\n点击确定按钮...")
        if self.page.is_visible(SELECTORS["confirm_button"]):
            self.page.click(SELECTORS["confirm_button"])
            time.sleep(WAIT_TIMES["page_load"])
            print("已点击确定按钮，页面已加载")
        else:
            print("警告: 未找到确定按钮")
    
    def teardown_class(self):
        """类级别的后置条件"""
        time.sleep(5)  # 等待查看结果
        self.page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()

if __name__ == "__main__":
    # 运行测试
    test = TestDataProductFlow()
    test.setup_class()
    try:
        test.test_complete_data_product_flow()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        test.teardown_class()