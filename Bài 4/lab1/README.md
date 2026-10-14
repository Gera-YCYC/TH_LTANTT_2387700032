# Bài 4 - Lab 1: Web Vulnerability Scanner (web-vuln-scanner)

## 1. Giới thiệu & Mục tiêu

Lab 1 tập trung xây dựng một công cụ quét và phát hiện các lỗ hổng ứng dụng web phổ biến theo chuẩn OWASP:
- **XSS (Cross-Site Scripting)**: Phát hiện lỗ hổng phản hồi mã độc JavaScript thông qua payload chuẩn hóa.
- **SQL Injection (SQLi)**: Kiểm thử các biến thể bypass xác thực, UNION-based và lệnh ngắt câu truy vấn cơ sở dữ liệu.
- **CSRF (Cross-Site Request Forgery)**: Phân tích biểu mẫu HTML để kiểm tra sự hiện diện của token chống giả mạo request (`csrf_token`, `_csrf`, `csrfmiddlewaretoken`).
- **SSRF (Server-Side Request Forgery)**: Phát hiện các tham số truyền URL có nguy cơ trỏ tới mạng nội bộ (`localhost`, `127.0.0.1`, dải IP riêng RFC 1918).
- **Report Generator**: Cơ chế tổng hợp các cảnh báo bảo mật theo mức độ rủi ro (`Critical`, `High`, `Medium`, `Low`).
- **Flask Web UI**: Cung cấp giao diện trực quan cho phép người dùng nhập URL, chọn loại scanner và theo dõi báo cáo kết quả.

---

## 2. Cấu trúc thư mục Lab 1

```
Bài 4/lab1/
├── docs/                       # Tài liệu & hình ảnh minh họa
│   └── images/
│       ├── step1_unittest.png       # Ảnh chụp chạy kiểm thử 9 unittests
│       ├── step2_cli_scan.png       # Ảnh chụp quét lỗ hổng qua CLI main.py
│       ├── step3_web_ui.png         # Ảnh chụp giao diện Web UI Flask
│       └── step4_scan_results.png   # Ảnh chụp kết quả phân loại rủi ro trên Web
├── requirements.txt            # Danh sách thư viện phụ thuộc (Flask, requests)
├── pytest.ini                  # Cấu hình test runner
├── .gitignore                  # Loại bỏ cache/bytecode
├── main.py                     # Script chạy CLI kiểm thử nhanh các scanner
├── scanners/                   # Các module quét lỗ hổng
│   ├── csrf_detector.py        # Module phát hiện thiếu CSRF token
│   ├── sql_injection_tester.py # Module kiểm tra SQL Injection trong URL query
│   ├── ssrf_tester.py          # Module phát hiện nguy cơ SSRF truy cập IP nội bộ
│   └── xss_scanner.py          # Module quét Reflected XSS với payload chuẩn hóa
├── report/                     # Module tổng hợp báo cáo
│   └── report_generator.py     # Hợp nhất các findings thành cấu trúc chuẩn
├── tests/                      # Bộ kiểm thử tự động Unittest
│   ├── test_csrf.py            # Test kiểm tra CSRF detector
│   ├── test_sql_injection.py   # Test phát hiện SQLi và URL an toàn
│   ├── test_ssrf.py            # Test phát hiện SSRF và IP hợp lệ
│   ├── test_xss.py             # Test giả lập (mock) quét XSS
│   └── test_report.py          # Test cấu trúc báo cáo (list & dict)
└── ui/                         # Giao diện Web Flask
    ├── app.py                  # Web server backend xử lý form kiểm thử
    └── templates/              # Giao diện HTML
        ├── index.html          # Trang form nhập URL và chọn scanner
        └── result.html         # Trang hiển thị kết quả phân loại theo mức rủi ro
```

---

## 3. Hướng dẫn từng bước thực hiện & Hình ảnh minh họa

### Bước 1: Khởi tạo môi trường & Cài đặt thư viện phụ thuộc

1. Tạo file [requirements.txt](requirements.txt) khai báo:
   ```txt
   Flask
   requests
   ```
2. Cài đặt các gói phụ thuộc bằng lệnh:
   ```powershell
   pip install -r requirements.txt
   ```
   *Giải thích*: `Flask` dùng để dựng web server cho UI kiểm thử cục bộ; `requests` dùng để gửi các HTTP GET request kèm payload kiểm thử lỗ hổng XSS đến web đích.

---

### Bước 2: Xây dựng Module kiểm tra CSRF (`scanners/csrf_detector.py`)

