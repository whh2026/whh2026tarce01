"""
API测试配置文件
"""
import os


class Config:
    """API测试配置类"""

    # 基础URL配置
    BASE_URL = os.getenv("API_BASE_URL", "http://192.168.0.183:30001")
    AUTH_URL = f"{BASE_URL}/api/v1/user-center/login"
    
    # 请求超时配置
    TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # 测试数据目录
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 测试配置
    RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))
    
    # 分页默认配置
    DEFAULT_PAGE_NUMBER = 1
    DEFAULT_PAGE_SIZE = 10
    
    # 用户认证配置（支持明文和哈希两种密码格式）
    DEFAULT_USERNAME = os.getenv("API_USERNAME", "admin")
    DEFAULT_PASSWORD = os.getenv("API_PASSWORD", "admin123")
    DEFAULT_PASS_HASH = os.getenv("API_PASS_HASH", "")  # 旧版哈希密码
    
    # 环境配置
    ENV = os.getenv("TEST_ENV", "dev")
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """
        获取完整的API URL
        
        Args:
            endpoint: API端点路径
            
        Returns:
            完整的API URL
        """
        return f"{cls.BASE_URL}{endpoint}"


# 创建配置实例
config = Config()
