"""
Sample Application for Lab 1 - CI/CD Basic Demonstration
"""

def get_welcome_message(username: str) -> str:
    """Trả về thông điệp chào mừng người dùng đăng nhập."""
    if not username:
        username = "Guest"
    return f"Hello, {username}!"


def deploy_service(branch: str, environment: str = "production") -> dict:
    """Mô phỏng tác vụ triển khai ứng dụng lên môi trường mục tiêu."""
    if not branch:
        raise ValueError("Branch name cannot be empty")
    return {
        "status": "success",
        "branch": branch,
        "environment": environment,
        "message": f"Successfully deployed branch '{branch}' to {environment}"
    }


if __name__ == "__main__":
    print(get_welcome_message("GitLab_User"))
    print(deploy_service("main", "production"))
