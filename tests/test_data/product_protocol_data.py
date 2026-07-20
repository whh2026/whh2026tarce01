import random
import string
import os

# 测试URL配置
TEST_URLS = {
    "product_protocol_main": "http://192.168.0.183:30001/datamarket/product-manage/productProtocol",
    "product_protocol_create": "http://192.168.0.183:30001/datamarket/product-manage/productProtocol/create"
}

# 页面元素选择器 - 适配新版页面 (/datamarket/product-manage/productProtocol)
SELECTORS = {
    # 页面通用选择器
    "protocol_title": "h1, h2, .protocol-title, [class*='title']",
    "success_message": ".el-message--success, .ant-message-success, .success, div:has-text('成功')",
    "error_message": ".el-message--error, .ant-message-error, .error, div:has-text('失败')",

    # 表格相关选择器
    "table_rows": ".el-table__body tr.el-table__row, .ant-table-row, tbody tr",
    "table_body": ".el-table__body, .ant-table-body, tbody",
    "chain_status": "td:nth-child(4) span.el-tag__content, td:nth-child(5) span.el-tag__content, td:nth-child(4), td:nth-child(5)",
    "publish_button": "button:has-text('发布'), .publish-btn, [class*='publish']",
    "name_cell": "td:nth-child(2)",
    "detail_button": ".el-table__body tr:first-child button:has-text('详情'), .el-table__row button:has-text('详情')",
    "edit_button": ".el-table__body tr:first-child button:has-text('编辑'), .el-table__row button:has-text('编辑')",
    "delete_button": ".el-table__body tr:first-child button:has-text('删除'), .el-table__row button:has-text('删除')",

    # 表单相关选择器（新增/编辑页面）
    "add_button": "button:has-text('新增协议')",
    "confirm_button": "button:has-text('确定')",
    "cancel_button": "button:has-text('取消')",
    # 新增页面字段
    "name_input": "input[placeholder*='请输入产品协议名称']",
    "desc_input": "textarea[placeholder*='请输入产品协议描述']",
    "file_upload_input": "input[type='file'].el-upload__input",
    "file_upload_button": "button:has-text('点击上传')",

    # 查询相关选择器（列表页）
    "search_input": "input[placeholder*='输入产品协议名称']",
    "search_button": "button:has-text('查询')",
    "reset_button": "button:has-text('重置')",
    "clear_search_button": "button:has-text('重置')",

    # 链上状态筛选
    "chain_status_filter": "label:has-text('链上状态') + div .el-select",
    "chain_status_option": ".el-select-dropdown__item:has-text('{status}'), [role='option']:has-text('{status}')",

    # 确认对话框选择器
    "confirm_dialog": ".el-message-box, div[role='dialog']",
    "dialog_ok_button": "button:has-text('确定'), button:has-text('确认'), .el-button--primary",
    "dialog_cancel_button": "button:has-text('取消'), button:has-text('关闭'), .el-button--default",

    # 删除相关选择器
    "delete_confirm_button": ".el-message-box button:has-text('确定'), .el-message-box .el-button--primary",

    # 不可编辑/不可删除对话框
    "uneditable_dialog": ".el-dialog:has(.el-dialog__title:has-text('不可编辑')), .el-overlay-dialog[aria-label='不可编辑']",
    "undeletable_dialog": ".el-dialog:has(.el-dialog__title:has-text('不可删除')), .el-overlay-dialog[aria-label='不可删除']",
    "dialog_close_button": ".el-dialog__headerbtn",
}

# 测试断言消息
ASSERT_MESSAGES = {
    "page_title_empty": "页面标题不能为空",
    "protocol_title_empty": "协议标题不能为空",
    "protocol_content_short": "协议内容不能为空且长度应足够长",
    "no_valid_chain_status": "列表中未找到任何可识别的链上状态记录",
    "protocol_not_in_list": "新增协议未出现在列表中",
    "no_publish_button": "新增协议行未出现发布按钮",
    "chain_status_error": "发布后链上状态异常: {status_text}",
    "publish_button_still_exists": "发布后仍显示发布按钮",
    "page_access_failed": "页面访问失败，当前URL: {url}",
    "no_delete_button": "目标协议行未找到删除按钮",
    "protocol_still_exists": "删除后协议仍然存在于列表中",
    "delete_confirm_not_found": "未找到删除确认对话框",
    "delete_success_not_found": "未找到删除成功提示",
    "file_upload_failed": "文件上传失败",
    "edit_dialog_not_found": "未找到编辑对话框",
}

# 测试数据生成函数
def generate_test_data():
    """生成测试数据"""
    random_digits = ''.join(random.choices(string.digits, k=10))
    return f"abc{random_digits}"

def generate_max_length_data():
    """生成最大长度测试数据"""
    name_desc_title = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
    body_content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=200))
    return name_desc_title, body_content

# 链上状态常量
CHAIN_STATUS = {
    "UNPUBLISHED": ["未上链", "未发布"],
    "PUBLISHING": ["上链中"],
    "PUBLISH_FAILED": ["上链失败"],
    "PUBLISHED": ["已上链", "已发布"]
}

# 测试用的链上状态列表
CHAIN_STATUS_TEST_LIST = ["未上链", "上链中", "上链失败", "已上链"]

# 测试等待时间配置
WAIT_TIMES = {
    "very_short": 500,
    "short": 1000,
    "medium": 2000,
    "long": 5000,
    "network": 5000
}

# 获取测试文件路径
def get_test_file_path():
    """获取用于上传的测试文件路径"""
    # 尝试多个可能的文件路径
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "930接口文档.docx"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "test_protocol.docx"),
        os.path.join(os.path.dirname(__file__), "..", "..", "assets", "test.docx"),
        r"D:\autotrace\traceai\docs\930接口文档.docx",
    ]
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path
    return None
