from flask import Flask
from flask_cors import CORS  # 1. Bu satırı en üste ekle

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])
    return app