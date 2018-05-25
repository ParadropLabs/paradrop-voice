from __future__ import print_function

import threading
import time

from flask import Flask, jsonify
from pocketsphinx import LiveSpeech


MAX_HISTORY = 100
PORT = 8278


server = Flask(__name__)

phrases = []


@server.route("/phrases")
def GET_phrases():
    return jsonify(phrases)


def main():
    # Run the web server in a separate thread.
    server_args = {
        "host": "0.0.0.0",
        "port": PORT
    }
    server_thread = threading.Thread(target=server.run, kwargs=server_args)
    server_thread.start()

    speech = LiveSpeech()
    for phrase in speech:
        phrases.append({
            "time": time.time(),
            "text": str(phrase)
        })
        del phrases[:-MAX_HISTORY]
