from flask import Flask
from flask_cors import CORS  # 1. Bu satırı en üste ekle

def create_app():
    app = Flask(__name__)
    CORS(app)
    return app