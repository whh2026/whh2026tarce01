# -*- coding: utf-8 -*-
"""
邮件发送配置
"""

import os
from typing import List

class EmailConfig:
    """邮件配置类"""
    
    # SMTP服务器配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    # 发件人配置
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')
    SENDER_NAME = os.getenv('SENDER_NAME', '测试报告系统')
    
    # 收件人配置
    RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '')
    
    @classmethod
    def get_recipients(cls) -> List[str]:
        """获取收件人列表"""
        recipients_str = cls.RECIPIENT_EMAILS
        if not recipients_str:
            return []
        
        # 支持逗号或分号分隔的多个邮箱
        recipients = [email.strip() for email in recipients_str.replace(';', ',').split(',')]
        return [email for email in recipients if email]
    
    @classmethod
    def is_configured(cls) -> bool:
        """检查邮件配置是否完整"""
        if not cls.SENDER_EMAIL:
            return False
        if not cls.SENDER_PASSWORD:
            return False
        if not cls.get_recipients():
            return False
        return True
    
    @classmethod
    def print_config_status(cls):
        """打印配置状态"""
        print("=" * 60)
        print("邮件配置状态")
        print("=" * 60)
        print(f"SMTP服务器: {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
        print(f"使用TLS: {cls.SMTP_USE_TLS}")
        print(f"发件人: {cls.SENDER_NAME} <{cls.SENDER_EMAIL}>")
        print(f"收件人: {', '.join(cls.get_recipients())}")
        print(f"配置完整: {'✅ 是' if cls.is_configured() else '❌ 否'}")
        print("=" * 60)
