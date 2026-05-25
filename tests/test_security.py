import unittest
from src.shared.utils.security import sanitize_query_param

class TestSecurity(unittest.TestCase):
    def test_sanitize_query_param_none(self):
        self.assertEqual(sanitize_query_param(None), "")

    def test_sanitize_query_param_normal_string(self):
        self.assertEqual(sanitize_query_param("hello"), "hello")

    def test_sanitize_query_param_single_apostrophe(self):
        self.assertEqual(sanitize_query_param("O'Connor"), "O''Connor")

    def test_sanitize_query_param_multiple_apostrophes(self):
        self.assertEqual(sanitize_query_param("it's a 'test'"), "it''s a ''test''")

    def test_sanitize_query_param_non_string(self):
        self.assertEqual(sanitize_query_param(123), "123")
        self.assertEqual(sanitize_query_param(True), "True")

if __name__ == '__main__':
    unittest.main()
