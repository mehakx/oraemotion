// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data directly to n8n webhook (with CORS headers now configured)
async function sendEmotionToN8N(emotionData) {
    // Direct n8n webhook URL (now with proper CORS headers)
    const webhookUrl = "https://mehax.app.n8n.cloud/webhook-test/https://ora-owjy.onrender.com/";
    
    console.log('🚀 Attempting to send to n8n webhook:', emotionData );
    
    try {
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                emotion: emotionData.emotion,
                confidence: emotionData.confidence,
                timestamp: new Date().toISOString(),
                text: emotionData.text,
                sessionId: emotionData.sessionId || 'default'
            })
        });
        
        const responseText = await response.text();
        console.log('✅ Webhook response:', responseText);
        return true;
    } catch (error) {
        console.error('❌ Failed to send to webhook:', error);
        return false;
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
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      
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
  }
  
  // Process emotion from speech
  async function processEmotion(text, confidence) {
    // Simple emotion detection based on keywords
    // In a real app, you'd use a more sophisticated model
    const emotions = {
      happy: ["happy", "joy", "excited", "great", "wonderful", "fantastic"],
      sad: ["sad", "unhappy", "depressed", "down", "blue", "upset"],
      angry: ["angry", "mad", "furious", "annoyed", "irritated", "frustrated"],
      fear: ["afraid", "scared", "frightened", "terrified", "anxious", "nervous"],
      surprise: ["surprised", "shocked", "amazed", "astonished", "wow"],
      disgust: ["disgusted", "gross", "yuck", "ew", "nasty"],
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
    
    // Display the detected emotion
    statusText.textContent = detectedEmotion;
    
    // Send to n8n webhook
    const emotionData = {
      emotion: detectedEmotion,
      confidence: confidence,
      text: text,
      sessionId: chatId
    };
    
    // Send to n8n webhook
    await sendEmotionToN8N(emotionData);
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
      console.error(err);
      chatHistory.innerHTML += `<div class="assistant error">⚠️ Chat failed.</div>`;
    }
  }
});
