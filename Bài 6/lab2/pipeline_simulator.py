import os
import sys
import shutil
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from security_gates.security_checker import SecurityGateChecker


class DocusaurusPipelineSimulator:
    def __init__(self, project_dir: str):
        self.project_dir = os.path.abspath(project_dir)
        self.build_dir = os.path.join(self.project_dir, "build")
        self.public_dir = os.path.join(self.project_dir, "public")
        self.logs = []

    def clean_artifacts(self):
        """Dọn dẹp thư mục artifacts cũ trước khi build mới."""
        for d in [self.build_dir, self.public_dir]:
            if os.path.exists(d):
                shutil.rmtree(d)

    def execute_build_stage(self) -> bool:
        """Stage 1: Build trang web tĩnh Docusaurus và lưu artifacts."""
        self.logs.append("[STAGE: BUILD] Bắt đầu build-job...")
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Mô phỏng quá trình Docusaurus compile ra HTML tĩnh
        index_html = os.path.join(self.build_dir, "index.html")
        with open(index_html, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><head><title>DevSecOps Tutorial</title></head>")
            f.write("<body><h1>Chào mừng đến với GitLab Pages DevSecOps!</h1></body></html>")
        
        self.logs.append(f"  ✓ Đã biên dịch xong. Artifact lưu tại: {self.build_dir}")
        self.logs.append("  ✓ Job 'build-job' hoàn thành xuất sắc!")
        return True

    def execute_security_stage(self) -> bool:
        """Stage 2: Quét bảo mật DevSecOps Security Gate."""
        self.logs.append("\n[STAGE: SECURITY] Bắt đầu security-scan...")
        checker = SecurityGateChecker(self.project_dir)
        res = checker.run_all()
        
        if res["passed"]:
            self.logs.append(f"  ✓ Không có lỗ hổng nguy hiểm. Security Gate PASSED!")
            return True
        else:
            self.logs.append(f"  ✗ Phát hiện {res['critical']} Critical, {res['high']} High rủi ro! Pipeline bị chặn!")
            return False

    def execute_deploy_stage(self) -> bool:
        """Stage 3: Triển khai GitLab Pages (di chuyển build/ -> public/)."""
        self.logs.append("\n[STAGE: DEPLOY] Bắt đầu job 'pages'...")
        if not os.path.exists(self.build_dir):
            self.logs.append("  ✗ Lỗi: Không tìm thấy artifacts từ stage build!")
            return False

        if os.path.exists(self.public_dir):
            shutil.rmtree(self.public_dir)
        
        # Lệnh: mv build/ public/
        shutil.move(self.build_dir, self.public_dir)
        self.logs.append(f"  ✓ Đã chuyển artifacts sang: {self.public_dir}")
        self.logs.append("  ✓ GitLab Pages deployment sẵn sàng tại: https://student-hutech.gitlab.io/my-pipeline-tutorial-project/")
        self.logs.append("  ✓ Job 'pages' hoàn tất thành công!")
        return True

    def run_pipeline(self) -> Dict[str, Any]:
        """Chạy tuần tự toàn bộ pipeline."""
        self.clean_artifacts()
        self.logs = ["=== BẮT ĐẦU CHẠY PIPELINE PHỨC TẠP LAB 2 ==="]
        
        # Stage 1: Build
        if not self.execute_build_stage():
            return {"status": "failed", "failed_at": "build", "logs": self.logs}
        
        # Stage 2: Security
        if not self.execute_security_stage():
            return {"status": "failed", "failed_at": "security", "logs": self.logs}
            
        # Stage 3: Deploy
        if not self.execute_deploy_stage():
            return {"status": "failed", "failed_at": "deploy", "logs": self.logs}

        self.logs.append("\n=== PIPELINE HOÀN TẤT THÀNH CÔNG (3/3 STAGES PASSED) ===")
        return {"status": "success", "logs": self.logs}


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sim = DocusaurusPipelineSimulator(current_dir)
    res = sim.run_pipeline()
    print("\n".join(res["logs"]))
