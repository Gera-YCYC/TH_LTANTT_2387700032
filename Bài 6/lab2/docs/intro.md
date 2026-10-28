---
sidebar_position: 1
---

# Giới thiệu DevSecOps & CI/CD Pipeline

Chào mừng bạn đến với tài liệu thực hành **Bài 6: Bảo mật với DevSecOps**!

## 1. DevSecOps là gì?
DevSecOps (Development - Security - Operations) là phương pháp luận tích hợp bảo mật xuyên suốt mọi giai đoạn trong vòng đời phát triển phần mềm (SDLC), thay vì chỉ kiểm tra bảo mật ở giai đoạn cuối cùng.

## 2. Các nguyên tắc cốt lõi trong DevSecOps
- **Shift Left Security**: Di chuyển các chốt kiểm tra bảo mật về giai đoạn sớm nhất của quy trình phát triển.
- **Tự động hóa kiểm thử**: Tích hợp SAST, DAST, SCA và Secret Scanning vào pipeline CI/CD.
- **Infrastructure as Code (IaC) Security**: Quét lỗ hổng cấu hình hạ tầng đám mây (Terraform, Ansible, Dockerfile).
- **Secrets Management**: Quản lý tập trung các thông tin nhạy cảm qua HashiCorp Vault hoặc AWS Secrets Manager, tuyệt đối không commit khóa API vào kho mã nguồn.

## 3. Kiến trúc Pipeline
Pipeline của dự án này gồm 3 giai đoạn chính:
1. `build`: Cài đặt thư viện phụ thuộc và biên dịch Docusaurus site.
2. `security`: Quét lỗ hổng bảo mật tự động bằng bộ quy tắc an ninh (Security Gate).
3. `deploy`: Xuất bản website tĩnh lên GitLab Pages thông qua thư mục `public/`.
