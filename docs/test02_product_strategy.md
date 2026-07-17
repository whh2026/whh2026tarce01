# TestProductStrategy 测试文档

## 文件路径
`tests/ui_tests/test02_product_strategy.py`

## 测试类概述
产品策略页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_page_elements` | 验证产品策略页面基本元素（表格、按钮、搜索框、分页、表头列） |
| 2 | `test_02_add_strategy_with_normal_fields` | 新增策略（正常字段长度，含名称、描述、运算符≥） |
| 3 | `test_03_add_strategy_with_max_length_fields` | 新增策略（最大长度字段，名称50字符、描述2000字符） |
| 4 | `test_04_add_and_delete_strategy` | 新增策略后立即删除（验证增删流程完整） |
| 5 | `test_05_search_strategy_by_name` | 按策略名称精确查询 |
| 6 | `test_06_search_strategy_by_name_fuzzy` | 按策略名称模糊查询（前3个字符） |
| 7 | `test_07_add_strategy_with_empty_name` | 策略名称为空时的必填校验 |
| 8 | `test_08_add_strategy_with_empty_operator` | 运算符为空时的必填校验 |
| 9 | `test_09_add_strategy_with_both_name_and_operator_empty` | 名称和运算符均为空时的双重必填校验 |
| 10 | `test_10_add_strategy_with_single_space_in_name` | 策略名称包含一个空格 |
| 11 | `test_11_add_strategy_with_angle_brackets_in_name` | 策略名称包含《》特殊字符 |
| 12 | `test_12_add_strategy_with_multiple_spaces_in_name` | 策略名称包含多个空格 |
| 13 | `test_13_add_strategy_with_spaces_in_multiple_fields` | 策略名称和描述均包含空格 |

## 测试覆盖范围
- 页面元素验证（表格列、按钮、分页、搜索框）
- 新增策略（正常/最大长度字段）
- 策略增删完整流程
- 按名称精确/模糊查询
- 必填字段校验（名称、运算符）
- 特殊字符处理（空格、《》）
- 运算符下拉选择（≥/=/>/</≤/≠）

## 测试统计
- **总计**: 13 个测试用例
- **当前状态**: ✅ 全部通过（2026-07-16 验证）

## 生命周期方法
- `setup_method`: 登录并导航到产品策略页面，等待 Vue 组件渲染
- `teardown_method`: 关闭浏览器上下文

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
