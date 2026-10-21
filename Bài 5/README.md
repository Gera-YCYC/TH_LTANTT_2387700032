# Bài 5: Phân tích và Kiểm thử Bảo mật

Tài liệu hướng dẫn chi tiết, tóm tắt lý thuyết và báo cáo thực hành toàn diện cho **Bài 5: Phân tích và Kiểm thử Bảo mật** (Static Analysis Security Testing & Dynamic Analysis Security Testing).

---

## 📑 Danh mục các bài Lab

| Bài Lab | Tên Dự Án | Mô tả Trọng Tâm | Trạng Thái Kiểm Thử | Báo Cáo Chi Tiết |
| :--- | :--- | :--- | :---: | :---: |
| **Lab 1** | **sast-tool** | Phân tích mã nguồn tĩnh (SAST): phân tích cây cú pháp trừu tượng AST (`ast`), nhận diện mẫu mã độc hại (`re`), động cơ luật bảo mật (`SecurityRuleEngine`), kiểm tra chất lượng mã (`flake8`), và xuất báo cáo chuẩn quốc tế SARIF (`sarif-om`). | **6/6 Passed** (100%) | [Xem Báo Cáo Lab 1](lab1/README.md) |
| **Lab 2** | **dast-tool** | Phân tích an ninh động (DAST) & thời gian thực (RST): giám sát tiến trình hệ thống (`RuntimeMonitor`), kiểm tra rò rỉ bộ nhớ & integer overflow (`MemoryAnalyzer`), phân tích lưu lượng mạng (`NetworkTrafficAnalyzer`), phát hiện hàm gọi nguy hiểm (`SecurityBehaviorChecker`), hộp cát cách ly (`VirtualSandbox`) và Flask REST API. | **5/5 Passed** (100%) | [Xem Báo Cáo Lab 2](lab2/README.md) |

---

## 1. 🔍 [Lab 1 - Static Analysis Security Testing (sast-tool)](lab1/README.md)

* **Thư mục thực hành**: `Bài 5/lab1/`
* **Mục tiêu**: Xây dựng công cụ kiểm thử bảo mật tĩnh (SAST) nhằm phát hiện sớm các lỗi cú pháp, lỗ hổng tiềm ẩn, và vi phạm chuẩn coding ngay trên mã nguồn trước khi biên dịch hay chạy chương trình.
* **Chi tiết từng bước**: Xem thêm tại [Báo cáo chi tiết Lab 1](lab1/README.md).

### Các bước thực hiện & Kết quả kiểm thử Lab 1:

1. **Chạy kiểm thử tự động (Unit Test 6/6 OK)**:
   ```powershell
   cd "d:\TH_LTANTT_2387700032\Bài 5\lab1"
   python -m unittest discover tests
   ```
   *Kết quả*: 6 test cases đều vượt qua thành công:
   - `test_eval_detection`: Phát hiện chính xác hàm `eval()` thông qua cây AST.
   - `test_flake8_detection`: Kiểm tra phân tích chất lượng mã nguồn bằng flake8.
   - `test_generate_report`: Xác thực việc sinh file báo cáo định dạng SARIF v2.1.0.
   - `test_evaluate`: Kiểm thử ánh xạ mức độ nghiêm trọng (`severity`) theo luật.
   - `test_hardcoded_password`: Bắt được biến password gán cứng trong mã nguồn.
   - `test_pickle_import`: Cảnh báo rủi ro deserialization khi import `pickle`.

2. **Quét phân tích các file mã nguồn mẫu**:
   ```powershell
   python -m sast_tool.main .\examples\vulnerable_01.py
   python -m sast_tool.main .\examples\vulnerable_02.py
   ```
   *Kết quả*: Sinh file `report.sarif` chứa danh sách chi tiết các phát hiện và vị trí dòng/cột.

---

## 2. 🛡️ [Lab 2 - Dynamic Analysis Security Testing (dast-tool)](lab2/README.md)

* **Thư mục thực hành**: `Bài 5/lab2/`
* **Mục tiêu**: Xây dựng nền tảng phân tích động (DAST) và kiểm thử an ninh thời gian thực (RST) để giám sát và phát hiện các mối nguy chỉ xuất hiện trong quá trình thực thi ứng dụng.
* **Chi tiết từng bước**: Xem thêm tại [Báo cáo chi tiết Lab 2](lab2/README.md).

