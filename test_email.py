#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试邮件发送功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tests.api_tests.utils.email_config import EmailConfig
from tests.api_tests.utils.email_sender import EmailSender


def test_email_config():
    """测试邮件配置"""
    print("=" * 60)
    print("测试邮件配置")
    print("=" * 60)
    
    # 打印配置状态
    EmailConfig.print_config_status()
    
    if not EmailConfig.is_configured():
        print("\n⚠️ 邮件配置不完整")
        print("\n请按照以下步骤配置邮件：")
        print("1. 复制 .env.example 为 .env")
        print("2. 编辑 .env 文件，填写实际的配置信息")
        print("3. 获取SMTP授权码（不是邮箱密码）")
        print("\n详细说明请参考 EMAIL_README.md")
        return False
    
    print("\n✅ 邮件配置完整")
    return True


def test_email_sender():
    """测试邮件发送器"""
    print("\n" + "=" * 60)
    print("测试邮件发送器")
    print("=" * 60)
    
    # 创建邮件发送器
    sender = EmailSender()
    
    # 发送测试邮件
    subject = "【测试邮件】测试报告系统邮件发送功能"
    body = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ 测试邮件</h1>
            </div>
            <div class="content">
                <p>这是一封测试邮件，用于验证测试报告系统的邮件发送功能。</p>
                <p>如果您收到这封邮件，说明邮件配置正确，系统可以正常发送测试报告。</p>
                <p><strong>测试时间：</strong> {timestamp}</p>
                <p>如有问题，请联系测试团队。</p>
            </div>
        </div>
    </body>
    </html>
    """.format(timestamp=sender.sender_name)
    
    print(f"\n正在发送测试邮件...")
    print(f"主题: {subject}")
    print(f"收件人: {', '.join(sender.recipients)}")
    
    success = sender.send(subject, body)
    
    if success:
        print("\n✅ 测试邮件发送成功！")
        print("请检查您的邮箱是否收到测试邮件。")
    else:
        print("\n❌ 测试邮件发送失败！")
        print("请检查邮件配置和网络连接。")
    
    return success


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("测试报告邮件系统 - 测试工具")
    print("=" * 60)
    
    # 测试配置
    config_ok = test_email_config()
    
    if not config_ok:
        print("\n❌ 配置测试失败，无法继续测试邮件发送")
        return 1
    
    # 测试发送
    send_ok = test_email_sender()
    
    if send_ok:
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 邮件发送测试失败")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
