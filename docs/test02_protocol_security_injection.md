# TestProtocolSecurityInjection 测试文档

## 文件路径
`tests/ui_tests/test02_protocol_security_injection.py`

## 测试类概述
协议安全注入测试类

## 测试用例列表

| 序号 | 测试方法 | 描述 |
|-----|---------|-----|
| 1 | `test_01_sql_injection_in_protocol_name_query` | 协议名称查询SQL注入攻击防御测试 |
| 2 | `test_02_js_injection_in_protocol_name_query` | 协议名称查询JavaScript注入防御测试 |
| 3 | `test_03_xss_injection_in_protocol_name_query` | 协议名称查询XSS跨站脚本注入防御测试 |

## 测试覆盖范围

## 生命周期方法
- setup_, teardown_

## 依赖与配置

---

**文档版本**: v1.0  
**生成时间**: 2026年6月
