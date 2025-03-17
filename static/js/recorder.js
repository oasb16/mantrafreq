document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const status = document.getElementById('status');
    const generatedImage = document.getElementById('generated-image');
    const frequencyList = document.getElementById('frequency-list');
    const analysisText = document.getElementById('analysis-text');

    const socket = io({ transports: ["websocket"] });
    let mediaRecorder;

    startButton.addEventListener('click', async () => {
        try {
            socket.emit('start_recording');
            frequencyList.innerHTML = ""; // Clear previous frequencies
            analysisText.innerHTML = "Analyzing..."; // Show analysis loading
            generatedImage.style.display = 'none';

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            mediaRecorder.addEventListener('dataavailable', async event => {
                if (event.data.size > 0) {
                    const arrayBuffer = await event.data.arrayBuffer();
                    const uint8Array = new Uint8Array(arrayBuffer);
                    const base64String = btoa(String.fromCharCode(...uint8Array));
                    socket.emit('audio_chunk', base64String);
                }
            });

            mediaRecorder.start(100);
            startButton.disabled = true;
            stopButton.disabled = false;
            status.textContent = 'Recording...';
        } catch (error) {
            console.error("Error accessing microphone:", error);
            status.textContent = "Microphone access denied.";
        }
    });

    stopButton.addEventListener('click', () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            socket.emit('stop_recording');
        }
        startButton.disabled = false;
        stopButton.disabled = true;
        status.textContent = 'Processing...';
    });

    socket.on('result', data => {
        status.textContent = data.message;

        if (data.analysis) {
            analysisText.innerHTML = data.analysis.replace(/\n/g, "<br>"); // Display formatted analysis
        } else {
            analysisText.innerHTML = "No analysis available.";
        }

        if (data.image) {
            generatedImage.src = data.image;
            generatedImage.style.display = 'block';
        } else {
            generatedImage.style.display = 'none';
        }
    });

    socket.on('frequency_update', data => {
        const freqElement = document.createElement("p");
        freqElement.textContent = `${data.frequency} Hz`;
        frequencyList.appendChild(freqElement);
    });
});
