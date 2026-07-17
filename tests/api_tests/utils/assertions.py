"""
断言工具类
提供常用的断言方法
"""
from typing import Any, Dict, List, Optional


class Assertions:
    """断言工具类"""

    @staticmethod
    def assert_response_success(response: Dict[str, Any], expected_code: int = 200):
        """
        断言响应成功
        
        Args:
            response: 响应数据
            expected_code: 期望的状态码，默认为 200
        """
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        assert response["code"] == expected_code, f"期望状态码 {expected_code}，实际得到 {response['code']}: {response['msg']}"

    @staticmethod
    def assert_response_structure(response: Dict[str, Any], required_fields: List[str]):
        """
        断言响应包含指定的字段
        
        Args:
            response: 响应数据
            required_fields: 必需的字段列表
        """
        for field in required_fields:
            assert field in response, f"响应中缺少必需字段: {field}"

    @staticmethod
    def assert_data_structure(data: Dict[str, Any], required_fields: List[str]):
        """
        断言数据包含指定的字段
        
        Args:
            data: 数据字典
            required_fields: 必需的字段列表
        """
        for field in required_fields:
            assert field in data, f"数据中缺少必需字段: {field}"

    @staticmethod
    def assert_list_field(data: Dict[str, Any], field_name: str):
        """
        断言指定字段是列表类型
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert isinstance(data[field_name], list), f"字段 '{field_name}' 不是列表类型"

    @staticmethod
    def assert_dict_field(data: Dict[str, Any], field_name: str):
        """
        断言指定字段是字典类型
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert isinstance(data[field_name], dict), f"字段 '{field_name}' 不是字典类型"

    @staticmethod
    def assert_int_field(data: Dict[str, Any], field_name: str):
        """
        断言指定字段是整数类型
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert isinstance(data[field_name], int), f"字段 '{field_name}' 不是整数类型"

    @staticmethod
    def assert_str_field(data: Dict[str, Any], field_name: str):
        """
        断言指定字段是字符串类型
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert isinstance(data[field_name], str), f"字段 '{field_name}' 不是字符串类型"

    @staticmethod
    def assert_field_value(data: Dict[str, Any], field_name: str, expected_value: Any):
        """
        断言指定字段的值等于期望值
        
        Args:
            data: 数据字典
            field_name: 字段名
            expected_value: 期望的值
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert data[field_name] == expected_value, f"字段 '{field_name}' 的值 '{data[field_name]}' 不等于期望值 '{expected_value}'"

    @staticmethod
    def assert_field_not_empty(data: Dict[str, Any], field_name: str):
        """
        断言指定字段不为空
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert data[field_name] is not None, f"字段 '{field_name}' 的值为 None"
        if isinstance(data[field_name], (str, list, dict)):
            assert len(data[field_name]) > 0, f"字段 '{field_name}' 的值为空"

    @staticmethod
    def assert_pagination(response: Dict[str, Any], expected_page_number: Optional[int] = None, expected_page_size: Optional[int] = None):
        """
        断言分页信息
        
        Args:
            response: 响应数据
            expected_page_number: 期望的页码
            expected_page_size: 期望的每页数量
        """
        assert "data" in response, "响应中缺少data字段"
        
        if expected_page_number is not None and "pageNumber" in response["data"]:
            assert response["data"]["pageNumber"] == expected_page_number, f"返回的pageNumber {response['data']['pageNumber']} 不等于期望值 {expected_page_number}"
        
        if expected_page_size is not None and "pageSize" in response["data"]:
            assert response["data"]["pageSize"] == expected_page_size, f"返回的pageSize {response['data']['pageSize']} 不等于期望值 {expected_page_size}"

    @staticmethod
    def assert_list_not_empty(data: Dict[str, Any], field_name: str):
        """
        断言列表字段不为空
        
        Args:
            data: 数据字典
            field_name: 字段名
        """
        assert field_name in data, f"数据中缺少字段: {field_name}"
        assert isinstance(data[field_name], list), f"字段 '{field_name}' 不是列表类型"
        assert len(data[field_name]) > 0, f"字段 '{field_name}' 的列表为空"


# 创建全局断言工具实例
assertions = Assertions()
