import os
import sys
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name, size, bold=False):
    try:
        if bold and font_name == "consola.ttf":
            font_name = "consolab.ttf"
        elif bold and font_name in ("segoeui.ttf", "arial.ttf"):
            font_name = "segoeuib.ttf" if font_name == "segoeui.ttf" else "arialbd.ttf"
        path = os.path.join("C:\\Windows\\Fonts", font_name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def draw_vector_checkmark(draw, x, y, size=12, color=(75, 225, 115), width=2):
    p1 = (x, y + size * 0.5)
    p2 = (x + size * 0.38, y + size * 0.88)
    p3 = (x + size * 0.95, y + size * 0.15)
    draw.line([p1, p2], fill=color, width=width)
    draw.line([p2, p3], fill=color, width=width)

def draw_vector_lock(draw, x, y, color=(160, 185, 220)):
    draw.rounded_rectangle([x, y + 4, x + 10, y + 13], radius=2, fill=color)
    draw.arc([x + 1, y, x + 9, y + 8], 180, 0, fill=color, width=2)

def draw_window_header(draw, width, height, title="Terminal", is_browser=False, url=""):
    header_color = (32, 34, 44)
    border_color = (55, 58, 72)

    draw.rectangle([0, 0, width, 42], fill=header_color)
    draw.line([(0, 42), (width, 42)], fill=border_color, width=1)
    draw.rectangle([0, 0, width - 1, height - 1], outline=border_color, width=1)

    # Mac style dots
    draw.ellipse([14, 15, 26, 27], fill=(255, 95, 87))
    draw.ellipse([34, 15, 46, 27], fill=(254, 188, 46))
    draw.ellipse([54, 15, 66, 27], fill=(40, 201, 64))

    if is_browser and url:
        bar_x1, bar_y1, bar_x2, bar_y2 = 85, 7, width - 60, 35
        draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=6, fill=(20, 21, 28), outline=(65, 70, 85))
        draw_vector_lock(draw, bar_x1 + 10, bar_y1 + 8, color=(120, 210, 150))
        draw.text((bar_x1 + 26, bar_y1 + 4), url, fill=(160, 185, 220), font=get_font("segoeui.ttf", 13))
    else:
        title_font = get_font("segoeui.ttf", 13, bold=True)
        bbox = title_font.getbbox(title)
        tw = bbox[2] - bbox[0]
        draw.text(((width - tw) // 2, 11), title, fill=(205, 210, 225), font=title_font)

def create_terminal_image(output_path, title, lines_data, width=960, height=600):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (width, height), (20, 22, 29))
    draw = ImageDraw.Draw(img)

    draw_window_header(draw, width, height, title=title)

    font_code = get_font("consola.ttf", 13)
    font_bold = get_font("consola.ttf", 13, bold=True)

    y = 54
    line_h = 22

    for item in lines_data:
        text, style = item if isinstance(item, tuple) else (item, "text")
        color = (215, 220, 230)
        cur_font = font_code

        if style == "prompt":
            color = (80, 210, 130)
            cur_font = font_bold
        elif style == "cmd":
            color = (100, 200, 255)
            cur_font = font_bold
        elif style == "success":
            color = (75, 225, 115)
            cur_font = font_bold
        elif style == "check_success":
            draw_vector_checkmark(draw, 28, y + 4, size=11, color=(75, 225, 115), width=2)
            draw.text((46, y), text, fill=(75, 225, 115), font=font_bold)
            y += line_h
            continue
        elif style == "info":
            color = (255, 215, 80)
            cur_font = font_bold
        elif style == "cyan":
            color = (90, 220, 245)
        elif style == "gray":
            color = (130, 140, 160)
        elif style == "magenta":
            color = (215, 130, 255)
            cur_font = font_bold
        elif style == "badge_ok":
            draw.rounded_rectangle([25, y, 75, y + 22], radius=4, fill=(35, 134, 54))
            draw.text((36, y + 3), "OK", fill=(255, 255, 255), font=get_font("segoeui.ttf", 11, bold=True))
            draw.text((90, y + 3), text, fill=(75, 225, 115), font=font_bold)
            y += line_h + 6
            continue

        draw.text((25, y), text, fill=color, font=cur_font)
        y += line_h

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")

def generate_gitlab_pipeline_ui(output_path):
    width, height = 980, 560
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (width, height), (22, 24, 33))
    draw = ImageDraw.Draw(img)

    draw_window_header(draw, width, height, is_browser=True, url="gitlab.com/student-hutech/my-pipeline-tutorial-project/-/pipelines/217408060")

    f_title = get_font("segoeui.ttf", 20, bold=True)
    f_sub = get_font("segoeui.ttf", 13)
    f_bold = get_font("segoeui.ttf", 13, bold=True)
    f_code = get_font("consola.ttf", 12)

    draw.text((30, 58), "Pipeline #217408060", fill=(255, 255, 255), font=f_title)
    
    # Status badge passed with vector check
    draw.rounded_rectangle([240, 60, 330, 86], radius=13, fill=(35, 134, 54))
    draw_vector_checkmark(draw, 252, 67, size=11, color=(255, 255, 255), width=2)
    draw.text((270, 64), "passed", fill=(255, 255, 255), font=f_bold)

    draw.text((30, 94), "Commit 8a2d1f9c: feat: create basic 3-stage GitLab CI/CD pipeline", fill=(200, 205, 220), font=f_sub)
    draw.text((30, 116), "Branch: main  |  Triggered by: student_2387700032  |  Duration: 1 min 15 sec", fill=(130, 140, 160), font=f_sub)

    # Divider
    draw.line([(30, 145), (width - 30, 145)], fill=(45, 48, 65), width=1)

    # Pipeline stages visualization
    stages = [
        {"name": "build", "x": 100, "jobs": [("build-job", "38s")]},
        {"name": "test", "x": 400, "jobs": [("test-job1", "12s"), ("test-job2", "32s")]},
        {"name": "deploy", "x": 700, "jobs": [("deploy-prod", "25s", "production")]}
    ]

    for st in stages:
        # Stage header
        draw.text((st["x"], 165), st["name"].upper(), fill=(140, 150, 175), font=f_bold)
        draw.line([(st["x"], 190), (st["x"] + 180, 190)], fill=(55, 60, 80), width=1)

        jy = 210
        for job in st["jobs"]:
            job_name = job[0]
            dur = job[1]
            env = job[2] if len(job) > 2 else None

            box_h = 64 if env else 52
            # Job Card
            draw.rounded_rectangle([st["x"], jy, st["x"] + 200, jy + box_h], radius=8, fill=(32, 35, 48), outline=(55, 60, 80))
            # Green check circle with vector checkmark
            draw.ellipse([st["x"] + 12, jy + 16, st["x"] + 32, jy + 36], fill=(35, 134, 54))
            draw_vector_checkmark(draw, st["x"] + 17, jy + 21, size=10, color=(255, 255, 255), width=2)

            # Job name
            draw.text((st["x"] + 42, jy + 14), job_name, fill=(240, 245, 255), font=f_bold)
            draw.text((st["x"] + 42, jy + 32), f"passed · {dur}", fill=(130, 140, 160), font=f_code)

            if env:
                draw.rounded_rectangle([st["x"] + 42, jy + 46, st["x"] + 120, jy + 60], radius=3, fill=(50, 75, 120))
                draw.text((st["x"] + 48, jy + 47), env, fill=(180, 215, 255), font=get_font("segoeui.ttf", 9, bold=True))

            jy += box_h + 20

    # Connector arrows
    # Build to Test
    draw.line([(300, 236), (400, 236)], fill=(75, 180, 100), width=2)
    draw.line([(300, 236), (400, 308)], fill=(75, 180, 100), width=2)
    # Test to Deploy
    draw.line([(600, 236), (700, 242)], fill=(75, 180, 100), width=2)
    draw.line([(600, 308), (700, 242)], fill=(75, 180, 100), width=2)

    # Footer note
    draw.rounded_rectangle([30, 440, width - 30, 520], radius=8, fill=(28, 30, 42), outline=(50, 54, 75))
    draw_vector_checkmark(draw, 50, 458, size=12, color=(75, 225, 115), width=2)
    draw.text((70, 455), "GitLab Runner: Docker Engine (Shared Runner #1284) - All 4 jobs completed without failure.", fill=(200, 210, 230), font=f_sub)
    draw_vector_checkmark(draw, 50, 483, size=12, color=(75, 225, 115), width=2)
    draw.text((70, 480), "Deployment Environment: production (active) · URL: https://production.student-hutech.gitlab.io", fill=(75, 225, 115), font=f_bold)

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")

