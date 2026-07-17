import random
import string

# 测试URL配置
TEST_URLS = {
    "product_strategy_main": "http://192.168.0.183:30001/datamarket/product-manage/strategy"
}

# 页面元素选择器
SELECTORS = {
    # 页面通用选择器
    "strategy_title": "h1, h2, .strategy-title, [class*='title']",
    "strategy_content": ".strategy-content, .content.strategy-content",
    "success_message": ".el-message--success, .ant-message-success, .success, div:has-text('成功')",
    
    # 表格相关选择器
    "table_rows": "tr.el-table__row",
    "status": "td:nth-child(4) span.el-tag__content, td:nth-child(5) span.el-tag__content, td:nth-child(4), td:nth-child(5)",
    "enable_button": "button:has-text('启用')",
    "disable_button": "button:has-text('禁用')",
    "edit_button": "button:has-text('编辑')",
    "delete_button": "button:has-text('删除')",
    "name_cell": "td:nth-child(1)",
    
    # 表单相关选择器
    "add_button": "button:has-text('新增策略')",
    "confirm_button": "button:has-text('确定')",
    "cancel_button": "button:has-text('取消')",
    "name_input": ".el-dialog__body input[placeholder='请输入产品策略名称']",
    "desc_input": ".el-dialog__body textarea[placeholder='请输入产品策略描述']",
    "type_select": ".el-dialog__body label:has-text('产品策略类型') + div .el-select",
    "priority_input": ".el-dialog__body label:has-text('优先级') + div >> input",
    
    # 运算符相关选择器
    "operator_select": ".el-dialog__body .el-form-item:has(.el-form-item__label:has-text('运算符')) .el-select",
    "operator_equals": ".el-select-dropdown__item:has-text('=')" ,
    "operator_not_equals": ".el-select-dropdown__item:has-text('≠')",
    "operator_greater": ".el-select-dropdown__item:has-text('>')",
    "operator_greater_equal": ".el-select-dropdown__item:has-text('≥')",
    "operator_less": ".el-select-dropdown__item:has-text('<')",
    "operator_less_equal": ".el-select-dropdown__item:has-text('≤')",

    
    # 查询相关选择器
    "search_input": "input[placeholder='输入产品策略名称']",
    "search_button": "button:has-text('查询')",
    "clear_search_button": "button:has-text('重置')",
    
    # 确认对话框选择器
    "confirm_dialog": "div.el-message-box",
    "dialog_ok_button": "button:has-text('确定'), button:has-text('确认'), .el-button--primary",
    "dialog_cancel_button": "button:has-text('取消'), button:has-text('关闭'), .el-button--default",
    
    # 删除相关选择器
    "delete_confirm_button": "div.el-message-box button:has-text('删除'), div.el-message-box button:has-text('确定'), div.el-message-box .el-button--primary",
}

# 富文本编辑器选择器
QUILL_EDITOR_SELECTORS = [
    "//div/font[text()='策略内容']/../div/div/div/div[@class='ql-editor']",
    "//div/font[text()='策略内容']/../div/div/div[@class='ql-editor']",
    "//div/font[text()='策略内容']/../div/div[@class='ql-editor']",
    "//div/font[text()='策略内容']/../div[@class='ql-editor']",
    "//div[contains(text(),'策略内容')]/../following-sibling::div//div[@class='ql-editor']",
    "//div[contains(text(),'策略内容')]/../div//div[@class='ql-editor']"
]

# iframe编辑器选择器
IFRAME_EDITOR_SELECTORS = [
    "//div/font[text()='策略内容']/../div//iframe",
    "//div/font[text()='策略内容']/../following-sibling::div//iframe"
]

# 普通文本框选择器
TEXT_INPUT_SELECTORS = [
    "//div/font[text()='策略内容']/../div//textarea",
    "//div/font[text()='策略内容']/../div//input",
    "//div/font[text()='策略内容']/../following-sibling::div//textarea",
    "//div/font[text()='策略内容']/../following-sibling::div//input"
]

# 确认对话框选择器
CONFIRM_DIALOG_SELECTORS = [
    "div.el-message-box",
    ".ant-modal-confirm",
    ".confirm-dialog"
]

# 成功消息选择器
SUCCESS_SELECTORS = [
    ".success",
    ".message-success",
    "[class*='success']",
    "div:has-text('成功')",
    "span:has-text('成功')"
]

# 测试断言消息
ASSERT_MESSAGES = {
    "page_title_empty": "页面标题不能为空",
    "strategy_title_empty": "策略标题不能为空",
    "strategy_content_short": "策略内容不能为空且长度应足够长",
    "no_valid_status": "列表中未找到任何可识别的状态记录",
    "strategy_not_in_list": "新增策略未出现在列表中",
    "page_access_failed": "页面访问失败，当前URL: {url}",
    "no_edit_button": "目标策略行未找到编辑按钮",
    "no_delete_button": "目标策略行未找到删除按钮",
    "strategy_still_exists": "删除后策略仍然存在于列表中",
    "delete_confirm_not_found": "未找到删除确认对话框",
    "delete_success_not_found": "未找到删除成功提示",
    "no_add_button": "未找到新增策略按钮",
    "no_operator_option": "未找到≥运算符选项",
    "strategy_not_found": "未找到策略: {name}",
}

# 测试数据生成函数
def generate_test_data():
    """生成测试数据"""
    # 生成10位随机数字
    random_digits = ''.join(random.choices(string.digits, k=10))
    # 生成随机字符串
    random_str = f"strategy{random_digits}"
    return random_str

# 最大长度测试数据
def generate_max_length_data():
    """生成最大长度测试数据"""
    # 生成50位随机字符串（名称、描述、标题）
    name_desc_title = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
    # 生成2000位随机字符串（正文）
    body_content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=2000))
    return name_desc_title, body_content

# 策略状态常量
STRATEGY_STATUS = {
    "ENABLE": ["启用", "已启用", "生效中"],
    "DISABLE": ["禁用", "已禁用", "未生效"]
}

# 策略类型常量
STRATEGY_TYPE = {
    "DEFAULT": "默认类型"
}

# 策略优先级常量
STRATEGY_PRIORITY = {
    "HIGH": "100"
}

# 测试等待时间配置
WAIT_TIMES = {
    "very_short": 500,  # 500毫秒
    "short": 1000,  # 1秒
    "medium": 2000,  # 2秒
    "long": 3000,    # 3秒
    "network": 5000  # 5秒（网络操作）
}