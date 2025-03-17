from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os, base64
import fal_client

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
openai.api_key = os.getenv('OPEN_API_KEY')

# Enable WebSockets with CORS
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_chunk')
def handle_audio_chunk(base64_data):
    try:
        # Decode Base64 data to bytes
        byte_data = base64.b64decode(base64_data)

        # Ensure buffer size is a multiple of element size (2 bytes for int16)
        if len(byte_data) % 2 != 0:
            byte_data += b'\x00'  # Pad with a null byte if necessary

        # Convert buffer to NumPy array
        audio_data = np.frombuffer(byte_data, dtype=np.int16)

        # Check if valid data exists
        if len(audio_data) == 0:
            emit('result', {'message': "Error: No audio data received", 'image': None})
            return

        # Perform FFT Analysis
        N = len(audio_data)
        T = 1.0 / 44100.0  # Assuming standard sample rate
        yf = fft(audio_data)
        xf = np.fft.fftfreq(N, T)[:N//2]

        # Find peak frequency
        if len(xf) > 0 and len(yf) > 0:
            idx = np.argmax(np.abs(yf[:N//2]))
            freq = float(xf[idx]) if idx < len(xf) else 0.0
        else:
            freq = 0.0

        # Ensure frequency is a valid number
        if np.isnan(freq) or np.isinf(freq):
            freq = 0.0

        # Convert frequency safely to a string
        freq_str = f"{freq:.2f}"

        # Log frequency for debugging
        print(f"Detected Frequency: {freq:.2f} Hz")
        if freq_str in "12":
            # Generate Image
            image_result = generate_image(str(freq_str))
        else:
            image_result = None

        # Send response to client
        emit('result', {'message': f"Detected Frequency: {freq_str} Hz", 'image': image_result})

    except Exception as e:
        print("Error processing audio:", str(e))
        emit('result', {'message': f"Error: {str(e)}", 'image': None})


def generate_image(frequency):
    """Generates an abstract visualization using fal.ai"""
    try:
        handler = fal_client.submit(
            "fal-ai/flux/dev",
            arguments={
                "prompt": f"Abstract visualization of sound wave at {frequency} Hz, ethereal, digital art, glowing resonance"
            },
        )
        return handler.get()
    except Exception as e:
        print("Image generation error:", str(e))
        return None

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
