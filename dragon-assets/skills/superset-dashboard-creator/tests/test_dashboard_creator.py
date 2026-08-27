#!/usr/bin/env python3
"""
Unit tests for Superset Dashboard Creator

Tests dashboard creation, chart generation, and auto recommendation.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add scripts directory to path
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(test_dir), 'scripts')
sys.path.insert(0, scripts_dir)

# Mock requests before importing
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from dashboard_creator import ChartRecommender, ChartConfig, DashboardInfo


class TestChartRecommender(unittest.TestCase):
    """Test chart recommendation engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.recommender = ChartRecommender()

    def test_recommend_trend_keywords(self):
        """Test recommendation with trend keywords."""
        columns = [{'name': 'date', 'type': 'DATE'}, {'name': 'value', 'type': 'FLOAT'}]

        result = self.recommender.recommend(columns, intent='趋势分析')

        self.assertIn('chart_type', result)
        self.assertIn(result['chart_type'], ['line', 'area', 'scatter'])

    def test_recommend_comparison_keywords(self):
        """Test recommendation with comparison keywords."""
        columns = [{'name': 'category', 'type': 'STRING'}, {'name': 'value', 'type': 'INT'}]

        result = self.recommender.recommend(columns, intent='对比分析')

        self.assertIn('chart_type', result)
        self.assertIn(result['chart_type'], ['bar', 'dist_bar', 'scatter'])

    def test_recommend_pie_keywords(self):
        """Test recommendation with pie/proportion keywords."""
        columns = [{'name': 'category', 'type': 'STRING'}, {'name': 'count', 'type': 'INT'}]

        result = self.recommender.recommend(columns, intent='占比分析')

        self.assertIn('chart_type', result)
        self.assertIn(result['chart_type'], ['pie', 'treemap', 'dist_bar'])

    def test_recommend_distribution_keywords(self):
        """Test recommendation with distribution keywords."""
        columns = [{'name': 'value', 'type': 'FLOAT'}]

        result = self.recommender.recommend(columns, intent='分布分析')

        self.assertIn('chart_type', result)
        self.assertIn(result['chart_type'], ['histogram', 'scatter', 'heatmap'])

    def test_recommend_kpi_keywords(self):
        """Test recommendation with KPI keywords."""
        columns = [{'name': 'metric', 'type': 'FLOAT'}]

        result = self.recommender.recommend(columns, intent='KPI指标')

        self.assertIn('chart_type', result)
        self.assertIn(result['chart_type'], ['gauge', 'big_number', 'big_number_total'])

    def test_recommend_by_data_types(self):
        """Test recommendation based on data types."""
        # Date + Float = Line chart
        columns = [{'name': 'date', 'type': 'DATE'}, {'name': 'value', 'type': 'FLOAT'}]
        result = self.recommender.recommend(columns)
        self.assertEqual(result['chart_type'], 'line')

        # String + Float = Bar chart
        columns = [{'name': 'category', 'type': 'STRING'}, {'name': 'value', 'type': 'FLOAT'}]
        result = self.recommender.recommend(columns)
        self.assertEqual(result['chart_type'], 'bar')

    def test_chart_type_map_exists(self):
        """Test that chart type map has expected keywords."""
        self.assertIn('趋势', ChartRecommender.CHART_TYPE_MAP)
        self.assertIn('对比', ChartRecommender.CHART_TYPE_MAP)
        self.assertIn('占比', ChartRecommender.CHART_TYPE_MAP)
        self.assertIn('分布', ChartRecommender.CHART_TYPE_MAP)
        self.assertIn('KPI', ChartRecommender.CHART_TYPE_MAP)

    def test_data_type_map_exists(self):
        """Test that data type map has expected combinations."""
        self.assertIn(('DATE', 'FLOAT'), ChartRecommender.DATA_TYPE_MAP)
        self.assertIn(('STRING', 'FLOAT'), ChartRecommender.DATA_TYPE_MAP)


