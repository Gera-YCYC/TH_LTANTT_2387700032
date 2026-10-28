# Bài 6: Bảo Mật Với DevSecOps

Tài liệu hướng dẫn chi tiết, tóm tắt lý thuyết và báo cáo thực hành toàn diện cho **Bài 6: Bảo Mật Với DevSecOps** (CI/CD Pipeline Security, GitLab CI/CD, Docusaurus, GitLab Pages và Security Gates).

---

## 📑 Danh mục các bài Lab

| Bài Lab | Tên Dự Án | Mô tả Trọng Tâm | Trạng Thái Kiểm Thử | Báo Cáo Chi Tiết |
| :--- | :--- | :--- | :---: | :---: |
| **Lab 1** | **gitlab-basic-pipeline** | Xây dựng pipeline CI/CD cơ bản trên GitLab: cấu hình `.gitlab-ci.yml`, quản lý các giai đoạn (`build`, `test`, `deploy`), thực thi kiểm thử song song, mô phỏng độ trễ (`sleep 20`), biến môi trường (`$GITLAB_USER_LOGIN`, `$CI_COMMIT_BRANCH`) và môi trường `production`. | **6/6 Passed** (100%) | [Xem Báo Cáo Lab 1](lab1/README.md) |
| **Lab 2** | **docusaurus-devsecops-pipeline** | Pipeline CI/CD phức tạp & DevSecOps Security Gates: đóng gói ứng dụng tài liệu Docusaurus bằng Docker image Node.js, luân chuyển tài nguyên qua **Artifacts** (`build/` ➔ `public/`), chốt kiểm soát an ninh tự động (Secret Scanning & SCA Dependency Check) và tự động xuất bản lên **GitLab Pages**. | **6/6 Passed** (100%) | [Xem Báo Cáo Lab 2](lab2/README.md) |

---

## 📖 Tóm Tắt Lý Thuyết Trọng Tâm

### 1. Tích hợp bảo mật trong CI/CD (Mục 6.1)
- **Triết lý "Shift Left Security"**: Di chuyển các biện pháp kiểm soát và kiểm thử bảo mật về các bước sớm nhất có thể trong quy trình phát triển nhằm giảm thiểu chi phí khắc phục và rủi ro rò rỉ.
- **Các thành phần bảo mật then chốt**:
  1. **Access Control**: Nguyên tắc ít quyền nhất (Principle of Least Privilege) và kích hoạt xác thực đa yếu tố (MFA).
  2. **Secrets Management**: Quản lý tập trung bằng HashiCorp Vault / AWS Secrets Manager, tuyệt đối không gán cứng secret vào git. Sử dụng công cụ tự động quét rò rỉ (TruffleHog, Gitleaks).
  3. **Code Signing & Integrity**: Ký số commit và artifact để bảo đảm tính toàn vẹn.
  4. **Security Gates (Cửa chắn an ninh)**: Tự động chặn pipeline nếu phát hiện lỗ hổng nghiêm trọng từ SAST, DAST hoặc SCA.
  5. **Bảo vệ CI/CD Runner**: Cô lập môi trường thực thi để tránh kẻ xấu lợi dụng hạ tầng runner làm bàn đạp tấn công.

### 2. Các phương pháp kiểm thử bảo mật tự động
- **SAST (Static Application Security Testing)**: Phân tích mã nguồn tĩnh phát hiện lỗi cú pháp, injection, logic rủi ro.
- **DAST (Dynamic Application Security Testing)**: Kiểm thử ứng dụng đang chạy ở runtime để tìm lỗ hổng tương tác.
- **SCA (Software Composition Analysis)**: Rà soát cơ sở dữ liệu lỗ hổng (CVE) của các thư viện mã nguồn mở bên thứ ba.
- **Secret Scanning**: Tự động nhận diện token, mật khẩu, khóa riêng tư vô tình bị commit.

### 3. Bảo mật Hạ tầng dưới dạng mã (IaC Security)
- Quét các file cấu hình Terraform, Ansible, CloudFormation, Dockerfile để phát hiện phân quyền quá rộng (wildcard permissions), cổng mở không cần thiết và thiếu mã hóa.

---

## 1. 🚀 [Lab 1 - Tạo và Chạy CI/CD Pipeline Cơ Bản](lab1/README.md)

* **Thư mục thực hành**: `Bài 6/lab1/`
* **Mục tiêu**: Làm quen với cú pháp YAML của GitLab CI/CD, định nghĩa thứ tự thực thi của các stage và job, xử lý biến môi trường định sẵn.
* **Chi tiết cấu hình**: Xem tại [Báo cáo Lab 1](lab1/README.md).

### Hướng dẫn kiểm thử Lab 1:
```powershell
cd "d:\TH_LTANTT_2387700032\Bài 6\lab1"
# 1. Chạy unit tests kiểm tra cấu hình và runner (6/6 OK)
python -m unittest discover -s tests

# 2. Chạy bộ giả lập pipeline Runner
python pipeline_simulator.py
```

![Giao diện trực quan Pipeline Graph trên GitLab CI/CD](lab1/docs/images/step3_gitlab_pipeline.png)

---

## 2. 🛡️ [Lab 2 - Pipeline CI/CD Phức Tạp & DevSecOps Security Gate](lab2/README.md)

* **Thư mục thực hành**: `Bài 6/lab2/`
* **Mục tiêu**: Xây dựng pipeline hoàn chỉnh cho website tài liệu Docusaurus, luân chuyển artifacts giữa các container và áp dụng Security Gate để chặn đứng mã nguồn không an toàn trước khi deploy lên GitLab Pages.
* **Chi tiết cấu hình**: Xem tại [Báo cáo Lab 2](lab2/README.md).

### Hướng dẫn kiểm thử Lab 2:
```powershell
cd "d:\TH_LTANTT_2387700032\Bài 6\lab2"
# 1. Chạy unit tests kiểm tra Docusaurus & Security Gate (6/6 OK)
python -m unittest discover -s tests

# 2. Chạy công cụ quét bảo mật độc lập
python security_gates/security_checker.py --target .

# 3. Chạy giả lập toàn bộ pipeline 3 giai đoạn (Build -> Security -> Deploy)
python pipeline_simulator.py
```

![Giao diện website Docusaurus trên GitLab Pages](lab2/docs/images/step4_docusaurus_pages.png)

---

## 📊 Bảng tổng kết kết quả kiểm thử toàn bài

| Bài thực hành | Tổng số Test Cases | Kết quả thực thi | Trạng thái |
| :--- | :---: | :---: | :---: |
| **Lab 1: Basic Pipeline** | 6 | 6/6 Passed | ✅ Hoàn thành xuất sắc |
| **Lab 2: Complex DevSecOps** | 6 | 6/6 Passed | ✅ Hoàn thành xuất sắc |
| **Toàn bộ Bài 6** | **12** | **12/12 Passed (100%)** | 🏆 Đạt chuẩn DevSecOps |

---

## 📚 Tài Liệu Tham Khảo
1. GitLab Inc. *GitLab CI/CD Documentation*. https://docs.gitlab.com/
2. Gruhn, V. (2020). *Securing DevOps*. O'Reilly Media.
3. OWASP Foundation. *OWASP Top Ten Web Application Security Risks*. https://owasp.org/www-project-top-ten/
4. Văn Thiên Hoàng, & Nguyễn Trọng Minh Hồng Phước. (2025). *Lập trình an ninh thông tin*. HUTECH.
