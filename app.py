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
    """Generates an ultra-immersive image using OpenAI's DALL·E 3 based on the cumulative frequency spectrum."""
    try:
        if not frequencies:
            print("No frequencies detected. Skipping image generation.")
            return None

        # Extract frequency details
        frequency_str = ", ".join(f"{freq:.2f} Hz" for freq in frequencies[:10])

        # Map frequencies to natural and human-based sounds
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

        # 🌍 Determine an immersive real-world setting based on detected sounds
        if {"Ocean Waves", "Wind Whistling", "Whale Songs"} & set(related_nature_sounds):
            scene = "a vast open seaface, with waves crashing, misty air, and birds gliding above the horizon."
        elif {"Birdsong", "Wind Whistling"} & set(related_nature_sounds):
            scene = "a lush mountain valley at sunrise, with golden rays piercing the mist, trees swaying, and birds fluttering."
        elif {"Thunder"} & set(related_nature_sounds):
            scene = "a powerful thunderstorm over a distant, futuristic city, with neon lights reflecting off the rain-soaked streets."
        else:
            scene = "an abstract cosmic landscape, where sound waves transform into swirling nebulae and floating energy ribbons."

        # 🌟 **Print Log for Debugging**
        print("\n🎵 **Frequencies Captured:**", frequencies)
        print("🔹 **Used in Image Prompt:**", frequency_str)
        print("🌿 **Related to Nature Sounds:**", related_nature_sounds if related_nature_sounds else "None")
        print("🗣️ **Human-Based Frequencies (Speech Range):**", related_human_sounds if related_human_sounds else "None")
        print("🌌 **Scene Chosen:**", scene)

        # 🔮 **Generate an Ultra-Optimized Prompt for DALL·E 3 using GPT-4o**
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        chat_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in prompt engineering, crafting highly immersive and surreal visuals based on sound frequencies."},
                {"role": "user", "content": f"""
                Given the following sound frequencies: {frequency_str}, create a hyper-optimized prompt for DALL·E 3 that results in a visually stunning, photorealistic representation. The scene should be deeply immersive and elicit emotions tied to these frequencies. The setting should be {scene}, with surreal, dreamlike lighting and ethereal effects. The image should make the user feel drawn into the world, evoking both serenity and awe. Craft the most powerful, emotionally resonant, and mesmerizing prompt possible.
                """}
            ],
            temperature=0.7,
            max_tokens=150,
        )

        refined_prompt = chat_response.choices[0].message.content.strip()
        print("\n🔮 **Generated Optimized DALL·E Prompt:**", refined_prompt)

        # 🎨 Generate the Image with DALL·E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # 🌟 Return Image URL
        print(f"\n\n🔗 **Generated Image URL:** {response.data[0].url if response.data else 'None'}")
        return response.data[0].url if response.data else None

    except Exception as e:
        print("⚠️ Image generation error:", str(e))
        return None

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
