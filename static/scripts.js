// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;
let lastDetectedEmotion = '';

// Add beautiful CSS styling inspired by the holographic design
const style = document.createElement('style');
style.textContent = `
  /* Holographic ORA Theme */
  body {
    background: #000000;
    color: #ffffff;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    background-image: 
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
  }

  .container {
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    box-shadow: 
      0 8px 32px rgba(0, 0, 0, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    max-width: 800px;
    margin: 20px auto;
    padding: 30px;
  }

  h1, h2 {
    background: linear-gradient(135deg, #ff6b9d, #c471ed, #12c2e9, #c471ed, #ff6b9d);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: holographicShift 3s ease-in-out infinite;
    text-align: center;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  @keyframes holographicShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }

  /* Record Button Styling */
  button {
    background: linear-gradient(135deg, #ff6b9d, #c471ed, #12c2e9);
    background-size: 300% 300%;
    border: none;
    border-radius: 50px;
    color: white;
    font-weight: 600;
    padding: 15px 30px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.4);
    animation: holographicShift 3s ease-in-out infinite;
    font-size: 16px;
    letter-spacing: 0.5px;
  }

  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(255, 107, 157, 0.6);
  }

  button:active {
    transform: translateY(0);
  }

  /* Chat Interface */
  #chat {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 20px;
    margin-top: 20px;
    backdrop-filter: blur(10px);
  }

  #chatHistory {
    max-height: 400px;
    overflow-y: auto;
    padding: 15px;
    border-radius: 15px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 15px;
  }

  /* Custom Scrollbar */
  #chatHistory::-webkit-scrollbar {
    width: 6px;
  }

  #chatHistory::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }

  #chatHistory::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ff6b9d, #c471ed);
    border-radius: 3px;
  }

  /* Chat Messages */
  .user {
    background: linear-gradient(135deg, rgba(255, 107, 157, 0.2), rgba(196, 113, 237, 0.2));
    border: 1px solid rgba(255, 107, 157, 0.3);
    border-radius: 18px 18px 5px 18px;
    padding: 12px 16px;
    margin: 10px 0;
    margin-left: 20%;
    color: #ffffff;
    box-shadow: 0 4px 15px rgba(255, 107, 157, 0.2);
    backdrop-filter: blur(10px);
  }

  .assistant {
    background: linear-gradient(135deg, rgba(18, 194, 233, 0.2), rgba(196, 113, 237, 0.2));
    border: 1px solid rgba(18, 194, 233, 0.3);
    border-radius: 18px 18px 18px 5px;
    padding: 12px 16px;
    margin: 10px 0;
    margin-right: 20%;
    color: #ffffff;
    box-shadow: 0 4px 15px rgba(18, 194, 233, 0.2);
    backdrop-filter: blur(10px);
  }

  /* Chat Input */
  .chat-input {
    display: flex;
    gap: 10px;
    align-items: center;
  }

  #userMessage {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 25px;
    padding: 12px 20px;
    color: #ffffff;
    font-size: 16px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
  }

  #userMessage:focus {
    outline: none;
    border-color: rgba(255, 107, 157, 0.5);
    box-shadow: 0 0 20px rgba(255, 107, 157, 0.3);
  }

  #userMessage::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }

  #sendBtn {
    padding: 12px 20px;
    border-radius: 25px;
    font-size: 14px;
  }

  /* Status Text */
  #status {
    text-align: center;
    margin: 20px 0;
    padding: 10px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.8);
  }

  /* Emotion Visualization */
  .emotion-display {
    text-align: center;
    margin: 20px 0;
    padding: 20px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  #emotion-label {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #ff6b9d, #c471ed, #12c2e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    text-transform: capitalize;
  }

  .intensity-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 10px;
  }

  #intensity-fill {
    height: 100%;
    background: linear-gradient(90deg, #ff6b9d, #c471ed, #12c2e9);
    border-radius: 4px;
    transition: width 0.5s ease;
    box-shadow: 0 0 10px rgba(255, 107, 157, 0.5);
  }

  /* Floating Animation */
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  .floating {
    animation: float 3s ease-in-out infinite;
  }

  /* Glow Effects */
  .glow {
    box-shadow: 
      0 0 20px rgba(255, 107, 157, 0.3),
      0 0 40px rgba(196, 113, 237, 0.2),
      0 0 60px rgba(18, 194, 233, 0.1);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .container {
      margin: 10px;
      padding: 20px;
    }
    
    .user, .assistant {
      margin-left: 10%;
      margin-right: 10%;
    }
    
    button {
      padding: 12px 24px;
      font-size: 14px;
    }
  }

  /* Hide default elements that might conflict */
  .btn {
    display: none;
  }
`;

