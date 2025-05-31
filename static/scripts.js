// Main variables
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;
let isFirstResponse = true;

// Function to send data to Make.com webhook (handles both emotion and chat)
async function sendToMakeWebhook(data) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('🚀 Attempting to send to Make.com webhook:', data);
    
    // Create payload for Make.com
    const payload = {
        user_id: chatId,
        session_id: chatId,
        timestamp: new Date().toISOString(),
        message_type: data.type || 'emotion', // 'emotion' or 'chat'
        primary_emotion: data.emotion || 'neutral',
        intensity_level: data.intensity || 0.7,
        raw_text: data.text || '',
        user_message: data.message || '',
        time_of_day: getTimeOfDay()
    };
    
    console.log('📦 Payload:', payload);
    
    try {
        // Try direct connection first
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (directResponse.ok) {
            const responseData = await directResponse.json();
            console.log('✅ Direct Make.com webhook success:', responseData);
            return responseData;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed, trying CORS proxy:', directError.message);
    }
    
    // Fallback to CORS proxy
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const response = await fetch(corsProxyUrl + encodeURIComponent(makeWebhookUrl), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const responseText = await response.text();
        console.log('✅ Proxy response:', responseText);
        
        try {
            const responseData = JSON.parse(responseText);
            console.log('Raw response received:', responseData);
            return responseData;
        } catch (parseError) {
            console.log('⚠️ Could not parse response as JSON:', responseText);
            return {response: responseText};
        }
    } catch (error) {
        console.error('❌ Failed to send to proxy:', error);
        return null;
    }
}

// Helper function to get time of day
function getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour < 6) return "night";
    if (hour < 12) return "morning";
    if (hour < 17) return "afternoon";
    if (hour < 22) return "evening";
    return "night";
}

// Function to display ORA's response in the chat
function displayOraResponse(responseData) {
    const chatHistory = document.getElementById("chatHistory");
    if (!chatHistory) return;
    
    console.log("Raw response received:", responseData);
    
    if (responseData && responseData.message) {
        // Clean response from Make.com
        let message = responseData.message;
        
        // Remove any JSON wrapper if present
        if (typeof message === 'string' && message.includes('"')) {
            try {
                const parsed = JSON.parse(message);
                if (parsed.response) {
                    message = parsed.response;
                }
            } catch (e) {
                // Keep original message if parsing fails
            }
        }
        
        // Display the message
        chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> ${message}</div>`;
    } else if (responseData && responseData.response) {
        // Handle response field
        chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> ${responseData.response}</div>`;
    } else {
        // Fallback message
        chatHistory.innerHTML += `<div class="assistant">🧘 <strong>ORA:</strong> I hear you. Let me provide some guidance based on what you've shared.</div>`;
    }
    
    // Scroll to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Show chat interface after first response
    if (isFirstResponse) {
        document.getElementById("chat").style.display = "block";
        isFirstResponse = false;
    }
}

// Initialize when DOM is loaded
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
        sendBtn.addEventListener("click", sendChatMessage);
    }
    
    if (userMessage) {
        userMessage.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendChatMessage();
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
            recordBtn.disabled = true;
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
                statusText.textContent = "Ready to record again";
                resetRecording();
            }
        };
        
        recognition.start();
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
        recordBtn.disabled = false;
        stopBtn.disabled = true;
    }
    
    // Process emotion from speech
    async function processEmotion(text, confidence) {
        // Simple emotion detection based on keywords
        const emotions = {
            happy: ["happy", "joy", "excited", "great", "wonderful", "fantastic", "amazing", "awesome", "love", "pleased", "cheerful", "delighted"],
            sad: ["sad", "unhappy", "depressed", "down", "blue", "upset", "disappointed", "miserable", "heartbroken", "dejected", "melancholy"],
            angry: ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "pissed", "livid", "outraged"],
            fear: ["afraid", "scared", "frightened", "terrified", "anxious", "nervous", "worried", "panic", "fearful", "alarmed"],
            surprise: ["surprised", "shocked", "amazed", "astonished", "wow", "unbelievable", "incredible", "stunned", "astounded"],
            disgust: ["disgusted", "gross", "yuck", "ew", "nasty", "revolting", "sick", "repulsed", "appalled"],
            neutral: []
        };
        
        let detectedEmotion = "neutral";
        let maxCount = 0;
        
        // Count emotion keywords
        for (const [emotion, keywords] of Object.entries(emotions)) {
            const count = keywords.filter(keyword => 
                text.toLowerCase().includes(keyword)
            ).length;
            
            if (count > maxCount) {
                maxCount = count;
                detectedEmotion = emotion;
            }
        }
        
        // Calculate intensity based on emotion detection
        let intensity = 0.7; // Default intensity
        if (maxCount > 0) {
            intensity = Math.min(0.6 + (maxCount * 0.2), 1.0);
        }
        
        // Update global variables for visualization
        window.currentEmotion = detectedEmotion;
        window.emotionIntensity = intensity;
        
        // Update the emotion panel
        const emotionLabel = document.getElementById("emotion-label");
        const intensityFill = document.getElementById("intensity-fill");
        
        if (emotionLabel) {
            emotionLabel.textContent = detectedEmotion;
        }
        
        if (intensityFill) {
            intensityFill.style.width = `${Math.round(intensity * 100)}%`;
            
            // Color based on emotion
            const emotionColors = {
                happy: "#4CAF50",
                sad: "#2196F3", 
                angry: "#F44336",
                fear: "#9C27B0",
                surprise: "#FF9800",
                disgust: "#795548",
                neutral: "#9E9E9E"
            };
            
            intensityFill.style.background = emotionColors[detectedEmotion] || "#9E9E9E";
        }
        
        // Display the detected emotion in status
        statusText.textContent = `${detectedEmotion} (${Math.round(intensity * 100)}%)`;
        
        console.log('😊 Emotion detected:', detectedEmotion, 'Intensity:', intensity);
        
        // Add user's speech to chat history
        if (chatHistory) {
            chatHistory.innerHTML += `<div class="user">🧑 "${text}"</div>`;
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        
        // Send emotion data to Make.com
        const emotionData = {
            type: 'emotion',
            emotion: detectedEmotion,
            intensity: intensity,
            text: text
        };
        
        const response = await sendToMakeWebhook(emotionData);
        
        if (response) {
            console.log('✅ Emotion data sent successfully to Make.com');
            displayOraResponse(response);
        } else {
            console.error('❌ Failed to send emotion data to Make.com');
            if (chatHistory) {
                chatHistory.innerHTML += `<div class="error">⚠️ Unable to connect to ORA wellness agent.</div>`;
            }
        }
    }

    // Function to send chat messages
    async function sendChatMessage() {
        if (!chatHistory || !userMessage) return;
        
        const text = userMessage.value.trim();
        if (!text) return;

        // Add user message to chat
        chatHistory.innerHTML += `<div class="user">🧑 ${text}</div>`;
        userMessage.value = "";
        chatHistory.scrollTop = chatHistory.scrollHeight;
        
        // Send chat message to Make.com
        const chatData = {
            type: 'chat',
            message: text,
            emotion: window.currentEmotion,
            intensity: window.emotionIntensity
        };
        
        const response = await sendToMakeWebhook(chatData);
        
        if (response) {
            console.log('✅ Chat message sent successfully to Make.com');
            displayOraResponse(response);
        } else {
            console.error('❌ Failed to send chat message to Make.com');
            chatHistory.innerHTML += `<div class="error">⚠️ Unable to send message to ORA.</div>`;
        }
    }
});
