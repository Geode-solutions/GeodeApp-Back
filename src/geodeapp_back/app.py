# Global packages
import argparse
import os
import time

# Third parties
import flask
import flask_cors
from flask_cors import cross_origin
from opengeodeweb_back import geode_functions, utils_functions, app_config
from opengeodeweb_back.routes import blueprint_routes
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import HTTPException

# Local libraries

""" Global config """
app = flask.Flask(__name__)

""" Config variables """
FLASK_DEBUG = True if os.environ.get("FLASK_DEBUG", default=None) == "True" else False

if FLASK_DEBUG == False:
    app.config.from_object(app_config.ProdConfig)
else:
    app.config.from_object(app_config.DevConfig)

DEFAULT_HOST = app.config.get("DEFAULT_HOST")
DEFAULT_PORT = int(app.config.get("DEFAULT_PORT"))
DEFAULT_DATA_FOLDER_PATH = app.config.get("DEFAULT_DATA_FOLDER_PATH")
DESKTOP_APP = app.config.get("DESKTOP_APP")
ORIGINS = app.config.get("ORIGINS")
SSL = app.config.get("SSL")
SECONDS_BETWEEN_SHUTDOWNS = float(app.config.get("SECONDS_BETWEEN_SHUTDOWNS"))

app.register_blueprint(
    blueprint_routes.routes,
    url_prefix="/opengeodeweb_back",
    name="opengeodeweb_back",
)

if FLASK_DEBUG == False:
    utils_functions.set_interval(utils_functions.kill_task, SECONDS_BETWEEN_SHUTDOWNS, app)

@app.errorhandler(HTTPException)
def errorhandler(e):
    return utils_functions.handle_exception(e)

@app.route("/", methods=["POST"])
@cross_origin()
def root():
    return flask.make_response({}, 200)

def run_server():
    parser = argparse.ArgumentParser(prog='GeodeApp-Back', description='Backend server for GeodeApp')
    parser.add_argument('-h', '--host', type=int, default=DEFAULT_HOST, help='Host to run on')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='Port to listen on')
    parser.add_argument('-d', '--debug', default=FLASK_DEBUG, help='Whether to run in debug mode', action='store_true')
    parser.add_argument('-dfp', '--data_folder_path', type=str, default=DEFAULT_DATA_FOLDER_PATH, help='Path to the folder where data is stored')
    parser.add_argument('-dktp', '--desktop', default=DESKTOP_APP, help='Whether the app is in desktop mode or not, if not, the server times out after ', action='store_true')
    parser.add_argument('-origin', '--allowed_origin', default=ORIGINS, help='Origins that are allowed to connect to the server')
    args = parser.parse_args()
    app.config.update(DATA_FOLDER_PATH=args.data_folder_path)
    app.config.update(DESKTOP_APP=args.desktop)
    flask_cors.CORS(app, origins=args.allowed_origin)
    print(f"Port: {args.port}, Debug: {args.debug}, Data folder path: {args.data_folder_path}, Desktop mode: {args.desktop}, Origins: {args.allowed_origin}", flush=True)
    app.run(debug=args.debug, host="0.0.0.0", port=args.port, ssl_context=SSL)


# ''' Main '''
if __name__ == "__main__":
    run_server()
