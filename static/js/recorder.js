import { RealtimeClient } from '@openai/realtime-api-beta';

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const status = document.getElementById('status');

    let mediaRecorder;
    let client;

    startButton.addEventListener('click', async () => {
        // Initialize the RealtimeClient
        client = new RealtimeClient({
            apiKey: 'YOUR_OPENAI_API_KEY',
            dangerouslyAllowAPIKeyInBrowser: true,
        });

        // Set up event handling
        client.on('response', (response) => {
            // Process the response from the API
            console.log('API Response:', response);
            status.textContent = 'Processing complete.';
        });

        // Connect to the Realtime API
        await client.connect();

        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.addEventListener('dataavailable', async (event) => {
            if (event.data.size > 0) {
                const arrayBuffer = await event.data.arrayBuffer();
                const audioData = new Int16Array(arrayBuffer);
                client.sendAudio(audioData);
            }
        });

        mediaRecorder.start(100); // Send data in 100ms chunks

        startButton.disabled = true;
        stopButton.disabled = false;
        status.textContent = 'Recording...';
    });

    stopButton.addEventListener('click', () => {
        mediaRecorder.stop();
        client.sendAudio(null); // Signal end of audio stream
        startButton.disabled = false;
        stopButton.disabled = true;
        status.textContent = 'Processing...';
    });
});
