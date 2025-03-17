from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os, base64
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
def handle_audio_chunk(base64_data):
    try:
        # Decode Base64 to binary
        byte_data = base64.b64decode(base64_data)

        # Ensure buffer size is a multiple of element size
        buffer_length = len(byte_data)
        if buffer_length % 2 != 0:
            byte_data += b'\x00'  # Padding to ensure even length

        # Convert byte buffer to NumPy array
        audio_data = np.frombuffer(byte_data, dtype=np.int16)

        # Perform FFT Analysis
        N = len(audio_data)
        T = 1.0 / 44100.0  # Assuming 44.1kHz sample rate
        yf = fft(audio_data)
        xf = np.fft.fftfreq(N, T)[:N//2]

        # Find peak frequency
        idx = np.argmax(np.abs(yf[:N//2]))
        freq = xf[idx]

        if freq in "12":
        # Log frequency for debugging
            print(f"Detected Frequency: {freq:.2f} Hz")

            # Generate Image
            image_result = generate_image(freq)
        else:
            image_result = "Lol no image"


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
