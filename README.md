# Frequency Immersion 🎵🔮

## **Overview**
Frequency Immersion is an innovative **real-time sound visualization tool** that captures audio frequencies and translates them into **immersive, photorealistic visuals** using OpenAI's DALL·E 3. It bridges the gap between **sound and sight**, allowing users to experience music, speech, and natural sounds in a whole new way.

## **🔧 Features**
- 🎙 **Real-Time Audio Capture** – Listens to the microphone and extracts dominant sound frequencies.
- 🔍 **Dynamic Frequency Analysis** – Matches captured frequencies to human and natural sound occurrences.
- 🎨 **AI-Powered Visual Generation** – Creates cinematic, photorealistic images that reflect the detected soundscape.
- 🌍 **Immersive & Context-Aware Environments** – Ensures generated visuals match real-world scenarios rather than abstract noise.
- 📊 **Live Frequency Display** – Shows detected frequencies dynamically.

## **🚀 How It Works**
1. **Start Recording** – Click the **Start Recording** button to begin capturing sound.
2. **Process Frequencies** – The system extracts and analyzes dominant sound frequencies.
3. **AI Scene Generation** – The AI determines real-world equivalents (e.g., ocean waves, birdsong, neon city hum, etc.) and generates an immersive environment.
4. **Visualize the Sound** – The AI creates and displays a **cinematic image** based on detected frequencies.

## **📂 Project Structure**
```
📁 Frequency-Immersion/
├── 📄 app.py             # Flask backend with WebSockets for real-time audio processing
├── 📄 recorder.js        # Frontend script for capturing and sending audio data
├── 📄 index.html         # Main UI for user interaction
├── 📄 style.css          # Modern and immersive UI design
├── 📁 static/            # Contains frontend assets (CSS, JS)
└── 📄 README.md          # You are here 📖
```

## **🛠 Installation & Setup**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/yourusername/frequency-immersion.git
cd frequency-immersion
```
### **2️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```
### **3️⃣ Set Up OpenAI API Key**
Create a `.env` file and add your API key:
```bash
OPENAI_API_KEY=your_api_key_here
```
### **4️⃣ Run the Application**
```bash
python app.py
```
### **5️⃣ Open in Browser**
Visit `http://localhost:5000` to start experiencing **Frequency Immersion**.

## **🖥️ Deployment**
Easily deploy on **Heroku** or any cloud platform:
```bash
git push heroku main
heroku open
```

## **📢 Known Issues & Fixes**
- **Microphone access denied?** Ensure your browser has permission to use the mic (`chrome://settings/content/microphone` for Chrome users).
- **WebSocket issues?** Restart the Flask server and ensure `socket.io` is correctly installed.
- **No image generated?** Check if your **OpenAI API key** is valid and has sufficient quota.

## **🤝 Contributing**
Pull requests are welcome! For major changes, open an issue first to discuss what you’d like to improve.

## **📜 License**
MIT License © 2025 **Your Name/Your Organization**

## **🌟 Support & Feedback**
If you love **Frequency Immersion**, give it a ⭐ on [GitHub](https://github.com/yourusername/frequency-immersion)!

---
🎶 **"Transforming sound waves into visual art"** 🎶

