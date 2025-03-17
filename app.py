from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os, base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Global list to store detected frequencies
frequency_list = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_recording')
def start_recording():
    """Clears the frequency list when recording starts."""
    global frequency_list
    frequency_list = []
    emit('status', {'message': 'Recording started...'})

@socketio.on('audio_chunk')
def handle_audio_chunk(base64_data):
    """Processes incoming audio chunks and accumulates frequency data."""
    global frequency_list
    try:
        byte_data = base64.b64decode(base64_data)
        
        # Ensure buffer size is a multiple of element size (2 bytes for int16)
        if len(byte_data) % 2 != 0:
            byte_data += b'\x00'

        audio_data = np.frombuffer(byte_data, dtype=np.int16)

        if len(audio_data) == 0:
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

        # Ensure valid frequency
        if np.isnan(freq) or np.isinf(freq):
            freq = 0.0

        # Store frequency
        frequency_list.append(freq)

    except Exception as e:
        print("Error processing audio:", str(e))

@socketio.on('stop_recording')
def stop_recording():
    """Processes the collected frequencies and generates an image."""
    global frequency_list
    try:
        if not frequency_list:
            emit('result', {'message': "No frequencies detected.", 'image': None})
            return

        # Generate image using cumulative frequency data
        image_url = generate_image(frequency_list)

        # Send response
        emit('result', {'message': "Recording stopped. Image generated.", 'image': image_url})

    except Exception as e:
        print("Error generating image:", str(e))
        emit('result', {'message': f"Error: {str(e)}", 'image': None})

def generate_image(frequencies):
    """Generates an image using OpenAI's DALL·E 3 based on cumulative frequency spectrum."""
    try:
        frequency_str = ", ".join(f"{freq:.2f} Hz" for freq in frequencies[:10])  # Limit for clarity

        client = openai.OpenAI()
        # Initialize OpenAI client
        client.api_key = os.getenv('OPEN_API_KEY')
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Abstract visualization of sound waves at {frequency_str}, ethereal, digital art, glowing resonance",
            size="1024x1024",
            quality="standard",
            n=1,
        )

        return response.data[0].url if response.data else None

    except Exception as e:
        print("Image generation error:", str(e))
        return None

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
