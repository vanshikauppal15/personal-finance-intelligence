from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def health_check():
        return {"status": "ok", "message": "Personal Finance Intelligence API running"}

    return app