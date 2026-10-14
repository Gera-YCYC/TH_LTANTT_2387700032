from jwt_cracker.cracker import JWTCracker
import jwt
import tempfile
import os

def test_crack_token():
    secret = "supersecret"
    token = jwt.encode({"sub": "test"}, secret, algorithm="HS256")

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("wrongpass\n123456\nsupersecret\n")
        f.flush()
        f.seek(0)
        file_path = f.name

    try:
        cracker = JWTCracker(token, file_path)
        found = cracker.crack()
        assert found == "supersecret"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