### Các bước thực hiện & Kết quả kiểm thử Lab 2:

1. **Chạy kiểm thử tự động (Unit Test 5/5 OK)**:
   ```powershell
   cd "d:\TH_LTANTT_2387700032\Bài 5\lab2"
   python -m unittest discover -s tests
   ```
   *Kết quả*: 5 test cases đều vượt qua thành công:
   - `test_check_overflow`: Kiểm tra phát hiện tràn số nguyên vượt ngưỡng 64-bit (`2**63`).
   - `test_get_network_stats`: Thu thập thống kê thông số mạng trên toàn bộ card mạng.
   - `test_cpu_and_memory`: Giám sát mức sử dụng CPU và bộ nhớ RAM của tiến trình.
   - `test_suspicious_calls`: Rà soát các lệnh gọi nhạy cảm (`os.system`, `eval`, `exec`).
   - `test_run_isolated`: Kiểm thử thực thi lệnh cô lập an toàn trong Sandbox tạm thời.

2. **Khởi chạy ứng dụng CLI tổng hợp**:
   ```powershell
   python main.py
   ```
   *Kết quả*: In ra đầy đủ thông số thời gian thực của tiến trình, bộ nhớ, mạng và kết quả thực thi trong Virtual Sandbox.

3. **Khởi chạy và giám sát qua Flask API**:
   ```powershell
   python app.py
   ```
   Hỗ trợ các REST API endpoints:
   - `GET /api/monitor`: Giám sát tiến trình CPU, RAM, file đang mở.
   - `GET /api/memory`: Kiểm tra rò rỉ bộ nhớ và tràn số nguyên.
   - `GET /api/network`: Thống kê gói tin và lưu lượng mạng theo từng card mạng.
   - `GET /api/security`: Cảnh báo các lệnh gọi nhạy cảm.
   - `POST /api/sandbox`: Thực thi câu lệnh trong môi trường hộp cát cô lập.

---

## 3. 📚 Tóm tắt Lý thuyết Cốt lõi Bài 5

### 3.1. Static Analysis Security Testing (SAST)
- **Cây cú pháp trừu tượng (AST)**: Biểu diễn cấu trúc ngữ pháp logic của code dưới dạng cây; mỗi nút đại diện cho một thành phần ngôn ngữ (hàm, biểu thức, biến). AST cho phép phân tích mã mà không cần thực thi, duyệt qua các node để tìm kiếm hành vi rủi ro (`ast.Call` của `eval`).
- **Kỹ thuật Pattern Matching**:
  - *Literal pattern*: Tìm trực tiếp chuỗi cố định (`os.system`, `eval`).
  - *Structural pattern*: Dựa vào cấu trúc AST.
  - *Semantic pattern*: Phân tích luồng dữ liệu (Taint Analysis: input người dùng -> xử lý -> thực thi).
- **Code Quality Metrics**: Đo lường độ phức tạp (Cyclomatic Complexity), độ dài hàm, độ lồng nhau (Nested Depth), và mật độ mã có mùi nguy hiểm (Security Smell Density).
- **Chuẩn SARIF**: Định dạng JSON tiêu chuẩn trao đổi kết quả kiểm thử tĩnh giữa các công cụ bảo mật và môi trường IDE / CI-CD.

### 3.2. Dynamic Analysis Security Testing (DAST)
- **Runtime Security Testing (RST)**: Theo dõi hành vi phần mềm khi đang chạy nhằm phát hiện lỗi bộ nhớ, injection trong runtime, lỗi logic, và hành vi bất thường.
- **Phân tích hành vi (Behavioral Analysis)**: Đánh giá hành vi theo thời gian thực thay vì so khớp chữ ký cố định; bao gồm Rule-based detection, Heuristic Analysis, Anomaly Detection và Machine Learning.
- **Phân tích trong môi trường hộp cát (Sandbox Analysis)**: Môi trường ảo hóa (VM), container (Docker/LXC), hoặc temporary isolated directory giúp cô lập ứng dụng không rõ nguồn gốc, phòng chống rủi ro gây hại tới máy chủ thật.
