# -*- coding: utf-8 -*-
"""
邮件发送工具类
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
from pathlib import Path
from typing import List, Optional
import os

from tests.api_tests.utils.email_config import EmailConfig


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        """初始化邮件发送器"""
        self.smtp_server = EmailConfig.SMTP_SERVER
        self.smtp_port = EmailConfig.SMTP_PORT
        self.use_tls = EmailConfig.SMTP_USE_TLS
        self.sender_email = EmailConfig.SENDER_EMAIL
        self.sender_password = EmailConfig.SENDER_PASSWORD
        self.sender_name = EmailConfig.SENDER_NAME
        self.recipients = EmailConfig.get_recipients()
    
    def create_message(self, subject: str, body: str, attachments: Optional[List[str]] = None) -> MIMEMultipart:
        """
        创建邮件消息
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件路径列表
        
        Returns:
            MIMEMultipart: 邮件消息对象
        """
        msg = MIMEMultipart()
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = ', '.join(self.recipients)
        msg['Subject'] = subject
        
        # 添加邮件正文
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 添加附件
        if attachments:
            for attachment_path in attachments:
                self._add_attachment(msg, attachment_path)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """
        添加附件到邮件
        
        Args:
            msg: 邮件消息对象
            file_path: 附件文件路径
        """
        path = Path(file_path)
        if not path.exists():
            print(f"警告: 附件文件不存在: {file_path}")
            return
        
        # 根据文件类型选择MIME类型
        mime_type = self._get_mime_type(path)
        
        with open(path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=path.name)
        
        part['Content-Disposition'] = f'attachment; filename="{path.name}"'
        msg.attach(part)
        print(f"已添加附件: {path.name} ({mime_type})")
    
    def _get_mime_type(self, path: Path) -> str:
        """
        根据文件扩展名获取MIME类型
        
        Args:
            path: 文件路径
        
        Returns:
            str: MIME类型
        """
        suffix = path.suffix.lower()
        mime_types = {
            '.html': 'text/html',
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.zip': 'application/zip',
            '.json': 'application/json',
        }
        return mime_types.get(suffix, 'application/octet-stream')
    
    def send(self, subject: str, body: str, attachments: Optional[List[str]] = None) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件路径列表
        
        Returns:
            bool: 发送是否成功
        """
        if not EmailConfig.is_configured():
            print("错误: 邮件配置不完整，无法发送邮件")
            EmailConfig.print_config_status()
            return False
        
        try:
            # 创建邮件消息
            msg = self.create_message(subject, body, attachments)
            
            # 连接SMTP服务器
            print(f"\n正在连接SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
                print("已启用TLS加密")
            
            # 登录
            print(f"正在登录: {self.sender_email}")
            server.login(self.sender_email, self.sender_password)
            print("登录成功")
            
            # 发送邮件
            print(f"正在发送邮件到: {', '.join(self.recipients)}")
            server.send_message(msg)
            print("✅ 邮件发送成功！")
            
            # 关闭连接
            server.quit()
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP认证失败: {e}")
            print("请检查发件人邮箱和密码是否正确")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 发送邮件时发生错误: {e}")
            return False
    
    def send_test_report(self, report_dir: str, test_results: dict) -> bool:
        """
        发送测试报告邮件
        
        Args:
            report_dir: 报告目录路径
            test_results: 测试结果字典
        
        Returns:
            bool: 发送是否成功
        """
        report_path = Path(report_dir)
        html_report = report_path / 'html' / 'report.html'
        test_output = report_path / 'html' / 'test_output.txt'
        
        # 检查报告文件是否存在
        if not html_report.exists():
            print(f"错误: HTML报告文件不存在: {html_report}")
            return False
        
        # 构建邮件主题
        subject = f"【测试报告】{test_results.get('timestamp', '')} - API自动化测试结果"
        
        # 构建邮件正文
        body = self._build_test_report_body(test_results, report_dir)
        
        # 收集附件
        attachments = []
        if html_report.exists():
            attachments.append(str(html_report))
        if test_output.exists():
            attachments.append(str(test_output))
        
        # 发送邮件
        return self.send(subject, body, attachments)
    
    def _build_test_report_body(self, test_results: dict, report_dir: str) -> str:
        """
        构建测试报告邮件正文
        
        Args:
            test_results: 测试结果字典
            report_dir: 报告目录路径
        
        Returns:
            str: HTML格式的邮件正文
        """
        total = test_results.get('total', 0)
        passed = test_results.get('passed', 0)
        failed = test_results.get('failed', 0)
        skipped = test_results.get('skipped', 0)
        errors = test_results.get('errors', 0)
        duration = test_results.get('duration', 0)
        pass_rate = test_results.get('pass_rate', 0)
        
        # 计算状态颜色
        status_color = '#28a745' if pass_rate >= 80 else '#ffc107' if pass_rate >= 60 else '#dc3545'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #007bff;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .summary {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .summary-item {{
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                }}
                .summary-label {{
                    font-weight: bold;
                    color: #666;
                }}
                .summary-value {{
                    font-size: 24px;
                    font-weight: bold;
                }}
                .passed {{ color: #28a745; }}
                .failed {{ color: #dc3545; }}
                .skipped {{ color: #ffc107; }}
                .errors {{ color: #fd7e14; }}
                .details {{
                    background-color: white;
                    padding: 20px;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .details h2 {{
                    margin-top: 0;
                    color: #007bff;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 30px;
                    background-color: #e9ecef;
                    border-radius: 15px;
                    overflow: hidden;
                    margin: 20px 0;
                }}
                .progress-fill {{
                    height: 100%;
                    background-color: {status_color};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 API自动化测试报告</h1>
                </div>
                
                <div class="summary">
                    <div class="summary-item">
                        <div class="summary-label">总测试数</div>
                        <div class="summary-value">{total}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">通过</div>
                        <div class="summary-value passed">{passed}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">失败</div>
                        <div class="summary-value failed">{failed}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">跳过</div>
                        <div class="summary-value skipped">{skipped}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">错误</div>
                        <div class="summary-value errors">{errors}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">通过率</div>
                        <div class="summary-value">{pass_rate:.1f}%</div>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate}%;">
                        {pass_rate:.1f}%
                    </div>
                </div>
                
                <div class="details">
                    <h2>📋 测试详情</h2>
                    <ul>
                        <li><strong>执行时间:</strong> {duration:.2f} 秒</li>
                        <li><strong>报告目录:</strong> {report_dir}</li>
                        <li><strong>测试时间:</strong> {test_results.get('timestamp', '')}</li>
                    </ul>
                </div>
                
                <div class="details">
                    <h2>📎 附件说明</h2>
                    <ul>
                        <li><strong>report.html:</strong> 完整的HTML测试报告</li>
                        <li><strong>test_output.txt:</strong> 测试输出日志</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>此邮件由测试报告系统自动发送</p>
                    <p>如有问题，请联系测试团队</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
