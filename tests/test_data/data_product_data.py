import random
import string

# 测试URL配置
TEST_URLS = {
    "data_product_main": "http://192.168.0.183:30003/registration/product/dataProduct",
    "data_product_create": "http://192.168.0.183:30003/registration/product/release"
}

# 页面元素选择器
SELECTORS = {
    # 页面通用选择器
    "page_title": "h1, h2, .page-title, [class*='title']",
    "page_content": ".page-content, .content, [class*='content']",
    "success_message": ".el-message--success, .ant-message-success, .success, div:has-text('成功')",
    "error_message": ".el-message--error, .ant-message-error, .error, div:has-text('失败')",
    
    # 表格相关选择器
    "table": ".el-table, .ant-table, table",
    "table_rows": "tr.el-table__row, .ant-table-row, tbody tr",
    "table_columns": "thead th",
    
    # 表单相关选择器
    "add_button": "button:has-text('数据产品登记'), button:has-text('新增'), .add-btn, [class*='add']",
    "confirm_button": "button:has-text('确定'), button:has-text('保存'), .confirm-btn, [class*='confirm']",
    "temporary_confirm_button": "button:has-text('暂存')",
    "next_step_button": "button:has-text('下一步')",  
    "cancel_button": "button:has-text('取消'), button:has-text('关闭'), .cancel-btn, [class*='cancel']",
    "data_product_name_input": "label:has-text('数据产品名称') ~ div .el-input__inner",
    "data_product_desc_textarea": "textarea[placeholder*='说明数据产品的基本信息，包括但不限于业务用途、内容、规模等']",
    "data_product_limit_textarea": "textarea[placeholder*='说明数据产品在使用过程中的任何限制或条件，标注使用限制场景']",
    "data_product_other_textarea": "textarea[placeholder*='请输入其他说明']",
    "data_product_markdown_textarea": "textarea[placeholder*='请输入Markdown内容...']",
    "data_product_type_select": "label:has-text('产品类型') + div",
    "data_product_subtype_select": "label:has-text('产品小类') + div",
    "data_product_number_input": "label:has-text('数据产品编号') + div >> input",
    "data_product_english_name_input": "label:has-text('数据产品英文名称') + div >> input",
    "data_product_tags_input": "label:has-text('数据产品标签') + div >> input",
    "data_product_category_select": "label:has-text('行业分类') + div",
    "data_product_region_select": "label:has-text('地域分类') + div",
    "data_product_time_range_input": "label:has-text('时间范围') + div >> input",
    "data_product_personal_info_select": "label:has-text('是否涉及个人信息') + div",
    "data_product_ownership_select": "label:has-text('权属信息') + div",
    
    # 详细信息页面选择器
    "data_product_api_name_input": "label:has-text('接口名称') + * input",
    "access_address_input": "label:has-text('正式接口地址') ~ div .el-input__inner",
    "redirect_address_input": "label:has-text('测试接口地址') ~ div .el-input__inner",
    "api_type_api_radio": "label:has-text('格式类型') ~ div .el-radio[aria-label='API']",
    "request_type_post_radio": "label:has-text('请求类型') ~ div .el-radio[aria-label='POST']",
    "need_auth_yes_radio": "label:has-text('是否需要授权') ~ div .el-radio[aria-label='是']",
    "input_param_name_input": ".el-form-item:has(label:has-text('入参信息')) .el-input__inner",
    
    # 上架信息页面选择器
    "need_apply_yes_radio": "label:has-text('是否需要申请使用') >> .el-radio:has-text('是')",
    "need_apply_no_radio": "label:has-text('是否需要申请使用') >> .el-radio:has-text('否')",
    "service_agreement_first_option": ".el-select-dropdown__item:first-child",
    "allow_third_party_checkbox": "label:has-text('允许第三方授权使用')",
    "delivery_strategy_select_button": "button:has-text('选择')",
    "delivery_strategy_table": ".el-table",
    "delivery_strategy_last_checkbox": ".el-table__row:last-child .el-checkbox__inner",
    "delivery_strategy_confirm_button": "div[role='dialog'][aria-label='选择策略'] button:has-text('确定')",
    
    # 新增用户选择的元素选择器
    "delivery_strategy_select_span": "span:has-text('选择')",
    "checkbox_inner_span": ".el-checkbox__inner",
    "primary_confirm_button": "button.el-button--primary:has-text('确定')",
    "header_span": "//*[@id=\"app\"]/div/section/div/main/div/div/div[2]/div/div[2]/div/div/header/span",
 
    
    # 价格信息页面选择器
    "price_type_select": "label:has-text('价格类型') + div",
    "price_input": "xpath=/html/body/div[1]/div/div/section/div/main/div/div/div[2]/div/form/div[2]/div[2]/div/div[3]/div/div/div[1]/div/div[1]/input",
    "measurement_unit_select": "label:has-text('计量方式') + div",
    "hidden_price_radio_yes": "label:has-text('是否隐藏价格') ~ div .el-radio:has-text('是')",
    "hidden_price_radio_no": "label:has-text('是否隐藏价格') ~ div .el-radio:has-text('否')",
    "payment_mode_select": "label:has-text('支付模式') + div",
    "payment_method_select": "label:has-text('支付方式') + div",
    
    # 查询相关选择器
    "search_input": "input[placeholder*='输入数据产品名称']",
    "search_button": "button:has-text('查询'), .search-btn, [class*='search']",
    "reset_button": "button:has-text('重置'), .reset-btn, [class*='reset']",
    
    # 操作相关选择器
    "edit_button": "button:has-text('编辑'), .edit-btn, [class*='edit']",
    "delete_button": "button:has-text('删除'), .delete-btn, [class*='delete']",
    "view_button": "button:has-text('查看'), .view-btn, [class*='view']",
    
    # 确认对话框选择器
    "confirm_dialog": "div.el-message-box, div.ant-modal-confirm",
    "dialog_ok_button": "button:has-text('确定'), button:has-text('确认'), .el-button--primary, .ant-btn-primary",
    "dialog_cancel_button": "button:has-text('取消'), button:has-text('关闭'), .el-button--default, .ant-btn-default",
    "delete_confirm_button": "div.el-message-box button:has-text('删除'), div.el-message-box button:has-text('确定'), div.ant-modal-confirm button:has-text('确定')",
}

