from flask import Flask
from application.api.biomarker import biomarker


def create_app():
    app = Flask(__name__)
    app.register_blueprint(biomarker, url_prefix=biomarker.url_prefix)

    @app.route('/')
    def index():
        return "hello world"

    return app
