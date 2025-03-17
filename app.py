from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os
import fal_client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
openai.api_key = os.getenv('OPEN_API_KEY')

# Force WebSockets and allow cross-origin requests
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", logger=True, engineio_logger=True)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        # Convert Uint8Array (JS) to proper byte buffer
        byte_data = bytes(data)
        audio_data = np.frombuffer(byte_data, dtype=np.int16)

        # Ensure buffer size is a multiple of 2
        if len(audio_data) % 2 != 0:
            audio_data = np.pad(audio_data, (0, 1), mode='constant')

        # Perform FFT Analysis
        N = len(audio_data)
        T = 1.0 / 44100.0  # Assuming 44.1kHz sample rate
        yf = fft(audio_data)
        xf = np.fft.fftfreq(N, T)[:N//2]

        # Find peak frequency
        idx = np.argmax(np.abs(yf[:N//2]))
        freq = xf[idx]

        # Log frequency for debugging
        print(f"Detected Frequency: {freq:.2f} Hz")

        # Generate Image
        image_result = generate_image(freq)

        # Send response to client
        emit('result', {'message': f"Detected Frequency: {freq:.2f} Hz", 'image': image_result})

    except Exception as e:
        print("Error processing audio:", str(e))
        emit('result', {'message': f"Error: {str(e)}", 'image': None})

def generate_image(frequency):
    """Generates an abstract visualization using fal.ai"""
    try:
        handler = fal_client.submit(
            "fal-ai/flux/dev",
            arguments={
                "prompt": f"Abstract visualization of sound wave at {frequency:.2f} Hz, ethereal, digital art, glowing resonance"
            },
        )
        return handler.get()
    except Exception as e:
        print("Image generation error:", str(e))
        return None

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
