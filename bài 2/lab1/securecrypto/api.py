# import os
# from flask import Flask, request, jsonify
# from securecrypto import aes_utils

# app = Flask(__name__)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FILES_DIR = os.path.join(BASE_DIR, 'upload')
# os.makedirs(FILES_DIR, exist_ok=True)


# @app.route('/encrypt', methods=['POST'])
# def encrypt():
#     f = request.files['file']
#     password = request.form['password']
#     save_path = os.path.join(FILES_DIR, f.filename)
#     f.save(save_path)
#     key = aes_utils.encrypt_file_aes(save_path, password)
#     return jsonify({"key": key})


# @app.route('/decrypt', methods=['POST'])
# def decrypt():
#     f = request.files['file']
#     password = request.form['password']  # Chuỗi key base64
#     save_path = os.path.join(FILES_DIR, "temp_" + f.filename)
#     f.save(save_path)
#     out_path = aes_utils.decrypt_file_aes(save_path, password)
#     return jsonify({"output": out_path})


# if __name__ == '__main__':
#     app.run()
#-----CODE CHỈNH SỬA----#
import os
from flask import Flask, request, jsonify
from securecrypto import aes_utils

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'upload')
os.makedirs(FILES_DIR, exist_ok=True)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "Thiếu file hoặc password"}), 400

    f = request.files['file']
    password = request.form['password']
    save_path = os.path.join(FILES_DIR, f.filename)
    f.save(save_path)
    
    key = aes_utils.encrypt_file_aes(save_path, password)
    return jsonify({"key": key})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Chấp nhận key gửi lên bằng key name là 'password' hoặc 'key'
    f = request.files.get('file')
    key_input = request.form.get('password') or request.form.get('key')
    
    if not f or not key_input:
        return jsonify({"error": "Thiếu file hoặc key giải mã"}), 400

    save_path = os.path.join(FILES_DIR, "uploaded_" + f.filename)
    f.save(save_path)
    
    try:
        out_path = aes_utils.decrypt_file_aes(save_path, key_input)
        return jsonify({"output": out_path})
    except Exception as e:
        return jsonify({"error": f"Lỗi giải mã: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True)