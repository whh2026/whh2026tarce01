# TestProductListPage 测试文档

## 文件路径
`tests/ui_tests/test05_product_list_page.py`

## 测试类概述
产品列表页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_access_product_list_page` | 访问产品列表页面，验证页面标题、表格、搜索框、数据产品名称/编码/行业分类/授权使用字段、查询按钮、分页组件等基本元素是否存在 |
| 2 | `test_02_get_product_detail_for_query` | 数据准备型用例：点击产品"详情"，抓取真实的产品名称和数据产品统一编码并存入类变量（`product_name_for_query`/`product_code_for_query`），供 test_03/test_04 查询使用 |
| 3 | `test_03_search_by_product_name` | 按产品名称精确查询：用 test_02 取到的名称填入搜索框并点"查询"，验证结果表格出现，查询后清空输入框 |
| 4 | `test_04_search_by_product_code` | 按产品编码精确查询：用 test_02 取到的编码查询，验证结果与编码匹配 |
| 5 | `test_05_reset_search` | 重置搜索：执行查询后点击"重置"，验证搜索条件被清空、列表恢复完整 |
| 6 | `test_06_view_product_detail` | 查看产品详情页：点击产品详情进入详情，验证能读取产品信息，再返回列表页 |
| 7 | `test_07_pagination` | 分页组件功能验证：切换分页（下一页等），验证列表数据正确刷新 |
| 8 | `test_08_filter_by_industry` | 按行业分类筛选：在行业下拉选择值后查询，验证筛选结果匹配所选行业 |
| 9 | `test_09_filter_by_product_type` | 按产品类型筛选：按产品类型筛选后查询，验证结果匹配所选类型 |
| 10 | `test_10_empty_search_result` | 空搜索结果处理：查询一个不存在的名称，验证页面显示空状态/无数据提示，不报错 |
| 11 | `test_11_click_product_detail` | 单次点击详情：进入一个产品详情页后返回，验证跳转与返回流程正常 |
| 12 | `test_12_click_multiple_product_details` | 多次点击详情：连续进入多个不同产品的详情页，验证多次跳转稳定无异常 |
| 13 | `test_13_sql_injection_in_product_name_query` | 产品名称查询 SQL 注入安全测试：在名称搜索框输入代表性 SQL 注入 payload（16 个，覆盖 OR 绕过/UNION/布尔盲注/报错提取/破坏性语句等），验证系统均做了安全拦截/转义，无数据泄露 |
| 14 | `test_14_sql_injection_in_product_code_query` | 产品编码查询 SQL 注入安全测试：同理在产品编码搜索框注入代表性 SQL payload，验证防护有效 |

## 测试覆盖范围

- **页面元素验证**：标题、表格、搜索框、字段、按钮、分页（test_01）
- **数据准备**：从真实详情页提取查询关键字（test_02）
- **功能查询**：按名称精确查询、按编码精确查询（test_03、test_04）
- **筛选条件**：按行业分类、按产品类型筛选（test_08、test_09）
- **重置与分页**：重置搜索条件、分页切换（test_05、test_07）
- **详情交互**：查看详情、单次/多次进入详情并返回（test_06、test_11、test_12）
- **空状态**：查询无结果时的空状态展示（test_10）
- **安全测试**：SQL 注入防御（名称、编码两个入口，test_13、test_14）

## 用例依赖关系

```
test_02 (数据准备: 提取真实名称+编码)
   ├── test_03 (按名称查询)
   └── test_04 (按编码查询)
```

> 说明：test_02 是数据准备用例，test_03/test_04 依赖其抓取的真实数据；其余用例相互独立。

## 测试统计
- **总计**: 14 个测试用例
- 功能/交互测试: 12 个（test_01~test_12）
- 安全测试: 2 个（test_13、test_14）

## 生命周期方法
- `setup_class`: 仅执行一次，启动浏览器、创建持久化 context 与 page（登录态通过 context cookie 保持）
- `setup_method`: 首个用例完成**一次性登录**（登录作为本页面测试的初始状态），其余用例仅 `goto` 回到产品列表页面，**不再重新登录**
- `teardown_method`: 不关闭页面/上下文，保留登录态供后续用例复用（失败截图由 conftest 钩子处理）
- `teardown_class`: 所有用例结束后关闭 page、context、browser

> 设计要点：登录只做一次，登录态通过持久化 context 保持；每个用例执行前回到产品列表页重置页面状态，避免用例间相互干扰。

## 依赖与配置
- 依赖 `tests/ui_tests/config.py` 中的 `UIConfig`（用户IP映射、超时配置）
- 依赖 `utils/base.py` 的 `Base` 基类（登录、页面导航、通用助手方法）
- 使用 Playwright 浏览器驱动，headless 模式下需在导航后等待 Vue 组件渲染

---

**文档版本**: v2.0  
**生成时间**: 2026年7月  
**更新说明**: 补充各用例详细功能描述、覆盖范围、依赖关系与统计
