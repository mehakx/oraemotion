// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to Make.com webhook
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/mg0z2u8k9gv069uo14pj1exbil0a6q17";
    
    console.log('🚀 Attempting to send to Make.com webhook via CORS proxy:', emotionData);
    
    // Create a simpler payload first
    const simplePayload = {
        emotion: emotionData.emotion,
        confidence: emotionData.confidence,
        text: emotionData.text,
        timestamp: new Date().toISOString(),
        sessionId: emotionData.sessionId || 'default'
    };
    
    console.log('📦 Simple payload:', simplePayload);
    
    try {
        // Try direct connection first (without CORS proxy)
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(simplePayload)
        });
        
        if (directResponse.ok) {
            const responseText = await directResponse.text();
            console.log('✅ Direct Make.com webhook success:', responseText);
            return true;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed, trying CORS proxy:', directError.message);
    }
    
    // Fallback to CORS proxy with simple payload
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const response = await fetch(corsProxyUrl + encodeURIComponent(makeWebhookUrl), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(simplePayload)
        });
        
        const responseText = await response.text();
        console.log('✅ Proxy response:', responseText);
        
        // Check if the response indicates success
        if (responseText && !responseText.includes('error')) {
            console.log('✅ Make.com webhook likely received data');
            return true;
        }
        
        return true;
    } catch (error) {
        console.error('❌ Failed to send to proxy:', error);
        return false;
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
      if (e.key === "Enter") {
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
    recordBtn.style.display = "inline-block";
    stopBtn.style.display = "none";
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
    
    // If no emotion words found, use neutral
    if (maxCount === 0) {
      detectedEmotion = "neutral";
    }
    
    // Update global variables for visualization
    window.currentEmotion = detectedEmotion;
    window.emotionIntensity = confidence;
    
    // Update the emotion panel
    const emotionLabel = document.getElementById("emotion-label");
    const intensityFill = document.getElementById("intensity-fill");
    
    if (emotionLabel) {
      emotionLabel.textContent = detectedEmotion;
    }
    
    if (intensityFill) {
      intensityFill.style.width = `${Math.round(confidence * 100)}%`;
      
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
    statusText.textContent = `${detectedEmotion} (${Math.round(confidence * 100)}%)`;
    
    console.log('😊 Emotion detected:', detectedEmotion, 'Intensity:', confidence);
    
    // Send to Make.com webhook
    const emotionData = {
      emotion: detectedEmotion,
      confidence: confidence,
      text: text,
      sessionId: chatId
    };
    
    // Send to Make.com webhook
    const success = await sendEmotionToMake(emotionData);
    
    if (success) {
      console.log('✅ Emotion data sent successfully to Make.com');
    } else {
      console.error('❌ Failed to send emotion data to Make.com');
      // statusText.textContent += ' (⚠️ Upload failed)';
    }
  }

  // Function to send chat messages
  async function sendMessage() {
    if (!chatHistory) return;
    
    const text = userMessage.value.trim();
    if (!text || !chatId) return;

    // Add user message to chat
    chatHistory.innerHTML += `<div class="user">🧑 ${text}</div>`;
    userMessage.value = "";

    try {
      // Send message to server
      const res = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ chat_id: chatId, message: text })
      });
      
      const { reply } = await res.json();
      
      // Add assistant reply to chat
      chatHistory.innerHTML += `<div class="assistant">🤖 ${reply}</div>`;
      
      // Scroll chat to bottom
      chatHistory.scrollTop = chatHistory.scrollHeight;
    } catch (err) {
      console.error('Chat error:', err);
      chatHistory.innerHTML += `<div class="assistant error">⚠️ Chat failed.</div>`;
    }
  }
});
