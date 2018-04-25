import speech_recognition as sr
import time
from threading import Thread
from flask import Flask, jsonify
import time
import sched, time

server = Flask(__name__)
dict = {}
list = []
index = 0

@server.route('/messages')
def GET_messages():
    print("inside messages")
    return jsonify(list)

def runServer():
    print("About to run server")
    server.run(host='0.0.0.0', port=6000)

# Run the web server in a separate thread.
thread = Thread(target = runServer)
thread.start()


# Record Audio
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    r.adjust_for_ambient_noise(source, duration = 1)
    audio = r.listen(source)
    text = r.recognize_google(audio)
    index = index + 1
    dict['index'] = index
    dict['transcript'] = text
    dict['timestamp'] = int(round(time.time() * 1000))
    list.append(dict)
    print("You said: " + text)
# Speech recognition using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    heardVoice = r.recognize_google(audio)
    checkString = "emergency detected"
    checkVideo = "share video"
    s = sched.scheduler(time.time, time.sleep)
    print("You said: " + heardVoice)
    if checkString in heardVoice:
        s.enter(0.3, checkVideo in heardVoice, (sched))
        print(heardVoice)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))