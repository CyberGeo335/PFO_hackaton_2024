# back/main.py

from flask import Flask
from routes import main_bp

def create_app():
    app = Flask(__name__)
    
    # Регистрация blueprint для обработки запросов
    app.register_blueprint(main_bp)
    
    return app
