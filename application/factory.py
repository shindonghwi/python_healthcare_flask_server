from flask import Flask
from application.api.biomarker import biomarker
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.register_blueprint(biomarker, url_prefix=biomarker.url_prefix)

    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.route('/')
    def index():
        return "mago demo healthcare"

    return app
