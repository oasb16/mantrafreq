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
        if not frequencies:
            print("No frequencies detected. Skipping image generation.")
            return None

        # Limit to first 10 for clarity in prompt
        frequency_str = ", ".join(f"{freq:.2f} Hz" for freq in frequencies[:10])

        # Map to known frequency ranges
        human_speech = [85, 300, 3400]  # Hz range for human speech
        nature_sounds = {
            "Birdsong": (2000, 8000),
            "Thunder": (20, 120),
            "Ocean Waves": (10, 500),
            "Wind Whistling": (1000, 4000),
            "Whale Songs": (10, 300),
        }

        related_nature_sounds = [name for name, (low, high) in nature_sounds.items() if any(low <= f <= high for f in frequencies)]
        related_human_sounds = [f for f in frequencies if human_speech[0] <= f <= human_speech[2]]

        print("\n🎵 **Frequencies Captured:**", frequencies)
        print("🔹 **Used in Image Prompt:**", frequency_str)
        print("🌿 **Related to Nature Sounds:**", related_nature_sounds if related_nature_sounds else "None")
        print("🗣️ **Human-Based Frequencies (Speech Range):**", related_human_sounds if related_human_sounds else "None")

        image_importance = "This image represents an abstract visualization of sound waves detected in the environment, translating unseen vibrations into a perceptible, artistic form."

        print("🎨 **Why This Image is Important:**", image_importance)

        # Initialize OpenAI client with API key
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a prompt engineering expert, crafting DALL·E prompts that create ultra-realistic, immersive visuals based on sound frequencies."},
                {"role": "user", "content": f"Given the following sound frequencies: {frequency_str}, craft a hyper-optimized prompt that results in a visually stunning, highly detailed, photorealistic representation of how these frequencies would be perceived by humans. Incorporate natural, cosmic, and emotional interpretations. The prompt should evoke sensations, energy, and a surreal yet deeply immersive scene."}
            ],
            temperature=0.7,  # Ensures a balance of creativity and control
            max_tokens=150,  # Keeps it concise yet powerful
        )

        refined_prompt = chat_response.choices[0].message.content.strip()
        print("\n🔮 **Generated Optimized DALL·E Prompt:**", refined_prompt)

        response = client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
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
