# TestDataProduct 测试文档

## 文件路径
`tests/ui_tests/test03_data_product.py`

## 测试类概述
数据产品页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_add_normal_data_product` | 新增普通数据产品 |
| 2 | `test_02_add_data_product_with_empty_name` | 数据产品名称为空时必填校验 |
| 3 | `test_03_add_data_product_with_special_characters` | 数据产品名称包含特殊字符 |
| 4 | `test_04_add_data_product_with_max_length` | 新增数据产品（最大长度字段） |
| 5 | `test_21_sql_injection_in_data_product_name_query` | 数据产品名称查询SQL注入安全测试 |

## 测试覆盖范围

## 生命周期方法
- setup_, teardown_

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
