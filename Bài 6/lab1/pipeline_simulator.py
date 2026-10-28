import os
import re
import sys
import time
from typing import Dict, List, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_simple_yaml(file_path: str) -> Dict[str, Any]:
    """
    Trình phân tích YAML đơn giản hỗ trợ cú pháp pipeline cơ bản của GitLab CI/CD.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    data: Dict[str, Any] = {}
    current_key = None
    current_sub_key = None
    in_list = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            raw_line = line.rstrip()
            stripped = raw_line.strip()

            # Bỏ qua comment và dòng trống
            if not stripped or stripped.startswith("#"):
                continue

            # Kiểm tra cấp 1 (Key chính: stages, build-job, test-job1, ...)
            if not raw_line.startswith(" ") and not raw_line.startswith("\t"):
                if ":" in stripped:
                    key, val = stripped.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    current_key = key
                    current_sub_key = None
                    if val == "":
                        data[current_key] = {}
                    else:
                        data[current_key] = val
                continue

            # Kiểm tra cấp 2 hoặc danh sách (ví dụ stages: - build)
            indent = len(raw_line) - len(raw_line.lstrip())

            if current_key == "stages":
                if isinstance(data.get("stages"), dict):
                    data["stages"] = []
                if stripped.startswith("-"):
                    stage_name = stripped.lstrip("-").strip()
                    data["stages"].append(stage_name)
                continue

            if isinstance(data.get(current_key), dict):
                if stripped.startswith("-") and current_sub_key:
                    # Item trong mảng con (ví dụ script: - echo ...)
                    item_val = stripped.lstrip("-").strip()
                    # Loại bỏ dấu ngoặc kép nếu có
                    if (item_val.startswith('"') and item_val.endswith('"')) or \
                       (item_val.startswith("'") and item_val.endswith("'")):
                        item_val = item_val[1:-1]
                    if not isinstance(data[current_key].get(current_sub_key), list):
                        data[current_key][current_sub_key] = []
                    data[current_key][current_sub_key].append(item_val)
                elif ":" in stripped:
                    sub_key, sub_val = stripped.split(":", 1)
                    sub_key = sub_key.strip()
                    sub_val = sub_val.strip()
                    # Xử lý comment cùng dòng
                    if "#" in sub_val:
                        sub_val = sub_val.split("#", 1)[0].strip()
                    current_sub_key = sub_key
                    if sub_val == "":
                        data[current_key][current_sub_key] = []
                    else:
                        if (sub_val.startswith('"') and sub_val.endswith('"')) or \
                           (sub_val.startswith("'") and sub_val.endswith("'")):
                            sub_val = sub_val[1:-1]
                        data[current_key][current_sub_key] = sub_val

    return data


class GitLabRunnerSimulator:
    """Mô phỏng GitLab Runner thực thi pipeline."""

    def __init__(self, ci_config_path: str, env_vars: Dict[str, str] = None):
        self.ci_config_path = ci_config_path
        self.config = parse_simple_yaml(ci_config_path)
        self.env = {
            "GITLAB_USER_LOGIN": "student_dev",
            "CI_COMMIT_BRANCH": "main",
            "CI_PIPELINE_ID": "217408060",
            "CI_JOB_STAGE": "",
        }
        if env_vars:
            self.env.update(env_vars)
        self.logs: List[str] = []

    def get_stages(self) -> List[str]:
        """Lấy danh sách các stage theo thứ tự."""
        stages = self.config.get("stages")
        if not stages:
            # Mặc định theo quy tắc GitLab nếu không khai báo stages
            stages = ["build", "test", "deploy"]
        return stages

    def get_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Lọc ra các job (bỏ qua 'stages')."""
        jobs = {}
        for k, v in self.config.items():
            if k != "stages" and isinstance(v, dict):
                jobs[k] = v
        return jobs

    def substitute_env(self, cmd: str) -> str:
        """Thay thế biến môi trường kiểu $VAR hoặc ${VAR}."""
        for var_name, var_val in self.env.items():
            cmd = cmd.replace(f"${var_name}", var_val)
            cmd = cmd.replace(f"${{{var_name}}}", var_val)
        return cmd

    def run_pipeline(self, fast_mode: bool = True) -> Dict[str, Any]:
        """
        Thực thi pipeline theo tuần tự các stage.
        Trong chế độ fast_mode, các lệnh sleep sẽ được mô phỏng nhanh thay vì chờ đợi lâu.
        """
        self.logs = []
        stages = self.get_stages()
        all_jobs = self.get_jobs()
        job_results = {}

        self.logs.append(f"=== Bắt đầu thực thi Pipeline #{self.env['CI_PIPELINE_ID']} ===")

        for stage in stages:
            stage_jobs = [j_name for j_name, j_data in all_jobs.items() if j_data.get("stage") == stage]
            if not stage_jobs:
                continue

            self.logs.append(f"\n--- Giai đoạn (Stage): {stage.upper()} ---")
            for job_name in stage_jobs:
                job_data = all_jobs[job_name]
                self.env["CI_JOB_STAGE"] = stage
                self.logs.append(f"Running job: {job_name} on gitlab-runner...")

                scripts = job_data.get("script", [])
                if isinstance(scripts, str):
                    scripts = [scripts]

                job_log = []
                for script_cmd in scripts:
                    resolved_cmd = self.substitute_env(script_cmd)
                    job_log.append(f"$ {resolved_cmd}")

                    if resolved_cmd.startswith("sleep"):
                        duration = 1
                        try:
                            parts = resolved_cmd.split()
                            if len(parts) > 1:
                                duration = int(parts[1])
                        except ValueError:
                            pass
                        if not fast_mode:
                            time.sleep(min(duration, 5))
                        job_log.append(f"[Mô phỏng chờ {duration}s hoàn tất]")
                    elif resolved_cmd.startswith("echo "):
                        echo_content = resolved_cmd[5:].strip()
                        if (echo_content.startswith('"') and echo_content.endswith('"')) or \
                           (echo_content.startswith("'") and echo_content.endswith("'")):
                            echo_content = echo_content[1:-1]
                        job_log.append(echo_content)

                env_prop = job_data.get("environment")
                if env_prop:
                    job_log.append(f"Deploying to environment: {env_prop}")

                job_results[job_name] = {
                    "stage": stage,
                    "status": "passed",
                    "logs": job_log
                }
                self.logs.extend([f"  {line}" for line in job_log])
                self.logs.append(f"Job {job_name} PASSED.")

        self.logs.append(f"\n=== Pipeline completed successfully! ===")
        return {
            "status": "success",
            "stages": stages,
            "jobs": job_results,
            "logs": self.logs
        }


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ci_file = os.path.join(current_dir, ".gitlab-ci.yml")
    runner = GitLabRunnerSimulator(ci_file, {
        "GITLAB_USER_LOGIN": "student_2387700032",
        "CI_COMMIT_BRANCH": "main"
    })
    results = runner.run_pipeline(fast_mode=True)
    print("\n".join(results["logs"]))
