# TestReceivedListPage 测试文档

## 文件路径
`tests/ui_tests/test08_received_list_page.py`

## 测试类概述
数据使用交付页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_access_received_list_page` | 访问数据使用交付页面并验证基本元素 |
| 2 | `test_02_filter_by_received_status` | 按交付状态筛选列表 |
| 3 | `test_03_view_received_detail` | 查看交付详情信息 |
| 4 | `test_04_view_record_detail` | 查看记录详情 |
| 5 | `test_05_enter_interface_debug` | 进入接口调试功能 |
| 6 | `test_07_query_by_delivery_number_exact` | 按交付编号精确查询 |
| 7 | `test_08_query_by_delivery_number_fuzzy` | 按交付编号模糊查询 |
| 8 | `test_09_query_by_delivery_number_empty` | 交付编号为空时的查询行为 |
| 9 | `test_10_query_by_product_name_exact` | 按产品名称精确查询 |
| 10 | `test_11_query_by_product_name_fuzzy` | 按产品名称模糊查询 |

## 测试覆盖范围

## 生命周期方法
- setup_, teardown_

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
