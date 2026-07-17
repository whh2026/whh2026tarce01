"""
API测试fixtures
提供可复用的测试fixtures
"""
import pytest
import requests
from typing import Generator, Dict, Any, Optional
from datetime import datetime, timedelta

from tests.api_tests.config.config import config


@pytest.fixture(scope="session")
def api_base():
    """
    API基础类fixture
    提供基础的API测试功能
    
    Yields:
        APIBase实例
    """
    class APIBase:
        def __init__(self):
            self.session = requests.Session()
            self.token = None
            self.token_expiry = None
            self.chain_address = None
            self.chain_alias = None
            self.space_id = None
            self.uin = None
        
        def login(self, username: Optional[str] = None, password: Optional[str] = None):
            """
            执行登录操作
            
            Args:
                username: 用户名
                password: 密码
            """
            login_data = {
                "username": username or config.DEFAULT_USERNAME,
                "password": password or config.DEFAULT_PASSWORD
            }
            
            response = self.session.post(
                config.AUTH_URL,
                json=login_data,
                timeout=config.TIMEOUT
            )
            
            assert response.status_code == 200, f"登录失败: {response.text}"
            
            token_data = response.json()
            assert "data" in token_data, "登录响应中缺少data字段"
            assert "token" in token_data["data"], "登录响应中缺少token字段"
            
            self.token = token_data["data"]["token"]
            # 设置token过期时间（假设token有效期为2小时）
            self.token_expiry = datetime.now() + timedelta(hours=2)
            
            # 获取链信息（这里需要根据实际API调整）
            self._fetch_chain_info()
        
        def _fetch_chain_info(self):
            """
            获取链信息
            需要根据实际API实现
            """
            # 这里需要根据实际的API来获取链信息
            # 暂时设置为None，需要根据实际情况调整
            pass
        
        def post(self, endpoint: str, json: Dict[str, Any] = None, **kwargs):
            """
            发送POST请求
            
            Args:
                endpoint: API端点
                json: 请求体数据
                **kwargs: 其他请求参数
                
            Returns:
                响应JSON数据
            """
            url = config.get_api_url(endpoint)
            headers = kwargs.pop('headers', {})
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            headers.setdefault("Content-Type", "application/json")
            
            response = self.session.post(
                url,
                json=json,
                headers=headers,
                timeout=config.TIMEOUT,
                **kwargs
            )
            
            return response.json()
        
        def get(self, endpoint: str, params: Dict[str, Any] = None, **kwargs):
            """
            发送GET请求
            
            Args:
                endpoint: API端点
                params: 查询参数
                **kwargs: 其他请求参数
                
            Returns:
                响应JSON数据
            """
            url = config.get_api_url(endpoint)
            headers = kwargs.pop('headers', {})
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=config.TIMEOUT,
                **kwargs
            )
            
            return response.json()
        
        def assert_response_success(self, response: Dict[str, Any], expected_code: int = 200):
            """
            断言响应成功
            
            Args:
                response: 响应数据
                expected_code: 期望的状态码
            """
            assert "code" in response, "响应中缺少code字段"
            assert "msg" in response, "响应中缺少msg字段"
            assert response["code"] == expected_code, f"期望状态码 {expected_code}，实际得到 {response['code']}: {response['msg']}"
        
        def is_token_expired(self) -> bool:
            """
            检查token是否已过期
            
            Returns:
                True如果token已过期，否则False
            """
            if not self.token_expiry:
                return True
            return datetime.now() > self.token_expiry
    
    base = APIBase()
    base.login()
    yield base
    base.session.close()


@pytest.fixture(scope="function")
def authenticated_request(api_base):
    """
    认证请求fixture
    提供已认证的请求方法
    
    Args:
        api_base: API基础类实例
        
    Yields:
        认证请求对象
    """
    class AuthenticatedRequest:
        def __init__(self, base):
            self.base = base
        
        def post(self, endpoint: str, json: Dict[str, Any] = None):
            """发送POST请求"""
            return self.base.post(endpoint, json=json)
        
        def get(self, endpoint: str, params: Dict[str, Any] = None):
            """发送GET请求"""
            return self.base.get(endpoint, params=params)
    
    yield AuthenticatedRequest(api_base)


@pytest.fixture(scope="function")
def product_test_data(api_base):
    """
    产品测试数据fixture
    提供产品测试相关的数据和方法
    
    Args:
        api_base: API基础类实例
        
    Yields:
        产品测试数据对象
    """
    class ProductTestData:
        def __init__(self, base):
            self.base = base
        
        def get_first_product_id(self) -> Optional[str]:
            """
            获取第一个产品的ID
            
            Returns:
                产品ID，如果没有产品则返回None
            """
            response = self.base.post("/api/v1/dpm-core-service/listProducts", json={
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 1
                },
                "sid": self.base.space_id,
                "address": self.base.chain_address,
                "filters": []
            })
            
            if response.get("code") == 200 and response.get("data", {}).get("list"):
                return response["data"]["list"][0].get("id")
            
            return None
        
        def get_first_product(self) -> Optional[Dict[str, Any]]:
            """
            获取第一个产品的完整信息
            
            Returns:
                产品信息字典，如果没有产品则返回None
            """
            response = self.base.post("/api/v1/dpm-core-service/listProducts", json={
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 1
                },
                "sid": self.base.space_id,
                "address": self.base.chain_address,
                "filters": []
            })
            
            if response.get("code") == 200 and response.get("data", {}).get("list"):
                return response["data"]["list"][0]
            
            return None
    
    yield ProductTestData(api_base)


@pytest.fixture(scope="function")
def test_context(api_base):
    """
    测试上下文fixture
    提供测试执行过程中的上下文信息
    
    Args:
        api_base: API基础类实例
        
    Yields:
        测试上下文对象
    """
    class TestContext:
        def __init__(self, base):
            self.base = base
            self.test_data = {}
            self.cleanup_actions = []
        
        def set_data(self, key: str, value: Any):
            """
            设置测试数据
            
            Args:
                key: 数据键
                value: 数据值
            """
            self.test_data[key] = value
        
        def get_data(self, key: str, default: Any = None) -> Any:
            """
            获取测试数据
            
            Args:
                key: 数据键
                default: 默认值
                
            Returns:
                数据值
            """
            return self.test_data.get(key, default)
        
        def add_cleanup(self, action):
            """
            添加清理操作
            
            Args:
                action: 清理函数
            """
            self.cleanup_actions.append(action)
        
        def cleanup(self):
            """执行所有清理操作"""
            for action in reversed(self.cleanup_actions):
                try:
                    action()
                except Exception as e:
                    print(f"清理操作执行失败: {e}")
            self.cleanup_actions.clear()
    
    context = TestContext(api_base)
    yield context
    context.cleanup()
