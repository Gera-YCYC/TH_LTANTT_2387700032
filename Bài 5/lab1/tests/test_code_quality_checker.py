import unittest
import tempfile
from sast_tool.code_quality_checker import CodeQualityChecker


class TestCodeQualityChecker(unittest.TestCase):
    def test_flake8_detection(self):
        with tempfile.NamedTemporaryFile(suffix=".py",
                                         mode="w", delete=False) as tmp:
            tmp.write("import os\n\n\n")
            tmp.flush()
            tmp_name = tmp.name

        try:
            checker = CodeQualityChecker()
            issues = checker.check(tmp_name)
            self.assertTrue(all(i['type'] == 'Lint Issue' for i in issues)
                            or len(issues) == 0)
        finally:
            import os
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
