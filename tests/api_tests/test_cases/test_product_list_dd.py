"""
产品列表API测试 - 数据驱动模式
"""
import pytest
import json
from tests.api_tests.base import APIBase
from tests.api_tests.utils.data_loader import data_loader
from tests.api_tests.utils.assertions import assertions


class TestProductList(APIBase):
    """产品列表接口测试类 - 数据驱动模式"""
    
    # 注意：这个类继承APIBase，setup_class会自动执行登录操作
    # 不再覆盖setup_class，使用父类的登录逻辑
    
    def test_01_list_products_with_custom_params(self):
        """[测试用例01] 测试使用自定义参数调用listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 用户提供的自定义请求参数
        request_data = {
            "paginationReq": {
                "pageNumber": 1,
                "pageSize": 10
            },
            "sid": self.space_id,
            "address": self.chain_address,
            "filters": []
        }
        
        print("\n=== [测试用例01] 测试listProducts接口（自定义参数） ===")
        print("[测试] 请求数据:")
        print(json.dumps(request_data, ensure_ascii=False, indent=2))
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        print("\n[测试] 返回数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        # 使用断言工具验证响应
        assertions.assert_response_success(response)
        
        if response["code"] == 200:
            assertions.assert_data_structure(response["data"], ["list"])
            assertions.assert_list_field(response["data"], "list")
            
            # 验证分页信息
            if "total" in response["data"]:
                assertions.assert_int_field(response["data"], "total")
            
            assertions.assert_pagination(response, 
                                    expected_page_number=request_data["paginationReq"]["pageNumber"],
                                    expected_page_size=request_data["paginationReq"]["pageSize"])
            
            print(f"\n[测试] 测试通过！成功获取{len(response['data']['list'])}个产品")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_02_list_products_with_empty_filters(self):
        """[测试用例02] 测试使用空filters调用listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        request_data = {
            "paginationReq": {
                "pageNumber": 1,
                "pageSize": 10
            },
            "sid": self.space_id,
            "address": self.chain_address,
            "filters": []
        }
        
        print("\n=== [测试用例02] 测试listProducts接口（空filters） ===")
        response = self.post(url, json=request_data)
        
        print("\n[测试] 返回数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        assertions.assert_response_structure(response, ["code", "msg"])
        print(f"\n[测试] 空filters测试 - 状态码: {response['code']}, 消息: {response['msg']}")
    
    @pytest.mark.parametrize("page_size", [5, 20, 50])
    def test_03_list_products_different_page_size(self, page_size):
        """[测试用例03] 测试不同pageSize参数"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        request_data = {
            "paginationReq": {
                "pageNumber": 1,
                "pageSize": page_size
            },
            "sid": self.space_id,
            "address": self.chain_address,
            "filters": []
        }
        
        print(f"\n=== [测试用例03] 测试listProducts接口（pageSize={page_size}） ===")
        response = self.post(url, json=request_data)
        
        print("\n[测试] 返回数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        assertions.assert_response_structure(response, ["code", "msg"])
        
        if response["code"] == 200:
            assertions.assert_data_structure(response["data"], ["list"])
            assertions.assert_list_field(response["data"], "list")
            print(f"\n[测试] pageSize={page_size} 测试通过！")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
