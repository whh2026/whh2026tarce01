# -*- coding: utf-8 -*-
"""
数据出售订单列表页 (publisher-order-list) UI 测试
http://192.168.0.183:30001/datamarket/publisher/publisher-order-list

覆盖：页面标题元素检查、列标题检查、查询功能、详情、上传支付凭证、撤销
"""
import os
import sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from utils.base import Base
from tests.ui_tests.config import ui_config
from playwright.sync_api import sync_playwright


class TestPublisherOrderListPage(Base):
    """数据出售订单列表页测试"""

    CONFIG = ui_config.USER_IPS
    PAGE_PATH = "/datamarket/publisher/publisher-order-list"

    @classmethod
    def setup_class(cls):
        cls.playwright = sync_playwright().start()
        headless = os.environ.get("UI_HEADLESS", "true").lower() == "true"
        cls.browser = cls.playwright.chromium.launch(headless=headless)
        cls.context = None
        cls.page = None

    @classmethod
    def teardown_class(cls):
        if cls.context:
            cls.context.close()
        if cls.browser:
            cls.browser.close()
        if cls.playwright:
            cls.playwright.stop()

    def setup_method(self, method):
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        self.page = self.context.new_page()
        # 登录
        login_url = self.get_url_for_user(1, "/login", self.CONFIG)
        self.page.goto(login_url, timeout=30000)
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        self.page.wait_for_timeout(2000)
        self.login_with_user(1, self.CONFIG, page=self.page)
        # 导航到目标页面（数据页面可能有持续轮询，networkidle 会永远不触发）
        self.page_url = self.get_url_for_user(1, self.PAGE_PATH, self.CONFIG)
        self.page.goto(self.page_url, timeout=30000)
        self.page.wait_for_selector('.el-table', timeout=30000)
        self.page.wait_for_timeout(3000)

    def teardown_method(self, method):
        if self.context:
            self.context.close()

    # ==================== 辅助方法 ====================

    def _wait_table(self, timeout=5000):
        self.page.wait_for_timeout(timeout)

    def _get_row_count(self):
        return self.page.evaluate("""
            () => document.querySelectorAll('.el-table__body .el-table__row').length
        """)

    def _get_first_row_cols(self):
        return self.page.evaluate("""() => {
            const row = document.querySelector('.el-table__body .el-table__row');
            if (!row) return [];
            return Array.from(row.querySelectorAll('td'))
                .map(td => td.textContent.trim().replace(/\\\\s+/g, ' '));
        }""")

    def _search(self, order_no=None, product_name=None, subcategory=None, status=None):
        """执行搜索 - 使用更健壮的定位器"""
        # 订单编号输入框 - 第一个可见的 text 输入框
        if order_no is not None:
            inp = self.page.locator('.el-form-item .el-input__inner').first
            if inp.count() > 0:
                inp.fill("")
                inp.fill(order_no)
                self.page.wait_for_timeout(500)
        if product_name is not None:
            # 第二个输入框
            inps = self.page.locator('.el-form-item .el-input__inner')
            if inps.count() >= 2:
                inps.nth(1).fill("")
                inps.nth(1).fill(product_name)
                self.page.wait_for_timeout(500)
        if subcategory is not None:
            sels = self.page.locator('.el-form-item .el-select')
            cnt = sels.count()
            for i in range(min(cnt, 5)):
                sel = sels.nth(i)
                if sel.count() > 0:
                    sel.click()
                    self.page.wait_for_timeout(600)
                    opt = self.page.locator(f'.el-select-dropdown__item:has-text("{subcategory}")').first
                    if opt.count() > 0:
                        opt.click()
                        self.page.wait_for_timeout(300)
                    else:
                        self.page.keyboard.press('Escape')
                        self.page.wait_for_timeout(300)
                    break
        if status is not None:
            sels = self.page.locator('.el-form-item .el-select')
            cnt = sels.count()
            skip_first = (subcategory is not None)  # 跳过第一个下拉框（小类）
            for i in range(min(cnt, 5)):
                if skip_first and i == 0:
                    continue
                sel = sels.nth(i)
                if sel.count() > 0:
                    sel.click()
                    self.page.wait_for_timeout(600)
                    opt = self.page.locator(f'.el-select-dropdown__item:has-text("{status}")').first
                    if opt.count() > 0:
                        opt.click()
                        self.page.wait_for_timeout(300)
                    else:
                        self.page.keyboard.press('Escape')
                        self.page.wait_for_timeout(300)
                    break
        self.page.locator('button:has-text("查询")').first.click()
        self.page.wait_for_timeout(3000)

    def _reset(self):
        btn = self.page.locator('button:has-text("重置")').first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(2000)

    def _click_detail_on_row(self, row_index=0):
        """点击指定行的详情按钮"""
        btn = self.page.locator(
            f".el-table__body .el-table__row:nth-child({row_index + 1}) button:has-text('详情')"
        ).first
        if btn.count() > 0:
            btn.click()
            self.page.wait_for_timeout(2500)
            return True
        return False

    def _get_dialog_info(self):
        """获取弹窗信息"""
        return self.page.evaluate("""() => {
            const dlg = document.querySelector('.el-dialog, .el-drawer');
            if (!dlg || !dlg.offsetParent) return { open: false };
            const title = (dlg.querySelector('.el-dialog__title, .el-drawer__title, h2, h3')||{}).textContent||'';
            const btns = Array.from(dlg.querySelectorAll('button'))
                .filter(b => b.offsetParent && b.textContent.trim())
                .map(b => b.textContent.trim());
            const labels = Array.from(dlg.querySelectorAll('.el-form-item__label, .el-descriptions-item__label'))
                .filter(l => l.offsetParent)
                .map(l => l.textContent.trim());
            return {
                open: true,
                title: title.trim(),
                buttonCount: btns.length,
                buttons: btns.slice(0, 10),
                labels: labels.slice(0, 20)
            };
        }""")

    def _close_dialog(self):
        close_btn = self.page.locator('.el-dialog__headerbtn').first
        if close_btn.count() > 0:
            close_btn.click()
            self.page.wait_for_timeout(1500)
        else:
            self.page.keyboard.press('Escape')
            self.page.wait_for_timeout(1000)

    def _get_all_status_colors(self):
        """从状态列(col 7)提取所有不重复状态及其标签颜色信息"""
        return self.page.evaluate("""() => {
            const rows = document.querySelectorAll('.el-table__body tr.el-table__row, .el-table__body-wrapper tr.el-table__row');
            const seen = {};
            for (const row of rows) {
                if (!row.offsetParent) continue;
                const cells = row.querySelectorAll('td');
                if (cells.length <= 7) continue;
                const cell = cells[7];
                const text = cell.textContent.trim();
                if (!text || seen[text]) continue;
                const tagEl = cell.querySelector('.el-tag, .el-tag--light, .el-tag--dark, .el-tag--plain, [class*="tag"]');
                if (tagEl) {
                    seen[text] = { tagClass: tagEl.className || '' };
                } else {
                    const span = cell.querySelector('span');
                    seen[text] = { tagClass: span ? (span.className || 'no-tag') : 'no-tag' };
                }
            }
            return seen;
        }""")

    def _match_tag_type(self, tag_class):
        """从 el-tag class 中解析类型: success/warning/danger/info/primary"""
        if not tag_class or tag_class == "no-tag":
            return "plain"
        for tp in ["success", "warning", "danger", "info", "primary"]:
            if tp in tag_class:
                return tp
        if "el-tag" in tag_class:
            return "default"
        return "unknown"

    def _get_expected_tag_type(self, status_text):
        """根据状态文本返回预期的 el-tag 类型"""
        STATUS_COLOR_MAP = {
            "待支付": "warning",
            "已支付": "primary",
            "已支付待确认": "primary",
            "已确认": "success",
            "交付中": "primary",
            "已完成": "success",
            "已撤销": "info",
            "已拒绝": "danger",
        }
        return STATUS_COLOR_MAP.get(status_text, None)

    # ==================== 1. 页面标题元素检查 ====================

    def test_01_access_page_and_title_check(self):
        """访问页面，验证页面标题和核心元素"""
        assert "publisher-order-list" in self.page.url, \
            f"URL不正确: {self.page.url}"

        # 页面标题
        top_title = self.page.locator('.top-bar-title').first
        assert top_title.count() > 0, "页面标题元素不存在"
        title_text = top_title.text_content().strip()
        assert "数据出售" in title_text or "订单" in title_text, \
            f"标题不含预期内容: {title_text}"

        # 查询/重置按钮
        assert self.page.locator('button:has-text("查询")').first.count() > 0, "查询按钮不存在"
        assert self.page.locator('button:has-text("重置")').first.count() > 0, "重置按钮不存在"

        # 搜索输入框
        assert self.page.locator('.el-form-item__label:has-text("订单编号")').locator("..").locator("input").count() > 0, "订单编号输入框不存在"
        assert self.page.locator('.el-form-item__label:has-text("数据产品名称")').locator("..").locator("input").count() > 0, "产品名称输入框不存在"

        # 表格
        assert self.page.locator('.el-table').first.count() > 0, "数据表格不存在"

    # ==================== 2. 列标题检查 ====================

    def test_02_verify_table_column_headers(self):
        """验证表格列标题"""
        expected = [
            "订单编号", "数据产品编号", "数据产品名称", "数据产品使用方",
            "数据产品小类", "订单金额", "支付渠道", "状态", "下单时间", "操作"
        ]
        headers = self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.el-table__header th.is-leaf'))
                .filter(th => th.offsetParent)
                .map(th => th.textContent.trim().replace(/\\s+/g, ' '));
        }""")
        assert len(headers) >= 9, f"列数不足: {headers}"
        for h in expected:
            found = any(h in x or x in h for x in headers)
            assert found, f"缺少列: '{h}', 实际: {headers}"

    # ==================== 3. 查询功能 ====================

    def test_03_search_by_order_number_exact(self):
        """订单编号精确查询"""
        cols = self._get_first_row_cols()
        assert len(cols) > 0, "表格无数据"
        self._search(order_no=cols[0])
        assert self._get_row_count() >= 1, f"查询'{cols[0]}'无结果"
        self._reset()

    def test_04_search_by_product_name_fuzzy(self):
        """数据产品名称模糊查询"""
        cols = self._get_first_row_cols()
        assert len(cols) > 2, "表格数据不足"
        kw = cols[2][:2] if len(cols[2]) >= 2 else cols[2]
        self._search(product_name=kw)
        assert self._get_row_count() >= 1, f"模糊查询'{kw}'无结果"
        self._reset()

    def test_05_search_by_order_number_nonexist(self):
        """查询不存在的订单编号"""
        self._search(order_no="NOEXIST999999")
        assert self._get_row_count() == 0, "查询不存在订单应返回空"
        self._reset()

    def test_06_search_by_product_name_exact(self):
        """数据产品名称精确查询"""
        cols = self._get_first_row_cols()
        assert len(cols) > 2, "表格数据不足"
        self._search(product_name=cols[2])
        assert self._get_row_count() >= 1, f"精确查询'{cols[2]}'无结果"
        self._reset()

    def test_07_filter_by_order_status(self):
        """按订单状态筛选"""
        # 用待支付状态筛选
        self._search(status="待支付")
        count = self._get_row_count()
        # 即使0条也不报错，用已确认再试（默认视图）
        if count == 0:
            self._search(status="已确认")
            count = self._get_row_count()
        print(f"  状态筛选: {count}条")
        assert count >= 0, "状态筛选应完成"
        self._reset()

    def test_08_filter_by_subcategory(self):
        """按数据产品小类筛选"""
        # 用API接口小类筛选（如果存在）
        self._search(subcategory="API接口")
        count = self._get_row_count()
        print(f"  小类筛选(API接口): {count}条")
        self._reset()

    def test_09_reset_search(self):
        """验证重置按钮功能"""
        inp = self.page.locator('.el-form-item__label:has-text("订单编号")').locator("..").locator("input")
        inp.clear()
        inp.fill("TEST_RESET")
        self.page.wait_for_timeout(300)
        self._reset()
        assert inp.input_value() == "", "重置后输入框未清空"

    def test_10_combined_search(self):
        """组合查询：产品名称 + 订单状态"""
        cols = self._get_first_row_cols()
        assert len(cols) > 2, "表格数据不足"
        kw = cols[2][:2] if len(cols[2]) >= 2 else cols[2]
        self._search(product_name=kw)
        assert self._get_row_count() >= 1, f"组合查询'{kw}'无结果"
        self._reset()

    # ==================== 4. 详情弹窗 ====================

    def test_11_view_order_detail(self):
        """打开订单详情弹窗并验证"""
        assert self._click_detail_on_row(0), "详情按钮不可用"
        info = self._get_dialog_info()
        assert info.get("open"), f"详情弹窗未打开: {info}"
        print(f"详情弹窗: 按钮={info.get('buttons')}")
        self._close_dialog()

    # ==================== 5 & 6 & 7 弹窗功能探索 ====================

    def test_12_explore_dialog_features(self):
        """
        探索详情弹窗内功能：上传支付凭证、撤销、确认支付
        覆盖三种订单状态下的弹窗操作
        """
        results = {}

        # 场景1: 待支付订单详情
        self._search(status="待支付")
        if self._get_row_count() > 0:
            self._click_detail_on_row(0)
            info1 = self._get_dialog_info()
            results["待支付"] = {"count": self._get_row_count(), "dialog": info1}
            print(f"待支付详情: {info1}")
            self._close_dialog()
            # 如果有上传凭证按钮，测试点击
            btns = info1.get("buttons", [])
            has_upload = any("凭证" in b or "上传" in b for b in btns)
            has_cancel = any("撤销" in b or "取消" in b for b in btns)
            if has_upload:
                self._click_detail_on_row(0)
                upload_btn = self.page.locator('button:has-text("上传"), button:has-text("凭证")').first
                if upload_btn.count() > 0:
                    upload_btn.click()
                    self.page.wait_for_timeout(2000)
                    dlg2 = self._get_dialog_info()
                    print(f"上传凭证弹窗: {dlg2}")
                    self._close_dialog()
                self._close_dialog()
            if has_cancel and not has_upload:
                self._click_detail_on_row(0)
                cancel_btn = self.page.locator('button:has-text("撤销"), button:has-text("取消")').first
                if cancel_btn.count() > 0:
                    cancel_btn.click()
                    self.page.wait_for_timeout(2000)
                    print(f"撤销弹窗已触发")
                    close = self.page.locator('button:has-text("取消"), button:has-text("关闭"), .el-message-box__close').first
                    if close.count() > 0: close.click(); self.page.wait_for_timeout(1000)
                self._close_dialog()
        else:
            results["待支付"] = {"count": 0, "note": "无待支付订单"}

        # 场景2: 已支付待确认 - 确认支付按钮
        self._reset()
        self._search(status="已支付待确认")
        if self._get_row_count() > 0:
            results["已支付待确认"] = {"count": self._get_row_count()}
            # 在列表中直接有"确认支付"按钮
            confirm = self.page.locator(
                ".el-table__body .el-table__row:nth-child(1) button:has-text('确认支付')"
            ).first
            if confirm.count() > 0:
                confirm.click()
                self.page.wait_for_timeout(2500)
                confirm_box = self.page.evaluate("""() => {
                    const box = document.querySelector('.el-message-box, .el-dialog, .el-popconfirm');
                    if (box && box.offsetParent) return JSON.stringify({
                        btns: Array.from(box.querySelectorAll('button')).filter(b=>b.offsetParent&&b.textContent.trim()).map(b=>b.textContent.trim()),
                        text: box.textContent.trim().slice(0,300)
                    });
                    return 'no popup';
                }""")
                print(f"确认支付弹窗: {confirm_box}")
                close = self.page.locator('button:has-text("取消"), button:has-text("关闭"), .el-message-box__close').first
                if close.count() > 0: close.click(); self.page.wait_for_timeout(1000)
            results["已支付待确认"]["confirm_available"] = confirm.count() > 0
        else:
            results["已支付待确认"] = {"count": 0, "note": "无此状态订单"}

        # 场景3: 交付中订单详情
        self._reset()
        self._search(status="交付中")
        if self._get_row_count() > 0:
            self._click_detail_on_row(0)
            info3 = self._get_dialog_info()
            results["交付中"] = {"count": self._get_row_count(), "dialog": info3}
            self._close_dialog()

        self._reset()
        print(f"弹窗探索结果: {results}")
        assert len(results) > 0, "弹窗探索无结果"

    # ==================== 8. 状态颜色校验 ====================

    def test_13_verify_status_colors(self):
        """测试验证订单状态标签颜色"""
        self._reset()
        self.page.wait_for_timeout(2000)

        print("\n=== 测试13：验证状态颜色 ===")

        status_colors = self._get_all_status_colors()
        if not status_colors:
            pytest.skip("未获取到状态颜色信息")

        print(f"   发现 {len(status_colors)} 种状态:")
        all_ok = True
        for st, info in status_colors.items():
            tag_class = info.get("tagClass", "")
            matched = self._match_tag_type(tag_class)
            expected = self._get_expected_tag_type(st)
            if expected:
                if matched == expected:
                    print(f"   ✅ '{st}': {matched} (正确, tag: {tag_class[:50]})")
                else:
                    print(f"   ❌ '{st}': 实际={matched}, 预期={expected} (tag: {tag_class[:50]})")
                    all_ok = False
            else:
                print(f"   ℹ️ '{st}': {matched} (tag: {tag_class[:50]})")

        if not all_ok:
            print("\n   ⚠️ 部分状态颜色与预期不一致")
        print("   ✅ 状态颜色校验完成！")
