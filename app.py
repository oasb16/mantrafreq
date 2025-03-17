from flask import Flask, render_template, request,
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os
import fal_client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
openai.api_key = os.getenv('OPEN_API_KEY')

# Force WebSockets and allow cross-origin requests
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    audio_data = np.frombuffer(data, dtype=np.int16)
    N = len(audio_data)
    T = 1.0 / 44100.0
    yf = fft(audio_data)
    xf = np.fft.fftfreq(N, T)[:N//2]
    idx = np.argmax(np.abs(yf[:N//2]))
    freq = xf[idx]
    target_freq = 417
    tolerance = 5
    
    if abs(freq - target_freq) <= tolerance:
        result = f"Correct! Detected frequency: {freq:.2f} Hz"
        image_result = generate_image(freq)
    else:
        result = f"Incorrect. Detected frequency: {freq:.2f} Hz"
        image_result = None
    
    emit('result', {'message': result, 'image': image_result})

def generate_image(frequency):
    handler = fal_client.submit(
        "fal-ai/flux/dev",
        arguments={
            "prompt": f"Abstract visualization of sound wave at {frequency:.2f} Hz, ethereal, digital art, glowing resonance"
        },
    )
    return handler.get()

if __name__ == '__main__':
    socketio.run(app, debug=True)
