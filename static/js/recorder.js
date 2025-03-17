document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const status = document.getElementById('status');
    const generatedImage = document.getElementById('generated-image');
    const socket = io();

    let mediaRecorder;

    startButton.addEventListener('click', async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.addEventListener('dataavailable', event => {
            if (event.data.size > 0) {
                event.data.arrayBuffer().then(buffer => {
                    socket.emit('audio_chunk', buffer);
                });
            }
        });

        mediaRecorder.start(100); // Send data in 100ms chunks
        startButton.disabled = true;
        stopButton.disabled = false;
        status.textContent = 'Recording...';
    });

    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
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