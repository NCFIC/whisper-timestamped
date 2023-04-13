import whisper_timestamped as whisper

# import json
# print(json.dumps(result, indent = 2, ensure_ascii = False))

import os
from flask import Flask, request
import requests
import json

settings = {
    'jarvisAuth': '51ae08b9a63acbfcbbd1b56860f7600f138471055f8049b81e3feb4b277210fc5f19763c4f5faf73b9d4a723fa74dff606b5f2deb66e566e8577bc25e6cb932f:62ba055059e9a0d1167c4b9c',
}

app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

@app.route("/generateTranscription", methods=['POST'])
def generate_transcription():

    data = request.get_json()
    sermon = data['sermon']

    if sermon['audio']['url']:
        # Download the audio file and save it locally
        filename = os.path.basename(sermon['audio']['url']).split('?')[0]
        with open(filename, 'wb') as f:
            response = requests.get(sermon['audio']['url'])
            f.write(response.content)

            audio = whisper.load_audio(filename)
            model = whisper.load_model("tiny", device="cpu")
            result = whisper.transcribe(model, audio)

            sermon_post_data = {
                'transcriptionSegments': result['segments'],
                'transcription': result['text'],
            }

            url = f'https://api.churchandfamilylife.com/' + sermon['collection'] + '/' + sermon['id'] + '?fields=["title"]'
            data = json.dumps(sermon_post_data)
            headers = {'authorization': settings['jarvisAuth'], 'Content-Type': 'application/json'}
            response = requests.put(url, data=data, headers=headers)

            return result

    else:
        return 'No audio URL provided'


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
