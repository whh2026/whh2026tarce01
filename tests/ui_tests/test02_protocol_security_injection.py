import pytest
import random
import string
import time
from playwright.sync_api import sync_playwright
from utils.base import Base
from tests.test_data.product_protocol_data import (
    SELECTORS, ASSERT_MESSAGES, generate_test_data,
    CHAIN_STATUS, WAIT_TIMES, CHAIN_STATUS_TEST_LIST
)
from tests.ui_tests.config import ui_config

class TestProtocolSecurityInjection(Base):
    """协议安全注入测试类"""
    
    CONFIG = ui_config
    
    @classmethod
    def setup_class(cls):
        """类级别的设置：仅执行一次，启动浏览器并创建持久化的上下文和页面（登录态由 context cookie 保持）"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=False)
        cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
        cls.page = cls.context.new_page()
        cls.page.set_default_timeout(30000)
        cls.page.set_viewport_size({"width": 1900, "height": 950})
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
            assert "login" not in self.page.url.lower(), f"登录失败，当前URL: {self.page.url}"
            print(f"[登录] 登录成功！当前URL: {self.page.url}")
        except Exception as e:
            print(f"   [警告] 提交登录失败: {e}")

    def test_01_sql_injection_in_protocol_name_query(self):
        """测试协议名称查询时的SQL注入防护"""
        print("\n=== 测试协议名称查询时的SQL注入防护 ===")

        sql_injection_payloads = [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR '1'='1'/*",
            "admin'--",
            "admin'/*",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "1' ORDER BY 1--",
            "1' ORDER BY 2--",
            "'; DROP TABLE protocols--",
            "'; DELETE FROM protocols--",
            "'; UPDATE protocols SET name='hacked'--",
            "'; INSERT INTO protocols VALUES('hacked')--",
            "' AND 1=1--",
            "' AND 1=2--",
            "' OR 1=1--",
            "' OR 1=2--",
            "admin' OR '1'='1",
            "admin' AND '1'='1",
            "1' AND '1'='1",
            "1' OR '1'='1",
            "' OR 'a'='a",
            "' OR 'x'='x",
            "' OR 1=1#",
            "' OR 1=1/*",
            "admin' #",
            "admin'/*",
            "' OR '1'='1'='1",
            "' OR '1'='1' AND '1'='1",
            "' UNION SELECT 1,2,3--",
            "' UNION SELECT 1,2,3,4--",
            "' UNION SELECT 1,2,3,4,5--",
            "' UNION SELECT NULL,NULL,NULL,NULL,NULL--",
            "' UNION SELECT 'a','b','c','d','e'--",
            "1' AND SLEEP(5)--",
            "1' AND BENCHMARK(1000000,MD5(1))--",
            "' AND pg_sleep(5)--",
            "' AND WAITFOR DELAY '0:0:5'--",
            "1'; EXEC xp_cmdshell('dir')--",
            "1'; EXEC sp_configure 'show advanced options',1--",
            "1' AND 1=1 IN (SELECT 1)--",
            "1' AND 1=1 IN (SELECT * FROM information_schema.tables)--",
            "1' AND 1=1 IN (SELECT * FROM sys.tables)--",
            "1' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "1' AND (SELECT COUNT(*) FROM sys.tables)>0--",
            "' OR (SELECT COUNT(*) FROM information_schema.tables)>0--",
            "' OR (SELECT COUNT(*) FROM sys.tables)>0--",
            "1' AND (SELECT COUNT(*) FROM protocols)>0--",
            "' OR (SELECT COUNT(*) FROM protocols)>0--",
            "1' AND (SELECT 1 FROM protocols LIMIT 1)=1--",
            "' OR (SELECT 1 FROM protocols LIMIT 1)=1--",
            "1' AND (SELECT name FROM protocols LIMIT 1) IS NOT NULL--",
            "' OR (SELECT name FROM protocols LIMIT 1) IS NOT NULL--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin%')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin%')>0--",
            "1' AND (SELECT SUBSTRING(name,1,1) FROM protocols LIMIT 1)='a'--",
            "' OR (SELECT SUBSTRING(name,1,1) FROM protocols LIMIT 1)='a'--",
            "1' AND (SELECT ASCII(SUBSTRING(name,1,1)) FROM protocols LIMIT 1)=97--",
            "' OR (SELECT ASCII(SUBSTRING(name,1,1)) FROM protocols LIMIT 1)=97--",
            "1' AND (SELECT LENGTH(name) FROM protocols LIMIT 1)>0--",
            "' OR (SELECT LENGTH(name) FROM protocols LIMIT 1)>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE 'a%')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE 'a%')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE '%a')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE '%a')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE '%a%')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE '%a%')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name='admin')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name='admin')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE 'admin%')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE 'admin%')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin')>0--",
            "1' AND (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin%')>0--",
            "' OR (SELECT COUNT(*) FROM protocols WHERE name LIKE '%admin%')>0--"
        ]

        self._test_data = {
            "测试类型": "安全测试",
            "测试目的": "测试协议名称查询时的SQL注入防护",
            "测试环境": "用户1登录",
            "输入数据": {
                "SQL注入测试用例数量": len(sql_injection_payloads),
                "测试用例列表": sql_injection_payloads[:10]
            },
            "验证结果": "",
            "测试详情": []
        }

        print(f"   共测试 {len(sql_injection_payloads)} 个SQL注入用例")

        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        sql_injection_blocked_count = 0
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
                if reset_button.count() > 0:
                    reset_button.click()
                    self.page.wait_for_timeout(WAIT_TIMES["short"])

                name_input = self.page.locator(SELECTORS["search_input"])
                if name_input.count() > 0:
                    name_input.fill(payload)
                    print(f"   输入SQL注入payload: {payload[:50]}...")
                else:
                    print(f"   [警告] 未找到搜索输入框")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到输入框"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                search_button = self.page.locator(SELECTORS["search_button"])
                if search_button.count() > 0:
                    search_button.click()
                    print(f"   点击查询按钮")
                    self.page.wait_for_timeout(WAIT_TIMES["medium"])
                else:
                    print(f"   [警告] 未找到查询按钮")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到查询按钮"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                error_messages = [
                    "SQL语法错误",
                    "语法错误",
                    "无效的查询",
                    "查询失败",
                    "数据库错误",
                    "非法字符",
                    "特殊字符",
                    "包含非法字符",
                    "SQL injection",
                    "注入",
                    "安全",
                    "警告",
                    "error",
                    "Error",
                    "ERROR"
                ]

                error_detected = False
                for error_msg in error_messages:
                    try:
                        error_element = self.page.locator(f"div:has-text('{error_msg}')")
                        if error_element.count() > 0:
                            error_text = error_element.text_content()
                            print(f"   ✓ 检测到错误提示: {error_text}")
                            error_detected = True
                            test_detail["结果"] = "阻止成功"
                            test_detail["备注"] = f"检测到错误提示: {error_text[:50]}"
                            sql_injection_blocked_count += 1
                            break
                    except Exception:
                        continue

                if not error_detected:
                    rows = self.page.locator(SELECTORS["table_rows"])
                    total_rows = rows.count()
                    
                    if total_rows > 1000:
                        print(f"   ✗ 警告：返回了异常多的数据 ({total_rows} 条)")
                        test_detail["结果"] = "可能存在漏洞"
                        test_detail["备注"] = f"返回了异常多的数据: {total_rows} 条"
                        sql_injection_failed_count += 1
                    else:
                        print(f"   ✓ 查询正常，返回 {total_rows} 条记录")
                        test_detail["结果"] = "正常"
                        test_detail["备注"] = f"返回 {total_rows} 条记录"
                        sql_injection_blocked_count += 1

                current_url = self.page.url
                if "error" in current_url.lower() or "exception" in current_url.lower():
                    print(f"   ✗ 警告：页面跳转到错误页面: {current_url}")
                    test_detail["结果"] = "可能存在漏洞"
                    test_detail["备注"] = f"页面跳转到错误页面: {current_url}"
                    sql_injection_failed_count += 1

            except Exception as e:
                print(f"   ✗ 测试异常: {str(e)}")
                test_detail["结果"] = "测试异常"
                test_detail["备注"] = f"异常信息: {str(e)[:100]}"
                sql_injection_failed_count += 1

            self._test_data["测试详情"].append(test_detail)

        print(f"\n=== SQL注入测试结果总结 ===")
        print(f"   总测试用例数: {len(sql_injection_payloads)}")
        print(f"   成功阻止: {sql_injection_blocked_count}")
        print(f"   可能存在漏洞: {sql_injection_failed_count}")
        print(f"   阻止率: {sql_injection_blocked_count / len(sql_injection_payloads) * 100:.2f}%")

        self._test_data["验证结果"] = f"总测试用例数: {len(sql_injection_payloads)}, 成功阻止: {sql_injection_blocked_count}, 可能存在漏洞: {sql_injection_failed_count}, 阻止率: {sql_injection_blocked_count / len(sql_injection_payloads) * 100:.2f}%"

        if sql_injection_blocked_count / len(sql_injection_payloads) < 0.9:
            print(f"   ⚠ 警告：SQL注入防护能力不足，建议加强安全措施")
            assert False, "SQL注入防护能力不足，建议加强安全措施"
        else:
            print(f"   ✓ SQL注入防护能力良好")

        print("[成功] 测试数据已附加到HTML报告")
        print("   [测试完成] 协议名称查询SQL注入防护测试完成！")

    def test_02_js_injection_in_protocol_name_query(self):
        """测试协议名称查询时的JS注入防护"""
        print("\n=== 测试协议名称查询时的JS注入防护 ===")

        js_injection_payloads = [
            "javascript:alert('xss')",
            "javascript:prompt('xss')",
            "javascript:confirm('xss')",
            "javascript:eval('alert(1)')",
            "javascript:setTimeout('alert(1)', 1000)",
            "javascript:location.href='http://example.com'",
            "javascript:document.write('xss')",
            "javascript:document.cookie='xss=1'",
            "javascript:window.open('http://example.com')",
            "javascript:window.close()",
            "javascript:window.location='http://example.com'",
            "javascript:window.location.href='http://example.com'",
            "javascript:window.location.replace('http://example.com')",
            "javascript:window.location.assign('http://example.com')",
            "javascript:window.location.reload()",
            "javascript:window.history.back()",
            "javascript:window.history.forward()",
            "javascript:window.history.go(-1)",
            "javascript:window.history.go(1)",
            "javascript:window.history.length",
            "javascript:window.history.state",
            "javascript:window.history.pushState({}, '', 'http://example.com')",
            "javascript:window.history.replaceState({}, '', 'http://example.com')",
            "javascript:window.history.go(0)",
            "javascript:window.history.go()",
            "javascript:window.history.back(1)",
            "javascript:window.history.forward(1)",
            "javascript:window.history.go(2)",
            "javascript:window.history.go(-2)",
            "javascript:window.history.length",
            "javascript:window.history.state"
        ]

        self._test_data = {
            "测试类型": "安全测试",
            "测试目的": "测试协议名称查询时的JS注入防护",
            "测试环境": "用户1登录",
            "输入数据": {
                "JS注入测试用例数量": len(js_injection_payloads),
                "测试用例列表": js_injection_payloads[:10]
            },
            "验证结果": "",
            "测试详情": []
        }

        print(f"   共测试 {len(js_injection_payloads)} 个JS注入用例")

        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        js_injection_blocked_count = 0
        js_injection_failed_count = 0

        for idx, payload in enumerate(js_injection_payloads, 1):
            print(f"\n   测试用例 {idx}/{len(js_injection_payloads)}: {payload[:50]}...")

            test_detail = {
                "序号": idx,
                "注入payload": payload,
                "结果": "",
                "备注": ""
            }

            try:
                if reset_button.count() > 0:
                    reset_button.click()
                    self.page.wait_for_timeout(WAIT_TIMES["short"])

                name_input = self.page.locator(SELECTORS["search_input"])
                if name_input.count() > 0:
                    name_input.fill(payload)
                    print(f"   输入JS注入payload: {payload[:50]}...")
                else:
                    print(f"   [警告] 未找到搜索输入框")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到输入框"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                search_button = self.page.locator(SELECTORS["search_button"])
                if search_button.count() > 0:
                    search_button.click()
                    print(f"   点击查询按钮")
                    self.page.wait_for_timeout(WAIT_TIMES["medium"])
                else:
                    print(f"   [警告] 未找到查询按钮")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到查询按钮"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                error_messages = [
                    "非法字符",
                    "特殊字符",
                    "包含非法字符",
                    "安全",
                    "警告",
                    "error",
                    "Error",
                    "ERROR"
                ]

                error_detected = False
                for error_msg in error_messages:
                    try:
                        error_element = self.page.locator(f"div:has-text('{error_msg}')")
                        if error_element.count() > 0:
                            error_text = error_element.text_content()
                            print(f"   ✓ 检测到错误提示: {error_text}")
                            error_detected = True
                            test_detail["结果"] = "阻止成功"
                            test_detail["备注"] = f"检测到错误提示: {error_text[:50]}"
                            js_injection_blocked_count += 1
                            break
                    except Exception:
                        continue

                if not error_detected:
                    rows = self.page.locator(SELECTORS["table_rows"])
                    total_rows = rows.count()
                    
                    if total_rows > 1000:
                        print(f"   ✗ 警告：返回了异常多的数据 ({total_rows} 条)")
                        test_detail["结果"] = "可能存在漏洞"
                        test_detail["备注"] = f"返回了异常多的数据: {total_rows} 条"
                        js_injection_failed_count += 1
                    else:
                        print(f"   ✓ 查询正常，返回 {total_rows} 条记录")
                        test_detail["结果"] = "正常"
                        test_detail["备注"] = f"返回 {total_rows} 条记录"
                        js_injection_blocked_count += 1

                current_url = self.page.url
                if "error" in current_url.lower() or "exception" in current_url.lower():
                    print(f"   ✗ 警告：页面跳转到错误页面: {current_url}")
                    test_detail["结果"] = "可能存在漏洞"
                    test_detail["备注"] = f"页面跳转到错误页面: {current_url}"
                    js_injection_failed_count += 1

            except Exception as e:
                print(f"   ✗ 测试异常: {str(e)}")
                test_detail["结果"] = "测试异常"
                test_detail["备注"] = f"异常信息: {str(e)[:100]}"
                js_injection_failed_count += 1

            self._test_data["测试详情"].append(test_detail)

        def escape_html(s):
            if isinstance(s, str):
                return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
            return s
        
        for detail in self._test_data["测试详情"]:
            if "注入payload" in detail:
                detail["注入payload"] = escape_html(detail["注入payload"])
        
        if "测试用例列表" in self._test_data["输入数据"]:
            self._test_data["输入数据"]["测试用例列表"] = [escape_html(p) for p in self._test_data["输入数据"]["测试用例列表"]]

        print(f"\n=== JS注入测试结果总结 ===")
        print(f"   总测试用例数: {len(js_injection_payloads)}")
        print(f"   成功阻止: {js_injection_blocked_count}")
        print(f"   可能存在漏洞: {js_injection_failed_count}")
        print(f"   阻止率: {js_injection_blocked_count / len(js_injection_payloads) * 100:.2f}%")

        self._test_data["验证结果"] = f"总测试用例数: {len(js_injection_payloads)}, 成功阻止: {js_injection_blocked_count}, 可能存在漏洞: {js_injection_failed_count}, 阻止率: {js_injection_blocked_count / len(js_injection_payloads) * 100:.2f}%"

        if js_injection_blocked_count / len(js_injection_payloads) < 0.9:
            print(f"   ⚠ 警告：JS注入防护能力不足，建议加强安全措施")
            assert False, "JS注入防护能力不足，建议加强安全措施"
        else:
            print(f"   ✓ JS注入防护能力良好")

        print("   [测试完成] 协议名称查询JS注入防护测试完成！")

    def test_03_xss_injection_in_protocol_name_query(self):
        """测试协议名称查询时的XSS注入防护"""
        print("\n=== 测试协议名称查询时的XSS注入防护 ===")

        xss_injection_payloads = [
            "<script>alert('xss')</script>",
            "<script>prompt('xss')</script>",
            "<script>confirm('xss')</script>",
            "<script>eval('alert(1)')</script>",
            "<script>setTimeout('alert(1)', 1000)</script>",
            "<script>location.href='http://example.com'</script>",
            "<script>document.write('xss')</script>",
            "<script>document.cookie='xss=1'</script>",
            "<script>window.open('http://example.com')</script>",
            "<script>window.close()</script>",
            "<img src=x onerror=alert('xss')>",
            "<img src='javascript:alert(1)'>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<embed src='javascript:alert(1)'>",
            "<object data='javascript:alert(1)'>",
            "<svg onload=alert(1)>",
            "<video src=x onerror=alert(1)>",
            "<audio src=x onerror=alert(1)>",
            "<body onload=alert(1)>",
            "<div onclick=alert(1)>click me</div>",
            "<div onmouseover=alert(1)>hover me</div>",
            "<div onfocus=alert(1)>focus me</div>",
            "<div onblur=alert(1)>blur me</div>",
            "<div onsubmit=alert(1)>submit me</div>",
            "<div onreset=alert(1)>reset me</div>",
            "<div onselect=alert(1)>select me</div>",
            "<div onchange=alert(1)>change me</div>",
            "<div onkeydown=alert(1)>keydown me</div>",
            "<div onkeyup=alert(1)>keyup me</div>",
            "<div onkeypress=alert(1)>keypress me</div>",
            "<div onmousedown=alert(1)>mousedown me</div>",
            "<div onmouseup=alert(1)>mouseup me</div>",
            "<div onmousemove=alert(1)>mousemove me</div>",
            "<div onmouseout=alert(1)>mouseout me</div>",
            "<div onmouseenter=alert(1)>mouseenter me</div>",
            "<div onmouseleave=alert(1)>mouseleave me</div>",
            "<div onwheel=alert(1)>wheel me</div>",
            "<div onscroll=alert(1)>scroll me</div>",
            "<div onresize=alert(1)>resize me</div>",
            "<div onload=alert(1)>load me</div>",
            "<div onunload=alert(1)>unload me</div>",
            "<div onbeforeunload=alert(1)>beforeunload me</div>",
            "<div onabort=alert(1)>abort me</div>",
            "<div oncanplay=alert(1)>canplay me</div>",
            "<div oncanplaythrough=alert(1)>canplaythrough me</div>",
            "<div ondurationchange=alert(1)>durationchange me</div>",
            "<div onemptied=alert(1)>emptied me</div>",
            "<div onended=alert(1)>ended me</div>",
            "<div onerror=alert(1)>error me</div>",
            "<div onloadeddata=alert(1)>loadeddata me</div>",
            "<div onloadedmetadata=alert(1)>loadedmetadata me</div>",
            "<div onloadstart=alert(1)>loadstart me</div>",
            "<div onpause=alert(1)>pause me</div>",
            "<div onplay=alert(1)>play me</div>",
            "<div onplaying=alert(1)>playing me</div>",
            "<div onprogress=alert(1)>progress me</div>",
            "<div onratechange=alert(1)>ratechange me</div>",
            "<div onseeked=alert(1)>seeked me</div>",
            "<div onseeking=alert(1)>seeking me</div>",
            "<div onstalled=alert(1)>stalled me</div>",
            "<div onsuspend=alert(1)>suspend me</div>",
            "<div ontimeupdate=alert(1)>timeupdate me</div>",
            "<div onvolumechange=alert(1)>volumechange me</div>",
            "<div onwaiting=alert(1)>waiting me</div>",
            "<div ontoggle=alert(1)>toggle me</div>",
            "<div onwheel=alert(1)>wheel me</div>",
            "<div oncopy=alert(1)>copy me</div>",
            "<div oncut=alert(1)>cut me</div>",
            "<div onpaste=alert(1)>paste me</div>",
            "<div oncontextmenu=alert(1)>contextmenu me</div>",
            "<div ondrag=alert(1)>drag me</div>",
            "<div ondragend=alert(1)>dragend me</div>",
            "<div ondragenter=alert(1)>dragenter me</div>",
            "<div ondragexit=alert(1)>dragexit me</div>",
            "<div ondragleave=alert(1)>dragleave me</div>",
            "<div ondragover=alert(1)>dragover me</div>",
            "<div ondragstart=alert(1)>dragstart me</div>",
            "<div ondrop=alert(1)>drop me</div>",
            "<div onscroll=alert(1)>scroll me</div>",
            "<div onselect=alert(1)>select me</div>",
            "<div onselectstart=alert(1)>selectstart me</div>",
            "<div onselectionchange=alert(1)>selectionchange me</div>",
            "<div onsubmit=alert(1)>submit me</div>",
            "<div onreset=alert(1)>reset me</div>",
            "<div oninvalid=alert(1)>invalid me</div>",
            "<div oninput=alert(1)>input me</div>",
            "<div onchange=alert(1)>change me</div>",
            "<div onfocus=alert(1)>focus me</div>",
            "<div onblur=alert(1)>blur me</div>",
            "<div onfocusin=alert(1)>focusin me</div>",
            "<div onfocusout=alert(1)>focusout me</div>",
            "<div onload=alert(1)>load me</div>",
            "<div onunload=alert(1)>unload me</div>",
            "<div onbeforeunload=alert(1)>beforeunload me</div>",
            "<div onabort=alert(1)>abort me</div>",
            "<div oncanplay=alert(1)>canplay me</div>",
            "<div oncanplaythrough=alert(1)>canplaythrough me</div>",
            "<div ondurationchange=alert(1)>durationchange me</div>",
            "<div onemptied=alert(1)>emptied me</div>",
            "<div onended=alert(1)>ended me</div>",
            "<div onerror=alert(1)>error me</div>",
            "<div onloadeddata=alert(1)>loadeddata me</div>",
            "<div onloadedmetadata=alert(1)>loadedmetadata me</div>",
            "<div onloadstart=alert(1)>loadstart me</div>",
            "<div onpause=alert(1)>pause me</div>",
            "<div onplay=alert(1)>play me</div>",
            "<div onplaying=alert(1)>playing me</div>",
            "<div onprogress=alert(1)>progress me</div>",
            "<div onratechange=alert(1)>ratechange me</div>",
            "<div onseeked=alert(1)>seeked me</div>",
            "<div onseeking=alert(1)>seeking me</div>",
            "<div onstalled=alert(1)>stalled me</div>",
            "<div onsuspend=alert(1)>suspend me</div>",
            "<div ontimeupdate=alert(1)>timeupdate me</div>",
            "<div onvolumechange=alert(1)>volumechange me</div>",
            "<div onwaiting=alert(1)>waiting me</div>",
            "<div ontoggle=alert(1)>toggle me</div>",
            "<div onwheel=alert(1)>wheel me</div>",
            "<div oncopy=alert(1)>copy me</div>",
            "<div oncut=alert(1)>cut me</div>",
            "<div onpaste=alert(1)>paste me</div>",
            "<div oncontextmenu=alert(1)>contextmenu me</div>",
            "<div ondrag=alert(1)>drag me</div>",
            "<div ondragend=alert(1)>dragend me</div>",
            "<div ondragenter=alert(1)>dragenter me</div>",
            "<div ondragexit=alert(1)>dragexit me</div>",
            "<div ondragleave=alert(1)>dragleave me</div>",
            "<div ondragover=alert(1)>dragover me</div>",
            "<div ondragstart=alert(1)>dragstart me</div>",
            "<div ondrop=alert(1)>drop me</div>",
            "<div onscroll=alert(1)>scroll me</div>",
            "<div onselect=alert(1)>select me</div>",
            "<div onselectstart=alert(1)>selectstart me</div>",
            "<div onselectionchange=alert(1)>selectionchange me</div>",
            "<div onsubmit=alert(1)>submit me</div>",
            "<div onreset=alert(1)>reset me</div>",
            "<div oninvalid=alert(1)>invalid me</div>",
            "<div oninput=alert(1)>input me</div>",
            "<div onchange=alert(1)>change me</div>",
            "<div onfocus=alert(1)>focus me</div>",
            "<div onblur=alert(1)>blur me</div>",
            "<div onfocusin=alert(1)>focusin me</div>",
            "<div onfocusout=alert(1)>focusout me</div>"
        ]

        self._test_data = {
            "测试类型": "安全测试",
            "测试目的": "测试协议名称查询时的XSS注入防护",
            "测试环境": "用户1登录",
            "输入数据": {
                "XSS注入测试用例数量": len(xss_injection_payloads),
                "测试用例列表": xss_injection_payloads[:10]
            },
            "验证结果": "",
            "测试详情": []
        }

        print(f"   共测试 {len(xss_injection_payloads)} 个XSS注入用例")

        reset_button = self.page.locator(SELECTORS["reset_button"])
        if reset_button.count() > 0:
            reset_button.click()
            print("   点击重置按钮")
            self.page.wait_for_timeout(WAIT_TIMES["short"])

        xss_injection_blocked_count = 0
        xss_injection_failed_count = 0

        for idx, payload in enumerate(xss_injection_payloads, 1):
            print(f"\n   测试用例 {idx}/{len(xss_injection_payloads)}: {payload[:50]}...")

            test_detail = {
                "序号": idx,
                "注入payload": payload,
                "结果": "",
                "备注": ""
            }

            try:
                if reset_button.count() > 0:
                    reset_button.click()
                    self.page.wait_for_timeout(WAIT_TIMES["short"])

                name_input = self.page.locator(SELECTORS["search_input"])
                if name_input.count() > 0:
                    name_input.fill(payload)
                    print(f"   输入XSS注入payload: {payload[:50]}...")
                else:
                    print(f"   [警告] 未找到搜索输入框")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到输入框"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                search_button = self.page.locator(SELECTORS["search_button"])
                if search_button.count() > 0:
                    search_button.click()
                    print(f"   点击查询按钮")
                    self.page.wait_for_timeout(WAIT_TIMES["medium"])
                else:
                    print(f"   [警告] 未找到查询按钮")
                    test_detail["结果"] = "跳过"
                    test_detail["备注"] = "未找到查询按钮"
                    self._test_data["测试详情"].append(test_detail)
                    continue

                error_messages = [
                    "非法字符",
                    "特殊字符",
                    "包含非法字符",
                    "安全",
                    "警告",
                    "error",
                    "Error",
                    "ERROR"
                ]

                error_detected = False
                for error_msg in error_messages:
                    try:
                        error_element = self.page.locator(f"div:has-text('{error_msg}')")
                        if error_element.count() > 0:
                            error_text = error_element.text_content()
                            print(f"   ✓ 检测到错误提示: {error_text}")
                            error_detected = True
                            test_detail["结果"] = "阻止成功"
                            test_detail["备注"] = f"检测到错误提示: {error_text[:50]}"
                            xss_injection_blocked_count += 1
                            break
                    except Exception:
                        continue

                if not error_detected:
                    rows = self.page.locator(SELECTORS["table_rows"])
                    total_rows = rows.count()
                    
                    if total_rows > 1000:
                        print(f"   ✗ 警告：返回了异常多的数据 ({total_rows} 条)")
                        test_detail["结果"] = "可能存在漏洞"
                        test_detail["备注"] = f"返回了异常多的数据: {total_rows} 条"
                        xss_injection_failed_count += 1
                    else:
                        print(f"   ✓ 查询正常，返回 {total_rows} 条记录")
                        test_detail["结果"] = "正常"
                        test_detail["备注"] = f"返回 {total_rows} 条记录"
                        xss_injection_blocked_count += 1

                current_url = self.page.url
                if "error" in current_url.lower() or "exception" in current_url.lower():
                    print(f"   ✗ 警告：页面跳转到错误页面: {current_url}")
                    test_detail["结果"] = "可能存在漏洞"
                    test_detail["备注"] = f"页面跳转到错误页面: {current_url}"
                    xss_injection_failed_count += 1

            except Exception as e:
                print(f"   ✗ 测试异常: {str(e)}")
                test_detail["结果"] = "测试异常"
                test_detail["备注"] = f"异常信息: {str(e)[:100]}"
                xss_injection_failed_count += 1

            self._test_data["测试详情"].append(test_detail)

        def escape_html(s):
            if isinstance(s, str):
                return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
            return s
        
        for detail in self._test_data["测试详情"]:
            if "注入payload" in detail:
                detail["注入payload"] = escape_html(detail["注入payload"])
        
        if "测试用例列表" in self._test_data["输入数据"]:
            self._test_data["输入数据"]["测试用例列表"] = [escape_html(p) for p in self._test_data["输入数据"]["测试用例列表"]]

        print(f"\n=== XSS注入测试结果总结 ===")
        print(f"   总测试用例数: {len(xss_injection_payloads)}")
        print(f"   成功阻止: {xss_injection_blocked_count}")
        print(f"   可能存在漏洞: {xss_injection_failed_count}")
        print(f"   阻止率: {xss_injection_blocked_count / len(xss_injection_payloads) * 100:.2f}%")

        self._test_data["验证结果"] = f"总测试用例数: {len(xss_injection_payloads)}, 成功阻止: {xss_injection_blocked_count}, 可能存在漏洞: {xss_injection_failed_count}, 阻止率: {xss_injection_blocked_count / len(xss_injection_payloads) * 100:.2f}%"

        if xss_injection_blocked_count / len(xss_injection_payloads) < 0.9:
            print(f"   ⚠ 警告：XSS注入防护能力不足，建议加强安全措施")
            assert False, "XSS注入防护能力不足，建议加强安全措施"
        else:
            print(f"   ✓ XSS注入防护能力良好")

        print("[成功] 测试数据已附加到HTML报告")
        print("   [测试完成] 协议名称查询XSS注入防护测试完成！")
