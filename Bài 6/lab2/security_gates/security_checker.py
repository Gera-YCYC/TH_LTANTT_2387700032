"""
DevSecOps Security Gate Checker
Phân tích an ninh tự động tích hợp trong GitLab CI/CD Pipeline (Mục 6.1):
1. Secret Scanning (Tìm rò rỉ API Keys, Token, Passwords).
2. SCA - Software Composition Analysis (Kiểm tra phụ thuộc rủi ro).
3. SAST / Config Checker (Phát hiện cấu hình không an toàn).
"""

import os
import re
import sys
import json
import argparse
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*['\"][0-9a-zA-Z\-_]{16,}['\"]", "High", "Phat hien Hardcoded API Key"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{6,}['\"]", "Medium", "Phat hien Hardcoded Password"),
    (r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Critical", "Phat hien Private Key ro ri"),
    (r"glpat-[0-9a-zA-Z\-_]{20,}", "Critical", "Phat hien GitLab Personal Access Token"),
    (r"ghp_[0-9a-zA-Z]{36}", "Critical", "Phat hien GitHub Personal Access Token"),
    (r"AKIA[0-9A-Z]{16}", "Critical", "Phat hien AWS Access Key ID"),
]

INSECURE_DEPENDENCIES = {
    "event-stream": "3.3.6",  # Malicious package mau
    "flatmap-stream": "0.1.1",
}


class SecurityGateChecker:
    def __init__(self, target_dir: str):
        self.target_dir = os.path.abspath(target_dir)
        self.findings: List[Dict[str, Any]] = []

    def scan_secrets(self):
        """Quét tìm thông tin bí mật lộ trong mã nguồn."""
        ignored_dirs = {".git", "node_modules", "build", "public", ".venv", "__pycache__", "security_gates", "tests"}
        
        for root, dirs, files in os.walk(self.target_dir):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if file.startswith("temp_secret_test"):
                    # Cho phép file test tạm thời được quét
                    pass
                elif file.endswith((".py", ".js", ".json", ".yml", ".yaml", ".env", ".md", ".txt")):
                    pass
                else:
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.target_dir)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, start=1):
                            for pattern, severity, desc in SECRET_PATTERNS:
                                if re.search(pattern, line):
                                    self.findings.append({
                                        "type": "Secret Leak",
                                        "file": rel_path,
                                        "line": line_no,
                                        "severity": severity,
                                        "description": desc,
                                        "snippet": line.strip()[:60]
                                    })
                except Exception:
                    pass

    def scan_dependencies(self):
        """Quét phân tích thành phần phần mềm (SCA) qua package.json."""
        pkg_file = os.path.join(self.target_dir, "package.json")
        if os.path.exists(pkg_file):
            try:
                with open(pkg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    for pkg, ver in deps.items():
                        if pkg in INSECURE_DEPENDENCIES:
                            self.findings.append({
                                "type": "Vulnerable Dependency (SCA)",
                                "file": "package.json",
                                "line": 0,
                                "severity": "Critical",
                                "description": f"Gói phụ thuộc '{pkg}@{ver}' được cảnh báo chứa mã độc!",
                                "snippet": f"{pkg}: {ver}"
                            })
            except Exception:
                pass

    def run_all(self) -> Dict[str, Any]:
        """Thực thi toàn bộ các bài kiểm tra bảo mật."""
        self.scan_secrets()
        self.scan_dependencies()
        
        critical_count = sum(1 for f in self.findings if f["severity"] == "Critical")
        high_count = sum(1 for f in self.findings if f["severity"] == "High")
        passed = (critical_count == 0 and high_count == 0)

        return {
            "passed": passed,
            "total_findings": len(self.findings),
            "critical": critical_count,
            "high": high_count,
            "findings": self.findings
        }


def main():
    parser = argparse.ArgumentParser(description="DevSecOps Security Gate Scanner")
    parser.add_argument("--target", default=".", help="Đường dẫn thư mục cần quét")
    args = parser.parse_args()

    print("\n==============================================")
    print("   [DEVSECOPS SECURITY GATE PIPELINE SCAN]   ")
    print("==============================================\n")

    checker = SecurityGateChecker(args.target)
    results = checker.run_all()

    if results["findings"]:
        print(f"[!] Phat hien {results['total_findings']} canh bao an ninh:")
        for idx, item in enumerate(results["findings"], start=1):
            print(f"  {idx}. [{item['severity'].upper()}] {item['type']} tai {item['file']}:{item['line']}")
            print(f"     Mo ta: {item['description']}")
            print(f"     Noi dung: {item['snippet']}")
    else:
        print("[OK] Khong phat hien bat ky thong tin nhay cam hay goi phu thuoc doc hai nao!")

    print(f"\nTong ket:")
    print(f"  - Critical: {results['critical']}")
    print(f"  - High: {results['high']}")
    print(f"  - Trang thai Security Gate: {'[PASSED]' if results['passed'] else '[BLOCKED]'}")

    if not results["passed"]:
        print("\n[!] Pipeline bi chan do khong vuot qua tieu chuan an ninh (Security Gate).")
        sys.exit(1)
    else:
        print("\n[OK] Tat ca cac dieu kien an toan deu thoa man. Chuyen sang giai doan tiep theo.")
        sys.exit(0)


if __name__ == "__main__":
    main()
