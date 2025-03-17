# Mantra Frequency Analyzer

## 🌿 Introduction
Welcome to the **Mantra Frequency Analyzer**, a sophisticated fusion of **ancient wisdom** and **modern technology**. This Flask-powered web application enables users to chant powerful mantras while verifying their accuracy through **real-time audio frequency analysis**. By leveraging the **OpenAI Realtime API**, this application ensures that your mantra resonates at the correct vibrational frequency, amplifying its spiritual potency.

---

## ✨ Features
- **🎤 Real-Time Audio Capture** – Captures live audio from your microphone.
- **🔍 Frequency Analysis** – Uses **Fast Fourier Transform (FFT)** to detect mantra frequencies.
- **📡 OpenAI Realtime API Integration** – Ensures precision and enhances user experience.
- **📊 Instant Feedback** – Notifies users if their chanting matches the target frequency.
- **🌐 Elegant UI** – Aesthetic, spiritual, and minimalistic design for an immersive experience.

---

## 📜 Project Structure
```
mantra_frequency_analyzer/
├── app.py                  # Main Flask Application
├── requirements.txt        # Python Dependencies
├── package.json            # JavaScript Dependencies
├── Procfile                # Heroku Deployment File
├── runtime.txt             # Python Version Specification
├── templates/
│   └── index.html         # Frontend UI
└── static/
    └── js/
        └── recorder.js    # Audio Capture and Processing
```

---

## ⚙️ Installation & Setup
### 🔹 Prerequisites
- **Python 3.8+**
- **Node.js & npm**
- **Heroku CLI (for deployment)**

### 🔹 Clone Repository
```bash
git clone https://github.com/yourusername/mantra_frequency_analyzer.git
cd mantra_frequency_analyzer
```

### 🔹 Python Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🔹 JavaScript Dependencies
```bash
npm install
```

### 🔹 OpenAI API Key Configuration
```bash
export OPENAI_API_KEY='your-api-key'  # Windows: set OPENAI_API_KEY='your-api-key'
```

### 🔹 Run Locally
```bash
flask run
```
🌎 Open `http://127.0.0.1:5000/` in your browser.

---

## 🚀 Deployment on Heroku
### 🔹 Login & Create App
```bash
heroku login
heroku create your-app-name
```

### 🔹 Configure API Key
```bash
heroku config:set OPENAI_API_KEY='your-api-key'
```

### 🔹 Deploy
```bash
git add .
git commit -m "Initial commit"
git push heroku main
```

### 🔹 Scale & Launch
```bash
heroku ps:scale web=1
heroku open
```

---

## 🎙️ How to Use
1. **Start Recording** 🎤 – Click the **Start** button to begin chanting.
2. **Recite the Mantra** 🧘 – Ensure proper pronunciation and frequency.
3. **Stop Recording** ⏹️ – Click the **Stop** button when done.
4. **Receive Feedback** 📊 – The app will analyze and validate your chant.

---

## 🏆 Why This Matters
Mantras are **powerful sound vibrations** that align the mind and spirit. Proper chanting enhances **meditative states, mental clarity, and spiritual growth**. This application ensures that you are chanting at the **correct vibrational frequency**, maximizing the mantra’s potency and impact.

---

## 🛠️ Technologies Used
- **Flask** – Web Framework
- **Flask-SocketIO** – WebSockets for real-time audio streaming
- **OpenAI Realtime API** – Advanced audio analysis
- **NumPy & SciPy** – Frequency detection & signal processing
- **Heroku** – Cloud deployment

---

## 🙏 Acknowledgments
- **OpenAI** – For their cutting-edge AI technology.
- **Flask Community** – For providing a robust and lightweight web framework.
- **Spiritual Gurus & Scholars** – For inspiring the pursuit of mantra perfection.

---

## 🕉️ Live with Intention
This application is more than just a tool—it is an **instrument of self-improvement and mindfulness**. By ensuring mantra accuracy, we align ourselves with higher frequencies of consciousness and well-being.

**🌟 Chant with precision. Meditate with intention. Elevate your spirit. 🌟**

🔗 *Connect with us:* [YourWebsite.com](#) | [GitHub](https://github.com/yourusername) | [Twitter](#)

---

