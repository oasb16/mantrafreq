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
    """Dynamically analyzes sound frequencies and generates an immersive image with DALL·E 3."""
    try:
        if not frequencies:
            print("No frequencies detected. Skipping image generation.")
            return None

        # Convert frequencies into a readable string
        frequency_str = ", ".join(f"{freq:.2f} Hz" for freq in frequencies[:10])  # Limit to 10 for clarity

        # Initialize OpenAI GPT client
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # 🔍 **Step 1: Ask GPT-4o for a SHORTER response**
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in sound frequency analysis and AI-generated imagery. "
                               "Your task is to analyze given frequencies for their real-world occurrences "
                               "(e.g., nature, music, machines, cosmic sounds) and summarize key insights concisely. "
                               "Then, create a **brief but ultra-immersive** DALL·E 3 prompt that translates these frequencies into a surreal, evocative image."
                },
                {
                    "role": "user",
                    "content": f"Analyze these sound frequencies: {frequency_str}. "
                               "Summarize in **5 short bullet points** how humans perceive them and their natural connections (e.g., thunder, wind, bird song). "
                               "Then, generate a **very concise and optimized** DALL·E 3 prompt that captures an immersive visual inspired by these sounds. "
                               "Limit response to **200 words total**."
                }
            ],
            temperature=0.6,
            max_tokens=200,  # Reduced to prevent long responses
        )

        # Extract GPT-4o's response
        result_text = response.choices[0].message.content.strip()

        # **New Extraction Logic:** Dynamically split response
        result_parts = result_text.split("\n\n")
        analysis_result = "\n\n".join(result_parts[:-1])  # Everything before last paragraph
        refined_prompt = result_parts[-1]  # Last paragraph is the optimized prompt

        print("\n🔍 **GPT-4o Analysis (Concise):**", analysis_result)
        print("\n🔮 **Optimized DALL·E 3 Prompt:**", refined_prompt)

        # 🎨 **Step 2: Generate Image using DALL·E 3**
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Extract image URL
        image_url = image_response.data[0].url if image_response.data else None

        # 🔥 **Final Print Statements**
        print("\n🎵 **Frequencies Captured:**", frequencies)
        print("🔹 **Used in Image Prompt:**", frequency_str)
        print("🌀 **Natural & Human Interpretations:**", analysis_result)
        print("🎨 **Why This Image is Important:** This image represents an artistic translation of sound waves, allowing humans to visualize and feel sound beyond mere auditory perception.")

        return image_url

    except Exception as e:
        print("Image generation error:", str(e))
        return None


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
