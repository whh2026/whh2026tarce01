# base.py 公共方法文档

## 概述

`base.py` 是 UI 自动化测试的基础类，包含登录管理、产品操作、审批流程等核心公共方法，用于支撑测试用例的执行。

---

## 目录

1. [测试框架方法](#测试框架方法)
2. [登录相关方法](#登录相关方法)
3. [URL构建方法](#url构建方法)
4. [产品管理方法](#产品管理方法)
5. [审批流程方法](#审批流程方法)
6. [查询验证方法](#查询验证方法)
7. [接口调试方法](#接口调试方法)
8. [数据获取方法](#数据获取方法)

---

## 测试框架方法

### 1. setup_class(cls)

**功能**：类级别初始化，所有测试方法执行前只执行一次

**参数**：无

**返回值**：无

**用法**：
```python
@classmethod
def setup_class(cls):
    # 启动浏览器、创建上下文和页面
    cls.playwright = sync_playwright().start()
    cls.browser = cls.playwright.chromium.launch(headless=False)
    cls.context = cls.browser.new_context(viewport={"width": 1900, "height": 950})
    cls.page = cls.context.new_page()
```

### 2. teardown_class(cls)

**功能**：类级别清理，所有测试方法执行后只执行一次

**参数**：无

**返回值**：无

### 3. setup_method(self, method)

**功能**：每个测试方法执行前的设置

**参数**：
- `method`: 当前测试方法对象

**返回值**：无

### 4. teardown_method(self, method)

**功能**：每个测试方法执行后的清理

**参数**：
- `method`: 当前测试方法对象

**返回值**：无

### 5. capture_failure_screenshot(self, method)

**功能**：捕获失败截图并附加到测试报告中

**参数**：
- `method`: 当前测试方法对象

**返回值**：无

---

## 登录相关方法

### 6. login(cls, self=None)

**功能**：通用登录方法，支持类级别和实例级别调用

**参数**：
- `self`: 实例对象（可选）

**返回值**：无

**用法**：
```python
Base.login()  # 类级别调用
self.login()  # 实例级别调用
```

### 7. login_with_ip(cls, ip, port, username, password, captchaAnswer, page)

**功能**：使用指定的IP和端口登录

**参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `ip` | str | 服务器IP地址 |
| `port` | str | 服务器端口号 |
| `username` | str | 用户名 |
| `password` | str | 密码 |
| `captchaAnswer` | str | 验证码 |
| `page` | Page | Playwright页面对象 |

**返回值**：无

**用法**：
```python
Base.login_with_ip("192.168.0.183", "30001", "admin", "password", "123456", self.page)
```

### 8. login_with_ip_direct(cls, ip, port, username, password, captchaAnswer, page)

**功能**：直接IP登录（与 `login_with_ip` 类似，流程略有不同）

**参数**：同 `login_with_ip`

**返回值**：无

### 9. login_with_user(cls, user_id=1, user_ips=None, fixed_port=None, page=None)

**功能**：根据用户ID登录

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_id` | int | 1 | 用户ID |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |
| `page` | Page | None | 页面对象 |

**user_ips 支持格式**：
```python
# 格式1: IP:端口
{"1": "192.168.0.183:30001", "2": "192.168.0.185:30001"}

# 格式2: 字典形式
{"ip": "192.168.0.183", "port": "30001"}
```

**返回值**：无

**用法**：
```python
# 使用默认用户配置登录
Base.login_with_user(user_id=1, page=self.page)

# 使用自定义用户配置
user_ips = {1: "192.168.0.183:30001", 2: "192.168.0.185:30001"}
Base.login_with_user(user_id=2, user_ips=user_ips, page=self.page)
```

---

## URL构建方法

### 10. get_url_for_ip(self, ip, port, path)

**功能**：根据IP和端口获取完整URL

**参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `ip` | str | 服务器IP地址 |
| `port` | str | 服务器端口 |
| `path` | str | 路径（如 `/login`） |

**返回值**：`str` - 完整的URL

**用法**：
```python
url = self.get_url_for_ip("192.168.0.183", "30001", "/login")
# 返回: "http://192.168.0.183:30001/login"
```

### 11. get_url_for_user(self, user_id, path, user_ips=None, fixed_port=None)

**功能**：根据用户ID获取URL

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_id` | int | - | 用户ID |
| `path` | str | - | 路径 |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |

**返回值**：`str` - 完整的URL

**用法**：
```python
url = self.get_url_for_user(1, "/datamarket/product/product-list")
# 返回: "http://192.168.0.183:30001/datamarket/product/product-list"
```

---

## 产品管理方法

### 12. create_data_product(self, need_apply=False, custom_name=None, need_auth=False)

**功能**：创建数据产品的完整流程

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `need_apply` | bool | False | 是否需要申请使用 |
| `custom_name` | str | None | 自定义产品名称 |
| `need_auth` | bool | False | 是否需要精准授权 |

**返回值**：`dict` - 包含产品信息的字典
```python
{
    "name": "产品名称",
    "code": "产品编码",
    "industry": "采矿业"
}
```

**用法**：
```python
# 创建普通产品
product_data = self.create_data_product()

# 创建需要授权的产品
product_data = self.create_data_product(need_auth=True)

# 使用自定义名称
product_data = self.create_data_product(custom_name="测试产品001")
```

### 13. search_product_and_apply(self, user_id, product_name, user_ips=None, fixed_port=None)

**功能**：搜索产品并申请

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_id` | int | - | 用户ID |
| `product_name` | str | - | 产品名称 |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |

**返回值**：`bool` - 是否找到并点击了立即申请按钮

**用法**：
```python
result = self.search_product_and_apply(2, "测试产品001")
if result:
    print("申请成功")
```

### 14. verify_product_status_in_received_list(self, product_name, expected_status="交付中", user_id=2, user_ips=None, fixed_port=None)

**功能**：在received-list页面验证产品状态

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `product_name` | str | - | 产品名称 |
| `expected_status` | str | "交付中" | 期望状态 |
| `user_id` | int | 2 | 用户ID |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |

**返回值**：无

**用法**：
```python
self.verify_product_status_in_received_list("测试产品001", "待交付")
```

---

## 审批流程方法

### 15. submit_application(self)

**功能**：提交申请

**参数**：无

**返回值**：`bool` - 是否成功提交申请

**用法**：
```python
success = self.submit_application()
if success:
    print("申请提交成功")
```

### 16. approve_product_application(self, product_name, user_id=1, user_ips=None, fixed_port=None)

**功能**：审核产品申请

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `product_name` | str | - | 产品名称 |
| `user_id` | int | 1 | 审核用户ID |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |

**返回值**：无

**用法**：
```python
self.approve_product_application("测试产品001", user_id=1)
```

---

## 查询验证方法

### 17. verify_product_stats(self, product_name, user_id=2, user_ips=None, fixed_port=None)

**功能**：验证产品统计信息

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `product_name` | str | - | 产品名称 |
| `user_id` | int | 2 | 用户ID |
| `user_ips` | dict | None | 用户IP映射字典 |
| `fixed_port` | str | None | 固定端口 |

**返回值**：无

### 18. search_in_received_list(self, product_name, user_id=2, user_ips=None, fixed_port=None)

**功能**：在接收列表中搜索产品

**参数**：同 `verify_product_stats`

**返回值**：无

---

## 接口调试方法

### 19. debug_interface(self, input_param="1234", wait_time=10)

**功能**：接口调试

**参数**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_param` | str | "1234" | 输入参数 |
| `wait_time` | int | 10 | 发起请求后的等待时间（秒） |

**返回值**：无

**用法**：
```python
# 使用默认参数
self.debug_interface()

# 使用自定义参数
self.debug_interface(input_param="2024-01-01", wait_time=15)
```

---

## 数据获取方法

### 20. get_test_data()

**功能**：从JSON文件读取测试数据

**参数**：无

**返回值**：`list` - 测试数据列表

**数据格式**：
```json
[
    {
        "username": "admin",
        "password": "ChainMaker123.",
        "captchaAnswer": "987423",
        "ip": "192.168.0.183",
        "port": "30001"
    }
]
```

**用法**：
```python
test_data = get_test_data()
username = test_data[0]["username"]
```

---

## 用户IP映射默认配置

```python
default_user_ips = {
    1: "192.168.0.183:30001",
    2: "192.168.0.185:30001"
}
```

- **用户1**：环境183
- **用户2**：环境185

---

## 注意事项

1. 所有方法均基于 Playwright 同步API实现
2. 网络请求等待使用 `networkidle` 状态，超时时间30秒
3. 元素定位采用多选择器策略，提高稳定性
4. 测试数据从 `data/ui_test_data.json` 文件读取
5. 截图保存到 `reports/screenshots` 目录（可通过环境变量 `SCREENSHOTS_DIR` 配置）