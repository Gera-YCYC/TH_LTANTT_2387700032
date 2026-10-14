# Bài 4 - Lab 2: JWT & OAuth Security Tools (jwt-security-tools)

## 1. Giới thiệu & Mục tiêu

Lab 2 tập trung vào việc nghiên cứu, triển khai và kiểm thử các cơ chế bảo mật xác thực hiện đại với **JSON Web Token (JWT)** và giao thức **OAuth 2.0**:
- **JWTValidator**: Kiểm tra tính toàn vẹn chữ ký, định dạng và thời hạn sống của token, xử lý chi tiết các ngoại lệ bảo mật (`ExpiredSignatureError`, `InvalidSignatureError`).
- **JWTCracker**: Thực nghiệm kỹ thuật dò khóa bí mật (brute-force dictionary attack) đối với token ký bằng thuật toán HMAC-SHA256 (`HS256`) có khóa yếu bằng cơ chế xử lý đa luồng (`ThreadPoolExecutor`).
- **OAuthClient**: Xây dựng client tương tác an toàn với Authorization Server theo chuẩn OAuth 2.0 Authorization Code Flow.
- **TokenManager**: Quản lý vòng đời token, phân định rõ ràng giữa Access Token (thời hạn ngắn) và Refresh Token (thời hạn dài) nhằm giảm thiểu rủi ro khi token bị đánh cắp.
- **APIGateway**: Triển khai API Gateway bảo vệ endpoint nội bộ `/protected`, kiểm soát quyền truy cập dựa trên HTTP Header `Authorization: Bearer <token>`.

---

## 2. Cấu trúc thư mục Lab 2

```
Bài 4/lab2/
├── docs/                       # Tài liệu & hình ảnh minh họa
│   └── images/
│       ├── step1_pytest.png           # Ảnh chụp kiểm thử 7 test cases pytest
│       ├── step2_token_gen.png        # Ảnh chụp sinh Access & Refresh Token
│       ├── step3_api_gateway_curl.png # Ảnh chụp kiểm tra xác thực bằng curl
│       └── step4_gitsecure.png        # Ảnh chụp xử lý cảnh báo bảo mật GitSecure
├── requirements.txt            # Danh sách thư viện phụ thuộc (PyJWT, requests, flask, pytest)
├── pytest.ini                  # Cấu hình pythonpath cho pytest
├── .gitignore                  # Loại bỏ cache/bytecode
├── main.py                     # Script sinh token mẫu và khởi chạy API Gateway server
├── api_gateway/                # Module API Gateway bảo vệ tài nguyên
│   └── gateway.py              # Flask server xác thực JWT Bearer header
├── jwt_cracker/                # Module Brute-force chữ ký JWT
│   └── cracker.py              # Bẻ khóa secret bằng từ điển với ThreadPoolExecutor
├── jwt_validator/              # Module thẩm định tính hợp lệ token
│   └── validator.py            # Kiểm tra chữ ký, thời hạn sống và phân loại lỗi
├── oauth_client/               # Module Client tương tác OAuth 2.0
│   └── client.py               # Sinh Authorization URL và đổi mã code lấy token
├── token_manager/              # Module quản lý vòng đời Token
│   └── manager.py              # Sinh và refresh Access Token từ Refresh Token
└── tests/                      # Bộ kiểm thử tự động Pytest
    ├── test_api_gateway.py     # Test xác thực route /protected (hợp lệ & không hợp lệ)
    ├── test_cracker.py         # Test bẻ khóa thành công secret trong wordlist
    ├── test_oauth_client.py    # Test cấu trúc URL ủy quyền OAuth 2.0
    ├── test_token_manager.py   # Test tạo cặp token và cơ chế refresh
    └── test_validator.py       # Test xác thực chữ ký đúng và phát hiện chữ ký sai
```

---

## 3. Hướng dẫn từng bước thực hiện & Hình ảnh minh họa

### Bước 1: Khởi tạo môi trường & Cài đặt thư viện phụ thuộc

1. Tạo file [requirements.txt](requirements.txt):
   ```txt
   PyJWT
   requests
   flask
   pytest
   ```
2. Cài đặt các gói phụ thuộc bằng lệnh:
   ```powershell
   pip install -r requirements.txt
   ```
3. Tạo file cấu hình [pytest.ini](pytest.ini):
   ```ini
   [pytest]
   pythonpath = .
   ```
   *Giải thích*: Cấu hình `pythonpath = .` chỉ định cho Pytest tự động nạp thư mục hiện hành vào đường dẫn tìm kiếm module của Python, giúp các file trong `tests/` có thể import trực tiếp từ `api_gateway`, `token_manager`, `jwt_validator`,... mà không gặp lỗi `ModuleNotFoundError`.

---

### Bước 2: Xây dựng Module API Gateway (`api_gateway/gateway.py`)

