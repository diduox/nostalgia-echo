# test_ip_location.py
import unittest
from unittest.mock import patch, Mock
import sys
import os

# 将app.py所在目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_location_info


class TestIPLocation(unittest.TestCase):

    @patch('app.requests.get')
    def test_get_location_info_success(self, mock_get):
        """测试成功获取IP地理位置信息"""
        # 模拟成功的API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'country': 'China',
            'regionName': 'Beijing',
            'city': 'Beijing',
            'isp': 'China Telecom'
        }
        mock_get.return_value = mock_response

        # 调用函数
        result = get_location_info('1.1.1.1')

        # 验证结果
        expected = {
            'country': 'China',
            'region': 'Beijing',
            'city': 'Beijing',
            'isp': 'China Telecom'
        }
        self.assertEqual(result, expected)

        # 验证requests.get被正确调用
        mock_get.assert_called_once_with('https://ipwhois.app/json/1.1.1.1')

    @patch('app.requests.get')
    def test_get_location_info_api_failure(self, mock_get):
        """测试API返回失败状态的情况"""
        # 模拟API返回失败状态
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'fail',
            'message': 'Invalid IP'
        }
        mock_get.return_value = mock_response

        # 调用函数
        result = get_location_info('invalid.ip')

        # 验证返回默认值
        expected = {
            'country': '未知',
            'region': '未知',
            'city': '未知',
            'isp': '未知'
        }
        self.assertEqual(result, expected)

    @patch('app.requests.get')
    def test_get_location_info_http_error(self, mock_get):
        """测试HTTP请求失败的情况"""
        # 模拟HTTP请求异常
        mock_get.side_effect = Exception('Network error')

        # 调用函数
        result = get_location_info('1.1.1.1')

        # 验证返回默认值
        expected = {
            'country': '未知',
            'region': '未知',
            'city': '未知',
            'isp': '未知'
        }
        self.assertEqual(result, expected)

    @patch('app.requests.get')
    def test_get_location_info_missing_fields(self, mock_get):
        """测试API返回部分字段缺失的情况"""
        # 模拟部分字段缺失的响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'success',
            'country': 'China',
            # regionName, city, isp 字段缺失
        }
        mock_get.return_value = mock_response

        # 调用函数
        result = get_location_info('1.1.1.1')

        # 验证缺失字段使用默认值
        expected = {
            'country': 'China',
            'region': '未知',
            'city': '未知',
            'isp': '未知'
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()