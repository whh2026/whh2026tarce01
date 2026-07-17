"""
数据加载工具类
用于加载和管理测试数据
"""
import json
import os
from typing import Dict, Any, Optional


class DataLoader:
    """数据加载器类，用于加载测试数据文件"""

    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化数据加载器
        
        Args:
            data_dir: 数据文件目录路径，默认为当前目录下的 data 文件夹
        """
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        else:
            self.data_dir = data_dir
        
        self._cache = {}

    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        加载 JSON 格式的测试数据文件
        
        Args:
            filename: 数据文件名（不含路径）
            
        Returns:
            包含测试数据的字典
        """
        filepath = os.path.join(self.data_dir, filename)
        
        if filepath in self._cache:
            return self._cache[filepath]
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"测试数据文件不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._cache[filepath] = data
            return data

    def get_test_case_data(self, filename: str, test_case_name: str) -> Dict[str, Any]:
        """
        获取指定测试用例的数据
        
        Args:
            filename: 数据文件名
            test_case_name: 测试用例名称
            
        Returns:
            测试用例数据
        """
        data = self.load_json(filename)
        
        if test_case_name not in data:
            raise KeyError(f"测试用例 '{test_case_name}' 在文件 '{filename}' 中不存在")
        
        return data[test_case_name]

    def get_all_test_cases(self, filename: str) -> Dict[str, Any]:
        """
        获取文件中所有测试用例
        
        Args:
            filename: 数据文件名
            
        Returns:
            所有测试用例数据
        """
        return self.load_json(filename)

    def reload(self, filename: str):
        """
        重新加载指定的数据文件（清除缓存）
        
        Args:
            filename: 数据文件名
        """
        filepath = os.path.join(self.data_dir, filename)
        if filepath in self._cache:
            del self._cache[filepath]

    def clear_cache(self):
        """清除所有缓存"""
        self._cache.clear()


# 创建全局数据加载器实例
data_loader = DataLoader()
