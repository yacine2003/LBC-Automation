// WebSocket connection
let ws = null;

// Session state
let sessionStartTime = null;
let timerInterval = null;
let captchaAudio = null;

// DOM elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const wsIndicator = document.getElementById('ws-indicator');
const wsStatus = document.getElementById('ws-status');
const botStatus = document.getElementById('bot-status');
const logsContainer = document.getElementById('logs-container');
const logsPlaceholder = document.getElementById('logs-placeholder');
const captchaAlert = document.getElementById('captcha-alert');

// Stats elements
const statPublished = document.getElementById('stat-published');
const statCurrent = document.getElementById('stat-current');
const statTime = document.getElementById('stat-time');
const statStatus = document.getElementById('stat-status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Connect WebSocket
    connectWebSocket();

    // Button handlers
    startBtn.addEventListener('click', startBot);
    stopBtn.addEventListener('click', stopBot);

    // Préparer l'audio pour captcha (son d'alerte)
    prepareCaptchaAudio();
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
        case 'status':
            // Update bot status
            botStatus.textContent = data.message;
            statStatus.textContent = data.message;
            addLog(data.message, 'info');
            break;

        case 'log':
            // Add log entry
            addLog(data.message, data.level || 'info');
            break;

        case 'captcha_detected':
            // Show captcha alert
            showCaptchaAlert();
            addLog('🚨 CAPTCHA DÉTECTÉ - Résolution manuelle requise', 'captcha');
            break;

        case 'captcha_resolved':
            // Hide captcha alert
            hideCaptchaAlert();
            addLog('✅ Captcha résolu - Reprise du processus', 'success');
            break;

        case 'ad_start':
            // Nouvelle annonce commencée
            statCurrent.textContent = data.ad_title || 'En cours...';
            addLog(`📝 Début publication: ${data.ad_title}`, 'info');
            break;

        case 'ad_complete':
            // Annonce terminée
            const currentCount = parseInt(statPublished.textContent) || 0;
            statPublished.textContent = currentCount + 1;
            statCurrent.textContent = '-';
            addLog(`✅ Annonce publiée: ${data.ad_title}`, 'success');
            break;

        case 'session_stats':
            // Update stats
            if (data.published !== undefined) statPublished.textContent = data.published;
            if (data.current) statCurrent.textContent = data.current;
            break;

        case 'bot_stopped':
            // Reset UI when bot stops
            stopSession();
            addLog('⏹ Bot arrêté', 'warning');
            break;

        case 'error':
            // Error message
            addLog(`❌ Erreur: ${data.message}`, 'error');
            break;
    }
}

// === LOGS MANAGEMENT ===
function addLog(message, level = 'info') {
    // Hide placeholder on first log
    if (logsPlaceholder) {
        logsPlaceholder.style.display = 'none';
    }

    // Create log entry
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${level}`;
    
    const timestamp = new Date().toLocaleTimeString('fr-FR');
    logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span>${message}`;
    
    logsContainer.appendChild(logEntry);
    
    // Auto-scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;

    // Limit logs to 100 entries
    const logs = logsContainer.querySelectorAll('.log-entry');
    if (logs.length > 100) {
        logs[0].remove();
    }
}

function clearLogs() {
    const logs = logsContainer.querySelectorAll('.log-entry');
    logs.forEach(log => log.remove());
    if (logsPlaceholder) {
        logsPlaceholder.style.display = 'block';
    }
}

// === CAPTCHA ALERT ===
function showCaptchaAlert() {
    captchaAlert.classList.add('active');
    playCaptchaSound();
}

function hideCaptchaAlert() {
    captchaAlert.classList.remove('active');
}

function prepareCaptchaAudio() {
    // Créer un contexte audio pour le son d'alerte
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        captchaAudio = audioContext;
    } catch (e) {
        console.warn('Audio not supported');
    }
}

function playCaptchaSound() {
    // Jouer un son d'alerte simple
    if (!captchaAudio) return;
    
    try {
        const oscillator = captchaAudio.createOscillator();
        const gainNode = captchaAudio.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(captchaAudio.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, captchaAudio.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, captchaAudio.currentTime + 0.5);
        
        oscillator.start(captchaAudio.currentTime);
        oscillator.stop(captchaAudio.currentTime + 0.5);
        
        // Répéter 3 fois
        setTimeout(() => playCaptchaSound(), 600);
        setTimeout(() => playCaptchaSound(), 1200);
    } catch (e) {
        console.warn('Could not play sound', e);
    }
}

// === SESSION TIMER ===
function startTimer() {
    sessionStartTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimer() {
    if (!sessionStartTime) return;
    
    const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    
    statTime.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// === SESSION MANAGEMENT ===
function stopSession() {
    stopTimer();
    botStatus.textContent = 'Bot arrêté';
    statStatus.textContent = 'Terminé';
    statCurrent.textContent = '-';
    
    startBtn.style.display = 'inline-block';
    startBtn.disabled = false;
    startBtn.textContent = '▶ DÉMARRER';
    stopBtn.style.display = 'none';
    stopBtn.disabled = false;
    stopBtn.textContent = '⏹ ARRÊTER';
    
    hideCaptchaAlert();
}

function startBot() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket non connecté. Veuillez patienter...');
        return;
    }

    // Reset stats
    statPublished.textContent = '0';
    statCurrent.textContent = 'Initialisation...';
    statTime.textContent = '00:00';
    statStatus.textContent = 'En cours';
    
    // Clear previous logs
    clearLogs();
    
    // Start timer
    startTimer();
    
    // Toggle buttons
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';

    // Send start command via WebSocket
    ws.send(JSON.stringify({
        type: 'start'
    }));

    botStatus.textContent = 'Démarrage en cours...';
    addLog('🚀 Démarrage de la session de publication...', 'info');
}

function stopBot() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket non connecté.');
        return;
    }

    // Send stop command
    ws.send(JSON.stringify({
        type: 'stop'
    }));

    // Toggle buttons
    stopBtn.disabled = true;
    stopBtn.textContent = '⏳ Arrêt...';

    botStatus.textContent = 'Arrêt du bot en cours...';
    addLog('⏸️ Demande d\'arrêt envoyée...', 'warning');
}