document.head.appendChild(style);

// Function to send emotion data to Make.com webhook (EMOTION ASSESSMENT)
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/1748846057780";
    
    console.log('🎯 Sending EMOTION ASSESSMENT to Make.com:', emotionData);
    
    // Create payload for EMOTION ASSESSMENT
    const emotionPayload = {
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        message_type: "emotion_assessment",           // KEY: This tells Make.com it's emotion assessment
        emotion: emotionData.emotion,
        intensity: emotionData.intensity,
        text: emotionData.text,                       // FIXED: This will be the speech text
        time_of_day: getTimeOfDay(),
        request_id: Math.random().toString(36)        // Unique ID to prevent caching
    };
    
    // Store the detected emotion for context
    lastDetectedEmotion = emotionData.emotion;
    
    console.log('📦 Emotion Assessment payload:', emotionPayload);
    
    try {
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emotionPayload)
        });
        
        if (directResponse.ok) {
            const responseText = await directResponse.text();
            console.log('✅ Emotion Assessment success (raw):', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('✅ Parsed JSON response:', responseData);
            } catch (parseError) {
                console.log('ℹ️ Response is not JSON, using as text:', responseText);
                responseData = { 
                    status: 'success', 
                    message: responseText || 'Emotion assessment completed' 
                };
            }
            
            displayOraResponse(responseData);
            return true;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed:', directError.message);
        return false;
    }
}

