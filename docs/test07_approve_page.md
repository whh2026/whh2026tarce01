# TestApprovePage 测试文档

## 文件路径
`tests/ui_tests/test07_approve_page.py`

## 测试类概述
审批页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_access_approve_page` | 访问审批页面并验证基本元素 |
| 2 | `test_02_filter_by_approve_status` | 按审批状态筛选审批列表 |
| 3 | `test_03_view_approve_detail` | 查看审批详情信息 |
| 4 | `test_04_query_by_application_number_exact` | 按申请编号精确查询 |
| 5 | `test_05_query_by_application_number_fuzzy` | 按申请编号模糊查询 |
| 6 | `test_06_query_by_product_name_exact` | 按产品名称精确查询 |
| 7 | `test_07_query_by_product_name_fuzzy` | 按产品名称模糊查询 |
| 8 | `test_08_query_by_product_name_empty` | 产品名称为空时的查询行为 |

## 测试覆盖范围

## 生命周期方法
- setup_, teardown_

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
