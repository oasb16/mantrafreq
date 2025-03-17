from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
from scipy.fft import fft
import openai, os, base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", ping_interval=25)

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

        if np.isnan(freq) or np.isinf(freq):
            freq = 0.0

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

        image_url, analysis_text = generate_image(frequency_list)

        emit('result', {
            'message': "Recording stopped. Image generated.",
            'image': image_url,
            'analysis': analysis_text
        })

    except Exception as e:
        print("Error generating image:", str(e))
        emit('result', {'message': f"Error: {str(e)}", 'image': None})


def generate_image(frequencies):
    """Creates an immersive visualization based on sound frequencies."""
    try:
        if not frequencies:
            print("No frequencies detected. Skipping image generation.")
            return None, "No analysis available."

        frequency_str = ", ".join(f"{freq:.2f} Hz" for freq in frequencies[:10])

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a frequency analyst and expert in AI-generated imagery. "
                               "Your task is to interpret these frequencies and create a **real-world immersive scene** "
                               "that matches them. Ensure a seamless **cinematic visual with dynamic motion, realistic lighting,** "
                               "and environmental accuracy."
                },
                {
                    "role": "user",
                    "content": f"Analyze these sound frequencies: {frequency_str}. "
                               "Match them to natural and human sources (e.g., ocean waves, thunderstorms, neon city hum, birds, wind, technology). "
                               "Then, construct an **ultra-immersive, hyper-realistic DALL·E 3 prompt** that "
                               "describes a visually consistent environment where these frequencies naturally occur. "
                               "It should feel **cinematic, deeply atmospheric, and engaging**, avoiding abstract waves or randomness."
                }
            ],
            temperature=0.5,
            max_tokens=200,
        )

        result_text = response.choices[0].message.content.strip()

        result_parts = result_text.split("\n\n")
        analysis_result = "\n\n".join(result_parts[:-1])
        refined_prompt = result_parts[-1]

        print("\n🔍 **GPT-4o Analysis Result:**", analysis_result)
        print("\n🎨 **Final DALL·E 3 Prompt:**", refined_prompt)

        image_response = client.images.generate(
            model="dall-e-3",
            prompt=refined_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = image_response.data[0].url if image_response.data else None

        return image_url, analysis_result

    except Exception as e:
        print("Image generation error:", str(e))
        return None, "Error generating analysis."


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
