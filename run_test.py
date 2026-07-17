import subprocess
import os
import re
from datetime import datetime
from pathlib import Path

# 添加邮件发送功能
import sys
sys.path.insert(0, str(Path(__file__).parent))
from tests.api_tests.utils.email_sender import EmailSender

def parse_test_results(output_file: str) -> dict:
    """
    解析测试输出文件，提取测试结果
    
    Args:
        output_file: 测试输出文件路径
    
    Returns:
        dict: 测试结果字典
    """
    result = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': 0,
        'duration': 0.0,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 解析测试结果统计
            # 查找类似 "32 passed, 10 failed, 1 skipped, 6 errors" 的模式
            pattern = r'(\d+)\s+passed,\s*(\d+)\s+failed,\s*(\d+)\s+skipped,\s*(\d+)\s+errors'
            match = re.search(pattern, content)
            
            if match:
                result['passed'] = int(match.group(1))
                result['failed'] = int(match.group(2))
                result['skipped'] = int(match.group(3))
                result['errors'] = int(match.group(4))
                result['total'] = result['passed'] + result['failed'] + result['skipped'] + result['errors']
            
            # 解析执行时间
            time_pattern = r'=\s*(\d+\.?\d*)\s+s'
            time_match = re.search(time_pattern, content)
            if time_match:
                result['duration'] = float(time_match.group(1))
            
    except Exception as e:
        print(f"解析测试结果时出错: {e}")
    
    return result

def run_tests():
    # 生成带时间戳的报告目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_dir = f'reports/{timestamp}'
    html_dir = f'{report_dir}/html'
    allure_dir = f'{report_dir}/allure'
    screenshots_dir = f'{report_dir}/screenshots'
    
    # 创建报告目录结构
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(allure_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("=== 运行测试并同时生成HTML和Allure报告 ===")
    # 设置环境变量，传递截图目录
    env = os.environ.copy()
    env['SCREENSHOTS_DIR'] = screenshots_dir
    
    # 运行pytest，同时生成HTML和Allure报告
    # 将输出保存到文件以便查看完整结果
    output_file = f'{html_dir}/test_output.txt'
    with open(output_file, 'w') as f:
        test_result = subprocess.run([
            # 'python', '-m', 'pytest', 'tests/api_tests/',
            'python', '-m', 'pytest', 'tests/ui_tests/', 
            f'--html={html_dir}/report.html', '--self-contained-html',
            f'--alluredir={allure_dir}',
            '-v'
        ], env=env, stdout=f, stderr=subprocess.STDOUT)
    print(f"测试输出已保存到: {os.path.abspath(output_file)}")
    
    print("\n=== 测试运行完成 ===")
    print(f"HTML报告路径: {os.path.abspath(f'{html_dir}/report.html')}")
    print(f"Allure报告数据路径: {os.path.abspath(allure_dir)}")
    print(f"截图保存路径: {os.path.abspath(screenshots_dir)}")
    print("\n要查看Allure报告，请运行:")
    print(f"allure serve {os.path.abspath(allure_dir)}")
    
    # 解析测试结果
    print("\n=== 解析测试结果 ===")
    test_results = parse_test_results(output_file)
    test_results['pass_rate'] = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    
    print(f"总测试数: {test_results['total']}")
    print(f"通过: {test_results['passed']}")
    print(f"失败: {test_results['failed']}")
    print(f"跳过: {test_results['skipped']}")
    print(f"错误: {test_results['errors']}")
    print(f"通过率: {test_results['pass_rate']:.1f}%")
    print(f"执行时间: {test_results['duration']:.2f}秒")
    
    # 发送测试报告邮件
    print("\n=== 发送测试报告邮件 ===")
    email_sender = EmailSender()
    email_sent = email_sender.send_test_report(report_dir, test_results)
    
    if email_sent:
        print("✅ 测试报告邮件发送成功！")
    else:
        print("⚠️ 测试报告邮件发送失败（可能是配置未设置）")
    
    return test_result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ 所有测试运行成功！")
    else:
        print("\n❌ 测试运行失败！")