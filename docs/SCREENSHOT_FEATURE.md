# 失败截图功能说明

## 功能概述

项目中已经集成了自动失败截图功能，当测试用例失败时会自动捕获当前页面状态并保存截图。

## 工作原理

1. **自动触发**: 当测试用例失败时，pytest 的 `pytest_runtest_makereport` 钩子会自动触发
2. **截图保存**: 调用 `Base.capture_failure_screenshot()` 方法保存截图到 `reports/screenshots/` 目录
3. **报告附加**: 将截图自动附加到 HTML 报告和 Allure 报告中

## 截图文件命名规则

```
{模块名}_{测试类名}_{测试方法名}_{时间戳}.png
```

示例：
```
ui_tests_test001_company_management_TestCompanyManagement_test_search_username_20260316_101914_982.png
```

## 配置选项

### 1. 修改截图目录

通过环境变量设置截图目录：

```powershell
# Windows PowerShell
$env:SCREENSHOTS_DIR = "custom/screenshots/path"

# Windows CMD
set SCREENSHOTS_DIR=custom/screenshots/path

# Linux/Mac
export SCREENSHOTS_DIR=custom/screenshots/path
```

### 2. pytest.ini 配置

在项目根目录的 `pytest.ini` 中配置：

```ini
[pytest]
# 测试文件匹配模式
python_files = test*.py *_test.py

# 测试类匹配模式
python_classes = Test*

# 测试函数匹配模式
python_functions = test_*

# 测试路径
testpaths = tests

# 最小 Python 版本
minversion = 6.0

# 添加默认参数
addopts = 
    -v
    --strict-markers
    --tb=short
```

## 使用方法

### 1. 运行所有测试（自动截图）

```powershell
python -m pytest tests/ui_tests/
```

### 2. 运行特定测试文件

```powershell
python -m pytest tests/ui_tests/test001_company_management.py
```

### 3. 运行特定测试用例

```powershell
python -m pytest tests/ui_tests/test001_company_management.py::TestCompanyManagement::test_search_username
```

### 4. 生成 HTML 报告（包含截图）

```powershell
python -m pytest tests/ui_tests/ --html=reports/test_report.html --self-contained-html
```

### 5. 生成 Allure 报告（包含截图）

```powershell
# 运行测试
python -m pytest tests/ui_tests/ --alluredir=reports/allure-results

# 生成报告
allure generate reports/allure-results -o reports/allure-report
```

## 截图功能特性

### ✅ 已实现的功能

1. **自动截图**: 测试失败时自动捕获页面状态
2. **全页截图**: 捕获整个页面，包括需要滚动的部分
3. **唯一文件名**: 使用时间戳确保文件名唯一
4. **多格式支持**: 同时支持 HTML 报告和 Allure 报告
5. **错误处理**: 如果截图失败，会尝试备用的截图方法
6. **Base64 编码**: 截图以 Base64 格式嵌入 HTML 报告，无需外部文件
7. **美观样式**: HTML 报告中的截图有边框和阴影效果

### 📁 截图存储位置

默认位置：`reports/screenshots/`

示例文件：
```
reports/screenshots/
├── ui_tests_test001_company_management_TestCompanyManagement_test_search_username_20260316_101914_982.png
├── ui_tests_test02_product_strategy_TestProductStrategy_test_01_page_elements_20260316_102015_123.png
└── ...
```

## 手动触发截图

如果需要在测试过程中手动截图，可以使用：

```python
# 在测试方法中
self.page.screenshot(path="reports/screenshots/manual_screenshot.png", full_page=True)
```

## 调试信息

当测试失败时，控制台会输出以下信息：

```
[截图] 测试失败，截图已保存：reports/screenshots\ui_tests_test_screenshot_test_TestFailureScreenshot_test_intentional_failure_20260316_101914_982.png
```

如果截图附加到 HTML 报告失败，会显示：

```
[警告] pytest-html extras模块不可用，截图未附加到HTML报告
```

## 故障排除

### 问题 1: 截图未生成

**可能原因**:
- 截图目录没有写权限
- 磁盘空间不足
- Playwright 截图功能异常

**解决方法**:
1. 检查 `reports/screenshots/` 目录是否存在且有写权限
2. 检查磁盘空间是否充足
3. 查看控制台输出的错误信息

### 问题 2: 截图未附加到 HTML 报告

**可能原因**:
- pytest-html 插件未安装
- extras 模块导入失败

**解决方法**:
1. 安装 pytest-html 插件：
   ```bash
   pip install pytest-html
   ```

2. 检查 conftest.py 中的 extras 导入

### 问题 3: 截图文件名过长

**可能原因**:
- 模块名、类名、方法名过长

**解决方法**:
- 已经优化了文件名生成逻辑，使用下划线替换点号
- 如果仍然过长，可以考虑缩短测试名称

## 最佳实践

1. **定期清理**: 定期清理旧的截图文件，避免占用过多磁盘空间
2. **版本控制**: 建议将截图目录添加到 `.gitignore`
3. **CI/CD**: 在持续集成中配置截图存储和报告生成
4. **命名规范**: 保持测试用例命名清晰，便于通过截图文件名定位问题

## 示例

### 完整测试运行示例

```powershell
# 运行所有测试并生成 HTML 报告
python -m pytest tests/ui_tests/ `
  --html=reports/test_report.html `
  --self-contained-html `
  -v

# 运行完成后，打开报告
start reports/test_report.html
```

### 查看失败截图

1. 打开 HTML 报告
2. 找到失败的测试用例
3. 在测试详情中查看"失败截图"部分
4. 点击截图可以查看完整大小的图片

## 技术实现

### 核心文件

1. **utils/base.py**: `capture_failure_screenshot()` 方法
2. **conftest.py**: `pytest_runtest_makereport` 钩子
3. **pytest.ini**: pytest 配置文件

### 工作流程

```
测试失败
  ↓
pytest_runtest_makereport 钩子触发
  ↓
调用 capture_failure_screenshot()
  ↓
保存截图到 reports/screenshots/
  ↓
附加到 HTML 报告（Base64 编码）
  ↓
附加到 Allure 报告（如果可用）
```

## 更新日志

- 2026-03-16: 改进了截图文件名生成逻辑，增加了毫秒级时间戳
- 2026-03-16: 添加了备用截图机制，提高可靠性
- 2026-03-16: 优化了 HTML 报告中的截图样式
- 2026-03-16: 改进了错误处理和日志输出
