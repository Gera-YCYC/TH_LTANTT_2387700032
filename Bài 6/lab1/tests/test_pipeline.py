import os
import sys
import unittest

LAB1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LAB1_DIR not in sys.path:
    sys.path.insert(0, LAB1_DIR)

from pipeline_simulator import parse_simple_yaml, GitLabRunnerSimulator


class TestGitLabBasicPipeline(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ci_file = os.path.join(self.base_dir, ".gitlab-ci.yml")

    def test_file_exists(self):
        """Kiểm tra tệp .gitlab-ci.yml tồn tại."""
        self.assertTrue(os.path.exists(self.ci_file), "Tệp .gitlab-ci.yml không tồn tại!")

    def test_pipeline_stages(self):
        """Kiểm tra pipeline định nghĩa đầy đủ 3 stages: build, test, deploy."""
        config = parse_simple_yaml(self.ci_file)
        stages = config.get("stages", [])
        self.assertEqual(stages, ["build", "test", "deploy"])

    def test_jobs_defined(self):
        """Kiểm tra các jobs theo đúng bài hướng dẫn: build-job, test-job1, test-job2, deploy-prod."""
        config = parse_simple_yaml(self.ci_file)
        expected_jobs = ["build-job", "test-job1", "test-job2", "deploy-prod"]
        for job in expected_jobs:
            self.assertIn(job, config, f"Thiếu job '{job}' trong tệp cấu hình!")

    def test_stages_mapping(self):
        """Kiểm tra mỗi job thuộc đúng stage tương ứng."""
        config = parse_simple_yaml(self.ci_file)
        self.assertEqual(config["build-job"].get("stage"), "build")
        self.assertEqual(config["test-job1"].get("stage"), "test")
        self.assertEqual(config["test-job2"].get("stage"), "test")
        self.assertEqual(config["deploy-prod"].get("stage"), "deploy")

    def test_variable_substitution(self):
        """Kiểm tra việc thay thế biến môi trường GITLAB_USER_LOGIN và CI_COMMIT_BRANCH."""
        runner = GitLabRunnerSimulator(self.ci_file, {
            "GITLAB_USER_LOGIN": "test_user_hutech",
            "CI_COMMIT_BRANCH": "dev-security"
        })
        result = runner.run_pipeline(fast_mode=True)
        self.assertEqual(result["status"], "success")

        # Kiểm tra nội dung log của build-job
        build_logs = "\n".join(result["jobs"]["build-job"]["logs"])
        self.assertIn("Hello, test_user_hutech!", build_logs)

        # Kiểm tra nội dung log của deploy-prod
        deploy_logs = "\n".join(result["jobs"]["deploy-prod"]["logs"])
        self.assertIn("dev-security", deploy_logs)
        self.assertIn("Deploying to environment: production", deploy_logs)

    def test_test_jobs_execution(self):
        """Kiểm tra 2 test-job thực thi và sleep giả lập hoạt động đúng."""
        runner = GitLabRunnerSimulator(self.ci_file)
        result = runner.run_pipeline(fast_mode=True)
        self.assertEqual(result["jobs"]["test-job1"]["status"], "passed")
        self.assertEqual(result["jobs"]["test-job2"]["status"], "passed")
        test2_logs = "\n".join(result["jobs"]["test-job2"]["logs"])
        self.assertIn("simulates a test that runs 20 seconds longer", test2_logs)


if __name__ == "__main__":
    unittest.main()
