import json
from enum import Enum
from threading import Thread

import pandas

import webview
from flask import Blueprint, Flask, render_template
from flask_cors import CORS
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import pymongo
from pymongo import MongoClient
from getmac import get_mac_address as gma
import diagram as diagram
import example_bp

PORT = 43968
URL = "localhost"

client = MongoClient("mongodb+srv://admin:mongodb9143@cluster0.femb8.mongodb.net/group5db?retryWrites=true&w=majority")
db = client['group5db']
collections = db.list_collection_names()
# cursor = collections.find()
# mongo_docs = list(cursor)
# mongo_docs = mongo_docs[:1]
# docs = pandas.DataFrame(columns=[])

# for num, doc in enumerate(mongo_docs):
#     doc["_id"] = str(doc["_id"])
#     doc_id = doc["_id"]
#     series_obj = pandas.Series(doc, name=doc_id)
#     docs = docs.append(series_obj)
#     docs.to_json("test_export_json.json")

class MESSAGE(Enum):
    FETCH_MAC_ADDRESSES = "Fetch MAC Addresses"
    GENERATE_DIAGRAM = "Generate Diagram"


app = Flask(__name__)

CORS(app)

# Disables caching for each flair app that uses PyWebView
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1


@app.after_request
def add_header(response):
    """
        Disables caching for each flair app that uses PyWebView
    """
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route("/")
def home():
    """
        Templates should be stored inside templates folder
    """
    return render_template("index.html")


websocket_bp = Blueprint(__name__, __name__)


@websocket_bp.route("/")
def handle_message(socket):
    while not socket.closed:
        try:
            event = json.loads(socket.receive())
        except:
            continue
        response = ""
        if event["message"] == MESSAGE.GENERATE_DIAGRAM.value:
            try:
                # TODO: Generate diagram using data from MongoDB Cloud
                analysis = example_bp.get_analysis()
                user_details = example_bp.get_user_details()
                diagram.generateDiagram(analysis)
                response = json.dumps({
                    "message": event["message"],
                    "data": "Successfully generated diagram"
                })
            except Exception as e:
                print("Exception: ", type(e))
                response = json.dumps({
                    "message": event["message"],
                    "data": "Failed to generate diagram"
                })
        elif event["message"] == MESSAGE.FETCH_MAC_ADDRESSES.value:
            # TODO: Fetch MAC addresses from MongoDB Cloud
           # for collection in collections:
                for collection in collections:
                    response = json.dumps({
                    "message": event["message"],
                    "data": [collection]
                    })
        if response:
            socket.send(response)


websocket = Sockets(app)

websocket.register_blueprint(websocket_bp, url_prefix='/websocket')


def run_app():
    server = pywsgi.WSGIServer(
        (URL, PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()


def main():
    server = Thread(target=run_app)
    server.daemon = True
    server.start()

    webview.create_window(
        "Diagram Generator",
        f"http://{URL}:{PORT}",
        width=600, height=300
    )

    webview.start()


if __name__ == '__main__':
    main()
