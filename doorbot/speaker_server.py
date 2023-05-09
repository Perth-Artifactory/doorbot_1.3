import base64
import io
import os
import tempfile
import threading
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from interfaces.text_to_speech import non_blocking_speak
from interfaces.sound_player import SoundPlayer

app = Flask(__name__)
auth = HTTPBasicAuth()

# Replace 'user' and 'password' with your desired credentials
users = {
    "user": generate_password_hash("password")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/speak', methods=['POST'])
@auth.login_required
def webhook_speak():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({'error': 'Missing text parameter'}), 400

    text = data['text']
    non_blocking_speak(text)

    return jsonify({'success': True})

@app.route('/play_mp3_base64', methods=['POST'])
@auth.login_required
def webhook_play_mp3_base64():
    data = request.get_json()
    if 'base64_mp3' not in data:
        return jsonify({'error': 'Missing base64_mp3 parameter'}), 400

    base64_mp3 = data['base64_mp3']
    mp3_data = base64.b64decode(base64_mp3)

    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
        temp_mp3.write(mp3_data)
        temp_mp3_path = temp_mp3.name

    def play_and_delete_mp3():
        SoundPlayer.play_sound(temp_mp3_path)
        SoundPlayer.wait_until_done()
        os.remove(temp_mp3_path)

    play_thread = threading.Thread(target=play_and_delete_mp3)
    play_thread.start()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
