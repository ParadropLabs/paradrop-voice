from __future__ import print_function

import os
import threading

from flask import Flask, jsonify, request

from .voice import VoiceService


PORT = int(os.environ.get("PORT", 8278))


server = Flask(__name__)
voice = VoiceService()


@server.route("/phrases")
def get_phrases():
    return jsonify(voice.get_phrases())


@server.route("/prompts", methods=["POST"])
def create_prompt():
    data = request.get_json()
    prompt = voice.create_prompt(**data)
    return jsonify(prompt)


@server.route("/prompts/<prompt_id>")
def get_prompt(prompt_id):
    return jsonify(voice.get_prompt(prompt_id))


@server.route("/status")
def get_status():
    return jsonify(voice.get_status())


def start_server():
    """
    Run the web server in a separate thread.
    """
    server_args = {
        "host": "0.0.0.0",
        "port": PORT
    }
    server_thread = threading.Thread(target=server.run, kwargs=server_args)
    server_thread.start()


def main():
    voice_thread = threading.Thread(target=voice.run)
    voice_thread.start()

    server.run(host="0.0.0.0", port=PORT)
