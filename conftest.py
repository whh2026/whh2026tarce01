import pytest
from datetime import datetime
import os

# 导入pytest-html插件以支持HTML报告中的截图附件
try:
    import pytest_html
    from pytest_html import extras
except ImportError:
    pytest_html = None
    extras = None

try:
    import allure
except ImportError:
    pass

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """保存测试结果并将截图附加到报告中"""
    outcome = yield
    rep = outcome.get_result()
    
    # 为每个测试方法保存结果（只有当 item.instance 存在时）
    if item.instance is not None:
        setattr(item.instance, f"_rep_{rep.when}", rep)
    
    # 如果是call阶段，添加测试数据到报告
    if rep.when == 'call':
        if item.instance is not None and hasattr(item.instance, '_test_data'):
            try:
                # 获取测试数据
                test_data = item.instance._test_data
                
                # 将测试数据转换为HTML格式
                if test_data:
                    test_data_html = _format_test_data_to_html(test_data)
                    
                    # 附加测试数据到报告
                    if extras is not None:
                        if not hasattr(rep, 'extras'):
                            rep.extras = []
                        rep.extras.append(extras.html(test_data_html))
                        print(f"[成功] 测试数据已附加到HTML报告")
            except Exception as e:
                print(f"[错误] 处理测试数据时出错：{e}")
                import traceback
                traceback.print_exc()
    
    # 如果是call阶段且失败，保存截图并附加到报告
    if rep.when == 'call' and rep.failed:
        if item.instance is not None and hasattr(item.instance, 'page'):
            try:
                # 直接调用实例的截图方法
                item.instance.capture_failure_screenshot(item.function)
                
                # 检查是否生成了截图路径
                if hasattr(item.instance, '_last_screenshot_path'):
                    screenshot_path = item.instance._last_screenshot_path
                    
                    if screenshot_path and os.path.exists(screenshot_path):
                        # 附加HTML到报告
                        if extras is not None:
                            # 将截图转换为base64格式
                            import base64
                            with open(screenshot_path, 'rb') as f:
                                screenshot_bytes = f.read()
                                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                            
                            # 直接设置 report.extras
                            if not hasattr(rep, 'extras'):
                                rep.extras = []
                            # 以HTML形式附加截图，控制大小和位置
                            screenshot_html = f"""
                            <div style="margin: 15px 0; padding: 10px; background-color: #f9f9f9; border-radius: 5px; border: 1px solid #ddd;">
                                <h4 style="margin: 0 0 10px 0; color: #333;">失败截图</h4>
                                <div style="text-align: center;">
                                    <img src="data:image/png;base64,{screenshot_base64}" style="max-width: 90%; max-height: 600px; border: 1px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" alt="失败截图" />
                                </div>
                            </div>
                            """
                            rep.extras.append(extras.html(screenshot_html))
                            print(f"[成功] 截图已附加到HTML报告")
                        else:
                            print(f"[警告] pytest-html extras模块不可用，截图未附加到HTML报告")
                    else:
                        print(f"[警告] 截图文件不存在：{screenshot_path}")
                else:
                    print(f"[警告] 未生成截图路径")
            except Exception as e:
                print(f"[错误] 处理失败截图时出错：{e}")
                import traceback
                traceback.print_exc()

def _format_test_data_to_html(test_data):
    """将测试数据格式化为HTML表格"""
    if not test_data:
        return "<p>无测试数据</p>"
    
    html = """
    <div style="margin: 10px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
        <h4 style="margin: 0 0 10px 0; color: #333;">测试数据</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background-color: #e0e0e0;">
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left; width: 30%;">字段</th>
                <th style="border: 1px solid #ddd; padding: 8px; text-align: left; width: 70%;">值</th>
            </tr>
    """
    
    for key, value in test_data.items():
        # 处理值，如果是字符串且包含换行符，则保留格式
        if isinstance(value, str):
            value = value.replace('\n', '<br>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        elif value is None:
            value = '<span style="color: #999;">None</span>'
        elif isinstance(value, bool):
            value = '<span style="color: green;">True</span>' if value else '<span style="color: red;">False</span>'
        
        html += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px; font-weight: bold;">{key}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{value}</td>
            </tr>
        """
    
    html += """
        </table>
    </div>
    """
    
    return html
