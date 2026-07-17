# API测试目录结构说明

## 目录架构

```
api_tests/
├── __init__.py                 # 包初始化文件
├── conftest.py                 # Pytest全局配置和fixtures
├── base.py                     # API测试基类（保留向后兼容）
├── config/                     # 配置文件目录
│   ├── __init__.py
│   └── config.py              # 配置类
├── data/                      # 测试数据目录
│   ├── products/              # 产品相关测试数据
│   ├── market/                # 市场相关测试数据
│   │   └── product_market_data.json
│   ├── registration/          # 注册相关测试数据
│   │   └── registration_data.json
│   ├── agreement/             # 协议相关测试数据
│   │   └── agreement_data.json
│   └── test_data.json        # 通用测试数据
├── fixtures/                  # Fixtures目录
│   ├── __init__.py
│   └── api_fixtures.py      # API相关fixtures
├── test_cases/               # 测试用例目录
│   ├── test_product_list.py   # 产品列表测试（旧版）
│   ├── test_product_list_dd.py # 产品列表测试（数据驱动版）
│   ├── test_product_market.py # 产品市场测试
│   ├── test_registration.py  # 注册测试
│   └── test_agreement.py     # 协议测试
└── utils/                    # 工具类目录
    ├── __init__.py
    ├── data_loader.py        # 数据加载器
    └── assertions.py        # 断言工具
```

## 数据驱动模式特点

### 1. 配置管理
- 使用 `config/config.py` 统一管理配置
- 支持环境变量配置
- 集中管理API URL、超时时间等配置

### 2. 数据分离
- 测试数据与测试代码分离
- 按功能模块组织数据文件
- 使用 `data_loader.py` 统一加载数据

### 3. 工具类
- `data_loader.py`: 提供数据加载功能，支持缓存
- `assertions.py`: 提供常用断言方法，减少重复代码

### 4. Fixtures
- `conftest.py`: 全局fixtures，提供session级别的认证和数据
- `fixtures/api_fixtures.py`: 专用的API测试fixtures

### 5. 测试用例
- 支持传统的测试用例（继承APIBase）
- 支持数据驱动测试用例（使用fixtures和工具类）
- 支持参数化测试

## 使用方法

### 传统方式（向后兼容）

```python
from tests.api_tests.base import APIBase

class TestMyAPI(APIBase):
    def test_something(self):
        response = self.post("/api/endpoint", json={"key": "value"})
        self.assert_response_success(response)
```

### 数据驱动方式（推荐）

```python
import pytest
from tests.api_tests.utils.data_loader import data_loader
from tests.api_tests.utils.assertions import assertions

def test_something(api_client, test_data):
    # 使用数据加载器获取测试数据
    test_case_data = test_data.get_test_case_data("test_data.json", "test_case_name")
    
    # 使用API客户端发送请求
    response = api_client.post("/api/endpoint", json=test_case_data)
    
    # 使用断言工具验证结果
    assertions.assert_response_success(response)
```

### 参数化测试

```python
@pytest.mark.parametrize("page_size", [5, 10, 20])
def test_pagination(api_client, page_size):
    response = api_client.post("/api/list", json={"pageSize": page_size})
    assertions.assert_response_success(response)
```

## 配置说明

### 环境变量

- `API_BASE_URL`: API基础URL（默认: http://192.168.0.183:30201）
- `API_TIMEOUT`: 请求超时时间（默认: 30秒）
- `API_USERNAME`: 默认用户名（默认: admin）
- `API_PASSWORD`: 默认密码（默认: admin123）
- `TEST_ENV`: 测试环境（默认: dev）
- `LOG_LEVEL`: 日志级别（默认: INFO）
- `RETRY_COUNT`: 重试次数（默认: 3）
- `RETRY_DELAY`: 重试延迟（默认: 1秒）

### 运行测试

```bash
# 运行所有API测试
pytest tests/api_tests/

# 运行特定模块的测试
pytest tests/api_tests/test_cases/test_product_list_dd.py

# 运行带标记的测试
pytest tests/api_tests/ -m smoke

# 运行特定测试用例
pytest tests/api_tests/ -k "test_01_list_products"

# 并行运行测试（需要安装pytest-xdist）
pytest tests/api_tests/ -n auto

# 生成测试报告
pytest tests/api_tests/ --html=report.html
```

## 数据文件格式

### JSON格式示例

```json
{
  "test_case_name": {
    "test_case_desc": "测试用例描述",
    "test_case_data": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

### 使用数据加载器

```python
from tests.api_tests.utils.data_loader import data_loader

# 加载整个数据文件
data = data_loader.load_json("test_data.json")

# 获取特定测试用例的数据
test_case_data = data_loader.get_test_case_data("test_data.json", "test_case_name")

# 获取所有测试用例
all_test_cases = data_loader.get_all_test_cases("test_data.json")
```

## 断言工具使用

```python
from tests.api_tests.utils.assertions import assertions

# 断言响应成功
assertions.assert_response_success(response, expected_code=200)

# 断言响应结构
assertions.assert_response_structure(response, ["code", "msg", "data"])

# 断言数据结构
assertions.assert_data_structure(data, ["list", "pagination"])

# 断言字段类型
assertions.assert_list_field(data, "list")
assertions.assert_dict_field(data, "pagination")
assertions.assert_int_field(data, "total")

# 断言字段值
assertions.assert_field_value(data, "status", "success")

# 断言字段不为空
assertions.assert_field_not_empty(data, "list")

# 断言分页信息
assertions.assert_pagination(response, expected_page_number=1, expected_page_size=10)
```

## 最佳实践

1. **数据分离**: 将测试数据存储在JSON文件中，便于维护
2. **使用工具类**: 使用data_loader和assertions工具类减少重复代码
3. **参数化测试**: 使用@pytest.mark.parametrize进行参数化测试
4. **使用fixtures**: 合理使用fixtures提供测试依赖
5. **测试标记**: 使用pytest标记对测试进行分类（smoke、regression等）
6. **环境隔离**: 使用环境变量管理不同环境的配置
7. **清理资源**: 在teardown中清理测试创建的资源
8. **独立测试**: 确保每个测试用例独立运行，不依赖其他测试

## 迁移指南

从传统模式迁移到数据驱动模式：

1. 将测试数据提取到JSON文件中
2. 使用data_loader加载数据
3. 使用assertions替代手动断言
4. 使用fixtures替代setup/teardown
5. 考虑使用参数化测试替代循环测试
