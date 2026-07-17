import pytest
import requests
import json
import uuid
import os
import logging
import copy
from datetime import datetime, timedelta

from tests.api_tests.config.config import Config

# 配置日志
logger = logging.getLogger("APIBase")
logger.setLevel(logging.DEBUG if os.getenv("API_LOG_DEBUG") else logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)

# 使用Config类的配置
BASE_URL = Config.BASE_URL
AUTH_URL = Config.AUTH_URL
TIMEOUT = Config.TIMEOUT

# 测试数据文件路径 - 使用绝对路径以避免相对路径问题
TEST_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "api_test_data.json")


def _mask_sensitive(data, mask_keys=None):
    """脱敏敏感字段，用于日志输出"""
    if mask_keys is None:
        mask_keys = {"passHash", "password", "Authorization", "token", "captchaAnswer"}
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k in mask_keys:
                result[k] = "***MASKED***"
            elif isinstance(v, (dict, list)):
                result[k] = _mask_sensitive(v, mask_keys)
            else:
                result[k] = v
        return result
    elif isinstance(data, list):
        return [_mask_sensitive(item, mask_keys) for item in data]
    return data

class APIBase:
    """API测试基础类，包含认证和请求处理"""
    
    @classmethod
    def setup_class(cls):
        """类级别的设置，所有测试方法执行前只执行一次"""
        cls.session = requests.Session()
        cls.token = None
        cls.token_expiry = None
        cls.chain_address = None
        cls.chain_alias = None
        cls.space_id = None
        cls.uin = None
        
        # 执行登录操作获取token
        cls.login()
    
    @classmethod
    def teardown_class(cls):
        """类级别的清理，所有测试方法执行后只执行一次"""
        if hasattr(cls, 'session') and cls.session:
            cls.session.close()
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        # 检查token是否有效，如果无效则重新登录
        if not self.token or self.__class__._is_token_expired():
            logger.info("Token无效或已过期，重新登录...")
            self.__class__.login()

    @classmethod
    def _is_token_expired(cls):
        """检查token是否已过期"""
        if not cls.token_expiry:
            return True
        return datetime.now() > cls.token_expiry
    
    def get_test_case_data(self, test_case_name, file_name=None):
        """
        根据测试用例名从测试数据中获取对应的测试用例信息
        
        Args:
            test_case_name (str): 测试用例名称
            file_name (str, optional): 测试数据文件名，如果不提供则使用类名加上_data.json
            
        Returns:
            dict: 测试用例信息，包含test_case_name、test_case_desc和test_case_data字段
        """
        import os
        import json
        
        # 如果未提供文件名，则使用当前测试类名加上_data.json
        if not file_name:
            # 获取当前测试类名
            class_name = self.__class__.__name__
            # 如果类名以Test开头，则去掉Test前缀
            if class_name.startswith('Test'):
                class_name = class_name[4:]
            # 将驼峰命名转换为蛇形命名
            snake_case_name = ''
            for i, char in enumerate(class_name):
                if i > 0 and char.isupper():
                    snake_case_name += '_'
                snake_case_name += char.lower()
            file_name = f"{snake_case_name}_data.json"
        
        # 构建测试数据文件路径 - 支持新的目录结构
        base_dir = os.path.dirname(__file__)
        
        # 尝试多个可能的路径
        possible_paths = [
            # 新的目录结构: data/{module}/{file_name}
            os.path.join(base_dir, 'data', snake_case_name.lower(), file_name),
            # 旧的目录结构: data/{file_name}
            os.path.join(base_dir, 'data', file_name),
        ]
        
        data_file = None
        for path in possible_paths:
            if os.path.exists(path):
                data_file = path
                break
        
        if not data_file:
            print(f"[警告] 测试数据文件未找到，尝试的路径: {possible_paths}")
            return {
                'test_case_name': test_case_name,
                'test_case_desc': f'{test_case_name}测试',
                'test_case_data': {}
            }
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[警告] 测试数据文件 {data_file} 格式错误: {e}")
            return {
                'test_case_name': test_case_name,
                'test_case_desc': f'{test_case_name}测试',
                'test_case_data': {}
            }
        
        # 直接通过测试用例名作为键获取测试数据
        test_case = test_data.get(test_case_name, {})
        
        # 如果找到测试用例数据，确保返回包含test_case_name的完整结构
        if test_case:
            return {
                'test_case_name': test_case_name,
                **test_case
            }
        
        # 如果未找到匹配的测试用例，返回默认值
        return {
            'test_case_name': test_case_name,
            'test_case_desc': f'{test_case_name}测试',
            'test_case_data': {}
        }
    
    @classmethod
    def login(cls):
        """登录方法，获取并存储token"""
        # 从环境变量读取凭据，支持 password(明文) 和 passHash(哈希) 两种模式
        username = os.getenv("API_USERNAME", Config.DEFAULT_USERNAME)
        plain_pw = os.getenv("API_PASSWORD", Config.DEFAULT_PASSWORD)
        hash_pw = os.getenv("API_PASS_HASH", "")
        has_plain = bool(plain_pw and plain_pw != "admin123")
        has_hash = bool(hash_pw)
        # 优先用明文，其次用哈希
        auth_key, auth_val = ("password", plain_pw) if has_plain else ("passHash", hash_pw) if has_hash else ("password", plain_pw)
        
        captchaAnswer = os.getenv("API_CAPTCHA_ANSWER", "987423")
        captchaId = None
        
        # 尝试获取captchaId
        captcha_url = f"{BASE_URL}/api/v1/user-center/captcha"
        logger.info("获取验证码: %s", captcha_url)
        
        try:
            captcha_response = cls.session.get(captcha_url, timeout=TIMEOUT)
            captcha_response.raise_for_status()
            captcha_data = captcha_response.json()
            captchaId = (captcha_data.get("data") or {}).get("captchaId")
            if captchaId:
                logger.info("验证码ID: %s", captchaId)
            else:
                logger.warning("未获取到captchaId，使用默认值")
                captchaId = "4CzuJqTEJceMbumDr1tE"
        except Exception as e:
            logger.warning("获取验证码失败: %s，使用默认值", e)
            captchaId = "4CzuJqTEJceMbumDr1tE"
        
        # 发送登录请求
        login_data = {
            "userName": username,
            auth_key: auth_val,
            "captchaAnswer": captchaAnswer,
            "captchaId": captchaId
        }
        
        logger.info("登录请求: %s", AUTH_URL)
        logger.debug("登录参数: %s", _mask_sensitive(login_data))
        
        response = cls.session.post(AUTH_URL, json=login_data, timeout=TIMEOUT)
        response.raise_for_status()
        
        response_data = response.json()
        logger.debug("登录响应: %s", json.dumps(_mask_sensitive(response_data), ensure_ascii=False)[:500])
        
        # 尝试从不同字段获取token
        data = response_data.get("data") or {}
        cls.token = response_data.get("token") or (data.get("token") if isinstance(data, dict) else None)
        cls.uin = response_data.get("uin") or (data.get("uin") if isinstance(data, dict) else None)
        
        logger.info("登录成功, token: ***%s", cls.token[-8:] if cls.token and len(cls.token) > 8 else "N/A")
        
        if not cls.token:
            raise ValueError("登录失败：未获取到token")
        
        # 设置token过期时间（假设token有效期为1小时）
        cls.token_expiry = datetime.now() + timedelta(hours=1)
        
        cls.session.headers.update({
            "Content-Type": "application/json"
        })
        
        # 登录成功后获取用户信息（包括address和sid）
        cls.get_user_info()
    
    @classmethod
    def get_user_info(cls, uin=None):
        """获取用户信息接口（classmethod，使用cls.session直接请求）"""
        url = f"{BASE_URL}/api/v1/user-center/get-user"
        user_uin = uin if uin is not None else cls.uin
        json_data = {"uin": user_uin}
        
        request_headers = {
            "Authorization": f"Bearer {cls.token}",
            "Content-Type": "application/json"
        }
        
        response = cls.session.post(url, json=json_data, headers=request_headers, timeout=TIMEOUT)
        response_data = response.json()
        
        # 存储响应中的address、alias、sid到类属性
        if response_data and isinstance(response_data, dict):
            data = response_data.get("data") or {}
            
            cls.chain_address = data.get("address") or response_data.get("address")
            cls.chain_alias = data.get("alias") or response_data.get("alias")
            cls.space_id = data.get("sid") or response_data.get("sid")
            
            # 如果直接获取失败，尝试从userSpaceInfo数组中获取
            if not cls.chain_address or not cls.chain_alias or not cls.space_id:
                user_space_info = data.get("userSpaceInfo", [])
                if user_space_info and isinstance(user_space_info, list) and len(user_space_info) > 0:
                    space_info = user_space_info[0]
                    cls.chain_address = space_info.get("address")
                    cls.chain_alias = space_info.get("alias")
                    cls.space_id = space_info.get("sid")
        
        return response_data
    
    def get(self, url, params=None, headers=None):
        """发送GET请求"""
        return self._send_request("GET", url, params=params, headers=headers)
    
    def post(self, url, json_data=None, json=None, data=None, headers=None):
        """发送POST请求"""
        # 支持两种参数名，保持向后兼容性
        if json is not None:
            json_data = json
        return self._send_request("POST", url, json_data=json_data, data=data, headers=headers)
    
    def put(self, url, json_data=None, json=None, data=None, headers=None):
        """发送PUT请求"""
        # 支持两种参数名，保持向后兼容性
        if json is not None:
            json_data = json
        return self._send_request("PUT", url, json_data=json_data, data=data, headers=headers)
    
    def delete(self, url, headers=None):
        """发送DELETE请求"""
        return self._send_request("DELETE", url, headers=headers)
    
    def _send_request(self, method, url, params=None, json_data=None, data=None, headers=None):
        """发送请求的底层方法"""
        # 确保URL是完整的
        if not url.startswith("http"):
            url = f"{BASE_URL}{url}"
        
        # 合并请求头
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # 只在有token时添加Authorization头
        if self.token:
            request_headers["Authorization"] = f"{self.token}"
        
        # 添加x-request-id头（36位UUID）
        request_headers["x-request-id"] = str(uuid.uuid4())
        
        # 添加User-Agent头
        request_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
        
        # 添加Content-Type头
        request_headers["Content-Type"] = "application/json"
        
        # 检查当前请求是否是login或get-user接口，如果是则跳过添加x-chain相关头
        skip_chain_headers = False
        if url.endswith("/api/v1/user-center/login") or url.endswith("/api/v1/user-center/get-user"):
            skip_chain_headers = True
        
        # 添加x-chain相关请求头（除了login和get-user接口）
        if not skip_chain_headers:
            if self.chain_address:
                request_headers["x-chain-address"] = self.chain_address
            if self.chain_alias:
                request_headers["x-chain-alias"] = self.chain_alias
            if self.space_id:
                request_headers["x-space-id"] = self.space_id
        
        logger.debug("[%s] %s", method, url)
        if params:
            logger.debug("  params: %s", params)
        if json_data:
            logger.debug("  body: %s", _mask_sensitive(json_data))
        
        # 发送请求
        response = self.session.request(
            method, url, params=params, json=json_data, data=data, headers=request_headers, timeout=TIMEOUT
        )
        
        try:
            response_json = response.json()
            return response_json
        except json.JSONDecodeError:
            raise ValueError(f"API返回非JSON响应 (status={response.status_code}): {response.text[:200]}")
    
    def assert_response_success(self, response, expected_status_code=200):
        """断言响应成功"""
        if isinstance(response, dict):
            # 如果响应是JSON对象
            assert "code" in response, "响应中缺少code字段"
            assert response["code"] == expected_status_code, f"响应状态码错误，预期{expected_status_code}，实际{response['code']}"
            assert response.get("success", True), "响应success字段为false"
        else:
            # 如果响应是字符串，尝试解析
            try:
                response_json = json.loads(response)
                self.assert_response_success(response_json, expected_status_code)
            except json.JSONDecodeError:
                # 如果无法解析为JSON，检查是否是简单的成功响应
                assert "success" in response.lower() or "ok" in response.lower(), f"响应不是预期的成功格式: {response}"
    
    def assert_response_data(self, response, expected_data):
        """断言响应数据包含预期内容"""
        if isinstance(response, dict):
            for key, value in expected_data.items():
                assert key in response, f"响应中缺少字段: {key}"
                assert response[key] == value, f"字段{key}值错误，预期{value}，实际{response[key]}"
        else:
            # 如果响应是字符串，检查是否包含预期内容
            for value in expected_data:
                assert value in response, f"响应中缺少内容: {value}"
    
    def generate_test_data(self, prefix="test", length=10):
        """生成测试数据"""
        import random
        import string
        
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{prefix}_{suffix}"
    
    def get_current_timestamp(self, format="%Y-%m-%d %H:%M:%S"):
        """获取当前时间戳"""
        return datetime.now().strftime(format)
