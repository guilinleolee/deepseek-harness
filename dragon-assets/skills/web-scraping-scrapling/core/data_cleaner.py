"""
数据清洗和验证模块

提供数据质量检查、清洗、验证等功能
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""

    def __init__(self):
        self.validation_rules = {}
        self.errors = []
        self.warnings = []

    def add_rule(self, field: str, rule_type: str, **kwargs):
        """
        添加验证规则

        Args:
            field: 字段名
            rule_type: 规则类型 (required, type, range, pattern, custom)
            **kwargs: 规则参数
        """
        if field not in self.validation_rules:
            self.validation_rules[field] = []

        self.validation_rules[field].append({
            'type': rule_type,
            'params': kwargs
        })

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据

        Args:
            data: 待验证的数据

        Returns:
            是否验证通过
        """
        self.errors = []
        self.warnings = []

        for field, rules in self.validation_rules.items():
            value = data.get(field)

            for rule in rules:
                result = self._apply_rule(field, value, rule)
                if not result['valid']:
                    self.errors.append(result['message'])
                elif result.get('warning'):
                    self.warnings.append(result['warning'])

        return len(self.errors) == 0

    def _apply_rule(self, field: str, value: Any, rule: Dict) -> Dict:
        """应用单个验证规则"""
        rule_type = rule['type']
        params = rule['params']

        if rule_type == 'required':
            if value is None or value == '':
                return {'valid': False, 'message': f"{field} is required"}

        elif rule_type == 'type':
            expected_type = params.get('value_type', params.get('type'))
            if expected_type == 'number':
                if value is not None and not isinstance(value, (int, float)):
                    return {'valid': False, 'message': f"{field} must be a number"}
            elif value is not None and not isinstance(value, expected_type):
                return {'valid': False, 'message': f"{field} must be {expected_type.__name__}"}

        elif rule_type == 'range':
            min_val = params.get('min')
            max_val = params.get('max')
            if value is not None:
                # 尝试转换为数字进行比较
                try:
                    num_value = float(value) if isinstance(value, str) else value
                    if min_val is not None and num_value < min_val:
                        return {'valid': False, 'message': f"{field} must be >= {min_val}"}
                    if max_val is not None and num_value > max_val:
                        return {'valid': False, 'message': f"{field} must be <= {max_val}"}
                except (ValueError, TypeError):
                    # 如果无法转换为数字，验证失败
                    return {'valid': False, 'message': f"{field} must be a number"}

        elif rule_type == 'pattern':
            pattern = params.get('pattern')
            if value is not None and not re.match(pattern, str(value)):
                return {'valid': False, 'message': f"{field} format invalid"}

        elif rule_type == 'url':
            if value is not None and not self._is_valid_url(str(value)):
                return {'valid': False, 'message': f"{field} must be a valid URL"}

        elif rule_type == 'email':
            if value is not None and not self._is_valid_email(str(value)):
                return {'valid': False, 'message': f"{field} must be a valid email"}

        return {'valid': True}

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return pattern.match(email) is not None

    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors

    def get_warnings(self) -> List[str]:
        """获取所有警告"""
        return self.warnings


