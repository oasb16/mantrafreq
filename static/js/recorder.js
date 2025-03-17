document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const status = document.getElementById('status');
    const generatedImage = document.getElementById('generated-image');

    const socket = io({ transports: ["websocket"] }); // Ensure WebSockets only

    let mediaRecorder;

    startButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            mediaRecorder.addEventListener('dataavailable', async event => {
                if (event.data.size > 0) {
                    const arrayBuffer = await event.data.arrayBuffer();
                    const uint8Array = new Uint8Array(arrayBuffer);

                    // Convert to Base64 for safe transmission
                    const base64String = btoa(String.fromCharCode(...uint8Array));

                    socket.emit('audio_chunk', base64String);
                }
            });

            mediaRecorder.start(100); // Send data in 100ms chunks
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
        }
        startButton.disabled = false;
        stopButton.disabled = true;
        status.textContent = 'Processing...';
    });

    socket.on('result', data => {
        status.textContent = data.message;
        if (data.image) {
            generatedImage.src = data.image;
            generatedImage.style.display = 'block';
        } else {
            generatedImage.style.display = 'none';
        }
    });
});
