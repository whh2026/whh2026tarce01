"""
Pytest配置文件
定义全局fixtures和测试配置
"""
import pytest
import requests
from datetime import datetime, timedelta
from typing import Generator

from tests.api_tests.config.config import config
from tests.api_tests.utils.data_loader import data_loader
from tests.api_tests.utils.assertions import assertions


@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    """
    创建API会话fixture（session级别）
    
    Yields:
        requests.Session对象
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def auth_token(api_session: requests.Session) -> str:
    """
    获取认证token fixture（session级别）
    
    Args:
        api_session: API会话对象
        
    Returns:
        认证token字符串
    """
    login_data = {
        "username": config.DEFAULT_USERNAME,
        "password": config.DEFAULT_PASSWORD
    }
    
    response = api_session.post(
        config.AUTH_URL,
        json=login_data,
        timeout=config.TIMEOUT
    )
    
    assert response.status_code == 200, f"登录失败: {response.text}"
    
    token_data = response.json()
    assert "data" in token_data, "登录响应中缺少data字段"
    assert "token" in token_data["data"], "登录响应中缺少token字段"
    
    return token_data["data"]["token"]


@pytest.fixture(scope="session")
def chain_info(api_session: requests.Session, auth_token: str) -> dict:
    """
    获取链信息fixture（session级别）
    
    Args:
        api_session: API会话对象
        auth_token: 认证token
        
    Returns:
        包含链信息的字典
    """
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    
    # 这里需要根据实际的API来获取链信息
    # 暂时返回空字典，需要根据实际情况调整
    return {
        "chain_address": None,
        "chain_alias": None,
        "space_id": None,
        "uin": None
    }


@pytest.fixture(scope="function")
def authenticated_headers(auth_token: str) -> dict:
    """
    获取认证请求头fixture（function级别）
    
    Args:
        auth_token: 认证token
        
    Returns:
        包含认证信息的请求头字典
    """
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture(scope="function")
def api_client(api_session: requests.Session, auth_token: str):
    """
    创建API客户端fixture（function级别）
    
    Args:
        api_session: API会话对象
        auth_token: 认证token
        
    Yields:
        API客户端对象
    """
    class APIClient:
        def __init__(self, session: requests.Session, token: str):
            self.session = session
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        
        def get(self, endpoint: str, params: dict = None, **kwargs):
            """发送GET请求"""
            url = config.get_api_url(endpoint)
            return self.session.get(url, params=params, headers=self.headers, timeout=config.TIMEOUT, **kwargs)
        
        def post(self, endpoint: str, json: dict = None, data: dict = None, **kwargs):
            """发送POST请求"""
            url = config.get_api_url(endpoint)
            return self.session.post(url, json=json, data=data, headers=self.headers, timeout=config.TIMEOUT, **kwargs)
        
        def put(self, endpoint: str, json: dict = None, data: dict = None, **kwargs):
            """发送PUT请求"""
            url = config.get_api_url(endpoint)
            return self.session.put(url, json=json, data=data, headers=self.headers, timeout=config.TIMEOUT, **kwargs)
        
        def delete(self, endpoint: str, **kwargs):
            """发送DELETE请求"""
            url = config.get_api_url(endpoint)
            return self.session.delete(url, headers=self.headers, timeout=config.TIMEOUT, **kwargs)
    
    yield APIClient(api_session, auth_token)


@pytest.fixture(scope="function")
def test_data():
    """
    测试数据fixture（function级别）
    
    Returns:
        数据加载器实例
    """
    return data_loader


@pytest.fixture(scope="function")
def test_assertions():
    """
    断言工具fixture（function级别）
    
    Returns:
        断言工具实例
    """
    return assertions


@pytest.fixture(scope="function")
def base_params(chain_info: dict) -> dict:
    """
    基础请求参数fixture（function级别）
    
    Args:
        chain_info: 链信息
        
    Returns:
        包含基础参数的字典
    """
    return {
        "address": chain_info.get("chain_address"),
        "sid": chain_info.get("space_id")
    }


@pytest.fixture(scope="function")
def pagination_params(page_number: int = 1, page_size: int = 10) -> dict:
    """
    分页参数fixture（function级别）
    
    Args:
        page_number: 页码
        page_size: 每页数量
        
    Returns:
        包含分页参数的字典
    """
    return {
        "paginationReq": {
            "pageNumber": page_number,
            "pageSize": page_size
        }
    }


def pytest_configure(config):
    """
    Pytest配置钩子
    
    Args:
        config: pytest配置对象
    """
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试标记"
    )
    config.addinivalue_line(
        "markers", "regression: 回归测试标记"
    )
    config.addinivalue_line(
        "markers", "api: API测试标记"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改测试项的钩子，可以自动添加标记或排序
    
    Args:
        config: pytest配置对象
        items: 测试项列表
    """
    for item in items:
        # 为所有API测试自动添加api标记
        if "api_tests" in str(item.fspath):
            item.add_marker(pytest.mark.api)