class DataCleaner:
    """数据清洗器"""

    def __init__(self):
        self.cleaning_stats = {
            'total_items': 0,
            'cleaned_items': 0,
            'removed_items': 0,
            'modifications': {}
        }

    def clean_text(self, text: str, remove_extra_spaces: bool = True,
                   remove_newlines: bool = False, strip_html: bool = False) -> str:
        """
        清洗文本数据

        Args:
            text: 原始文本
            remove_extra_spaces: 是否移除多余空格
            remove_newlines: 是否移除换行符
            strip_html: 是否移除HTML标签

        Returns:
            清洗后的文本
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ''

        cleaned = text

        # 移除HTML标签
        if strip_html:
            cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # 移除多余空格
        if remove_extra_spaces:
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 移除换行符
        if remove_newlines:
            cleaned = cleaned.replace('\n', ' ').replace('\r', '')

        return cleaned

    def clean_number(self, value: Any, default: float = 0.0) -> float:
        """
        清洗数字数据

        Args:
            value: 原始值
            default: 默认值

        Returns:
            清洗后的数字
        """
        if value is None:
            return default

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # 移除货币符号、逗号等
            cleaned = re.sub(r'[^\d.-]', '', value)
            try:
                return float(cleaned)
            except ValueError:
                return default

        return default

    def clean_url(self, url: str, add_protocol: bool = True, remove_fragment: bool = False) -> Optional[str]:
        """
        清洗URL数据

        Args:
            url: 原始URL
            add_protocol: 是否添加协议
            remove_fragment: 是否移除fragment (#后面的部分)

        Returns:
            清洗后的URL
        """
        if not url:
            return None

        url = url.strip()

        # 移除fragment
        if remove_fragment and '#' in url:
            url = url.split('#')[0]

        # 添加协议
        if add_protocol and not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return url if self._is_valid_url(url) else None

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None

    def clean_list(self, items: List, remove_duplicates: bool = True,
                   remove_empty: bool = True) -> List:
        """
        清洗列表数据

        Args:
            items: 原始列表
            remove_duplicates: 是否移除重复项
            remove_empty: 是否移除空值

        Returns:
            清洗后的列表
        """
        if not isinstance(items, list):
            return []

        cleaned = items

        # 移除空值
        if remove_empty:
            cleaned = [item for item in cleaned if item is not None and item != '']

        # 移除重复项
        if remove_duplicates:
            cleaned = list(dict.fromkeys(cleaned))  # 保持顺序

        return cleaned

    def normalize_json(self, data: Union[str, Dict]) -> Dict:
        """
        标准化JSON数据

        Args:
            data: JSON字符串或字典

        Returns:
            标准化后的字典
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON: {data[:100]}")
                return {}

        if not isinstance(data, dict):
            return {}

        return data

    def remove_null_fields(self, data: Dict, fields: Optional[List[str]] = None) -> Dict:
        """
        移除空字段

        Args:
            data: 原始数据
            fields: 指定要检查的字段，None表示检查所有字段

        Returns:
            清洗后的数据
        """
        if fields is None:
            fields = list(data.keys())

        cleaned = data.copy()
        for field in fields:
            if field in cleaned and cleaned[field] is None:
                del cleaned[field]

        return cleaned

    def clean_batch(self, data_list: List[Dict],
                   validators: Optional[List[DataValidator]] = None) -> List[Dict]:
        """
        批量清洗数据

        Args:
            data_list: 数据列表
            validators: 验证器列表

        Returns:
            清洗后的数据列表
        """
        self.cleaning_stats['total_items'] = len(data_list)
        cleaned_data = []

        for i, item in enumerate(data_list):
            try:
                # 清洗数据
                cleaned_item = self._clean_item(item)

                # 验证数据
                if validators:
                    valid = True
                    for validator in validators:
                        if not validator.validate(cleaned_item):
                            valid = False
                            logger.warning(f"Item {i} validation failed: {validator.get_errors()}")
                            break

                    if not valid:
                        self.cleaning_stats['removed_items'] += 1
                        continue

                cleaned_data.append(cleaned_item)
                self.cleaning_stats['cleaned_items'] += 1

            except Exception as e:
                logger.error(f"Error cleaning item {i}: {e}")
                self.cleaning_stats['removed_items'] += 1

        return cleaned_data

    def _clean_item(self, item: Dict) -> Dict:
        """清洗单个数据项"""
        cleaned = {}

        for key, value in item.items():
            # 根据值类型进行清洗
            if isinstance(value, str):
                # 尝试识别并转换为数字
                if self._looks_like_number(value):
                    cleaned[key] = self.clean_number(value)
                else:
                    # 不是数字，作为文本处理
                    cleaned[key] = self.clean_text(value)
            elif isinstance(value, (int, float)):
                cleaned[key] = value
            elif isinstance(value, list):
                cleaned[key] = self.clean_list(value)
            elif value is None:
                pass  # 跳过空值
            else:
                cleaned[key] = value

        return cleaned

    @staticmethod
    def _looks_like_number(text: str) -> bool:
        """检测字符串是否像数字"""
        if not isinstance(text, str):
            return False
        # 移除常见的数字格式符号
        cleaned = re.sub(r'[\$,\s%]', '', text)
        try:
            float(cleaned)
            return True
        except ValueError:
            return False

    def get_stats(self) -> Dict:
        """获取清洗统计信息"""
        return self.cleaning_stats.copy()

    def print_stats(self):
        """打印清洗统计"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("Data Cleaning Statistics")
        print("="*50)
        print(f"Total items: {stats['total_items']}")
        print(f"Cleaned items: {stats['cleaned_items']}")
        print(f"Removed items: {stats['removed_items']}")
        if stats['total_items'] > 0:
            success_rate = (stats['cleaned_items'] / stats['total_items']) * 100
            print(f"Success rate: {success_rate:.2f}%")
        print("="*50 + "\n")
