import argparse
from application.factory import create_app
from config.app import config_by_name

parser = argparse.ArgumentParser(description='argument instance')
parser.add_argument('--env', required=False, default='dev', help='environment')
args = parser.parse_args()

app = create_app()

if __name__ == '__main__':
    print('dev info: DEBUG: {}, host: {}, port: {}'.format(
        config_by_name['dev'].DEBUG, config_by_name['dev'].host, config_by_name['dev'].port)
    )
    app.run(debug=config_by_name['prod'].DEBUG, host=config_by_name['prod'].host, port=config_by_name['prod'].port)
