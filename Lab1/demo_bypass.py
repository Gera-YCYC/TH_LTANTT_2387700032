from securevalidator import sanitize_sql_input

# 1. Dữ liệu viết hoa (giống test case chuẩn)
safe_test = "' OR 1=1 --"
print("[1] Test chuẩn (in hoa):")
print("    Input: ", safe_test)
print("    Output:", sanitize_sql_input(safe_test))

# 2. Dữ liệu viết thường hoặc xen kẽ hoa thường
bypass_test_1 = "' or 1=1 --"
bypass_test_2 = "admin' union select 1,2,3 --"

print("\n[2] Kiểm tra payload vượt rào (chữ thường):")
print("    Input: ", bypass_test_1)
print("    Output:", sanitize_sql_input(bypass_test_1))

print("\n[3] Kiểm tra payload truy vấn dữ liệu:")
print("    Input: ", bypass_test_2)
print("    Output:", sanitize_sql_input(bypass_test_2))