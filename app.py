from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    # Convert audio data to numpy array
    audio_data = np.frombuffer(data, dtype=np.int16)
    
    # Perform FFT to find frequency components
    N = len(audio_data)
    T = 1.0 / 44100.0  # Assuming a sample rate of 44100 Hz
    yf = fft(audio_data)
    xf = np.fft.fftfreq(N, T)[:N//2]
    
    # Find the peak frequency
    idx = np.argmax(np.abs(yf[:N//2]))
    freq = xf[idx]
    
    # Define the target frequency for the mantra (e.g., 417 Hz)
    target_freq = 417
    tolerance = 5  # Allowable deviation in Hz
    
    # Check if the detected frequency matches the target frequency within tolerance
    if abs(freq - target_freq) <= tolerance:
        result = f"Correct! Detected frequency: {freq:.2f} Hz"
    else:
        result = f"Incorrect. Detected frequency: {freq:.2f} Hz"
    
    emit('result', result)

if __name__ == '__main__':
    socketio.run(app, debug=True)
