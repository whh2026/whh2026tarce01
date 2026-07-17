# TestUserManagement 测试文档

## 文件路径
`tests/ui_tests/test002_user_management_rules.py`

## 测试类概述
用户管理页面测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_search_username` | 按用户名搜索 |
| 2 | `test_02_add_user` | 新增用户 |
| 3 | `test_03_view_user_detail` | 查看用户详情 |
| 4 | `test_04_edit_user` | 编辑用户信息 |
| 5 | `test_05_delete_user` | 删除用户 |
| 6 | `test_06_pagination` | 分页功能验证 |
| 7 | `test_07_reset_search` | 重置搜索条件 |
| 8 | `test_08_disable_user` | 禁用用户 |
| 9 | `test_09_enable_user` | 启用用户 |
| 10 | `test_10_add_user_validation` | 新增用户表单校验 |
| 11 | `test_11_username_must_start_with_auto` | 用户名必须以"auto"开头规则校验 |
| 12 | `test_12_search_by_nickname` | 按昵称搜索用户 |
| 13 | `test_13_search_by_role_type` | 按角色类型搜索用户 |
| 14 | `test_14_edit_user_validation` | 编辑用户表单校验 |
| 15 | `test_15_role_dependency_validation` | 角色依赖关系校验 |

## 测试覆盖范围

## 生命周期方法
- setup_, teardown_

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
