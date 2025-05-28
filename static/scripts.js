// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to n8n webhook with improved error handling
async function sendEmotionToN8N(emotionData) {
    const n8nWebhookUrl = "https://mehax.app.n8n.cloud/webhook/receive-emotion-data";
    
    console.log('🚀 Attempting to send to webhook:', emotionData);
    
    const payload = {
        emotion: emotionData.emotion,
        confidence: emotionData.confidence,
        timestamp: new Date().toISOString(),
        text: emotionData.text,
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
        
        if (response.ok) {
            const responseData = await response.json();
            console.log('✅ Direct webhook success:', responseData);
            return true;
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed, trying CORS proxy:', directError.message);
        
        try {
            const corsProxyUrl = "https://api.allorigins.win/raw?url=";
            const proxyResponse = await fetch(corsProxyUrl + encodeURIComponent(n8nWebhookUrl), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            const responseText = await proxyResponse.text();
            console.log('✅ Proxy response:', responseText);
            
            try {
                const responseData = JSON.parse(responseText);
                console.log('✅ Parsed proxy response data:', responseData);
            } catch (parseError) {
                console.log('⚠️ Could not parse proxy response as JSON:', responseText);
            }
            
            return true;
        } catch (proxyError) {
            console.error('❌ Both direct and proxy failed:', proxyError);
            
            try {
                const altProxyUrl = "https://cors-anywhere.herokuapp.com/";
                const altResponse = await fetch(altProxyUrl + n8nWebhookUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (altResponse.ok) {
                    const altResponseData = await altResponse.json();
                    console.log('✅ Alternative proxy success:', altResponseData);
                    return true;
                }
            } catch (altError) {
                console.error('❌ All connection methods failed:', altError);
            }
            
            return false;
        }
    }
}

// Initialize when DOM is fully loaded
window.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const statusText = document.getElementById("status");
  const chatHistory = document.getElementById("chat-history");
  const userMessage = document.getElementById("user-message");
  const sendBtn = document.getElementById("send-btn");
  
  // Initialize chat ID
  chatId = Date.now().toString();
  console.log('🆔 Chat ID initialized:', chatId);
  
  // ✅ Test webhook POST on load
  fetch("https://mehax.app.n8n.cloud/webhook/receive-emotion-data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      emotion: "startup_test",
      confidence: 1,
      message: "Testing POST from DOMContentLoaded",
      sessionId: chatId
    })
  })
  .then(res => res.text())
  .then(data => console.log("🚀 Webhook test POST response:", data))
  .catch(err => console.error("⚠️ Webhook test failed:", err));

  // Set up event listeners
  if (recordBtn) recordBtn.addEventListener("click", startRecording);
  if (stopBtn) stopBtn.addEventListener("click", stopRecording);
  if (sendBtn) sendBtn.addEventListener("click", sendMessage);
  if (userMessage) {
    userMessage.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
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
      console.log('🎤 Recording started');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      console.log('🗣️ Speech recognized:', transcript, 'Confidence:', confidence);
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
    if (recognition) recognition.stop();
    resetRecording();
  }

  function resetRecording() {
    isRecording = false;
    recordBtn.style.display = "inline-block";
    stopBtn.style.display = "none";
  }

  async function processEmotion(text, confidence) {
    const emotions = {
      happy: ["happy", "joy", "excited", "great", "wonderful", "fantastic", "amazing", "awesome", "love", "pleased"],
      sad: ["sad", "unhappy", "depressed", "down", "blue", "upset", "disappointed", "miserable", "heartbroken"],
      angry: ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "pissed"],
      fear: ["afraid", "scared", "frightened", "terrified", "anxious", "nervous", "worried", "panic"],
      surprise: ["surprised", "shocked", "amazed", "astonished", "wow", "unbelievable", "incredible"],
      disgust: ["disgusted", "gross", "yuck", "ew", "nasty", "revolting", "sick"],
      neutral: []
    };

    let detectedEmotion = "neutral";
    let maxCount = 0;

    for (const [emotion, keywords] of Object.entries(emotions)) {
      const count = keywords.filter(keyword => text.toLowerCase().includes(keyword)).length;
      if (count > maxCount) {
        maxCount = count;
        detectedEmotion = emotion;
      }
    }

    if (maxCount === 0) detectedEmotion = "neutral";

    window.currentEmotion = detectedEmotion;
    window.emotionIntensity = confidence;

    statusText.textContent = `${detectedEmotion} (${Math.round(confidence * 100)}%)`;

    console.log('😊 Emotion detected:', detectedEmotion, 'Intensity:', confidence);

    const emotionData = {
      emotion: detectedEmotion,
      confidence: confidence,
      text: text,
      sessionId: chatId
    };

    const success = await sendEmotionToN8N(emotionData);
    if (success) {
      console.log('✅ Emotion data sent successfully');
    } else {
      console.error('❌ Failed to send emotion data');
    }
  }

  async function sendMessage() {
    if (!chatHistory) return;

    const text = userMessage.value.trim();
    if (!text || !chatId) return;

    chatHistory.innerHTML += `<div class="user">🧑 ${text}</div>`;
    userMessage.value = "";

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, message: text })
      });

      const { reply } = await res.json();
      chatHistory.innerHTML += `<div class="assistant">🤖 ${reply}</div>`;
      chatHistory.scrollTop = chatHistory.scrollHeight;
    } catch (err) {
      console.error('Chat error:', err);
      chatHistory.innerHTML += `<div class="assistant error">⚠️ Chat failed.</div>`;
    }
  }
});

