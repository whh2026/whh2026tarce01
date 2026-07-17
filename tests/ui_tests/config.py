"""
UI测试配置文件
"""
import os


class UIConfig:
    """UI测试配置类"""

    # 用户IP映射配置
    USER_IPS = {
        1: os.getenv("UI_USER_1_IP", "192.168.0.183:30001"),
        2: os.getenv("UI_USER_2_IP", "192.168.0.185:30001")
    }
    
    # 默认用户ID
    DEFAULT_USER_ID = int(os.getenv("UI_DEFAULT_USER_ID", "1"))
    
    # 等待时间配置
    DEFAULT_TIMEOUT = int(os.getenv("UI_DEFAULT_TIMEOUT", "30000"))
    SHORT_TIMEOUT = int(os.getenv("UI_SHORT_TIMEOUT", "5000"))
    
    # 截图目录
    SCREENSHOT_DIR = os.getenv("UI_SCREENSHOT_DIR", "reports/screenshots")
    
    @classmethod
    def get_user_config(cls, user_id: int = None) -> dict:
        """
        获取用户配置
        
        Args:
            user_id: 用户ID，默认使用默认用户
            
        Returns:
            用户配置字典
        """
        if user_id is None:
            user_id = cls.DEFAULT_USER_ID
        return cls.USER_IPS
    
    @classmethod
    def get_user_url(cls, user_id: int = None) -> str:
        """
        获取用户URL
        
        Args:
            user_id: 用户ID，默认使用默认用户
            
        Returns:
            用户URL字符串
        """
        if user_id is None:
            user_id = cls.DEFAULT_USER_ID
        return cls.USER_IPS.get(user_id, cls.USER_IPS[1])


# 创建配置实例
ui_config = UIConfig()
