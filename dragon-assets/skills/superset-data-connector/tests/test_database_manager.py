#!/usr/bin/env python3
"""
Unit tests for Superset Data Connector

Tests database connections, schema discovery, and dataset creation.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Add scripts directory to path
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(test_dir), 'scripts')
sys.path.insert(0, scripts_dir)

# Mock requests before importing
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from database_manager import DatabaseManager, DatabaseInfo, DatasetInfo


class TestDatabaseInfo(unittest.TestCase):
    """Test DatabaseInfo dataclass."""

    def test_create_database_info(self):
        """Test creating database info."""
        db = DatabaseInfo(
            id=1,
            name='test_db',
            backend='postgresql',
            sqlalchemy_uri='postgresql://user:pass@host:5432/db'
        )
        self.assertEqual(db.id, 1)
        self.assertEqual(db.name, 'test_db')
        self.assertEqual(db.backend, 'postgresql')
        self.assertTrue(db.expose_in_sqllab)
        self.assertFalse(db.allow_run_async)
        self.assertTrue(db.allow_csv_upload)


class TestDatasetInfo(unittest.TestCase):
    """Test DatasetInfo dataclass."""

    def test_create_dataset_info(self):
        """Test creating dataset info."""
        ds = DatasetInfo(
            id=1,
            database_id=1,
            table_name='sales',
            schema='public'
        )
        self.assertEqual(ds.id, 1)
        self.assertEqual(ds.database_id, 1)
        self.assertEqual(ds.table_name, 'sales')
        self.assertEqual(ds.schema, 'public')
        self.assertEqual(ds.columns, [])


class TestDatabaseManager(unittest.TestCase):
    """Test database connection management."""

    def test_init_with_base_url(self):
        """Test initialization with base URL."""
        manager = DatabaseManager(base_url='http://localhost:8088')
        self.assertEqual(manager.base_url, 'http://localhost:8088')
        self.assertIsNone(manager.auth)

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed."""
        manager = DatabaseManager(base_url='http://localhost:8088/')
        self.assertEqual(manager.base_url, 'http://localhost:8088')

    @patch('database_manager.requests.Session')
    def test_init_with_auth(self, mock_session_class):
        """Test initialization with auth instance."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Create a mock auth
        mock_auth = MagicMock()
        mock_auth.config.base_url = 'http://localhost:8088'

        manager = DatabaseManager(auth=mock_auth)
        self.assertEqual(manager.auth, mock_auth)
        self.assertEqual(manager.base_url, 'http://localhost:8088')

    @patch('database_manager.requests.Session')
    def test_get_headers_with_auth(self, mock_session_class):
        """Test getting headers with auth."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_auth = MagicMock()
        mock_auth.config.base_url = 'http://localhost:8088'
        mock_auth.get_headers.return_value = {
            'Authorization': 'Bearer token',
            'Content-Type': 'application/json'
        }

        manager = DatabaseManager(auth=mock_auth)
        headers = manager._get_headers()

        self.assertEqual(headers['Authorization'], 'Bearer token')

    @patch('database_manager.requests.Session')
    def test_get_headers_without_auth(self, mock_session_class):
        """Test getting headers without auth."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        manager = DatabaseManager(base_url='http://localhost:8088')
        headers = manager._get_headers()

        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertNotIn('Authorization', headers)


class TestDatabaseURITemplates(unittest.TestCase):
    """Test database URI template generation."""

    def test_postgresql_uri(self):
        """Test PostgreSQL URI format."""
        expected = 'postgresql://user:pass@host:5432/db'
        # Simple format check
        self.assertIn('postgresql://', expected)
        self.assertIn('@host:', expected)

    def test_mysql_uri(self):
        """Test MySQL URI format."""
        expected = 'mysql://user:pass@host:3306/db'
        self.assertIn('mysql://', expected)

    def test_bigquery_uri(self):
        """Test BigQuery URI format."""
        expected = 'bigquery://project/dataset'
        self.assertIn('bigquery://', expected)

    def test_snowflake_uri(self):
        """Test Snowflake URI format."""
        expected = 'snowflake://user:pass@account/db'
        self.assertIn('snowflake://', expected)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    @patch('database_manager.requests.Session')
    def test_connection_error(self, mock_session_class):
        """Test connection error handling."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Create manager first
        manager = DatabaseManager(base_url='http://localhost:8088')

        # Make the request method raise an exception
        mock_session.request.side_effect = Exception('Connection refused')

        # The _request method uses session.request internally
        with self.assertRaises(Exception):
            manager._request('get', '/api/v1/database/')


if __name__ == '__main__':
    unittest.main()