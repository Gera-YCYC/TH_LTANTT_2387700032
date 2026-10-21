# Bài 5 - Lab 1: Static Analysis Security Testing (sast-tool)

## 1. Giới thiệu & Mục tiêu

Lab 1 tập trung xây dựng công cụ phân tích bảo mật tĩnh (**Static Analysis Security Testing - SAST**) dành cho mã nguồn Python. Công cụ phân tích cú pháp và ngữ nghĩa của mã nguồn mà không cần thực thi chương trình, giúp phát hiện sớm các lỗ hổng bảo mật ngay trong quá trình phát triển (Shift-Left Security).

### Các thành phần chính trong hệ thống SAST:
- **ASTAnalyzer**: Phân tích cây cú pháp trừu tượng (Abstract Syntax Tree) bằng thư viện chuẩn `ast` của Python để phát hiện các hàm tiềm ẩn nguy cơ cao như `eval()`.
- **VulnPatternMatcher**: Nhận diện và ánh xạ các mẫu mã độc hại (Pattern Matching) bằng Regex: phát hiện hardcoded password, import thư viện nguy hiểm (`pickle` deserialization).
- **SecurityRuleEngine**: Hệ thống luật bảo mật linh hoạt dựa trên cấu hình JSON (`rules/default_rules.json`), tự động gán mức độ nghiêm trọng (`high`, `medium`, `low`) cho từng phát hiện.
- **CodeQualityChecker**: Đánh giá chất lượng mã nguồn thông qua `flake8`, đo lường các vấn đề định dạng và code smell để giảm thiểu rủi ro bảo mật.
- **SarifReporter**: Xuất kết quả kiểm tra theo định dạng tiêu chuẩn quốc tế **SARIF** (Static Analysis Results Interchange Format v2.1.0), tương thích với GitHub Advanced Security và VSCode SARIF Viewer.

---

## 2. Cấu trúc thư mục Lab 1

```
Bài 5/lab1/
├── requirements.txt            # Danh sách thư viện phụ thuộc (flake8, sarif-om, jsonpickle)
├── examples/                   # Mã nguồn mẫu dùng để kiểm thử quét lỗ hổng
│   ├── vulnerable_01.py        # Mẫu chứa hardcoded password, import pickle, eval()
│   └── vulnerable_02.py        # Mẫu chứa dangerous eval(), file read, exec()
├── rules/                      # Cấu hình luật bảo mật
│   └── default_rules.json      # Quy tắc phân loại mức độ nghiêm trọng (high, medium, low)
├── sast_tool/                  # Gói mã nguồn công cụ SAST
│   ├── __init__.py             # Định danh Python package
│   ├── ast_analyzer.py         # Phân tích AST phát hiện hàm nguy hiểm (eval)
│   ├── code_quality_checker.py # Tích hợp flake8 kiểm tra chất lượng mã
│   ├── main.py                 # Điểm khởi chạy CLI chính phân tích file mã nguồn
│   ├── sarif_reporter.py       # Bộ xuất báo cáo chuẩn SARIF v2.1.0
│   ├── security_rule_engine.py # Động cơ đối chiếu luật bảo mật
│   └── vuln_pattern_matcher.py # Nhận diện mẫu Regex (hardcoded credentials, pickle)
└── tests/                      # Bộ kiểm thử tự động Unittest (6 test cases)
    ├── __init__.py
    ├── test_ast_analyzer.py          # Kiểm thử phân tích AST
    ├── test_code_quality_checker.py  # Kiểm thử flake8 linter
    ├── test_sarif_reporter.py        # Kiểm thử sinh file SARIF
    ├── test_security_rule_engine.py  # Kiểm thử gán severity theo rules
    └── test_vuln_pattern_matcher.py  # Kiểm thử regex pattern matching
```

---

## 3. Hướng dẫn cài đặt & Thực thi

### Bước 1: Cài đặt thư viện phụ thuộc
Tại thư mục `Bài 5/lab1`, cài đặt các gói cần thiết:
```powershell
pip install -r requirements.txt
```

### Bước 2: Chạy kiểm thử tự động (Unit Test)
Chạy toàn bộ 6 bài kiểm thử tự động với `unittest`:
```powershell
python -m unittest discover tests
```
**Kết quả mong đợi:**
```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.979s

OK
```

### Bước 3: Phân tích file mã nguồn không an toàn mẫu
1. Kiểm tra file mẫu `vulnerable_01.py`:
```powershell
python -m sast_tool.main .\examples\vulnerable_01.py
```
Output:
```text
Analysis complete.
    Report saved to report.sarif with 5 issues.
```

2. Kiểm tra file mẫu `vulnerable_02.py`:
```powershell
python -m sast_tool.main .\examples\vulnerable_02.py
```
Output:
```text
Analysis complete.
    Report saved to report.sarif with 1 issues.
```

### Bước 4: Xem báo cáo trên Visual Studio Code (SARIF Viewer)
1. Cài đặt extension **SARIF Viewer** từ Microsoft trên VSCode.
2. Mở file [report.sarif](report.sarif) đã tạo ra sau khi quét.
3. Extension sẽ trực quan hóa danh sách các lỗi, vị trí dòng, cột và mức độ rủi ro tương ứng trong mã nguồn.

---

## 4. Tóm tắt Kiến thức Lý thuyết Cốt lõi

1. **AST (Abstract Syntax Tree)**:
   - Đại diện cấu trúc cú pháp của mã nguồn dưới dạng cây logic, bỏ qua các chi tiết không quan trọng như khoảng trắng hoặc dấu chấm phẩy.
   - Thư viện `ast` của Python cho phép duyệt qua các node (`ast.walk`), tìm kiếm các hàm gọi rủi ro như `ast.Call` với identifier `eval` hoặc `exec`.

2. **Pattern Matching**:
   - Khác với tìm kiếm từ khóa đơn thuần, pattern matching kiểm tra ngữ cảnh dựa trên biểu thức chính quy (Regex) hoặc cấu trúc câu lệnh.
   - Phát hiện các mẫu rò rỉ secret: `password\s*=\s*".*"` hoặc module nguy hiểm `import\s+pickle`.

3. **SARIF Standard (Static Analysis Results Interchange Format)**:
   - Định dạng chuẩn JSON do OASIS ban hành giúp chuẩn hóa đầu ra của mọi công cụ SAST/DAST, tạo điều kiện tích hợp liền mạch vào CI/CD pipelines (GitHub Actions, GitLab CI).