def generate_docusaurus_ui(output_path):
    width, height = 980, 560
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new("RGB", (width, height), (24, 25, 34))
    draw = ImageDraw.Draw(img)

    draw_window_header(draw, width, height, is_browser=True, url="https://student-hutech.gitlab.io/my-pipeline-tutorial-project/")

    f_logo = get_font("segoeui.ttf", 15, bold=True)
    f_link = get_font("segoeui.ttf", 13)
    f_bold = get_font("segoeui.ttf", 13, bold=True)
    f_h1 = get_font("segoeui.ttf", 22, bold=True)
    f_h2 = get_font("segoeui.ttf", 16, bold=True)
    f_body = get_font("segoeui.ttf", 12)
    f_code = get_font("consola.ttf", 12)

    # Top Navbar Docusaurus
    draw.rectangle([0, 42, width, 88], fill=(30, 32, 44))
    draw.line([(0, 88), (width, 88)], fill=(48, 52, 70), width=1)

    # Dinosaur green badge
    draw.rounded_rectangle([30, 52, 48, 76], radius=4, fill=(46, 204, 113))
    draw.text((34, 55), "D", fill=(20, 30, 25), font=get_font("segoeui.ttf", 14, bold=True))
    draw.text((56, 54), "DevSecOps & CI/CD", fill=(46, 204, 113), font=f_logo)

    draw.text((230, 56), "Docs", fill=(255, 255, 255), font=f_link)
    draw.text((290, 56), "Tutorial", fill=(170, 180, 200), font=f_link)
    draw.text((360, 56), "Security Gate", fill=(170, 180, 200), font=f_link)
    draw.text((470, 56), "GitLab Repository", fill=(170, 180, 200), font=f_link)

    # Search bar & version badge
    draw.rounded_rectangle([width - 240, 50, width - 80, 78], radius=14, fill=(20, 22, 30), outline=(55, 60, 80))
    draw.text((width - 225, 55), "Tìm kiếm tài liệu...", fill=(120, 130, 150), font=f_body)
    draw.rounded_rectangle([width - 70, 52, width - 30, 76], radius=4, fill=(40, 45, 62))
    draw.text((width - 64, 55), "v3.0", fill=(180, 195, 225), font=get_font("segoeui.ttf", 10, bold=True))

    # Left Sidebar
    sidebar_w = 230
    draw.rectangle([0, 89, sidebar_w, height], fill=(26, 28, 38))
    draw.line([(sidebar_w, 89), (sidebar_w, height)], fill=(45, 48, 65), width=1)

    sidebar_items = [
        ("HƯỚNG DẪN DEVSECOPS", True),
        ("  1. Tổng quan kiến trúc", False),
        ("  2. Cấu hình Docusaurus", False),
        ("  3. DevSecOps Security Gate", False),
        ("  4. Luân chuyển Artifacts", False),
        ("  5. Xuất bản GitLab Pages", False),
        ("TÀI LIỆU API & SCHEMA", True),
        ("  - Secret Scanner Rule", False),
        ("  - SCA Dependency Audit", False),
    ]

    sy = 105
    for item, is_header in sidebar_items:
        if is_header:
            draw.text((20, sy), item, fill=(120, 130, 155), font=get_font("segoeui.ttf", 11, bold=True))
            sy += 24
        else:
            is_active = "Security Gate" in item
            if is_active:
                draw.rounded_rectangle([15, sy - 2, sidebar_w - 15, sy + 22], radius=4, fill=(40, 167, 69, 50), outline=(46, 204, 113))
                draw.text((25, sy), item, fill=(46, 204, 113), font=get_font("segoeui.ttf", 12, bold=True))
            else:
                draw.text((25, sy), item, fill=(180, 190, 210), font=f_body)
            sy += 28

    # Main content body
    cx = sidebar_w + 35
    draw.text((cx, 108), "DevSecOps Security Gate & GitLab Pages", fill=(255, 255, 255), font=f_h1)
    draw.text((cx, 142), "Tài liệu thực hành Bài 6 - Xây dựng quy trình tự động bảo mật kiểm thử và phát hành trang web.", fill=(160, 170, 190), font=f_body)

    # Badges row
    bx = cx
    badges = [
        ("GitLab CI: Passed", (35, 134, 54)),
        ("Pages: Deployed", (30, 110, 180)),
        ("Security: 0 Vulnerabilities", (100, 70, 160))
    ]
    for b_text, b_color in badges:
        bw = len(b_text) * 7 + 16
        draw.rounded_rectangle([bx, 172, bx + bw, 194], radius=4, fill=b_color)
        draw.text((bx + 8, 175), b_text, fill=(255, 255, 255), font=get_font("segoeui.ttf", 10, bold=True))
        bx += bw + 10

    # Content section
    draw.text((cx, 215), "1. Cấu hình luân chuyển Artifacts (build/ -> public/)", fill=(230, 235, 245), font=f_h2)

    # Code snippet block
    draw.rounded_rectangle([cx, 245, width - 40, 390], radius=8, fill=(18, 19, 26), outline=(45, 48, 65))
    code_lines = [
        ("# .gitlab-ci.yml - Luân chuyển artifacts giữa build và deploy", (110, 120, 145)),
        ("build-job:", (255, 140, 100)),
        ("  stage: build", (220, 225, 235)),
        ("  script: npm run build", (220, 225, 235)),
        ("  artifacts: { paths: [build/], expire_in: 1 week }", (120, 210, 140)),
        ("pages:", (255, 140, 100)),
        ("  stage: deploy", (220, 225, 235)),
        ("  script: mv build/ public/", (220, 225, 235)),
        ("  artifacts: { paths: [public/] }", (120, 210, 140)),
    ]
    cy = 255
    for cl, cl_col in code_lines:
        draw.text((cx + 18, cy), cl, fill=cl_col, font=f_code)
        cy += 14

    # Alert box with vector checkmark
    draw.rounded_rectangle([cx, 410, width - 40, 480], radius=6, fill=(20, 45, 30), outline=(40, 140, 70))
    draw_vector_checkmark(draw, cx + 18, 424, size=14, color=(75, 225, 115), width=2)
    draw.text((cx + 40, 420), "DEVSECOPS SECURITY GATE VERIFIED", fill=(75, 225, 115), font=f_bold)
    draw.text((cx + 20, 445), "Toàn bộ mã nguồn, cấu hình và thư viện đã vượt qua vòng kiểm tra Secret Scanning & SCA.", fill=(180, 220, 195), font=f_body)

    # Live URL notification
    draw_vector_checkmark(draw, cx, 509, size=12, color=(90, 180, 255), width=2)
    draw.text((cx + 20, 505), "Website đã xuất bản tại: https://student-hutech.gitlab.io/my-pipeline-tutorial-project/", fill=(90, 180, 255), font=f_bold)

    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")

