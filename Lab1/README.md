# TH_LTANTT_2387700032
Thuc hanh Lap trinh An ninh thong tin - 2387700032 - Le Dang Khoa
Dòng thay code thay đổi 
sanitized = re.sub(r"\b(OR|AND|SELECT|INSERT|DELETE|UPDATE|DROP|UNION|WHERE)\b",
                       "", sanitized, flags=re.IGNORECASE)
sanitized = re.sub(r"\b(OR|AND|SELECT|INSERT|DELETE|UPDATE|DROP|UNION|WHERE)\b", "", sanitized)
<!-- Vẫn vượt qua toàn bộ unit test hiện tại (test_validators.py):
Trong bài test test_sanitize_sql_input_injection, chuỗi test đầu vào là "' OR 1=1 --" (từ OR được viết in hoa toàn bộ).   
Biểu thức regex khi không có flags=re.IGNORECASE vẫn khớp và xóa được chữ OR viết hoa.   
Đoạn self.assertNotIn("OR", sanitized.upper()) vẫn trả về True, vì vậy lệnh chạy test vẫn pass 100%.  
 Cách vượt qua cơ chế bảo vệ (Bypass SQL Injection):
 Do đã xóa cờ re.IGNORECASE, bộ lọc giờ đây phân biệt chữ hoa/chữ thường (case-sensitive).
 Kẻ tấn công chỉ cần truyền vào các từ khóa viết thường hoặc viết xen kẽ chữ hoa chữ thường như or, Or, select, uNiOn.
 Bộ lọc sẽ bỏ qua hoàn toàn các chuỗi này, cho phép payload SQL Injection lọt qua hệ thống mà không bị loại bỏ. -->