- **File**: [api_gateway/gateway.py](api_gateway/gateway.py)
- **Mục đích**: Cung cấp lớp cổng bảo vệ endpoint `/protected` trên ứng dụng Flask.
- **Giải thích mã nguồn**:
  - Khi client gửi request đến `/protected`, server lấy chuỗi token từ header HTTP:
    ```python
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    ```
  - Gọi `jwt.decode(token, self.secret, algorithms=[self.algorithm])`:
    - Nếu chữ ký hợp lệ và token chưa hết hạn: Trả về HTTP 200 JSON `{"message": "Access granted", "user": payload["sub"]}`.
    - Nếu token sai hoặc không hợp lệ: Bắt ngoại lệ `jwt.InvalidTokenError`, từ chối truy cập và trả về HTTP 401 JSON `{"message": "Access denied"}`.

---

### Bước 3: Xây dựng Module bẻ khóa JWT Secret (`jwt_cracker/cracker.py`)

- **File**: [jwt_cracker/cracker.py](jwt_cracker/cracker.py)
- **Mục đích**: Chứng minh nguy cơ bảo mật khi sử dụng khóa bí mật (secret key) ngắn hoặc yếu trong thuật toán đối xứng HMAC-SHA256 (`HS256`).
- **Giải thích mã nguồn**:
  - Vì JWT mang tính chất không trạng thái (stateless) và chữ ký được tính toán theo công thức công khai:
    $$\text{Signature} = \text{HMAC-SHA256}(\text{Base64Url}(\text{Header}) + "." + \text{Base64Url}(\text{Payload}), \text{Secret})$$
    kẻ tấn công có thể thử hàng triệu mật khẩu từ điển trên máy tính cá nhân (offline attack) mà không cần tương tác với server mục tiêu.
  - Class `JWTCracker` đọc danh sách ứng viên mật khẩu từ file `wordlist_path`.
  - Sử dụng `ThreadPoolExecutor(max_workers=10)` để giải mã song song. Nếu `jwt.decode` không quăng lỗi `InvalidTokenError`, secret đó chính là khóa bí mật hợp lệ và được trả về ngay lập tức.

---

### Bước 4: Xây dựng Module thẩm định JWT Validator (`jwt_validator/validator.py`)

- **File**: [jwt_validator/validator.py](jwt_validator/validator.py)
- **Mục đích**: Kiểm tra toàn diện tính hợp lệ của token và phân loại rõ ràng lý do từ chối.
- **Giải thích mã nguồn**:
  - Bắt riêng biệt từng ngoại lệ theo cấp độ:
    - `ExpiredSignatureError`: Token đã hết hạn (`exp` nhỏ hơn thời điểm hiện tại).
    - `InvalidSignatureError`: Chữ ký số không khớp (dữ liệu bị sửa đổi hoặc ký bằng secret khác).
    - `InvalidTokenError`: Định dạng token không đúng chuẩn Base64URL hoặc cấu trúc Header/Payload bị hỏng.
  - Kết quả trả về dưới dạng từ điển `{"valid": True/False, "reason": "...", "payload": ...}` thuận tiện cho việc log kiểm toán.

---

### Bước 5: Xây dựng OAuth 2.0 Client (`oauth_client/client.py`)

- **File**: [oauth_client/client.py](oauth_client/client.py)
- **Mục đích**: Hiện thực luồng xác thực chuẩn **Authorization Code Flow** của giao thức OAuth 2.0.
- **Giải thích mã nguồn**:
  - Hàm `get_auth_url(scope="openid")`: Tạo đường dẫn đưa người dùng đến Authorization Server để đăng nhập và cấp quyền, gồm các tham số: `response_type=code`, `client_id`, `redirect_uri`, và `scope`.
  - Hàm `get_token(code)`: Sau khi người dùng đồng ý ủy quyền và nhận mã `code`, client gửi request HTTP POST tới `token_url` với `grant_type=authorization_code`, kèm `client_id` và `client_secret` để đổi lấy access token chính thức mà không bao giờ cần biết mật khẩu gốc của người dùng.

---

### Bước 6: Xây dựng Module Quản lý Vòng đời Token (`token_manager/manager.py`)

- **File**: [token_manager/manager.py](token_manager/manager.py)
- **Mục đích**: Hiện thực cơ chế phân cấp token bảo vệ API.
- **Giải thích mã nguồn**:
  - `access_exp`: 15 phút (giảm thiểu thiệt hại nếu token bị chặn bắt trên đường truyền).
  - `refresh_exp`: 24 giờ (dùng để cấp lại access token mới khi hết hạn mà không bắt người dùng đăng nhập lại).
  - Hàm `generate_tokens(user_id)`: Sinh cặp `access_token` (claim `"type": "access"`) và `refresh_token` (claim `"type": "refresh"`).
  - Hàm `refresh_access_token(refresh_token)`: Xác minh tính toàn vẹn của refresh token, kiểm tra claim `"type" == "refresh"`, sau đó cấp phát một access token mới.

