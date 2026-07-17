# TestProductProtocol 测试文档

## 文件路径
`tests/ui_tests/test01_product_protocol.py`

## 测试类概述
产品协议页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_page_elements` | 验证产品协议页面基本元素（表格、按钮、搜索框、分页等） |
| 2 | `test_02_publish_button_visibility_by_chain_status` | 验证不同链状态下发布按钮的可见性 |
| 3 | `test_03_add_protocol_with_max_length_fields` | 新增协议（最大长度字段，名称50字符、正文2000字符） |
| 4 | `test_04_add_and_publish_protocol` | 新增协议并发布上线 |
| 5 | `test_05_add_new_protocol` | 新增协议（正常字段长度） |
| 6 | `test_06_query_protocol_by_name` | 按协议名称精确查询 |
| 7 | `test_07_query_protocol_by_name_fuzzy` | 按协议名称模糊查询（前3个字符） |
| 8 | `test_08_query_protocol_by_chain_status` | 按链状态筛选查询协议 |
| 9 | `test_09_add_and_delete_protocol` | 新增协议后立即删除 |
| 10 | `test_10_query_and_reset_filters` | 查询后重置筛选条件 |
| 11 | `test_11_add_protocol_with_single_space_in_name` | 协议名称包含一个空格 |
| 12 | `test_12_add_protocol_with_multiple_spaces_in_name` | 协议名称包含多个空格 |
| 13 | `test_13_add_protocol_with_spaces_in_multiple_fields` | 协议名称和描述均包含空格 |
| 14 | `test_14_add_protocol_with_angle_brackets_in_name` | 协议名称包含《》特殊字符 |
| 15 | `test_15_sql_injection_in_protocol_name_query` | 协议名称查询SQL注入安全测试 |
| 16 | `test_16_js_injection_in_protocol_name_query` | 协议名称查询JS注入安全测试 |
| 17 | `test_17_xss_injection_in_protocol_name_query` | 协议名称查询XSS注入安全测试 |
| 18 | `test_18_view_protocol_detail` | 查看协议详情 |
| 19 | `test_19_edit_protocol` | 编辑协议信息 |
| 20 | `test_20_add_protocol_direct` | 直接新增协议（简化流程） |

## 测试覆盖范围
- 页面元素验证
- 新增、编辑、删除协议
- 按名称、链状态查询
- 模糊查询与重置筛选
- 发布按钮可见性（按链状态）
- 特殊字符处理（空格、《》）
- 安全注入防御（SQL/JS/XSS）
- 最大长度字段边界测试
- 协议详情查看

## 测试统计
- **总计**: 20 个测试用例

## 生命周期方法
- `setup_method`: 登录并导航到产品协议页面
- `teardown_method`: 关闭浏览器上下文

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
