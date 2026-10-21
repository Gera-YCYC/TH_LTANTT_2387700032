# Bài 5 - Lab 2: Dynamic Analysis Security Testing (dast-tool)

## 1. Giới thiệu & Mục tiêu

Lab 2 xây dựng nền tảng phân tích bảo mật động (**Dynamic Analysis Security Testing - DAST**) và kiểm thử an ninh thời gian thực (**Runtime Security Testing - RST**). Khác với SAST chỉ xem xét mã nguồn tĩnh, DAST/RST trực tiếp quan sát và giám sát hành vi ứng dụng khi nó đang thực thi trong môi trường thực tế hoặc môi trường cách ly (Sandbox).

### Các thành phần chính trong hệ thống DAST:
- **RuntimeMonitor**: Sử dụng `psutil` để giám sát tiến trình đang chạy theo thời gian thực (PID): đo lường phần trăm CPU (`get_cpu_usage`), dung lượng bộ nhớ RAM chiếm dụng (`rss`), danh sách các file descriptors / file đang mở (`open_files`).
- **MemoryAnalyzer**: Kiểm tra các bất thường trong bộ nhớ: phát hiện rò rỉ đối tượng trong bộ nhớ chưa được dọn dẹp (`gc.garbage`), và kiểm tra các số nguyên vượt quá kích thước 64-bit integer overflow (`2**63`).
- **NetworkTrafficAnalyzer**: Thu thập thống kê lưu lượng mạng trên từng card mạng vật lý và ảo (`psutil.net_io_counters(pernic=True)`): tổng byte gửi/nhận, số lượng gói tin, lỗi truyền thông.
- **SecurityBehaviorChecker**: Quét phát hiện các hành vi gọi hàm hệ thống nguy hiểm (`os.system`, `eval`, `exec`) có nguy cơ dẫn tới RCE (Remote Code Execution) hoặc leo thang đặc quyền.
- **VirtualSandbox**: Tạo thư mục tạm thời độc lập bằng `tempfile.mkdtemp()` và thực thi lệnh trong môi trường cách ly con (`subprocess.run`), ngăn ngừa phần mềm độc hại gây hại trực tiếp tới hệ thống máy chủ thật.
- **Flask RESTful Monitoring API**: Dựng web service cung cấp các API endpoints JSON giám sát trực tiếp từ xa.

---

## 2. Cấu trúc thư mục Lab 2

```
Bài 5/lab2/
├── requirements.txt                # Danh sách thư viện phụ thuộc (psutil, Flask)
├── __init__.py                     # Định danh Python package
├── memory_analyzer.py              # Phân tích rò rỉ bộ nhớ (leak) và tràn số (overflow)
├── network_traffic_analyzer.py     # Thống kê lưu lượng mạng qua card mạng
├── runtime_monitor.py              # Giám sát thông số tiến trình (CPU, RAM, files)
├── security_behavior_checker.py    # Nhận diện các lệnh gọi nguy hiểm (system, eval, exec)
├── virtual_sandbox.py              # Môi trường thực thi lệnh cách ly tạm thời
├── main.py                         # Chương trình CLI tổng hợp kiểm tra toàn bộ thành phần
├── app.py                          # Flask API phục vụ giám sát và kiểm thử DAST từ xa
└── tests/                          # Bộ kiểm thử tự động Unittest (5 test cases)
    ├── __init__.py
    ├── test_memory_analyzer.py           # Kiểm thử kiểm tra tràn số
    ├── test_network_traffic_analyzer.py  # Kiểm thử thu thập thông số mạng
    ├── test_runtime_monitor.py           # Kiểm thử đo lường CPU & RAM
    ├── test_security_behavior_checker.py # Kiểm thử phát hiện syscalls nguy hiểm
    └── test_virtual_sandbox.py           # Kiểm thử thực thi trong sandbox cô lập
```

---

## 3. Danh sách Endpoints của Flask API (`app.py`)

| Phương thức | Endpoint | Chức năng | Dữ liệu trả về mẫu |
| :---: | :--- | :--- | :--- |
| `GET` | `/api/monitor` | Giám sát CPU, bộ nhớ RAM, và file đang mở của tiến trình | `{"cpu_usage": 0.0, "memory_usage": 18456576, "open_files": [...]}` |
| `GET` | `/api/memory` | Kiểm tra rò rỉ bộ nhớ và integer overflow | `{"memory_leaks": "[]", "overflow_test": true}` |
| `GET` | `/api/network` | Thống kê gói tin và lưu lượng mạng trên các card mạng | `{"network_stats": {"Ethernet": {...}, "Wi-Fi": {...}}}` |
| `GET` | `/api/security` | Rà soát các lệnh gọi nhạy cảm | `{"suspicious_calls": ["os.system", "eval", "exec"]}` |
| `POST` | `/api/sandbox` | Chạy lệnh an toàn trong môi trường hộp cát | Request: `{"command": "echo Hello"}`<br>Response: `{"stdout": "Hello\n", "stderr": ""}` |

---

## 4. Hướng dẫn cài đặt & Thực thi

### Bước 1: Cài đặt thư viện phụ thuộc
Tại thư mục `Bài 5/lab2`:
```powershell
pip install -r requirements.txt
```

### Bước 2: Chạy kiểm thử tự động (Unit Test)
Chạy toàn bộ 5 bài kiểm thử tự động:
```powershell
python -m unittest discover -s tests
```
**Kết quả mong đợi:**
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 1.113s

OK
```

### Bước 3: Chạy ứng dụng kiểm tra toàn diện qua CLI
Chạy file [main.py](main.py):
```powershell
python main.py
```
**Kết quả thực tế:**
```text
[+] Monitoring current process: 6984
CPU Usage: 0.0
Memory Usage: 16826368
Open Files: [popenfile(path='C:\\Windows\\System32\\en-US\\KernelBase.dll.mui', fd=-1)]
Memory Leaks: []
Overflow Test: True
Network Stats: {'Wi-Fi': snetio(...), ...}
Suspicious Calls: ['os.system', 'eval', 'exec']
Sandbox stdout: Hello Sandbox
Sandbox stderr: 
```

### Bước 4: Khởi chạy Flask Server & Kiểm thử API
Khởi động server API:
```powershell
python app.py
```
Truy cập các endpoint từ trình duyệt hoặc công cụ gửi request (cURL / Postman / PowerShell):
```powershell
# Kiểm tra endpoint giám sát tiến trình
curl http://127.0.0.1:5000/api/monitor

# Kiểm tra endpoint bộ nhớ
curl http://127.0.0.1:5000/api/memory

# Thực thi lệnh trong sandbox qua POST request
curl -X POST http://127.0.0.1:5000/api/sandbox -H "Content-Type: application/json" -d "{\"command\":\"echo Test\"}"
```

---

## 5. Tóm tắt Kiến thức Lý thuyết Cốt lõi

1. **Runtime Security Testing (RST)**:
   - Theo dõi và phát hiện các rủi ro chỉ phát sinh khi phần mềm chạy: rò rỉ vùng nhớ, race condition, truy cập tài nguyên bất thường.

2. **Phân tích hành vi (Behavioral Analysis)**:
   - Thay vì kiểm tra theo chữ ký mã (signature-based), phân tích hành vi quan sát các tương tác giữa tiến trình và hệ điều hành (System calls, Network sockets, File I/O) để cảnh báo kịp thời hành vi bất thường.

3. **Môi trường Sandbox (Hộp cát)**:
   - Cơ chế cách ly tài nguyên đảm bảo các lệnh thực thi không thể làm thay đổi hệ thống tệp tin hoặc trạng thái của hệ điều hành chính.
