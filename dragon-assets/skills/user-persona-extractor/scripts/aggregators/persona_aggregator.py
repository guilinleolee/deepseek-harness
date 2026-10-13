#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户画像聚合器
Persona Aggregator

负责将多个数据源的用户画像数据进行聚合分析，生成综合的用户画像。
"""

from typing import Dict, List, Any
from datetime import datetime


class PersonaAggregator:
    """用户画像数据聚合器"""

    def __init__(self):
        """初始化聚合器"""
        self.sources_data = []

        # 数据源权重（可根据数据质量和可信度调整）
        self.weights = {
            'SourceBaiduIndex': 1.0,
            'SourceDouyinIndex': 0.9,
            'SourceWechatIndex': 0.85,
            'Source5118': 0.95,  # 如果使用 5118 API
            'SourceToutiaoIndex': 0.9,
            'SourceXinbang': 0.85,
        }

    def add_source_data(self, data: Dict[str, Any]):
        """
        添加数据源

        Args:
            data: 数据源返回的用户画像数据
        """
        if data.get('success', False):
            self.sources_data.append(data)

    def aggregate(self) -> Dict[str, Any]:
        """
        聚合所有数据源

        Returns:
            聚合后的用户画像数据
        """
        if not self.sources_data:
            return {
                'success': False,
                'error': '没有可用的数据源'
            }

        # 获取关键词
        keyword = self.sources_data[0].get('keyword', '')

        # 获取数据源列表
        sources = [d.get('source', '') for d in self.sources_data]

        # 聚合人口统计数据
        demographics = {
            'age': self._aggregate_age(),
            'gender': self._aggregate_gender(),
            'region': self._aggregate_region(),
        }

        # 提取核心用户画像
        core_persona = self._extract_core_persona(demographics)

        # 生成洞察
        insights = self._generate_insights(demographics)

        return {
            'success': True,
            'keyword': keyword,
            'sources': sources,
            'source_count': len(self.sources_data),
            'demographics': demographics,
            'core_persona': core_persona,
            'insights': insights,
            'metadata': {
                'aggregation_time': datetime.now().isoformat(),
                'data_sources': sources,
            }
        }

    def _aggregate_age(self) -> Dict[str, float]:
        """
        聚合年龄分布

        Returns:
            标准化的年龄分布
            {
                '18-24': 0.15,
                '25-30': 0.35,
                '31-35': 0.28,
                '36-40': 0.15,
                '40+': 0.07
            }
        """
        age_groups = ['18-24', '25-30', '31-35', '36-40', '40+']
        aggregated = {}

        for group in age_groups:
            values = []
            weights = []

            for source_data in self.sources_data:
                source_name = source_data.get('source', '')
                age_data = source_data.get('demographics', {}).get('age', {})

                if group in age_data:
                    values.append(age_data[group])
                    weights.append(self.weights.get(source_name, 0.5))

            if values:
                # 加权平均
                weighted_sum = sum(v * w for v, w in zip(values, weights))
                weight_sum = sum(weights)
                aggregated[group] = round(weighted_sum / weight_sum, 4)
            else:
                aggregated[group] = 0.0

        return aggregated

    def _aggregate_gender(self) -> Dict[str, float]:
        """
        聚合性别分布

        Returns:
            标准化的性别分布
            {
                'male': 0.62,
                'female': 0.38
            }
        """
        genders = ['male', 'female']
        aggregated = {}

        for gender in genders:
            values = []
            weights = []

            for source_data in self.sources_data:
                source_name = source_data.get('source', '')
                gender_data = source_data.get('demographics', {}).get('gender', {})

                if gender in gender_data:
                    values.append(gender_data[gender])
                    weights.append(self.weights.get(source_name, 0.5))

            if values:
                # 加权平均
                weighted_sum = sum(v * w for v, w in zip(values, weights))
                weight_sum = sum(weights)
                aggregated[gender] = round(weighted_sum / weight_sum, 4)
            else:
                aggregated[gender] = 0.0

        # 归一化（确保总和为1）
        total = aggregated.get('male', 0) + aggregated.get('female', 0)
        if total > 0:
            aggregated['male'] = round(aggregated['male'] / total, 4)
            aggregated['female'] = round(aggregated['female'] / total, 4)

        return aggregated

    def _aggregate_region(self) -> List[Dict]:
        """
        聚合地域分布

        Returns:
            标准化的地域分布
            [
                {'region': '广东', 'percentage': 0.18, 'rank': 1},
                {'region': '北京', 'percentage': 0.15, 'rank': 2},
                ...
            ]
        """
        region_scores = {}
        region_weights = {}

        # 收集所有地域数据
        for source_data in self.sources_data:
            source_name = source_data.get('source', '')
            weight = self.weights.get(source_name, 0.5)
            region_data = source_data.get('demographics', {}).get('region', [])

            for item in region_data:
                region = item.get('region', '')
                percentage = item.get('percentage', 0)

                if region:
                    if region not in region_scores:
                        region_scores[region] = 0
                        region_weights[region] = 0

                    region_scores[region] += percentage * weight
                    region_weights[region] += weight

        # 计算加权平均
        result = []
        for region, score in region_scores.items():
            weight = region_weights[region]
            if weight > 0:
                avg_percentage = round(score / weight, 4)
                result.append({
                    'region': region,
                    'percentage': avg_percentage,
                })

        # 按占比排序
        result.sort(key=lambda x: x['percentage'], reverse=True)

        # 添加排名并只取 TOP 10
        for idx, item in enumerate(result[:10], 1):
            item['rank'] = idx

        return result[:10]

    def _extract_core_persona(self, demographics: Dict) -> Dict[str, Any]:
        """
        提取核心用户画像

        Args:
            demographics: 人口统计数据

        Returns:
            核心用户画像
        """
        # 找出主要年龄段
        age_dist = demographics.get('age', {})
        primary_age = max(age_dist.items(), key=lambda x: x[1])[0] if age_dist else '未知'
        primary_age_pct = age_dist.get(primary_age, 0)

        # 计算性别比例
        gender_dist = demographics.get('gender', {})
        male_ratio = gender_dist.get('male', 0)
        if male_ratio > 0.6:
            gender_dominant = '男性为主'
            gender_desc = f"男性占 {male_ratio*100:.1f}%"
        elif male_ratio < 0.4:
            gender_dominant = '女性为主'
            gender_desc = f"女性占 {(1-male_ratio)*100:.1f}%"
        else:
            gender_dominant = '性别均衡'
            gender_desc = f"男性 {male_ratio*100:.1f}%，女性 {(1-male_ratio)*100:.1f}%"

        # 找出 TOP 3 地域
        region_dist = demographics.get('region', [])
        top_regions = [r['region'] for r in region_dist[:3]]
        top_regions_pct = sum(r['percentage'] for r in region_dist[:3])

        # 生成用户画像描述
        age_desc_map = {
            '18-24': 'Z世代年轻用户',
            '25-30': '职场青年群体',
            '31-35': '职场中坚力量',
            '36-40': '资深职场人士',
            '40+': '成熟决策群体'
        }

        user_profile = (
            f"{age_desc_map.get(primary_age, '')}，"
            f"{gender_desc}，"
            f"主要集中在{'、'.join(top_regions[:2])}等地区"
        )

        return {
            'primary_age': primary_age,
            'primary_age_pct': round(primary_age_pct * 100, 1),
            'gender_ratio': gender_dist,
            'gender_dominant': gender_dominant,
            'gender_desc': gender_desc,
            'top_regions': top_regions,
            'top_regions_pct': round(top_regions_pct * 100, 1),
            'user_profile': user_profile,
        }

    def _generate_insights(self, demographics: Dict) -> List[str]:
        """
        生成洞察

        Args:
            demographics: 人口统计数据

        Returns:
            洞察列表
        """
        insights = []

        # 年龄洞察
        age_dist = demographics.get('age', {})
        if age_dist:
            max_age = max(age_dist.items(), key=lambda x: x[1])
            insights.append(
                f"核心年龄段为 {max_age[0]} 岁，占比 {max_age[1]*100:.1f}%"
            )

            # 判断用户成熟度
            young_pct = age_dist.get('18-24', 0)
            mature_pct = age_dist.get('36-40', 0) + age_dist.get('40+', 0)

            if young_pct > 0.4:
                insights.append("用户群体偏年轻，内容应注重视觉化和趣味性")
            elif mature_pct > 0.3:
                insights.append("用户群体较成熟，内容应注重专业性和深度")

        # 性别洞察
        gender_dist = demographics.get('gender', {})
        if gender_dist:
            male_ratio = gender_dist.get('male', 0)

            if male_ratio > 0.7:
                insights.append(
                    f"男性用户占主导（{male_ratio*100:.1f}%），"
                    "内容策略应偏向男性视角"
                )
            elif male_ratio < 0.3:
                insights.append(
                    f"女性用户占主导（{(1-male_ratio)*100:.1f}%），"
                    "内容策略应偏向女性视角"
                )

        # 地域洞察
        region_dist = demographics.get('region', [])
        if region_dist:
            # 计算一线城市占比
            tier_1_regions = ['北京', '上海', '广州', '深圳']
            tier_1_pct = sum(
                r['percentage'] for r in region_dist
                if r['region'] in tier_1_regions
            )

            if tier_1_pct > 0.5:
                insights.append(
                    f"一线城市用户占比高达 {tier_1_pct*100:.1f}%，"
                    "用户消费能力强，可推荐高客单价产品"
                )

            # 判断地域集中度
            top_3_pct = sum(r['percentage'] for r in region_dist[:3])
            if top_3_pct > 0.5:
                insights.append(
                    f"TOP3 地域占比 {top_3_pct*100:.1f}%，"
                    "用户地域高度集中，可进行区域化营销"
                )

        return insights

    def get_content_strategy(self, demographics: Dict) -> Dict[str, Any]:
        """
        根据用户画像获取内容策略

        Args:
            demographics: 人口统计数据

        Returns:
            内容策略建议
        """
        age_dist = demographics.get('age', {})
        gender_dist = demographics.get('gender', {})

        # 获取主要年龄段
        primary_age = max(age_dist.items(), key=lambda x: x[1])[0] if age_dist else '25-30'

        # 根据年龄段返回策略
        strategies = {
            '18-24': {
                'tone': '轻松、幽默、互动性强',
                'format': '短视频、图文、表情包',
                'topics': ['娱乐', '二次元', '游戏', '潮流'],
                'length': '短视频<30秒，图文<500字',
                'platforms': ['抖音', 'B站', '小红书']
            },
            '25-30': {
                'tone': '共鸣、实用、有态度',
                'format': '中长视频、深度图文',
                'topics': ['职场', '情感', '生活方式', '个人成长'],
                'length': '视频3-5分钟，图文800-1500字',
                'platforms': ['知乎', '公众号', 'B站']
            },
            '31-35': {
                'tone': '专业、理性、有价值',
                'format': '深度图文、课程、直播',
                'topics': ['育儿', '理财', '健康', '职业发展'],
                'length': '视频5-10分钟，图文1500-3000字',
                'platforms': ['公众号', '知乎', '得到']
            },
            '36-40': {
                'tone': '权威、深度、有洞见',
                'format': '深度文章、案例分析',
                'topics': ['管理', '投资', '教育', '行业洞察'],
                'length': '视频10-20分钟，图文3000字以上',
                'platforms': ['公众号', '知乎', '领英']
            },
            '40+': {
                'tone': '稳重、可信、有温度',
                'format': '长文、音频、视频',
                'topics': ['养生', '旅游', '时事', '家庭'],
                'length': '灵活，注重质量',
                'platforms': ['公众号', '今日头条', '音频平台']
            }
        }

        return strategies.get(primary_age, strategies['25-30'])

    def reset(self):
        """重置聚合器"""
        self.sources_data = []
