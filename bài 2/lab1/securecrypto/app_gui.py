# import tkinter as tk
# from tkinter import filedialog
# from securecrypto import aes_utils


# def encrypt():
#     file = filedialog.askopenfilename()
#     if not file:
#         return
#     pw = password_entry.get()
#     key = aes_utils.encrypt_file_aes(file, pw)
#     result_label.config(text=f"Key: {key}")


# def decrypt():
#     file = filedialog.askopenfilename()
#     if not file:
#         return
#     pw = password_entry.get()
#     out = aes_utils.decrypt_file_aes(file, pw)
#     result_label.config(text=f"Output: {out}")


# root = tk.Tk()
# root.title("SecureCrypto GUI")

# password_entry = tk.Entry(root, show="*")
# password_entry.pack()

# tk.Button(root, text="Encrypt", command=encrypt).pack()
# tk.Button(root, text="Decrypt", command=decrypt).pack()

# result_label = tk.Label(root, text="")
# result_label.pack()

# root.mainloop()
#----CODE CHỈNH SỬA----#
import tkinter as tk
from tkinter import filedialog, messagebox
from securecrypto import aes_utils

def encrypt():
    file = filedialog.askopenfilename()
    if not file:
        return
    pw = password_entry.get().strip()
    if not pw:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập mật khẩu!")
        return
    key = aes_utils.encrypt_file_aes(file, pw)
    result_entry.delete(0, tk.END)
    result_entry.insert(0, key)
    messagebox.showinfo("Thành công", f"Đã mã hóa xong!\nFile lưu tại: {file}.enc\nKey đã được điền vào ô kết quả.")

def decrypt():
    file = filedialog.askopenfilename()
    if not file:
        return
    # Lấy key từ ô nhập (nếu để trống ô nhập mật khẩu thì lấy từ ô kết quả vừa sinh)
    key_input = password_entry.get().strip() or result_entry.get().strip()
    if not key_input:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập chuỗi Key (Base64) để giải mã!")
        return
    try:
        out = aes_utils.decrypt_file_aes(file, key_input)
        messagebox.showinfo("Thành công", f"Giải mã thành công!\nFile lưu tại: {out}")
    except Exception as e:
        messagebox.showerror("Lỗi giải mã", f"Không thể giải mã: {e}")

root = tk.Tk()
root.title("SecureCrypto GUI")
root.geometry("400x250")

tk.Label(root, text="Mật khẩu (Encrypt) hoặc Key Base64 (Decrypt):").pack(pady=5)
password_entry = tk.Entry(root, show="*", width=40)
password_entry.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Encrypt", width=12, command=encrypt).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Decrypt", width=12, command=decrypt).grid(row=0, column=1, padx=5)

tk.Label(root, text="Key sinh ra (Dùng để giải mã):").pack(pady=5)
result_entry = tk.Entry(root, width=45)
result_entry.pack(pady=5)

root.mainloop()