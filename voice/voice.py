from pocketsphinx import LiveSpeech


def main():
    speech = LiveSpeech()

    for phrase in speech:
        print(phrase)
