from flask import Flask
from application.api.biomarker import biomarker
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(biomarker, url_prefix=biomarker.url_prefix)

    @app.route('/')
    def index():
        return "hello world"

    return app
