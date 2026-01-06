// WebSocket connection
let ws = null;
let canvas = null;
let ctx = null;

// DOM elements
const startBtn = document.getElementById('start-btn');
const wsIndicator = document.getElementById('ws-indicator');
const wsStatus = document.getElementById('ws-status');
const botStatus = document.getElementById('bot-status');
const viewer = document.getElementById('viewer');
const placeholder = viewer.querySelector('.placeholder');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('browser-canvas');
    ctx = canvas.getContext('2d');

    // Connect WebSocket
    connectWebSocket();

    // Start button handler
    startBtn.addEventListener('click', startBot);

    // Canvas click handler (for Captcha interaction)
    canvas.addEventListener('click', handleCanvasClick);
});

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('[WebSocket] Connected');
        wsIndicator.classList.add('connected');
        wsStatus.textContent = 'Connecté';
    };

    ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        wsIndicator.classList.remove('connected');
        wsStatus.textContent = 'Déconnecté';

        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'screenshot':
            // Display screenshot on canvas
            displayScreenshot(data.image);
            break;

        case 'status':
            // Update bot status
            botStatus.textContent = data.message;
            break;

        case 'log':
            // Display log message
            console.log('[Bot]', data.message);
            break;
    }
}

function displayScreenshot(base64Image) {
    // Hide placeholder, show canvas
    placeholder.style.display = 'none';
    canvas.style.display = 'block';

    // Create image from base64
    const img = new Image();
    img.onload = () => {
        // Resize canvas to match image
        canvas.width = img.width;
        canvas.height = img.height;

        // Draw image
        ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/png;base64,${base64Image}`;
}

function startBot() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket non connecté. Veuillez patienter...');
        return;
    }

    // Disable button
    startBtn.disabled = true;
    startBtn.textContent = '⏳ En cours...';

    // Send start command via WebSocket
    ws.send(JSON.stringify({
        type: 'start'
    }));

    botStatus.textContent = 'Démarrage en cours...';
}

function handleCanvasClick(event) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    // Get click coordinates relative to canvas
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    // Send click to backend
    ws.send(JSON.stringify({
        type: 'click',
        x: Math.round(x),
        y: Math.round(y)
    }));

    console.log(`[Click] Sent to bot: (${Math.round(x)}, ${Math.round(y)})`);

    // Visual feedback
    ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, 2 * Math.PI);
    ctx.fill();

    // Fade out the red circle
    setTimeout(() => {
        // Redraw from last screenshot
        // (will be overwritten by next frame anyway)
    }, 200);
}
