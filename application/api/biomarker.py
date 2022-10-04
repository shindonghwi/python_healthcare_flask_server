from flask import Blueprint, Response
import json

route = 'biomarker'

biomarker = Blueprint(route, __name__)
biomarker.url_prefix = '/{}'.format(route)

APPLICATION_JSON = 'application/json'


@biomarker.route('/')
def index():
    return Response(json.dumps("Biomarker API"), mimetype=APPLICATION_JSON)


@biomarker.route('/test')
def phase_today():
    return Response(json.dumps({"status:": 200, "msg": "bio"}))
