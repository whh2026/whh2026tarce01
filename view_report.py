#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试报告查看器
启动本地HTTP服务器来查看测试报告
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def find_latest_report():
    """查找最新的测试报告目录"""
    import re
    
    reports_dir = Path('reports')
    if not reports_dir.exists():
        print(f"错误: 报告目录 {reports_dir} 不存在")
        return None
    
    # 获取所有报告目录，只匹配时间戳格式（YYYYMMDD_HHMMSS）
    timestamp_pattern = re.compile(r'^\d{8}_\d{6}$')
    report_dirs = [d for d in reports_dir.iterdir() 
                  if d.is_dir() and timestamp_pattern.match(d.name)]
    
    if not report_dirs:
        print(f"错误: 在 {reports_dir} 中没有找到报告目录")
        print(f"可用的目录: {[d.name for d in reports_dir.iterdir() if d.is_dir()]}")
        return None
    
    # 按名称排序（时间戳格式：YYYYMMDD_HHMMSS）
    latest_report = max(report_dirs, key=lambda x: x.name)
    print(f"找到最新的报告目录: {latest_report}")
    return latest_report

def start_server(port=8000):
    """启动HTTP服务器"""
    # 查找最新的报告目录
    report_dir = find_latest_report()
    if not report_dir:
        return False
    
    html_dir = report_dir / 'html'
    if not html_dir.exists():
        print(f"错误: HTML报告目录 {html_dir} 不存在")
        return False
    
    report_file = html_dir / 'report.html'
    if not report_file.exists():
        print(f"错误: 报告文件 {report_file} 不存在")
        return False
    
    # 切换到报告目录
    os.chdir(html_dir)
    
    # 创建自定义的请求处理器
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            """自定义日志格式"""
            print(f"[{self.log_date_time_string()}] {format % args}")
    
    # 启动服务器
    try:
        with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
            server_url = f"http://localhost:{port}/report.html"
            print("=" * 60)
            print("测试报告查看器")
            print("=" * 60)
            print(f"报告目录: {html_dir}")
            print(f"服务器地址: {server_url}")
            print("=" * 60)
            print("\n正在启动服务器...")
            
            # 自动打开浏览器
            webbrowser.open(server_url)
            print(f"✅ 已在浏览器中打开报告: {server_url}")
            print("\n按 Ctrl+C 停止服务器")
            print("=" * 60)
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"错误: 端口 {port} 已被占用")
            print(f"请尝试使用其他端口，例如: python view_report.py --port 8001")
        else:
            print(f"错误: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        return True
    
    return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试报告查看器')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口 (默认: 8000)')
    args = parser.parse_args()
    
    start_server(args.port)

if __name__ == "__main__":
    main()
