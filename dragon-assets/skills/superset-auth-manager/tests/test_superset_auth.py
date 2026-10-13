#!/usr/bin/env python3
"""
Unit tests for Superset Authentication Manager

Tests JWT authentication, token caching, and guest token generation.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add scripts directory to path
test_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(os.path.dirname(test_dir), 'scripts')
sys.path.insert(0, scripts_dir)

# Mock requests before importing the module
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

from superset_auth import SupersetAuth, TokenCache, SupersetConfig


class TestTokenCache(unittest.TestCase):
    """Test token caching with Fernet encryption."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache = TokenCache(cache_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_token(self):
        """Test saving and loading tokens."""
        test_token = {
            'access_token': 'test_token_123',
            'refresh_token': 'refresh_456',
            'expires_in': 3600
        }

        # Save token
        self.cache.save('http://localhost:8088', 'admin', test_token)

        # Load token
        loaded = self.cache.load('http://localhost:8088', 'admin')
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['access_token'], 'test_token_123')
        self.assertEqual(loaded['refresh_token'], 'refresh_456')

    def test_load_nonexistent_token(self):
        """Test loading a token that doesn't exist."""
        result = self.cache.load('http://nonexistent:8088', 'unknown')
        self.assertIsNone(result)

    def test_clear_token(self):
        """Test clearing tokens."""
        self.cache.save('http://localhost:8088', 'admin', {'access_token': 'test', 'expires_in': 3600})
        self.cache.clear()
        result = self.cache.load('http://localhost:8088', 'admin')
        self.assertIsNone(result)

    def test_cache_key_consistency(self):
        """Test that cache keys are consistent for same URL/username."""
        key1 = self.cache._get_cache_key('http://localhost:8088', 'admin')
        key2 = self.cache._get_cache_key('http://localhost:8088', 'admin')
        self.assertEqual(key1, key2)

    def test_cache_key_uniqueness(self):
        """Test that cache keys differ for different URL/username."""
        key1 = self.cache._get_cache_key('http://localhost:8088', 'admin')
        key2 = self.cache._get_cache_key('http://localhost:8088', 'user')
        key3 = self.cache._get_cache_key('http://other:8088', 'admin')
        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key1, key3)


class TestSupersetConfig(unittest.TestCase):
    """Test SupersetConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SupersetConfig(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        self.assertEqual(config.provider, 'db')
        self.assertEqual(config.refresh_threshold_minutes, 5)
        self.assertEqual(config.timeout, 30)

    def test_custom_values(self):
        """Test custom configuration values."""
        config = SupersetConfig(
            base_url='http://custom:9090',
            username='user',
            password='pass',
            provider='ldap',
            refresh_threshold_minutes=10,
            timeout=60
        )
        self.assertEqual(config.base_url, 'http://custom:9090')
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.password, 'pass')
        self.assertEqual(config.provider, 'ldap')
        self.assertEqual(config.refresh_threshold_minutes, 10)
        self.assertEqual(config.timeout, 60)


class TestSupersetAuth(unittest.TestCase):
    """Test Superset authentication manager."""

    def test_init_with_params(self):
        """Test initialization with parameters."""
        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        self.assertEqual(auth.config.base_url, 'http://localhost:8088')
        self.assertEqual(auth.config.username, 'admin')
        self.assertEqual(auth.config.password, 'admin')

    def test_init_missing_params(self):
        """Test initialization with missing parameters."""
        with self.assertRaises(ValueError):
            SupersetAuth(base_url=None, username=None, password=None)

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        auth = SupersetAuth(
            base_url='http://localhost:8088/',
            username='admin',
            password='admin'
        )
        self.assertEqual(auth.config.base_url, 'http://localhost:8088')

    @patch('superset_auth.requests.Session')
    def test_login_success(self, mock_session_class):
        """Test successful login."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        result = auth.login()

        self.assertEqual(result['access_token'], 'test_access_token')
        self.assertEqual(auth._access_token, 'test_access_token')

    @patch('superset_auth.requests.Session')
    def test_get_access_token_auto_login(self, mock_session_class):
        """Test auto-login when getting access token."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Set up mock response before creating auth (login happens in __init__)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'auto_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )

        # Reset mock and set up fresh response for get_access_token
        mock_session.post.reset_mock()
        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = {
            'access_token': 'fresh_token',
            'refresh_token': 'refresh_token',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response2

        token = auth.get_access_token()

        # Token should be from cache (already logged in during init)
        self.assertIsNotNone(token)

    @patch('superset_auth.requests.Session')
    def test_get_headers(self, mock_session_class):
        """Test getting authorization headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Set up mock for login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'auto_token',
            'refresh_token': 'refresh',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        headers = auth.get_headers()

        # The token will be auto_token because login is called
        self.assertIn('Bearer', headers['Authorization'])
        self.assertEqual(headers['Content-Type'], 'application/json')

    @patch('superset_auth.requests.Session')
    def test_status(self, mock_session_class):
        """Test getting authentication status."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'token',
            'refresh_token': 'refresh',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        auth.login()

        status = auth.status()
        self.assertEqual(status['base_url'], 'http://localhost:8088')
        self.assertEqual(status['username'], 'admin')
        self.assertTrue(status['has_token'])

    @patch('superset_auth.requests.Session')
    def test_logout(self, mock_session_class):
        """Test logout clears tokens."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'token',
            'refresh_token': 'refresh',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )
        auth.login()
        auth.logout()

        self.assertIsNone(auth._access_token)
        self.assertIsNone(auth._refresh_token)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    @patch('superset_auth.requests.Session')
    def test_login_failure_401(self, mock_session_class):
        """Test login failure with 401."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception('Unauthorized')
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='wrong'
        )

        with self.assertRaises(Exception):
            auth.login()

    @patch('superset_auth.requests.Session')
    def test_guest_token_success(self, mock_session_class):
        """Test guest token generation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Set up mock for login
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'admin_token',
            'refresh_token': 'refresh',
            'expires_in': 3600
        }
        mock_session.post.return_value = mock_response

        auth = SupersetAuth(
            base_url='http://localhost:8088',
            username='admin',
            password='admin'
        )

        # Call login first
        auth.login()

        # Now mock the guest token response
        mock_session.post.reset_mock()
        guest_response = MagicMock()
        guest_response.status_code = 200
        guest_response.json.return_value = {'token': 'guest_token_123'}
        mock_session.post.return_value = guest_response

        guest_token = auth.create_guest_token(
            resources=[{'type': 'dashboard', 'id': '1'}]
        )

        self.assertEqual(guest_token, 'guest_token_123')


if __name__ == '__main__':
    unittest.main()