class TestChartConfig(unittest.TestCase):
    """Test ChartConfig dataclass."""

    def test_create_chart_config(self):
        """Test creating chart configuration."""
        config = ChartConfig(
            chart_type='bar',
            title='Sales by Category',
            dataset_id=1,
            x_axis='category',
            y_axis='sales'
        )
        self.assertEqual(config.chart_type, 'bar')
        self.assertEqual(config.title, 'Sales by Category')
        self.assertEqual(config.dataset_id, 1)
        self.assertEqual(config.x_axis, 'category')
        self.assertEqual(config.y_axis, 'sales')

    def test_chart_config_with_groupby(self):
        """Test chart configuration with groupby."""
        config = ChartConfig(
            chart_type='line',
            title='Sales Trend',
            dataset_id=1,
            x_axis='date',
            y_axis='sales',
            groupby=['region', 'product']
        )
        self.assertEqual(config.groupby, ['region', 'product'])

    def test_chart_config_with_filters(self):
        """Test chart configuration with filters."""
        filters = [{'col': 'region', 'op': '==', 'val': 'East'}]
        config = ChartConfig(
            chart_type='bar',
            title='East Region Sales',
            dataset_id=1,
            x_axis='product',
            y_axis='sales',
            filters=filters
        )
        self.assertEqual(config.filters, filters)


class TestDashboardInfo(unittest.TestCase):
    """Test DashboardInfo dataclass."""

    def test_create_dashboard_info(self):
        """Test creating dashboard info."""
        dashboard = DashboardInfo(
            id=1,
            title='Sales Dashboard',
            slug='sales-dashboard'
        )
        self.assertEqual(dashboard.id, 1)
        self.assertEqual(dashboard.title, 'Sales Dashboard')
        self.assertEqual(dashboard.slug, 'sales-dashboard')
        self.assertEqual(dashboard.charts, [])

    def test_dashboard_with_charts(self):
        """Test dashboard with chart IDs."""
        dashboard = DashboardInfo(
            id=1,
            title='Analytics Dashboard',
            charts=[1, 2, 3]
        )
        self.assertEqual(len(dashboard.charts), 3)
        self.assertIn(1, dashboard.charts)


class TestChartTypes(unittest.TestCase):
    """Test various chart types support."""

    def test_supported_chart_types(self):
        """Test that common chart types are in mappings."""
        all_chart_types = set()
        for types in ChartRecommender.CHART_TYPE_MAP.values():
            all_chart_types.update(types)

        # Verify common chart types
        self.assertIn('line', all_chart_types)
        self.assertIn('bar', all_chart_types)
        self.assertIn('pie', all_chart_types)
        self.assertIn('scatter', all_chart_types)
        self.assertIn('heatmap', all_chart_types)


class TestTemplates(unittest.TestCase):
    """Test dashboard templates."""

    def test_executive_dashboard_template(self):
        """Test executive dashboard template concept."""
        # Executive dashboards typically include KPI charts
        expected_charts = ['big_number', 'gauge', 'line']
        for chart in expected_charts:
            self.assertIn(chart, ['big_number', 'gauge', 'line', 'bar', 'pie'])

    def test_operational_dashboard_template(self):
        """Test operational dashboard template concept."""
        # Operational dashboards typically include trend charts
        expected_charts = ['line', 'bar', 'area']
        for chart in expected_charts:
            self.assertIn(chart, ['line', 'bar', 'area', 'scatter'])


class TestQuantitativeCharts(unittest.TestCase):
    """Test quantitative chart scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.recommender = ChartRecommender()

    def test_large_dataset_recommendation(self):
        """Test recommendation for large datasets."""
        columns = [{'name': 'date', 'type': 'DATE'}, {'name': 'value', 'type': 'FLOAT'}]

        # Large dataset should still work
        result = self.recommender.recommend(columns, row_count=1000000)

        self.assertIn('chart_type', result)

    def test_small_dataset_recommendation(self):
        """Test recommendation for small datasets."""
        columns = [{'name': 'category', 'type': 'STRING'}, {'name': 'value', 'type': 'INT'}]

        result = self.recommender.recommend(columns, row_count=10)

        self.assertIn('chart_type', result)


if __name__ == '__main__':
    unittest.main()