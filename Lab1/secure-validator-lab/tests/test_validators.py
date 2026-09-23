import unittest
from securevalidator import (
    validate_email, validate_url, validate_filename,
    sanitize_sql_input, sanitize_html_input
)

class TestValidators(unittest.TestCase):
    def setUp(self):
        print("\n Running:", self._testMethodName)

    def test_validate_email_valid(self):
        self.assertTrue(validate_email("user@example.com"))

    def test_validate_email_invalid(self):
        self.assertFalse(validate_email("user@@example..com"))

    def test_validate_url_valid(self):
        self.assertTrue(validate_url("https://example.com"))

    def test_validate_url_invalid(self):
        self.assertFalse(validate_url("ftp://example.com"))

    def test_validate_filename_valid(self):
        self.assertTrue(validate_filename("report.pdf"))

    def test_validate_filename_traversal(self):
        self.assertFalse(validate_filename("../../etc/passwd"))

    def test_sanitize_sql_input_injection(self):
        input_str = "' OR 1=1 --"
        sanitized = sanitize_sql_input(input_str)
        self.assertNotIn("'", sanitized)
        self.assertNotIn("--", sanitized)
        self.assertNotIn("OR", sanitized.upper())

    def test_sanitize_sql_input_safe_text(self):
        input_str = "hello world"
        sanitized = sanitize_sql_input(input_str)
        self.assertEqual(sanitized, "hello world")

    def test_sanitize_html_input_script(self):
        input_str = '<script>alert("XSS")</script>'
        sanitized = sanitize_html_input(input_str)
        self.assertEqual(sanitized, '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;')

    def test_sanitize_html_input_safe_text(self):
        input_str = "Hello World"
        sanitized = sanitize_html_input(input_str)
        self.assertEqual(sanitized, "Hello World")

#         from securevalidator import sanitize_sql_input

# # 1. Dữ liệu viết hoa (giống test case chuẩn)
# safe_test = "' OR 1=1 --"
# print("[1] Test chuẩn (in hoa):")
# print("    Input: ", safe_test)
# print("    Output:", sanitize_sql_input(safe_test))

# # 2. Dữ liệu viết thường hoặc xen kẽ hoa thường
# bypass_test_1 = "' or 1=1 --"
# bypass_test_2 = "admin' union select 1,2,3 --"

# print("\n[2] Kiểm tra payload vượt rào (chữ thường):")
# print("    Input: ", bypass_test_1)
# print("    Output:", sanitize_sql_input(bypass_test_1))

# print("\n[3] Kiểm tra payload truy vấn dữ liệu:")
# print("    Input: ", bypass_test_2)
# print("    Output:", sanitize_sql_input(bypass_test_2))
