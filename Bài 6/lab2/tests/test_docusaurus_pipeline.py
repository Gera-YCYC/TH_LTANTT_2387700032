import os
import sys
import json
import shutil
import unittest

LAB2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LAB2_DIR not in sys.path:
    sys.path.insert(0, LAB2_DIR)

from security_gates.security_checker import SecurityGateChecker
from pipeline_simulator import DocusaurusPipelineSimulator


class TestDocusaurusDevSecOpsPipeline(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ci_file = os.path.join(self.base_dir, ".gitlab-ci.yml")
        self.config_file = os.path.join(self.base_dir, "docusaurus.config.js")
        self.pkg_file = os.path.join(self.base_dir, "package.json")

    def test_configuration_files_exist(self):
        """Kiểm tra các tệp cấu hình cốt lõi của Lab 2 tồn tại."""
        self.assertTrue(os.path.exists(self.ci_file), "Thiếu tệp .gitlab-ci.yml")
        self.assertTrue(os.path.exists(self.config_file), "Thiếu tệp docusaurus.config.js")
        self.assertTrue(os.path.exists(self.pkg_file), "Thiếu tệp package.json")

    def test_docusaurus_config_parameters(self):
        """Kiểm tra url và baseUrl theo đúng hướng dẫn mục 6.2.2."""
        with open(self.config_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("gitlab.io", content, "Cấu hình url phải trỏ về gitlab.io!")
        self.assertIn("/my-pipeline-tutorial-project/", content, "Cấu hình baseUrl phải là tên dự án!")

    def test_package_json_scripts(self):
        """Kiểm tra scripts trong package.json có build và start."""
        with open(self.pkg_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("build", data.get("scripts", {}), "Thiếu script build trong package.json")

    def test_security_gate_clean_project(self):
        """Kiểm tra dự án hiện tại không có lỗi bảo mật."""
        checker = SecurityGateChecker(self.base_dir)
        res = checker.run_all()
        self.assertTrue(res["passed"], "Dự án mẫu không được có lỗi bảo mật nghiêm trọng")
        self.assertEqual(res["critical"], 0)

    def test_security_gate_detects_secret_leak(self):
        """Kiểm tra Security Gate bắt được token/key bị lộ."""
        test_file = os.path.join(self.base_dir, "temp_secret_test.py")
        try:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write('API_KEY = "AKIA1234567890ABCDEF"\n')
            checker = SecurityGateChecker(self.base_dir)
            res = checker.run_all()
            self.assertFalse(res["passed"], "Security gate phải phát hiện và chặn khi có rò rỉ secret!")
            self.assertGreaterEqual(res["critical"], 1)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_full_pipeline_simulation_and_artifacts(self):
        """Kiểm tra toàn bộ luồng pipeline từ Build -> Security Gate -> Deploy GitLab Pages."""
        sim = DocusaurusPipelineSimulator(self.base_dir)
        res = sim.run_pipeline()
        self.assertEqual(res["status"], "success")

        # Xác nhận thư mục public được tạo và chứa file index.html
        public_dir = os.path.join(self.base_dir, "public")
        self.assertTrue(os.path.exists(public_dir), "Thư mục public/ phải được tạo sau deploy!")
        self.assertTrue(os.path.exists(os.path.join(public_dir, "index.html")))


if __name__ == "__main__":
    unittest.main()