- **File**: [scanners/csrf_detector.py](scanners/csrf_detector.py)
- **Mục đích**: CSRF (Cross-Site Request Forgery) xảy ra khi ứng dụng web không có cơ chế xác nhận request đến từ chính người dùng hay từ trang thứ ba. Cách phòng chống phổ biến là nhúng **CSRF token bí mật** vào mỗi biểu mẫu.
- **Giải thích mã nguồn**:
  - Khai báo danh sách các Regular Expression (`csrf_token_patterns`) tương ứng các tên token phổ biến trong các framework như Django (`csrfmiddlewaretoken`), Spring Security (`_csrf`), hoặc chuẩn chung (`csrf_token`).
  - Hàm `scan(html_content)` duyệt qua nội dung mã HTML:
    - Nếu tìm thấy pattern token -> Trả về `{'csrf_protected': True}`.
    - Nếu không tìm thấy -> Trả về `{'csrf_protected': False, 'desc': 'No CSRF token found, vulnerable to CSRF', 'risk': 'Medium'}`.

---

### Bước 3: Xây dựng Module kiểm tra SQL Injection (`scanners/sql_injection_tester.py`)

- **File**: [scanners/sql_injection_tester.py](scanners/sql_injection_tester.py)
- **Mục đích**: Phát hiện các tham số trên query string của URL chứa các payload đặc trưng của tấn công SQL Injection.
- **Giải thích mã nguồn**:
  - Khởi tạo thư viện payload mẫu:
    - `' OR '1'='1`: Tấn công logic vượt qua xác thực (Classic SQLi).
    - `'; DROP TABLE users;--`: Tấn công thực thi nhiều câu lệnh (Stacked Query).
    - `" OR 1=1--`: Tấn công logic dạng chuỗi dấu nháy kép.
    - `' UNION SELECT NULL--`: Kỹ thuật khai thác UNION-based SQLi.
  - Hàm `scan(url)`: Sử dụng `urllib.parse.urlparse` và `parse_qs` để tách từng cặp tham số (`param: value`) từ URL. Nếu bất kỳ giá trị nào chứa payload SQLi đã định nghĩa, hệ thống ghi nhận một finding có mức độ rủi ro là `Critical`.

---

### Bước 4: Xây dựng Module phát hiện SSRF (`scanners/ssrf_tester.py`)

- **File**: [scanners/ssrf_tester.py](scanners/ssrf_tester.py)
- **Mục đích**: SSRF (Server-Side Request Forgery) xảy ra khi server nhận một URL từ client và fetch nội dung của URL đó mà không kiểm duyệt, dẫn tới khả năng truy cập các dịch vụ nội bộ hoặc Cloud Metadata (như `169.254.169.254` trên AWS).
- **Giải thích mã nguồn**:
  - Định nghĩa tập regex nhận dạng dải mạng nội bộ (Internal/Private IPs):
    - `127.0.0.1` và `localhost` (Loopback interface).
    - `10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12` (Dải địa chỉ IP riêng theo RFC 1918).
  - Hàm `scan(url)` tách query string của URL và kiểm tra giá trị tham số. Nếu xuất hiện địa chỉ IP nội bộ, cảnh báo nguy cơ SSRF với mức độ rủi ro `High`.

---

### Bước 5: Xây dựng Module quét Reflected XSS (`scanners/xss_scanner.py`)

- **File**: [scanners/xss_scanner.py](scanners/xss_scanner.py)
- **Mục đích**: Tự động gửi request chứa các payload script XSS và kiểm tra phản hồi từ máy chủ.
- **Giải thích mã nguồn**:
  - Chuẩn bị danh sách payload:
    - `<script>alert(1)</script>` (Thẻ script kinh điển).
    - `'><svg/onload=alert(1)>` (Thẻ SVG với event handler nhằm bypass bộ lọc thẻ script).
  - Hàm `scan(url)` gửi HTTP GET tới `url?q=<payload>` với `timeout=5`.
  - Nếu payload xuất hiện nguyên vẹn trong nội dung HTML phản hồi (`payload in resp.text`), điều đó chứng minh máy chủ không thực hiện Output Encoding hoặc Input Sanitization, gán nhãn nguy cơ `HIGH`.

---

### Bước 6: Xây dựng Module tạo báo cáo tập trung (`report/report_generator.py`)

