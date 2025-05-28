// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to n8n webhook
async function sendEmotionToN8N(emotionData) {
    const n8nWebhookUrl = "https://mehax.app.n8n.cloud/webhook/receive-emotion-data";
    
    console.log('🚀 Sending to n8n webhook:', emotionData);
    
    const payload = {
        emotion: emotionData.emotion,
        confidence: emotionData.confidence,
        timestamp: new Date().toISOString(),
        text: emotionData.text || '',
        sessionId: emotionData.sessionId || 'default'
    };
    
    try {
        const response = await fetch(n8nWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            body: JSON.stringify(payload)
        });
        
        console.log('📡 Response status:', response.status);
        
        // Try to parse response regardless of status
        let responseData;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
            console.log('📄 Response data:', responseData);
        } else {
            const textResponse = await response.text();
            console.log('📄 Response text:', textResponse);
            responseData = { text: textResponse };
        }
        
        if (!response.ok) {
            console.error(`❌ HTTP ${response.status}:`, responseData);
            // Don't throw - we still want to update the UI
        } else {
            console.log('✅ Webhook success:', responseData);
        }
        
        // Update UI with any Claude response if available
        if (responseData.analysis || responseData.message) {
            updateEmotionPanel(emotionData.emotion, emotionData.confidence, responseData.analysis || responseData.message);
        }
        
        return true;
        
    } catch (error) {
        console.error('❌ Network error:', error);
        // Don't let network errors break the app
        return false;
    }
}

// Update emotion panel with analysis
function updateEmotionPanel(emotion, confidence, analysis = null) {
    const emotionLabel = document.getElementById("emotion-label");
    const intensityFill = document.getElementById("intensity-fill");
    
    if (emotionLabel) {
        emotionLabel.textContent = emotion;
    }
    
    if (intensityFill) {
        intensityFill.style.width = `${confidence * 100}%`;
        
        // Color based on emotion
        const emotionColors = {
            happy: '#4CAF50',
            sad: '#2196F3',
            angry: '#f44336',
            fear: '#9C27B0',
            surprise: '#FF9800',
            disgust: '#795548',
            neutral: '#607D8B'
        };
        
        intensityFill.style.background = emotionColors[emotion] || '#607D8B';
    }
    
    // Show analysis if available
    if (analysis) {
        const statusText = document.getElementById("status");
        if (statusText) {
            statusText.textContent = analysis;
        }
    }
}

