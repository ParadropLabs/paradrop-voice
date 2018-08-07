from __future__ import print_function

import os
import time
import tempfile
import pygame

import pyttsx3
import queue
import sphinxbase
from pocketsphinx import Decoder, get_model_path

AUDIO_CACHE = {}

def play_audio(url):
    data = ""
    if url in AUDIO_CACHE:
        data = AUDIO_CACHE[url]
    else:
        r = requests.get(url)
        data = r.content
        AUDIO_CACHE[url] = data
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'wb') as f:
        f.write(data)
    #pygame.init()
    pygame.mixer.music.load(tmp.name)
    pygame.mixer.music.play()
    time.sleep(7) 
    pygame.mixer.music.stop()
    #thread.exit()

def get_decoder_config():
    """
    Get a populated configuration object for the pocketsphinx Decoder.
    """
    model_dir = get_model_path()

    config = Decoder.default_config()
    config.set_string("-dict", os.path.join(model_dir, "cmudict-en-us.dict"))
    config.set_string("-fdict", os.path.join(model_dir, "en-us/noisedict"))
    config.set_string("-featparams", os.path.join(model_dir, "en-us/feat.params"))
    config.set_string("-hmm", os.path.join(model_dir, "en-us"))
    config.set_string("-lm", os.path.join(model_dir, "en-us.lm.bin"))
    config.set_string("-mdef", os.path.join(model_dir, "en-us/mdef"))
    config.set_string("-mean", os.path.join(model_dir, "en-us/means"))
    config.set_string("-sendump", os.path.join(model_dir, "en-us/sendump"))
    config.set_string("-tmat", os.path.join(model_dir, "en-us/transition_matrices"))
    config.set_string("-var", os.path.join(model_dir, "en-us/variances"))

    return config


class VoiceService(object):
    audio_device = None
    buffer_size = 2048
    sampling_rate = 16000

    def __init__(self):
        config = get_decoder_config()
        self.decoder = Decoder(config)

        self.speech = pyttsx3.init()
        pygame.init()

        self.audio = sphinxbase.Ad(self.audio_device, self.sampling_rate)
        self.buffer = bytearray(self.buffer_size)

        self.default_search = self.decoder.get_search()
        self.in_speech = False
        self.max_history = 100
        self.phrases = []
        self.prompts = {}

        self.next_prompt_id = 1

        self.current_prompt = None
        self.prompt_queue = queue.Queue()

    def create_prompt(self, message=None, message_url=None, search="enable", timeout=15):
        """
        Create a new prompt and add it to the queue.

        Currently, only one type of prompt is supported. We play a message,
        then wait for someone to say a specific word (the search word) within
        the alloted amount of time.

        The status of the prompt can be retrieved by calling get_prompt with
        the appropriate id.

        timeout: prompt timeout in seconds, expected to be either None or numeric.
        """
        if timeout is not None:
            # Be forgiving of caller who may have passed timeout as a string.
            timeout = float(timeout)

        prompt = {
            "created_time": time.time(),
            "detected": False,
            "detected_time": None,
            "id": self.get_next_prompt_id(),
            "message": message,
            "message_url": message_url,
            "search": search,
            "search_started": False,
            "search_started_time": None,
            "played": False,
            "played_time": None,
            "timeout": timeout,
            "timed_out": False
        }
        self.prompts[str(prompt['id'])] = prompt
        self.prompt_queue.put(prompt)
        return prompt

    def get_next_prompt_id(self):
        """
        Get a unique ID for a prompt.
        """
        tmp = self.next_prompt_id
        self.next_prompt_id += 1
        return tmp

    def get_phrases(self):
        """
        Get the history of detected phrases.
        """
        return self.phrases

    def get_prompt(self, prompt_id):
        """
        Get information about a prompt.
        """
        return self.prompts[str(prompt_id)]

    def get_status(self):
        """
        Get the system status.
        """
        status = {
            "current_prompt": self.current_prompt,
            "in_speech": self.decoder.get_in_speech(),
            "queue_length": len(self.prompt_queue),
            "search": self.decoder.get_search()
        }
        return status

    def process_hypothesis(self, hypothesis):
        print("SPEECH {}".format(hypothesis.hypstr))

        phrase = {
            "search": self.decoder.get_search(),
            "time": time.time(),
            "text": hypothesis.hypstr
        }
        self.phrases.append(phrase)
        del self.phrases[:-self.max_history]

    def run_next_prompt(self):
        if self.prompt_queue.empty():
            self.create_prompt(None, search="paradrop", timeout=None)

        self.current_prompt = self.prompt_queue.get_nowait()
        self.decoder.set_search(self.current_prompt['search'])

        if self.current_prompt['message'] is not None:
            self.audio.stop_recording()
            #self.speech.say(self.current_prompt['message'])
            if self.current_prompt['message_url'] is not None:
                #thread.start_new_thread(play_audio, ( self.current_prompt['message_url'],))
                play_audio(self.current_prompt['message_url'])
                self.current_prompt['played'] = True
            self.current_prompt['played_time'] = time.time()
            #self.speech.runAndWait()
            self.audio.start_recording()

        self.current_prompt['search_started_time'] = time.time()
        self.current_prompt['search_started'] = True

    def detect_timeout(self):
        """
        Check if the current prompt has timed out.
        """
        if self.current_prompt is None:
            # No active prompt to timeout.
            return False

        if self.decoder.get_in_speech():
            # Defer timeout if decoder reports that speech is in progress.  A
            # person may be speaking the target phrase currently.
            return False

        if self.current_prompt['timeout'] is None:
            # If timeout is None, then only timeout when there is another item
            # in the queue.
            return not self.prompt_queue.empty()
        else:
            diff = time.time() - self.current_prompt['search_started_time']
            return diff >= self.current_prompt['timeout']

    def run(self):
        self.decoder.set_keyphrase("allow", "allow")
        self.decoder.set_keyphrase("enable", "enable")
        self.decoder.set_keyphrase("paradrop", "para drop")

        self.audio.start_recording()
        while True:
            if self.current_prompt is None:
                self.run_next_prompt()
                self.decoder.start_utt()

            self.audio.readinto(self.buffer)
            self.decoder.process_raw(self.buffer, False, False)

            if self.in_speech and not self.decoder.get_in_speech():
                self.decoder.end_utt()

                hypothesis = self.decoder.hyp()
                if hypothesis is not None:
                    self.process_hypothesis(hypothesis)
                    self.current_prompt['detected'] = True
                    self.current_prompt['detected_time'] = time.time()
                    self.current_prompt = None
                else:
                    self.decoder.start_utt()

            if self.detect_timeout():
                self.decoder.end_utt()
                self.current_prompt['timed_out'] = True
                self.current_prompt = None

            self.in_speech = self.decoder.get_in_speech()