- **File**: [report/report_generator.py](report/report_generator.py)
- **Mục đích**: Nhận kết quả từ nhiều module quét độc lập và hợp nhất thành một định dạng báo cáo duy nhất chuẩn hóa:
  ```json
  {
    "vulnerabilities": [
      { "param": "id", "desc": "Potential SQL Injection", "risk": "Critical" },
      { "param": "url", "desc": "Potential SSRF to internal resource", "risk": "High" }
    ]
  }
  ```
- **Giải thích mã nguồn**: Phương thức `generate(findings_list)` hỗ trợ cả đầu vào dạng danh sách con (nested list) lẫn từ điển đơn lẻ (dictionary), giúp các scanner có thể tích hợp linh hoạt.

---

### Bước 7: Kiểm thử tự động với Unittest

Chạy toàn bộ 9 bài kiểm thử đơn vị tự động từ thư mục `Bài 4/lab1`:

```powershell
python -m unittest discover tests
```

**Kết quả thực tế**:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.003s

OK
```

![Bước 7: Chạy kiểm thử tự động 9 Unittests thành công](docs/images/step1_unittest.png)

- `test_csrf.py`: Kiểm thử trường hợp form có chứa thẻ CSRF token và trường hợp thiếu token.
- `test_sql_injection.py`: Kiểm thử URL chứa payload `' OR '1'='1` (phát hiện lỗi) và URL tham số bình thường (không cảnh báo).
- `test_ssrf.py`: Kiểm thử URL truyền `http://127.0.0.1/admin` (phát hiện SSRF) và URL public thông thường.
- `test_xss.py`: Sử dụng `unittest.mock.patch` mô phỏng phản hồi từ `requests.get` để kiểm thử logic phát hiện XSS độc lập với mạng ngoài.
- `test_report.py`: Kiểm thử tính đúng đắn khi hợp nhất các findings dạng list và dict.

---

### Bước 8: Chạy chương trình chính CLI (`main.py`)

Thực thi file [main.py](main.py) để chạy thử nghiệm tổng hợp:

```powershell
python main.py
```

**Kết quả xuất ra màn hình Console**:
```
=== Vulnerability Report ===
Param: id, Desc: Potential SQL Injection, Risk: Critical
Param: N/A, Desc: None, Risk: None
Param: url, Desc: Potential SSRF to internal resource, Risk: High
```

![Bước 8: Kết quả thực thi chương trình quét CLI main.py](docs/images/step2_cli_scan.png)

*Phân tích*: URL mẫu kiểm thử chứa đồng thời tham số SQLi và SSRF nên cả 2 lỗ hổng đều được phát hiện chính xác; form HTML mẫu chứa CSRF token hợp lệ nên không cảnh báo lỗ hổng CSRF.

---

### Bước 9: Khởi chạy Giao diện Web UI Flask

1. Khởi động Web Server tại cổng 5000:
   ```powershell
   python ui/app.py
   ```
2. Mở trình duyệt truy cập: `http://127.0.0.1:5000/`

![Bước 9a: Giao diện Web Vulnerability Scanner](docs/images/step3_web_ui.png)

3. Điền URL mục tiêu cần kiểm tra, ví dụ:
   ```
   http://testphp.vulnweb.com/artists.php?artist=1' OR '1'='1
   ```
   Hoặc kiểm thử SSRF:
   ```
   http://example.com/fetch?url=http://127.0.0.1:8080/admin
   ```
4. Chọn các công cụ kiểm thử (XSS Scanner, SQL Injection Tester, CSRF Detector, SSRF Tester) và nhấn nút **Bắt đầu kiểm thử**.
5. Màn hình kết quả sẽ hiển thị chi tiết:
   - Loại lỗ hổng
   - Vị trí tham số bị tấn công (`param`)
   - Mô tả chi tiết nguy cơ
   - Mức độ rủi ro với viền và nền màu trực quan (`Critical`/`HIGH` màu đỏ, `MEDIUM` màu vàng cam, `LOW` màu xanh lá).

![Bước 9b: Kết quả phân loại lỗ hổng trực quan trên Web UI](docs/images/step4_scan_results.png)

---

## 4. Tổng kết đánh giá

- Công cụ đã hoàn thiện đầy đủ 5 thành phần theo yêu cầu của Bài thực hành 4.2.
- Kiến trúc module hóa cao, tách biệt rõ ràng giữa logic quét ([scanners/](scanners/)), logic tổng hợp báo cáo ([report/](report/)), giao diện hiển thị ([ui/](ui/)) và kiểm thử ([tests/](tests/)).
- Đạt tỷ lệ vượt qua bài kiểm thử **100% (9/9 unittests)**.