// Initialize when DOM is fully loaded
window.addEventListener("DOMContentLoaded", () => {
    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    const statusText = document.getElementById("status");
    const chatHistory = document.getElementById("chatHistory");
    const userMessage = document.getElementById("userMessage");
    const sendBtn = document.getElementById("sendBtn");
    
    // Initialize chat ID
    chatId = Date.now().toString();
    console.log('🆔 Chat ID initialized:', chatId);
    
    // Set up event listeners
    if (recordBtn) {
        recordBtn.addEventListener("click", startRecording);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener("click", stopRecording);
    }
    
    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }
    
    if (userMessage) {
        userMessage.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Speech recognition setup
    let recognition = null;
    let isRecording = false;
    
    function startRecording() {
        if (isRecording) return;
        
        if (!window.webkitSpeechRecognition && !window.SpeechRecognition) {
            statusText.textContent = "Speech recognition not supported in this browser.";
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        
        recognition.onstart = () => {
            isRecording = true;
            statusText.textContent = "Listening...";
            recordBtn.style.display = "none";
            stopBtn.style.display = "inline-block";
            stopBtn.disabled = false;
            console.log('🎤 Recording started');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            
            console.log('🗣️ Speech recognized:', transcript, 'Confidence:', confidence);
            
            // Process the speech
            processEmotion(transcript, confidence);
        };
        
        recognition.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            statusText.textContent = `Error: ${event.error}`;
            resetRecording();
        };
        
        recognition.onend = () => {
            if (isRecording) {
                statusText.textContent = "Processing...";
                resetRecording();
            }
        };
        
        try {
            recognition.start();
        } catch (error) {
            console.error("Failed to start recognition:", error);
            statusText.textContent = "Failed to start recording";
            resetRecording();
        }
    }
    
    function stopRecording() {
        if (!isRecording) return;
        
        if (recognition) {
            recognition.stop();
        }
        
        resetRecording();
    }
    
    function resetRecording() {
        isRecording = false;
        recordBtn.style.display = "inline-block";
        stopBtn.style.display = "none";
        stopBtn.disabled = true;
    }
    
    // Process emotion from speech
    async function processEmotion(text, confidence) {
        // Enhanced emotion detection
        const emotions = {
            happy: ["happy", "joy", "excited", "great", "wonderful", "fantastic", "amazing", "awesome", "love", "pleased", "good", "excellent", "delighted"],
            sad: ["sad", "unhappy", "depressed", "down", "blue", "upset", "disappointed", "miserable", "heartbroken", "sorry", "grief", "melancholy"],
            angry: ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "pissed", "outraged", "livid"],
            fear: ["afraid", "scared", "frightened", "terrified", "anxious", "nervous", "worried", "panic", "fearful", "dread"],
            surprise: ["surprised", "shocked", "amazed", "astonished", "wow", "unbelievable", "incredible", "unexpected", "stunning"],
            disgust: ["disgusted", "gross", "yuck", "ew", "nasty", "revolting", "sick", "repulsed", "awful"],
            neutral: []
        };
        
        let detectedEmotion = "neutral";
        let maxScore = 0;
        
        // Score each emotion based on keyword presence and position
        const lowerText = text.toLowerCase();
        
        for (const [emotion, keywords] of Object.entries(emotions)) {
            let score = 0;
            
            for (const keyword of keywords) {
                if (lowerText.includes(keyword)) {
                    // Give higher score if keyword appears early in the text
                    const position = lowerText.indexOf(keyword);
                    score += 1 + (1 - position / lowerText.length) * 0.5;
                }
            }
            
            if (score > maxScore) {
                maxScore = score;
                detectedEmotion = emotion;
            }
        }
        
        // Update global variables for visualization
        window.currentEmotion = detectedEmotion;
        window.emotionIntensity = confidence;
        
        // Update UI immediately
        updateEmotionPanel(detectedEmotion, confidence);
        statusText.textContent = `Detected: ${detectedEmotion} (${Math.round(confidence * 100)}%)`;
        
        console.log('😊 Emotion detected:', detectedEmotion, 'Intensity:', confidence);
        
        // Show chat section after first analysis
        const chatSection = document.getElementById("chat");
        if (chatSection) {
            chatSection.style.display = "block";
        }
        
        // Send to n8n webhook
        const emotionData = {
            emotion: detectedEmotion,
            confidence: confidence,
            text: text,
            sessionId: chatId
        };
        
        // Send to n8n webhook (don't await to avoid blocking UI)
        sendEmotionToN8N(emotionData).then(success => {
            if (success) {
                console.log('✅ Emotion data sent successfully');
            } else {
                console.log('⚠️ Failed to send emotion data, but continuing');
            }
        });
    }
    
    // Function to send chat messages
    async function sendMessage() {
        if (!chatHistory) return;
        
        const text = userMessage.value.trim();
        if (!text) return;
        
        // Clear input immediately
        userMessage.value = "";
        
        // Add user message to chat
        const userDiv = document.createElement('div');
        userDiv.className = 'user';
        userDiv.textContent = `🧑 ${text}`;
        chatHistory.appendChild(userDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        // Process emotion from chat message
        processEmotion(text, 0.8); // Use fixed confidence for typed messages
        
        // Add a placeholder for AI response
        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'assistant';
        assistantDiv.textContent = '🤖 Analyzing emotion...';
        chatHistory.appendChild(assistantDiv);
        
        // Note: The actual response will come from n8n webhook
    }
});