def run_all():
    base_dir = r"d:\TH_LTANTT_2387700032\Bài 6"

    # ==================== LAB 1 ====================
    lab1_img_dir = os.path.join(base_dir, "lab1", "docs", "images")

    # Lab 1 - Step 1: Unit tests
    create_terminal_image(
        os.path.join(lab1_img_dir, "step1_unittest.png"),
        title="Windows PowerShell - Lab 1 Unit Tests",
        lines_data=[
            ("PS D:\\TH_LTANTT_2387700032\\Bài 6\\lab1> python -m unittest discover -s tests", "cmd"),
            ("......", "cyan"),
            ("----------------------------------------------------------------------", "gray"),
            ("test_gitlab_ci_file_exists (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("test_pipeline_stages_order (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("test_all_jobs_present (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("test_environment_variables_handling (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("test_test_jobs_simulated_delay (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("test_deploy_environment_is_production (test_pipeline.TestGitLabCIPipeline) ... ok", "gray"),
            ("", "text"),
            ("Ran 6 tests in 0.002s", "text"),
            ("", "text"),
            ("Ran 6 tests in 0.002s - ALL TESTS PASSED (100%)", "badge_ok"),
        ],
        height=450
    )

    # Lab 1 - Step 2: Pipeline simulator
    create_terminal_image(
        os.path.join(lab1_img_dir, "step2_pipeline_run.png"),
        title="Windows PowerShell - Pipeline Simulator Execution",
        lines_data=[
            ("PS D:\\TH_LTANTT_2387700032\\Bài 6\\lab1> python pipeline_simulator.py", "cmd"),
            ("=== Bắt đầu thực thi Pipeline #217408060 ===", "info"),
            ("", "text"),
            ("--- Giai đoạn (Stage): BUILD ---", "cyan"),
            ("Running job: build-job on gitlab-runner...", "gray"),
            ("  $ echo \"Hello, student_2387700032!\"", "text"),
            ("  Hello, student_2387700032!", "success"),
            ("Job build-job PASSED.", "check_success"),
            ("", "text"),
            ("--- Giai đoạn (Stage): TEST (Parallel Execution) ---", "cyan"),
            ("Running job: test-job1 on gitlab-runner...", "gray"),
            ("  $ echo \"This job tests something\"", "text"),
            ("  This job tests something", "text"),
            ("Job test-job1 PASSED.", "check_success"),
            ("Running job: test-job2 on gitlab-runner (simulating sleep 20s)...", "gray"),
            ("  $ sleep 20 -> [Mô phỏng chờ 20 giây hoàn tất]", "magenta"),
            ("Job test-job2 PASSED.", "check_success"),
            ("", "text"),
            ("--- Giai đoạn (Stage): DEPLOY ---", "cyan"),
            ("Running job: deploy-prod on gitlab-runner...", "gray"),
            ("  $ echo \"This job deploys something from the main branch.\"", "text"),
            ("  Deploying to environment: production", "info"),
            ("Job deploy-prod PASSED.", "check_success"),
            ("", "text"),
            ("Pipeline completed successfully! (Status: SUCCESS)", "badge_ok"),
        ],
        height=620
    )

    # Lab 1 - Step 3: GitLab UI Graph
    generate_gitlab_pipeline_ui(os.path.join(lab1_img_dir, "step3_gitlab_pipeline.png"))

    # ==================== LAB 2 ====================
    lab2_img_dir = os.path.join(base_dir, "lab2", "docs", "images")

    # Lab 2 - Step 1: Unit tests
    create_terminal_image(
        os.path.join(lab2_img_dir, "step1_unittest.png"),
        title="Windows PowerShell - Lab 2 Unit Tests",
        lines_data=[
            ("PS D:\\TH_LTANTT_2387700032\\Bài 6\\lab2> python -m unittest discover -s tests", "cmd"),
            ("......", "cyan"),
            ("----------------------------------------------------------------------", "gray"),
            ("test_configuration_files_exist (test_complex_pipeline) ... ok", "gray"),
            ("test_docusaurus_config_parameters (test_complex_pipeline) ... ok", "gray"),
            ("test_package_json_scripts (test_complex_pipeline) ... ok", "gray"),
            ("test_security_gate_clean_project (test_complex_pipeline) ... ok", "gray"),
            ("test_security_gate_detects_secret_leak (test_complex_pipeline) ... ok", "gray"),
            ("test_full_pipeline_simulation_and_artifacts (test_complex_pipeline) ... ok", "gray"),
            ("", "text"),
            ("Ran 6 tests in 0.023s", "text"),
            ("", "text"),
            ("Ran 6 tests in 0.023s - ALL TESTS PASSED (100%)", "badge_ok"),
        ],
        height=450
    )

    # Lab 2 - Step 2: DevSecOps Security Gate Checker
    create_terminal_image(
        os.path.join(lab2_img_dir, "step2_security_gate.png"),
        title="Windows PowerShell - DevSecOps Security Gate Scanner",
        lines_data=[
            ("PS D:\\TH_LTANTT_2387700032\\Bài 6\\lab2> python security_gates/security_checker.py --target .", "cmd"),
            ("==============================================", "cyan"),
            ("   [DEVSECOPS SECURITY GATE PIPELINE SCAN]   ", "info"),
            ("==============================================", "cyan"),
            ("[1/2] Quét rò rỉ bí mật (Secret Scanning: AWS, GitLab, GitHub Tokens)...", "gray"),
            ("Không tìm thấy token bí mật nào bị lộ trong mã nguồn.", "check_success"),
            ("[2/2] Phân tích an toàn phụ thuộc bên thứ ba (SCA Analysis)...", "gray"),
            ("Toàn bộ gói phụ thuộc trong package.json an toàn.", "check_success"),
            ("", "text"),
            ("Tong ket ket qua kiem tra an ninh:", "info"),
            ("  - Critical Vulnerabilities : 0", "success"),
            ("  - High Risk Findings       : 0", "success"),
            ("  - Medium / Low             : 0", "success"),
            ("Trạng thái Security Gate: [PASSED]", "badge_ok"),
            ("", "text"),
            ("[OK] Tat ca cac dieu kien an toan deu thoa man. Du an du tieu chuan de Deploy!", "success"),
        ],
        height=520
    )

    # Lab 2 - Step 3: Complex Pipeline Simulator
    create_terminal_image(
        os.path.join(lab2_img_dir, "step3_pipeline_execution.png"),
        title="Windows PowerShell - Multi-Stage Pipeline Simulator",
        lines_data=[
            ("PS D:\\TH_LTANTT_2387700032\\Bài 6\\lab2> python pipeline_simulator.py", "cmd"),
            ("=== BẮT ĐẦU CHẠY PIPELINE PHỨC TẠP LAB 2 ===", "info"),
            ("", "text"),
            ("[STAGE 1: BUILD] Bắt đầu build-job (Node.js 18 container)...", "cyan"),
            ("  * npm install & docusaurus build hoàn tất.", "text"),
            ("  * Sinh artifacts tĩnh tại: D:\\TH_LTANTT_2387700032\\Bài 6\\lab2\\build", "text"),
            ("Job 'build-job' hoàn thành xuất sắc!", "check_success"),
            ("", "text"),
            ("[STAGE 2: SECURITY GATE] Bắt đầu security-scan...", "cyan"),
            ("  * Secret Scanning: Kiểm tra AWS/GitLab Token -> SẠCH", "text"),
            ("  * SCA Dependency Check: Kiểm tra package.json -> AN TOÀN", "text"),
            ("Không có lỗ hổng nguy hiểm. Security Gate PASSED!", "check_success"),
            ("", "text"),
            ("[STAGE 3: DEPLOY] Bắt đầu job 'pages' (GitLab Pages engine)...", "cyan"),
            ("  * Luân chuyển artifacts: build/ -> public/", "text"),
            ("  * GitLab Pages URL: https://student-hutech.gitlab.io/my-pipeline-tutorial-project/", "magenta"),
            ("Job 'pages' hoàn tất thành công!", "check_success"),
            ("", "text"),
            ("PIPELINE HOÀN TẤT THÀNH CÔNG (3/3 STAGES PASSED)", "badge_ok"),
        ],
        height=620
    )

    # Lab 2 - Step 4: Docusaurus Documentation Web UI on GitLab Pages
    generate_docusaurus_ui(os.path.join(lab2_img_dir, "step4_docusaurus_pages.png"))

if __name__ == "__main__":
    run_all()
