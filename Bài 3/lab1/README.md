# Bài 3 - Lab 1: SecureChat

## Mục tiêu

Xây dựng chat TCP đa luồng có TLS hai chiều (mTLS), xác minh chứng chỉ CA, nhiều phòng và mã hóa đầu-cuối AES-GCM. Server chỉ định tuyến ciphertext, không nhận khóa mã hóa nội dung.

## Chuẩn bị & Cài đặt

1. Cài Python 3.10+ và OpenSSL 1.1.1+; kiểm tra bằng:
   ```powershell
   python --version
   openssl version
   ```
2. Mở PowerShell tại thư mục `Bài 3/lab1`, tạo môi trường ảo và cài thư viện:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
3. Chạy kiểm thử tự động: `python -m pytest -q`.

---

## Hướng dẫn từng bước & Chạy Demo (Step-by-Step Demo)

### Bước 1: Phát hành Chứng chỉ TLS x509 hai chiều (mTLS)

Chạy script PowerShell `make-certs.ps1` để tự động khởi tạo Root CA (`ca.crt`, `ca.key`), Server Certificate (`server.crt`, `server.key` với CN `localhost`) và Client Certificate (`client.crt`, `client.key` với CN `securechat-client`):

```powershell
.\make-certs.ps1
```

*(Nếu PowerShell chặn script, chạy `Set-ExecutionPolicy -Scope Process Bypass` trước).*

![Bước 1: Sinh chứng chỉ CA, Server và Client bằng OpenSSL](docs/images/step1_cert_gen.png)

---

### Bước 2: Khởi chạy SecureChat TLS Server

Mở Terminal thứ nhất tại `Bài 3/lab1` và khởi chạy server TCP socket có bọc TLS/SSL Context:

```powershell
python -m securechat.server
```

Server yêu cầu mTLS (`CERT_REQUIRED`), xác thực chứng chỉ client thông qua Root CA và lắng nghe các kết nối bảo mật.

![Bước 2: Khởi chạy SecureChat TLS Server](docs/images/step2_server_start.png)

---

### Bước 3: Khởi chạy Client A (Alice) & Tham gia Phòng Chat

Mở Terminal thứ hai tại `Bài 3/lab1`. Đặt secret dùng chung mã hóa AES-GCM (ngoài băng) và khởi chạy client:

```powershell
$env:SECURECHAT_E2E_SECRET = "CyberChatSharedKey2026Secret!"
python -m securechat.client
```

Nhập tên người dùng (ví dụ: `Alice`) và tên phòng chat (ví dụ: `general`). Client thực hiện bắt tay TLS 2 chiều thành công và xác nhận chứng chỉ server `localhost`.

![Bước 3: Client A đăng nhập và tham gia phòng chat general](docs/images/step3_client1_connect.png)

---

### Bước 4: Khởi chạy Client B (Bob) & Trao đổi Tin nhắn Mã hóa E2E

Mở Terminal thứ ba tại `Bài 3/lab1`, đặt cùng mã secret `SECURECHAT_E2E_SECRET` và đăng nhập với tên `Bob` vào cùng phòng `general`:

```powershell
$env:SECURECHAT_E2E_SECRET = "CyberChatSharedKey2026Secret!"
python -m securechat.client
```

Gửi tin nhắn giữa Alice và Bob. Nội dung tin nhắn được mã hóa AES-256-GCM tại client trước khi truyền qua mạng. Server chỉ nhận và chuyển tiếp ciphertext mà không thể giải mã nội dung.

![Bước 4: Trao đổi tin nhắn đã mã hóa AES-GCM giữa Alice và Bob](docs/images/step4_client2_chat.png)

---

### Bước 5: Thử nghiệm Cách ly Phòng Chat (Room Isolation)

Mở thêm một client ở phòng khác (ví dụ: `cyber`). Do tên phòng được gắn làm Associated Data (AD) trong giao thức AES-GCM:
- Tin nhắn gửi ở phòng `general` chỉ tới các client trong phòng `general`.
- Client ở phòng `cyber` không nhận được dữ liệu của phòng `general`.
- Nếu ciphertext bị gửi nhầm phòng, quá trình giải mã AES-GCM tag sẽ thất bại ngay lập tức.

![Bước 5: Kiểm tra cách ly tin nhắn giữa các phòng chat](docs/images/step5_room_isolation.png)

---

## Báo cáo thực hiện

- **Cấu trúc mã nguồn**: Phân tách rõ ràng thành `securechat/` (server, client, connection_manager, room_manager, protocol, message_encryption) và `tests/`.
- **TLS xác thực hai chiều**: Server bật `CERT_REQUIRED`, kiểm tra chứng chỉ do Root CA cấp. Client kiểm tra CA và hostname `localhost`.
- **Mã hóa E2E**: Sử dụng AES-GCM với Galois Counter Mode cung cấp đồng thời tính bảo mật (confidentiality) và tính toàn vẹn (integrity).
- **Phòng chat & Định tuyến**: Server định tuyến gói dựa trên header metadata (username, room), giữ an toàn tối đa cho dữ liệu người dùng.

## Giới hạn an toàn

Dùng riêng cho môi trường thực hành. Chứng chỉ tự ký, khóa không được bảo vệ bằng passphrase và secret chia sẻ không có quy trình phân phối/đổi khóa. Không dùng cấu hình này cho dữ liệu thật hoặc triển khai Internet. Mỗi client hiện dùng chung room secret nên thành viên trong phòng có thể đọc tin nhắn của nhau.