// Function to send chat messages (WELLNESS COACHING)
async function sendChatMessage(messageText) {
    const makeWebhookUrl = "https://hook.eu2.make.com/1748846057780";
    
    console.log('💬 Sending WELLNESS COACHING message:', messageText);
    
    // Create payload for WELLNESS COACHING
    const chatPayload = {
        user_id: chatId,
        session_id: chatId,
        timestamp: new Date().toISOString(),
        message_type: "wellness_coaching",            // KEY: This tells Make.com it's ongoing coaching
        emotion: lastDetectedEmotion || 'neutral',    // Keep context of detected emotion
        intensity: window.emotionIntensity || 0.7,
        text: messageText,                            // FIXED: This will be the chat message text
        time_of_day: getTimeOfDay(),
        request_id: Math.random().toString(36)        // Unique ID to prevent caching
    };
    
    console.log('📦 Wellness Coaching payload:', chatPayload);
    
    try {
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(chatPayload)
        });
        
        if (directResponse.ok) {
            const responseText = await directResponse.text();
            console.log('✅ Wellness Coaching success (raw):', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('✅ Parsed JSON response:', responseData);
            } catch (parseError) {
                console.log('ℹ️ Response is not JSON, using as text:', responseText);
                responseData = { 
                    status: 'success', 
                    message: responseText || 'Wellness coaching response received' 
                };
            }
            
            displayOraResponse(responseData);
            return true;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed:', directError.message);
        return false;
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

// Enhanced function to display ORA's response in the chat
function displayOraResponse(responseData) {
    console.log("Raw response received:", responseData);
    
    // Show the chat section with animation
    const chatDiv = document.getElementById("chat");
    if (chatDiv) {
        chatDiv.style.display = "block";
        chatDiv.classList.add("glow");
        setTimeout(() => chatDiv.classList.remove("glow"), 2000);
    }
    
    // Get the chat history element
    const chatHistory = document.getElementById("chatHistory");
    if (!chatHistory) {
        console.error("Chat history element not found!");
        return;
    }
    
    // Extract the message from the response
    let message = "";
    
    if (responseData && responseData.message) {
        message = responseData.message;
    } else if (responseData && responseData.response) {
        message = responseData.response;
    } else if (responseData && responseData.status === "success") {
        message = "I hear you. How can I support your wellness journey today?";
    } else {
        message = "I'm here to support you. Please share more about how you're feeling.";
        console.log("Unexpected response format:", responseData);
    }
    
    // Add the message to chat history with typing animation
    if (message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'assistant';
        messageDiv.innerHTML = `🧘 <strong>ORA:</strong> <span class="typing-text"></span>`;
        chatHistory.appendChild(messageDiv);
        
        // Typing animation
        const typingElement = messageDiv.querySelector('.typing-text');
        let i = 0;
        const typeWriter = () => {
            if (i < message.length) {
                typingElement.textContent += message.charAt(i);
                i++;
                setTimeout(typeWriter, 30);
            }
        };
        typeWriter();
        
        chatHistory.scrollTop = chatHistory.scrollHeight;
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
  
  // Add floating animation to main elements
  if (recordBtn) recordBtn.classList.add("floating");
  
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
      statusText.textContent = "✨ Listening to your emotions...";
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
        statusText.textContent = "✨ Ready to listen again";
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
    // Enhanced emotion detection
    const emotions = {
      happy: ["happy", "joy", "excited", "great", "wonderful", "fantastic", "amazing", "awesome", "love", "pleased", "cheerful", "delighted", "thrilled", "elated"],
      sad: ["sad", "unhappy", "depressed", "down", "blue", "upset", "disappointed", "miserable", "heartbroken", "dejected", "melancholy", "grief"],
      angry: ["angry", "mad", "furious", "annoyed", "irritated", "frustrated", "rage", "hate", "pissed", "livid", "outraged", "enraged"],
      fear: ["afraid", "scared", "frightened", "terrified", "anxious", "nervous", "worried", "panic", "fearful", "alarmed", "stressed"],
      surprise: ["surprised", "shocked", "amazed", "astonished", "wow", "unbelievable", "incredible", "stunned", "astounded", "bewildered"],
      disgust: ["disgusted", "gross", "yuck", "ew", "nasty", "revolting", "sick", "repulsed", "appalled", "revolted"],
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
    
    // Calculate intensity
    let intensity = 0.7;
    if (maxCount > 0) {
      intensity = Math.min(0.6 + (maxCount * 0.2), 1.0);
    }
    
    // Update global variables
    window.currentEmotion = detectedEmotion;
    window.emotionIntensity = intensity;
    
    // Update the emotion display with enhanced styling
    const emotionLabel = document.getElementById("emotion-label");
    const intensityFill = document.getElementById("intensity-fill");
    
    if (emotionLabel) {
      emotionLabel.textContent = detectedEmotion;
      emotionLabel.classList.add("floating");
    }
    
    if (intensityFill) {
      intensityFill.style.width = `${Math.round(intensity * 100)}%`;
      
      // Enhanced emotion colors
      const emotionColors = {
        happy: "linear-gradient(90deg, #ff6b9d, #ffd93d)",
        sad: "linear-gradient(90deg, #4facfe, #00f2fe)", 
        angry: "linear-gradient(90deg, #ff416c, #ff4b2b)",
        fear: "linear-gradient(90deg, #a8edea, #fed6e3)",
        surprise: "linear-gradient(90deg, #ffecd2, #fcb69f)",
        disgust: "linear-gradient(90deg, #667eea, #764ba2)",
        neutral: "linear-gradient(90deg, #bdc3c7, #2c3e50)"
      };
      
      intensityFill.style.background = emotionColors[detectedEmotion] || emotionColors.neutral;
    }
    
    // Display status with emoji
    const emotionEmojis = {
      happy: "😊",
      sad: "😢", 
      angry: "😠",
      fear: "😰",
      surprise: "😲",
      disgust: "🤢",
      neutral: "😐"
    };
    
    statusText.textContent = `${emotionEmojis[detectedEmotion]} ${detectedEmotion} (${Math.round(intensity * 100)}%)`;
    
    console.log('😊 Emotion detected:', detectedEmotion, 'Intensity:', intensity);
    
    // Add user's speech to chat history
    if (chatHistory) {
      const userDiv = document.createElement('div');
      userDiv.className = 'user';
      userDiv.innerHTML = `🧑 "${text}"`;
      chatHistory.appendChild(userDiv);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    // Send to Make.com webhook - FIXED: Use speech text for emotion assessment
    const emotionData = {
      emotion: detectedEmotion,
      intensity: intensity,
      text: text,                    // This is the speech text for emotion assessment
      sessionId: chatId
    };
    
    const success = await sendEmotionToMake(emotionData);
    
    if (success) {
      console.log('✅ Emotion data sent successfully to Make.com');
    } else {
      console.error('❌ Failed to send emotion data to Make.com');
      statusText.textContent = "Error sending data to Make.com";
    }
  }
  
  // Send chat message function - FIXED: Use chat message text for wellness coaching
  function sendMessage() {
    const messageText = userMessage.value.trim();
    if (!messageText) return;
    
    // Add user message to chat with animation
    const userDiv = document.createElement('div');
    userDiv.className = 'user';
    userDiv.innerHTML = `🧑 ${messageText}`;
    chatHistory.appendChild(userDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Clear input
    userMessage.value = "";
    
    // Send to Make.com - FIXED: Use chat message text for wellness coaching
    sendChatMessage(messageText);
  }
});

