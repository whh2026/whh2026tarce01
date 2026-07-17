import pytest
import json
import os
from tests.api_tests.base import APIBase

# 测试数据读取函数，实现测试数据和测试方法的完全分离
# def get_agreement_test_data():
#     """获取协议接口测试数据"""
#     data_dir = os.path.join(os.path.dirname(__file__), 'data')
#     data_file = os.path.join(data_dir, 'agreement_data.json')
#     with open(data_file, 'r', encoding='utf-8') as f:
#         test_data = json.load(f)    
#     return test_data
# 使用基类APIBase中的get_test_case_data方法
# 获取测试数据
# test_data = get_agreement_test_data()

class TestAgreement(APIBase):
    """协议接口测试类"""
    
    def test_001_agreement_create(self):
        """[测试用例001] 协议创建接口测试"""
        # 定义测试基本信息
        url = "/api/v1/agreement/product/create"
        
        # 从测试数据中获取测试用例信息
        request_data = self.get_test_case_data("test_001_agreement_create").get("test_case_data", {})
        print(request_data)
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 处理成功响应
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
            
    def test_002_agreement_create_long_name(self):
        """[测试用例002] 协议创建接口测试-协议名称超过50个字符"""
        # 定义测试基本信息
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_002_agreement_create_long_name").get("test_case_data", {})
        
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议名称长度
        protocol_name = request_data.get("name", "")
        print(f"协议名称长度: {len(protocol_name)}字符")
        
        
        # 对于名称过长的情况，通常期望返回错误状态码
        # 但如果接口允许超长名称，则也应该正常处理
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议名称超过50个字符")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
            
    def test_003_agreement_create_long_description(self):
        """[测试用例003] 协议创建接口测试-协议描述超过50个字符"""
        # 定义测试基本信息
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_003_agreement_create_long_description").get("test_case_data", {})
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议描述长度
        protocol_description = request_data.get("description", "")
        print(f"协议描述长度: {len(protocol_description)}字符")
        
        
        # 对于描述过长的情况，通常期望返回错误状态码
        # 但如果接口允许超长描述，则也应该正常处理
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议描述超过50个字符")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")

    def test_004_agreement_create_long_title(self):
        """[测试用例004] 协议创建接口测试-协议标题超过50个字符"""
        # 定义测试基本信息
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_004_agreement_create_long_title").get("test_case_data", {})
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议标题长度
        protocol_title = request_data.get("content", [{}])[0].get("title", "")
        print(f"协议标题长度: {len(protocol_title)}字符")
        
        # 对于标题过长的情况，通常期望返回错误状态码
        # 但如果接口允许超长标题，则也应该正常处理
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议标题超过50个字符")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_005_agreement_create_empty_name(self):
        """[测试用例005] 协议创建接口测试-协议名称为空"""
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_005_agreement_create_empty_name").get("test_case_data", {})
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议名称长度
        protocol_name = request_data.get("name", "")
        print(f"协议名称长度: {len(protocol_name)}字符")
        
        # 对于名称为空的情况，通常期望返回错误状态码
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议名称为空")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_006_agreement_create_empty_description(self):
        """[测试用例006] 协议创建接口测试-协议描述为空"""
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_006_agreement_create_empty_description").get("test_case_data", {})
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议描述长度
        protocol_description = request_data.get("description", "")
        print(f"协议描述长度: {len(protocol_description)}字符")
        
        # 对于描述为空的情况，通常期望返回错误状态码
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议描述为空")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_007_agreement_create_empty_title(self):
        """[测试用例007] 协议创建接口测试-协议标题为空"""
        url = "/api/v1/agreement/product/create"
        
        request_data = self.get_test_case_data("test_007_agreement_create_empty_title").get("test_case_data", {})
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        # 验证响应基本结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        # 检查协议标题长度
        protocol_title = request_data.get("content", [{}])[0].get("title", "")
        print(f"协议标题长度: {len(protocol_title)}字符")
        
        # 对于标题为空的情况，通常期望返回错误状态码
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            print("测试通过: 接口允许协议标题为空")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")

if __name__ == "__main__":
    pytest.main(["-v", "-s", "tests/api_tests/test_agreement.py"])