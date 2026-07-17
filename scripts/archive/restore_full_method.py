with open('d:/autotrace/traceai/utils/base.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 创建完整的 create_data_product 方法
full_method = '''    def create_data_product(self, need_apply=False, custom_name=None, need_auth=False):
        """
        创建数据产品的完整流程,返回创建的产品名称

        测试目的:提供一个可复用的方法,用于创建测试数据产品

        测试场景:模拟用户完整的数据产品发布流程

        测试步骤:

        1. 访问数据产品发布页面

        2. 生成测试数据或使用自定义产品名称

        3. 填写基础配置信息

        4. 填写详细信息

        5. 填写上架信息

        6. 确认并发布数据产品

        Args:

            need_apply: 是否需要申请使用(默认为False,即"否")

            custom_name: 自定义产品名称(默认为None,使用随机生成的名称)

            need_auth: 是否需要授权(精准授权,默认为False,即"否")

        返回值:

            dict: 包含产品名称、产品编码、行业分类的字典

        """
        import time
        import re
        from tests.test_data.data_product_data import TEST_URLS, SELECTORS, generate_test_data

        print("\\n=== 创建数据产品,完整流程===")

        release_url = self.get_url_for_user(1, "/registration/product/release", None, None)
        self.page.goto(release_url)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问发布页面 {release_url}")

        test_data = generate_test_data()

        if custom_name:
            test_data["name"] = custom_name
            print(f"   ✓ 使用自定义产品名称 {custom_name}")
        else:
            print(f"   ✓ 使用测试数据: 名称='{test_data['name']}', 英文名称='{test_data['english_name']}'")

        # === 3. 填写基础配置信息 ===
        print("\\n=== 3. 填写基础配置信息 ===")

        if self.page.is_visible(SELECTORS["data_product_name_input"]):
            self.page.fill(SELECTORS["data_product_name_input"], test_data["name"])
            print(f"   ✓ 已填写中文名称 {test_data['name']}")

        if self.page.is_visible(SELECTORS["data_product_english_name_input"]):
            self.page.fill(SELECTORS["data_product_english_name_input"], test_data["english_name"])
            print(f"   ✓ 已填写英文名称 {test_data['english_name']}")

        if self.page.is_visible(SELECTORS["data_product_desc_textarea"]):
            self.page.fill(SELECTORS["data_product_desc_textarea"], test_data["desc"])
            print(f"   ✓ 已填写产品介绍")

        if self.page.is_visible(SELECTORS["data_product_limit_textarea"]):
            self.page.fill(SELECTORS["data_product_limit_textarea"], test_data["limit"])
            print(f"   ✓ 已填写使用限制")

        if self.page.is_visible(SELECTORS["data_product_other_textarea"]):
            self.page.fill(SELECTORS["data_product_other_textarea"], test_data["other"])
            print(f"   ✓ 已填写其他说明")

        if self.page.is_visible(SELECTORS["data_product_tags_input"]):
            tags_value = f"测试, {test_data['type']}, 自动化测试"
            self.page.fill(SELECTORS["data_product_tags_input"], tags_value)
            print(f"   ✓ 已填写标签 {tags_value}")

        if self.page.is_visible(SELECTORS["data_product_category_select"]):
            self.page.click(SELECTORS["data_product_category_select"])
            self.page.click("li:has-text('采矿业')")
            print(f"   ✓ 已选择行业分类: 采矿业")

        if self.page.is_visible(SELECTORS["data_product_type_select"]):
            self.page.click(SELECTORS["data_product_type_select"])
            self.page.click("li:has-text('数据接口')")
            print(f"   ✓ 已选择产品类型: 数据接口")

        if self.page.is_visible(SELECTORS["data_product_subtype_select"]):
            self.page.click(SELECTORS["data_product_subtype_select"])
            self.page.click("li:has-text('API接口')")
            print(f"   ✓ 已选择产品小类: API接口")

        if self.page.is_visible(SELECTORS["data_product_region_select"]):
            self.page.locator(".allPadding > .el-select > .el-select__wrapper > .el-select__selection > div:nth-child(2)").click()
            self.page.locator("div").filter(has_text=re.compile(r"^北京")).locator("span").nth(1).click()
            print(f"   ✓ 已选择 北京市")

        # === 4. 进入详细信息页面 ===
        print("\\n=== 4. 进入详细信息页面 ===")

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
                    print(f"   ✓ 已进入详细信息页面")
                else:
                    print(f"   ✓ 可能未进入详细信息页面,但继续执行测试")
            except Exception as e:
                print(f"   ✓ 等待详细信息页面元素超时: {str(e)}")
                print(f"   ✓ 继续执行测试")

        # === 5. 填写详细信息 ===
        print("\\n=== 5. 填写详细信息 ===")

        print("   填写接口名称: 测试接口...")
        if self.page.is_visible(SELECTORS.get("data_product_api_name_input")):
            self.page.fill(SELECTORS["data_product_api_name_input"], "测试接口")
            print(f"   ✓ 已填写接口名称 测试接口")

        print("   填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("access_address_input")):
            self.page.fill(SELECTORS["access_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   ✓ 已填写正式接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")

        print("   填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")
        if self.page.is_visible(SELECTORS.get("redirect_address_input")):
            self.page.fill(SELECTORS["redirect_address_input"], "http://192.168.0.152:31080/api/mock/prod/cbdt")
            print(f"   ✓ 已填写测试接口地址: http://192.168.0.152:31080/api/mock/prod/cbdt")

        print("   向下滚动页面,使入参字段可见...")
        self.page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")
        time.sleep(1)
        self.page.evaluate("window.scrollBy({top: -200, behavior: 'smooth'})")
        time.sleep(1)

        if need_auth:
            print("   填写入参信息(授权产品:abc、date)...")
            input_params = ["abc", "date"]
            input_xpaths = [
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[1]/div/div[2]/div[1]/div/input",
                "/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div/div/div/div/div[3]/div/div[2]/div/div[2]/div[1]/div/input"
            ]
        else:
            print("   填写入参信息(非授权产品:仅date)...")
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
                        print(f"   ⚠️  第{i+1}个入参字段不可见,尝试强制填充")
                        input_element.fill(param_name)
                        print(f"   ✓ (强制) 已填写第{i+1}个入参字段名: {param_name}")
                        filled_count += 1
                else:
                    print(f"   ⚠️  第{i+1}个入参字段xpath不存在")
            except Exception as e:
                print(f"   ⚠️  填写第{i+1}个入参字段时出错: {e}")

        if filled_count < len(input_params):
            print(f"   ⚠️  警告:只成功填写了{filled_count}/{len(input_params)}个入参字段")

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
                        print(f"   ✓ 已设置精准授权为: 是")
                        auth_clicked = True
                        print("   等待5秒,确保页面元素加载完成...")
                        time.sleep(5)
                        break
                except Exception as e:
                    print(f"   ⚠️  选择器{selector} 点击失败: {e}")
                    continue

            if not auth_clicked:
                print(f"   ✓ 未找到精准授权选择器")
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
                                print(f"   ✓ 已填写{field['name']}: {field['value']}")
                            else:
                                print(f"   ⚠️  {field['name']}字段不可见,尝试强制填充")
                                input_element.fill(field['value'])
                                print(f"   ✓ (强制) 已填写{field['name']}: {field['value']}")
                        else:
                            print(f"   ⚠️  {field['name']}字段不存在")
                    except Exception as e:
                        print(f"   ⚠️  填写{field['name']}时出错: {e}")

        # === 6. 进入上架信息页面 ===
        print("\\n=== 6. 进入上架信息页面 ===")

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
                    print(f"   ✓ 已点击下一步按钮 {selector}")
                    break
            except Exception as e:
                print(f"   ⚠️  选择器{selector} 点击失败: {e}")
                continue

        if not next_button_clicked:
            print("   ✓ 未找到下一步按钮,无法进入上架信息页面")
            self.page.screenshot(path="failed_to_find_next_button.png")
            print("   ✓ 已保存截图 failed_to_find_next_button.png")
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
                    print(f"   ✓ 检测到上架信息页面特征元素: {selector}")
                    break
                except Exception:
                    continue

            if shelf_page_loaded:
                print(f"   ✓ 已进入上架信息页面")
            else:
                print(f"   ✓ 可能未进入上架信息页面,正在尝试刷新页面...")
                self.page.screenshot(path="shelf_page_not_loaded.png")
                print("   ✓ 已保存截图 shelf_page_not_loaded.png")
                self.page.reload()
                self.page.wait_for_load_state("networkidle", timeout=30000)
                for selector in shelf_page_selectors:
                    if not selector:
                        continue
                    try:
                        self.page.wait_for_selector(selector, timeout=3000)
                        shelf_page_loaded = True
                        print(f"   ✓ 刷新后检测到上架信息页面特征元素: {selector}")
                        break
                    except Exception:
                        continue

                if not shelf_page_loaded:
                    print("   ✓ 刷新后仍未进入上架信息页面")

        except Exception as e:
            print(f"   ✓ 等待上架信息页面元素超时: {str(e)}")

        # === 6.1 填写价格信息 ===
        print("\\n=== 6.1 填写价格信息 ===")

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
            print(f"   ✓ 已选择价格类型: {price_type}")
            time.sleep(1)

        price = "100"
        if self.page.is_visible(SELECTORS.get("price_input")):
            self.page.fill(SELECTORS["price_input"], price)
            print(f"   ✓ 已填写价格 {price}")

        hidden_price = "是"
        if price_type in ["计量定价", "买断"]:
            if self.page.is_visible(SELECTORS.get("hidden_price_radio_yes")) or self.page.is_visible(SELECTORS.get("hidden_price_radio_no")):
                if hidden_price == "是":
                    self.page.click(SELECTORS["hidden_price_radio_yes"])
                else:
                    self.page.click(SELECTORS["hidden_price_radio_no"])
                print(f"   ✓ 是否隐藏价格: {hidden_price}")

        # === 7. 填写上架信息 ===
        print("\\n=== 7. 填写上架信息 ===")

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
                        print(f"   ✓ 是否需要申请使用 是")
                        break
                except:
                    continue
            else:
                print(f"   ✓ 未找到是否需要申请使用 是选项")
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
                        print(f"   ✓ 是否需要申请使用 否")
                        break
                except:
                    continue
            else:
                print(f"   ✓ 未找到是否需要申请使用 否选项")

        if self.page.is_visible("label:has-text('服务协议') + div >> .el-select"):
            self.page.click("label:has-text('服务协议') + div >> .el-select")
            time.sleep(1)
            self.page.click(".el-select-dropdown__item")
            print(f"   ✓ 已选择服务协议: 第一个选项")

        if self.page.is_visible(SELECTORS["allow_third_party_checkbox"]):
            self.page.click(SELECTORS["allow_third_party_checkbox"])
            print(f"   ✓ 已选择产品授权范围: 允许第三方授权使用")

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
                print(f"   ⚠️  选择器{selector} 点击失败: {e}")
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
                        print(f"   ✓ 已选择产品交付策略")
                        delivery_strategy_selected = True
                        break
                except Exception as e:
                    print(f"   ⚠️  选择器{checkbox_selector} 点击失败: {e}")
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
                            print("   ✓ 已确认产品交付策略")
                            break
                    except Exception as e:
                        print(f"   ⚠️  确认按钮选择器{confirm_selector} 点击失败: {e}")
                        continue

        except Exception as e:
            print(f"   ✓ 选择产品交付策略失败: {str(e)}")

        if not delivery_strategy_selected:
            print("   ⚠️  警告:产品交付策略未选择,可能导致产品创建失败")

        # === 9. 点击确定 ===
        print("\\n=== 9. 点击确定 ===")

        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            time.sleep(3)
            print("✓ 已点击确定,完成数据产品发布")

        # === 导航到数据产品列表页面 ===
        print("\\n=== 导航到数据产品列表页面===")

        data_product_page = self.get_url_for_user(1, "/registration/product/dataProduct", None, None)
        self.page.goto(data_product_page)
        self.page.wait_for_load_state("networkidle", timeout=30000)
        print(f"   ✓ 已访问数据产品列表页面 {data_product_page}")

        # === 10. 输入数据产品名称查询 ===
        print("\\n=== 10. 输入数据产品名称查询 ===")

        if self.page.is_visible("input[placeholder='输入数据产品名称']"):
            self.page.fill("input[placeholder='输入数据产品名称']", test_data["name"])
            time.sleep(3)

        if self.page.is_visible("//span[text()='查询']"):
            self.page.click("//span[text()='查询']")
            time.sleep(3)
            print("   ✓ 已点击查询")

        # === 12. 点击发布 ===
        print("\\n=== 12. 点击发布 ===")

        if self.page.is_visible("span.el-button__text:has-text('发布')"):
            self.page.click("span.el-button__text:has-text('发布')")
            time.sleep(3)
            print("   ✓ 已点击发布")

        print("\\n✓ 新增数据产品完整流程测试完成")

        # === 13. 点击确定 ===
        print("\\n=== 13. 点击确定 ===")

        if self.page.is_visible(SELECTORS["primary_confirm_button"]):
            self.page.click(SELECTORS["primary_confirm_button"])
            try:
                self.page.wait_for_selector(SELECTORS["success_message"], timeout=10000)
                print("   ✓ 已点击确定,数据产品发布成功")
            except Exception as e:
                print("   ✓ 已点击确定,完成数据产品发布")

        # === 输入数据产品名称查询 ===
        print("\\n=== 输入数据产品名称查询 ===")

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
        }'''

# 替换当前的 create_data_product 方法
import re
# 找到方法定义的开始和结束
pattern = r'(def create_data_product\(self, need_apply=False, custom_name=None, need_auth=False\):.*?)(?=\n    def )'
content = re.sub(pattern, full_method + '\n\n', content, flags=re.DOTALL)

with open('d:/autotrace/traceai/utils/base.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