# 断言消息
ASSERT_MESSAGES = {
    "page_access_failed": "页面访问失败，当前URL: {url}",
    "page_title_empty": "页面标题不能为空",
    "add_button_not_found": "未找到新增数据产品按钮",
    "data_product_created": "数据产品创建失败",
    "data_product_deleted": "数据产品删除失败",
    "search_result_empty": "搜索结果为空",
    "max_length_validation_failed": "最大长度验证失败",
}

# 等待时间配置（毫秒）
WAIT_TIMES = {
    "page_load": 3000,
    "element_load": 2000,
    "dialog_appear": 1000,
    "message_appear": 1000,
}

# 数据产品类型
DATA_PRODUCT_TYPES = [
    "结构化数据",
    "非结构化数据",
    "半结构化数据",
    "实时数据流"
]

# 数据格式
DATA_FORMATS = [
    "JSON",
    "CSV",
    "XML",
    "Parquet",
    "ORC",
    "AVRO"
]

# 生成随机测试数据
def generate_test_data():
    """生成随机测试数据，包含名称、描述和其他字段"""
    # 生成随机中文名称（8-20个字符）
    name_length = random.randint(8, 20)
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=name_length))
    
    # 生成符合规则的英文名称（6-30个字符，只包含大小写字母、数字、下划线、中横线、小数点）
    # 允许的字符集：大小写字母、数字、下划线、中横线、小数点
    english_name_chars = string.ascii_letters + string.digits + "_-."
    english_name_length = random.randint(6, 30)
    
    # 确保以字母开头
    english_name = random.choice(string.ascii_letters)
    
    # 中间字符可以是大小写字母、数字、下划线、中横线、小数点
    for _ in range(english_name_length - 2):
        english_name += random.choice(english_name_chars)
    
    # 确保以字母或数字结尾
    english_name += random.choice(string.ascii_letters + string.digits)
    
    # 生成随机描述
    desc_length = random.randint(50, 100)
    desc = ''.join(random.choices(string.ascii_letters + string.digits + string.whitespace, k=desc_length))
    
    # 生成随机使用限制
    limit_length = random.randint(50, 100)
    limit = ''.join(random.choices(string.ascii_letters + string.digits + string.whitespace, k=limit_length))
    
    # 生成随机其他说明
    other_length = random.randint(50, 100)
    other = ''.join(random.choices(string.ascii_letters + string.digits + string.whitespace, k=other_length))
    
    # 随机选择数据类型
    data_type = random.choice(DATA_PRODUCT_TYPES)
    
    return {
        "name": name,
        "english_name": english_name,
        "desc": desc,
        "limit": limit,
        "other": other,
        "type": data_type
    }

# 生成最大长度的测试数据
def generate_max_length_data():
    """生成最大长度的测试数据，用于边界值测试"""
    # 生成最大长度的名称（假设最大长度为100）
    max_length_name = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
    
    # 生成最大长度的英文名称（最大长度为50，只包含允许的字符）
    english_name_chars = string.ascii_letters + string.digits + "_-."
    max_length_english_name = random.choice(string.ascii_letters)  # 开头必须是字母
    for _ in range(48):  # 中间48个字符
        max_length_english_name += random.choice(english_name_chars)
    max_length_english_name += random.choice(string.ascii_letters + string.digits)  # 结尾必须是字母或数字
    
    # 生成最大长度的描述（假设最大长度为500）
    max_length_desc = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=500))
    
    return max_length_name, max_length_english_name, max_length_desc

# 生成特殊字符的测试数据
def generate_special_chars_data():
    """生成包含特殊字符的测试数据，用于验证特殊字符处理"""
    special_chars = string.punctuation
    name = f"Test{random.choice(special_chars)}Data{random.choice(special_chars)}Product"
    desc = f"这是一个包含特殊字符的测试描述：{special_chars}"
    
    return name, desc