---

### Bước 7: Kiểm thử tự động với Pytest

Thực thi lệnh kiểm thử Pytest từ thư mục `Bài 4/lab2`:

```powershell
pytest tests
```

**Kết quả thực tế**:
```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\TH_LTANTT_2387700032\Bài 4\lab2
configfile: pytest.ini
collected 7 items

tests\test_api_gateway.py ..                                             [ 28%]
tests\test_cracker.py .                                                  [ 42%]
tests\test_oauth_client.py .                                             [ 57%]
tests\test_token_manager.py .                                            [ 71%]
tests\test_validator.py ..                                               [100%]

======================= 7 passed, 12 warnings in 0.66s ========================
```

![Bước 7: Chạy kiểm thử tự động 7 Pytest cases thành công](docs/images/step1_pytest.png)

- **Đánh giá**: Toàn bộ **7/7 test cases** đều pass thành công!
- **Giải thích các Warning**: PyJWT đưa ra cảnh báo `InsecureKeyLengthWarning: The HMAC key is ... bytes long, which is below the minimum recommended length of 32 bytes for SHA256 (RFC 7518 Section 3.2)`. Cảnh báo này phản ánh chính xác mục tiêu của bài học: khi lập trình viên dùng khóa bí mật quá ngắn (< 32 ký tự / 256 bits), hệ thống sẽ đứng trước nguy cơ bị bẻ khóa bằng kỹ thuật Brute-Force như module `JWTCracker` đã thực nghiệm.

---

### Bước 8: Khởi chạy chương trình chính & Thử nghiệm xác thực API Gateway

1. Khởi chạy [main.py](main.py):
   ```powershell
   python main.py
   ```
2. Console in ra chuỗi Access Token và Refresh Token, đồng thời bật server Flask tại cổng 5000:

![Bước 8a: Khởi chạy main.py sinh Access & Refresh Token](docs/images/step2_token_gen.png)

3. Mở Command Prompt hoặc PowerShell gửi request kèm header ủy quyền:
   ```powershell
   curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/protected
   ```
   **Kết quả phản hồi (HTTP 200)**:
   ```json
   {"message": "Access granted", "user": "phuoc"}
   ```
4. Thử nghiệm gửi request với token không hợp lệ:
   ```powershell
   curl -H "Authorization: Bearer invalid_token" http://127.0.0.1:5000/protected
   ```
   **Kết quả phản hồi (HTTP 401)**:
   ```json
   {"message": "Access denied"}
   ```

![Bước 8b: Thử nghiệm xác thực API Gateway với curl](docs/images/step3_api_gateway_curl.png)

---

### Bước 9: Bài học kinh nghiệm & Xử lý Cảnh báo Nhạy cảm khi Commit (GitSecure)

- **Vấn đề thực tế (Trang 29 của tài liệu)**:
  Khi commit code lên hệ thống Git có cài đặt công cụ kiểm tra bảo mật (như GitSecure hoặc Git Pre-commit Hook), commit bị từ chối với lỗi:
  ```
  COMMIT BLOCKED by GitSecure:
  - Sensitive info found in jwt-security-tools/main.py: pattern secret\s*=\s*['"][A-Za-z0-9_\-]{8,}['"]
  ```
- **Nguyên nhân**: Hệ thống phát hiện chuỗi khóa bí mật (secret key) được gán cứng (hard-coded) trực tiếp trong mã nguồn. Nếu kho mã nguồn được đẩy lên GitHub/GitLab, kẻ tấn công có thể quét commit history để đánh cắp khóa ký token.
- **Biện pháp khắc phục chuẩn công nghiệp**:
  1. Sử dụng biến môi trường (Environment Variable) để nạp khóa bí mật thay vì viết chuỗi tĩnh:
     ```python
     import os
     secret = os.environ["JWT_SECRET"]
     ```
  2. Lưu trữ bí mật trong file `.env` cục bộ và thêm `.env` vào file `.gitignore` để không bao giờ bị đẩy lên remote repository.
  3. Định kỳ luân chuyển khóa bí mật (Secret Key Rotation) trên môi trường triển khai thực tế.

![Bước 9: Xử lý cảnh báo rò rỉ khóa bảo mật GitSecure thành công](docs/images/step4_gitsecure.png)

---

## 4. Tổng kết đánh giá

- Hoàn thành đầy đủ 5 module bảo mật JWT theo yêu cầu của Bài thực hành 4.4.
- Đạt **100% test cases** thành công trên Pytest (7/7 tests passed).
- Hiểu rõ cơ chế bảo vệ của JWT, rủi ro khóa bí mật yếu, luồng ủy quyền OAuth 2.0 và quy tắc bảo mật mã nguồn không để lộ secret.
