from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import sys
from vosk import Model, KaldiRecognizer, SetLogLevel


app = Flask(__name__)
CORS(app)

SAMPLE_RATE = 16000
SetLogLevel(0)
model = Model(lang="en-us")
rec = KaldiRecognizer(model, SAMPLE_RATE)

def ffmpeg(file):
    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                                file,
                                "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                                stdout=subprocess.PIPE) as process:

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                print(rec.Result())
            else:
                print(rec.PartialResult())

        return rec.FinalResult()


@app.route('/audio-recognize', methods=['POST']) 
def index():
    files = request.files
    file = files.get('file')
    print(file)

    with open(os.path.abspath('file.wav'), 'wb') as f:
        f.write(file.stream._file)

    res = ffmpeg('file.wav')
    response = jsonify({'result': res})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)