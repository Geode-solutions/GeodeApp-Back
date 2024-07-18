""" Packages """

import os
import dotenv

import flask
import flask_cors
import time


from opengeodeweb_back import geode_functions
from opengeodeweb_back.routes import blueprint_routes

from werkzeug.exceptions import HTTPException

from werkzeug.exceptions import HTTPException

from .config import *


if os.path.isfile("./.env"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    dotenv.load_dotenv(os.path.join(basedir, ".env"))

""" Global config """
app = flask.Flask(__name__)


def kill_task():
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.exists(TIME_FOLDER):
        os.mkdir(TIME_FOLDER)

    if len(os.listdir(LOCK_FOLDER)) == 0:
        print(f"No files in the {LOCK_FOLDER} folder, shutting down...", flush=True)
        os._exit(0)
    if not os.path.isfile(TIME_FOLDER + "/time.txt"):
        print("'time.txt' file doesn't exist, shutting down...", flush=True)
        os._exit(0)
    if os.path.isfile(TIME_FOLDER + "/time.txt"):
        with open(TIME_FOLDER + "/time.txt", "r") as file:
            try:
                last_request_time = float(file.read())
            except Exception as e:
                print("error : ", str(e), flush=True)
                os._exit(0)
            current_time = time.time()
            if (current_time - last_request_time) / 60 > MINUTES_BEFORE_TIMEOUT:
                print(
                    "Server timed out due to inactivity, shutting down...", flush=True
                )
                os._exit(0)
    if os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        os.remove(LOCK_FOLDER + "/ping.txt")


""" Config variables """
FLASK_DEBUG = True if os.environ.get("FLASK_DEBUG", default=None) == "True" else False


if FLASK_DEBUG == False:
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(DevConfig)

ID = app.config.get("ID")
PORT = int(app.config.get("PORT"))
ORIGINS = app.config.get("ORIGINS")
SSL = app.config.get("SSL")
LOCK_FOLDER = app.config.get("LOCK_FOLDER")
TIME_FOLDER = app.config.get("TIME_FOLDER")
MINUTES_BEFORE_TIMEOUT = float(app.config.get("MINUTES_BEFORE_TIMEOUT"))
SECONDS_BETWEEN_SHUTDOWNS = float(app.config.get("SECONDS_BETWEEN_SHUTDOWNS"))


app.register_blueprint(
    blueprint_routes.routes,
    url_prefix="/opengeodeweb_back",
    name="opengeodeweb_back",
)

if FLASK_DEBUG == False:
    geode_functions.set_interval(kill_task, SECONDS_BETWEEN_SHUTDOWNS)
flask_cors.CORS(app, origins=ORIGINS)


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = flask.json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@app.route("/geodeapp/createbackend", methods=["POST"])
def create_backend():
    return flask.make_response({"ID": str("123456")}, 200)


@app.route("/", methods=["POST"])
def root():
    return flask.make_response({"ID": str("123456")}, 200)


def run_server():
    print(f"Python is running in {FLASK_DEBUG} mode")
    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=PORT, ssl_context=SSL)


# ''' Main '''
if __name__ == "__main__":
    run_server()
