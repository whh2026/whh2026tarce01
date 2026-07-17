import pytest
import json
from tests.api_tests.base import APIBase

class TestProductList(APIBase):
    """产品列表接口测试类"""
    
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
        
        # 验证返回数据结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            assert "list" in response["data"], "data中缺少list字段"
            assert isinstance(response["data"]["list"], list), "list字段不是数组类型"
            
            # 验证分页信息
            if "total" in response["data"]:
                assert isinstance(response["data"]["total"], int), "total字段不是整数类型"
            if "pageNumber" in response["data"]:
                assert response["data"]["pageNumber"] == request_data["paginationReq"]["pageNumber"], "返回的pageNumber与请求不符"
            if "pageSize" in response["data"]:
                assert response["data"]["pageSize"] == request_data["paginationReq"]["pageSize"], "返回的pageSize与请求不符"
            
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
        
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        print(f"\n[测试] 空filters测试 - 状态码: {response['code']}, 消息: {response['msg']}")
    
    def test_03_list_products_different_page_size(self):
        """[测试用例03] 测试不同pageSize参数"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        page_sizes = [5, 20, 50]
        
        for page_size in page_sizes:
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
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                assert len(response["data"]["list"]) <= page_size, f"返回的产品数量({len(response['data']['list'])})超过pageSize({page_size})"
                print(f"\n[测试] pageSize={page_size}测试通过！返回{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_04_list_products_with_filters(self):
        """[测试用例04] 测试带过滤条件的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 用户提供的带过滤条件的请求参数
        request_data = {
            "paginationReq": {
                "pageNumber": 1,
                "pageSize": 10
            },
            "sid": self.space_id,
            "address": self.chain_address,
            "filters": [
                {"key": "zhName", "values": ["接"]},
                {"key": "state", "values": ["1"]},
                {"key": "subType", "values": ["201"]}
            ]
        }
        
        print("\n=== [测试用例04] 测试listProducts接口（带过滤条件） ===")
        print("[测试] 请求数据:")
        print(json.dumps(request_data, ensure_ascii=False, indent=2))
        
        # 发送POST请求
        response = self.post(url, json=request_data)
        
        print("\n[测试] 返回数据:")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        
        # 验证返回数据结构
        assert "code" in response, "响应中缺少code字段"
        assert "msg" in response, "响应中缺少msg字段"
        
        if response["code"] == 200:
            assert "data" in response, "响应中缺少data字段"
            assert "list" in response["data"], "data中缺少list字段"
            assert isinstance(response["data"]["list"], list), "list字段不是数组类型"
            
            print(f"\n[测试] 带过滤条件测试通过！成功获取{len(response['data']['list'])}个产品")
        else:
            pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_05_list_products_single_filter(self):
        """[测试用例05] 测试单个过滤条件的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试单个过滤条件的场景
        filter_scenarios = [
            {"key": "zhName", "values": ["接"]},  # 名称包含"接"
            {"key": "state", "values": ["1"]},  # 状态为1
            {"key": "state", "values": ["4"]},  # 状态为4
            {"key": "subType", "values": ["201"]},  # 子类型为201
            {"key": "type", "values": ["2"]}  # 类型为2
        ]
        
        for i, single_filter in enumerate(filter_scenarios):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": self.space_id,
                "address": self.chain_address,
                "filters": [single_filter]
            }
            
            print(f"\n=== [测试用例05] 测试listProducts接口（单个过滤条件 #{i+1}） ===")
            print(f"[测试] 过滤条件: {single_filter}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                print(f"\n[测试] 单个过滤条件测试通过！成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_06_list_products_combination_filters(self):
        """[测试用例06] 测试不同组合过滤条件的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试不同组合的过滤条件
        combination_scenarios = [
            # 名称+状态组合
            [
                {"key": "zhName", "values": ["接"]},
                {"key": "state", "values": ["4"]}
            ],
            # 类型+子类型组合
            [
                {"key": "type", "values": ["2"]},
                {"key": "subType", "values": ["201"]}
            ],
            # 名称+类型+状态组合
            [
                {"key": "zhName", "values": ["产品"]},
                {"key": "type", "values": ["2"]},
                {"key": "state", "values": ["4"]}
            ]
        ]
        
        for i, filters in enumerate(combination_scenarios):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": filters
            }
            
            print(f"\n=== [测试用例06] 测试listProducts接口（组合过滤条件 #{i+1}） ===")
            print(f"[测试] 过滤条件组合: {json.dumps(filters, ensure_ascii=False)}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                products = response["data"]["list"]
                
                # 验证返回的产品是否符合所有过滤条件
                for product in products:
                    product_data = product.get("productItem", {})
                    for filter_item in filters:
                        filter_key = filter_item["key"]
                        filter_values = filter_item["values"]
                        
                        # 根据不同的过滤条件进行验证
                        if filter_key == "zhName":
                            # 名称包含关系验证
                            product_name = product_data.get("zhName", "")
                            assert any(value in product_name for value in filter_values), \
                                f"产品名称'{product_name}'不包含过滤条件'{filter_values}'"
                        elif filter_key == "state":
                            # 状态精确匹配验证
                            product_state = str(product_data.get("state", ""))
                            assert product_state in filter_values, \
                                f"产品状态'{product_state}'不在过滤条件'{filter_values}'中"
                        elif filter_key == "type":
                            # 类型精确匹配验证
                            product_type = str(product_data.get("type", ""))
                            assert product_type in filter_values, \
                                f"产品类型'{product_type}'不在过滤条件'{filter_values}'中"
                        elif filter_key == "subType":
                            # 子类型精确匹配验证
                            product_subtype = str(product_data.get("subType", ""))
                            assert product_subtype in filter_values, \
                                f"产品子类型'{product_subtype}'不在过滤条件'{filter_values}'中"
                
                print(f"\n[测试] 组合过滤条件测试通过！成功获取{len(products)}个产品，且所有产品均符合过滤条件")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_07_list_products_invalid_filters(self):
        """[测试用例07] 测试无效过滤条件的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试无效的过滤条件
        invalid_scenarios = [
            {"key": "invalid_key", "values": ["test"]},  # 无效的key
            {"key": "zhName", "values": ["nonexistent_product"]},  # 不存在的产品名称
            {"key": "state", "values": ["999"]},  # 无效的状态值
            {"key": "subType", "values": ["0"]}  # 无效的子类型值
        ]
        
        for i, invalid_filter in enumerate(invalid_scenarios):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": [invalid_filter]
            }
            
            print(f"\n=== [测试用例07] 测试listProducts接口（无效过滤条件 #{i+1}） ===")
            print(f"[测试] 无效过滤条件: {invalid_filter}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            # 即使过滤条件无效，接口也应该返回200（空结果或错误消息）
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                print(f"\n[测试] 无效过滤条件测试通过！返回{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_08_list_products_name_search_variations(self):
        """[测试用例08] 测试不同名称搜索模式的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试不同的名称搜索模式
        name_variations = [
            "接",  # 单个字符
            "产品",  # 通用关键词
            "测试",  # 测试相关
            "1222",  # 数字
            "A"  # 英文开头
        ]
        
        for name in name_variations:
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": [{"key": "zhName", "values": [name]}]
            }
            
            print(f"\n=== [测试用例08] 测试listProducts接口（名称搜索: '{name}'） ===")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                print(f"\n[测试] 名称搜索测试通过！成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_09_list_products_different_page_numbers(self):
        """[测试用例09] 测试不同页面号码（pageNumber）的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试不同的页面号码
        page_numbers = [1, 2, 3]
        
        for page_number in page_numbers:
            request_data = {
                "paginationReq": {
                    "pageNumber": page_number,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": []
            }
            
            print(f"\n=== [测试用例09] 测试listProducts接口（pageNumber={page_number}） ===")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                
                # 验证返回的页码是否正确
                if "pageNumber" in response["data"]:
                    assert response["data"]["pageNumber"] == page_number, f"返回的pageNumber与请求不符，请求{page_number}，实际{response['data']['pageNumber']}"
                
                print(f"\n[测试] 页面号码测试通过！成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_10_list_products_multi_value_filters(self):
        """[测试用例10] 测试多值过滤条件（同一个key有多个value）的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试同一个key下的多个value过滤
        multi_value_scenarios = [
            # 单个key的多值过滤
            [{"key": "state", "values": ["1", "4", "7"]}],  # 多种状态同时过滤
            [{"key": "subType", "values": ["201"]}],  # 子类型为201
            # 多个key的多值过滤组合
            [
                {"key": "state", "values": ["1", "4", "7"]},
                {"key": "subType", "values": ["201"]}
            ]
        ]
        
        for i, filters in enumerate(multi_value_scenarios):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": filters
            }
            
            print(f"\n=== [测试用例10] 测试listProducts接口（多值过滤条件 #{i+1}） ===")
            print(f"[测试] 多值过滤条件: {json.dumps(filters, ensure_ascii=False)}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                print(f"\n[测试] 多值过滤条件测试通过！成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_11_list_products_specific_field_combinations(self):
        """[测试用例11] 测试特定字段组合过滤的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试特定的字段组合过滤
        specific_combinations = [
            # 状态+子类型组合
            [
                {"key": "state", "values": ["1"]},
                {"key": "subType", "values": ["201"]}
            ],
            # 名称+状态组合
            [
                {"key": "zhName", "values": ["接"]},
                {"key": "state", "values": ["1"]}
            ],
            # 类型+子类型组合
            [
                {"key": "type", "values": ["2"]},
                {"key": "subType", "values": ["201"]}
            ],
            # 名称+状态+子类型组合（用户提供的复杂过滤条件）
            [
                {"key": "zhName", "values": ["接"]},
                {"key": "state", "values": ["1"]},
                {"key": "subType", "values": ["201"]}
            ]
        ]
        
        for i, filters in enumerate(specific_combinations):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": filters
            }
            
            print(f"\n=== [测试用例11] 测试listProducts接口（特定字段组合 #{i+1}） ===")
            print(f"[测试] 字段组合: {json.dumps(filters, ensure_ascii=False)}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                products = response["data"]["list"]
                print(f"\n[测试] 特定字段组合测试通过！成功获取{len(products)}个产品")
                
                # 验证返回的产品是否符合过滤条件
                if filters and products:
                    # 检查第一个产品是否符合所有过滤条件
                    first_product = products[0]
                    product_data = first_product.get("productItem", {})
                    for filter_item in filters:
                        filter_key = filter_item["key"]
                        filter_values = filter_item["values"]
                        
                        # 根据不同的过滤条件进行验证
                        if filter_key == "zhName":
                            # 名称包含关系验证
                            product_name = product_data.get("zhName", "")
                            assert any(value in product_name for value in filter_values), \
                                f"产品名称'{product_name}'不包含过滤条件'{filter_values}'"
                        elif filter_key == "state":
                            # 状态精确匹配验证
                            product_state = str(product_data.get("state", ""))
                            assert product_state in filter_values, \
                                f"产品状态'{product_state}'不在过滤条件'{filter_values}'中"
                        elif filter_key == "type":
                            # 类型精确匹配验证
                            product_type = str(product_data.get("type", ""))
                            assert product_type in filter_values, \
                                f"产品类型'{product_type}'不在过滤条件'{filter_values}'中"
                        elif filter_key == "subType":
                            # 子类型精确匹配验证
                            product_subtype = str(product_data.get("subType", ""))
                            assert product_subtype in filter_values, \
                                f"产品子类型'{product_subtype}'不在过滤条件'{filter_values}'中"
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_12_list_products_boundary_conditions(self):
        """[测试用例12] 测试边界条件的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试pageSize的边界条件
        boundary_page_sizes = [
            1,  # 最小pageSize
            100,  # 较大的pageSize
            500  # 非常大的pageSize
        ]
        
        for page_size in boundary_page_sizes:
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": page_size
                },
                "sid": "254b70297a4aaa13da2978dd4a495s00",
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "filters": []
            }
            
            print(f"\n=== [测试用例12] 测试listProducts接口（边界条件 pageSize={page_size}） ===")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                
                # 验证返回的产品数量不超过请求的pageSize
                assert len(response["data"]["list"]) <= page_size, f"返回的产品数量({len(response['data']['list'])})超过pageSize({page_size})"
                
                # 新增：验证返回的pageSize与请求一致
                if "pageSize" in response["data"]:
                    assert response["data"]["pageSize"] == page_size, f"返回的pageSize与请求不符，请求{page_size}，实际{response['data']['pageSize']}"
                
                print(f"\n[测试] 边界条件测试通过！pageSize={page_size}时成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")
    
    def test_13_list_products_different_address_and_sid(self):
        """[测试用例13] 测试不同地址和sid参数的listProducts接口"""
        url = "/api/v1/dpm-core-service/listProducts"
        
        # 测试不同的address和sid组合
        address_sid_combinations = [
            # 默认地址和sid
            {
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "sid": "254b70297a4aaa13da2978dd4a495s00"
            },
            # 不同的sid
            {
                "address": "9d681b67a521b6926a1778c3d4978655b50748d7",
                "sid": "254b70297a4aaa13da2978dd4a495s01"
            },
            # 不同的address
            {
                "address": "0d681b67a521b6926a1778c3d4978655b50748d8",
                "sid": "254b70297a4aaa13da2978dd4a495s00"
            }
        ]
        
        for i, (address, sid) in enumerate([(item["address"], item["sid"]) for item in address_sid_combinations]):
            request_data = {
                "paginationReq": {
                    "pageNumber": 1,
                    "pageSize": 10
                },
                "sid": sid,
                "address": address,
                "filters": []
            }
            
            print(f"\n=== [测试用例13] 测试listProducts接口（不同address和sid组合 #{i+1}） ===")
            print(f"[测试] address={address}, sid={sid}")
            
            response = self.post(url, json=request_data)
            
            print("\n[测试] 返回数据:")
            print(json.dumps(response, ensure_ascii=False, indent=2))
            
            assert "code" in response, "响应中缺少code字段"
            
            if response["code"] == 200:
                assert "data" in response, "响应中缺少data字段"
                assert "list" in response["data"], "data中缺少list字段"
                print(f"\n[测试] 不同address和sid组合测试通过！成功获取{len(response['data']['list'])}个产品")
            else:
                pytest.fail(f"接口返回非成功状态码: {response['code']}, 消息: {response.get('msg', '未知错误')}")

if __name__ == "__main__":
    pytest.main(["-v", "-s", "tests/api_tests/test_product_list.py"])
