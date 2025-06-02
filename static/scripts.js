// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to Make.com webhook (EMOTION ASSESSMENT)
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('🎯 Sending EMOTION ASSESSMENT to Make.com:', emotionData);
    
    // Create payload for EMOTION ASSESSMENT
    const emotionPayload = {
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        message_type: "emotion_assessment",           // KEY: This tells Make.com it's emotion assessment
        emotion: emotionData.emotion,
        intensity: emotionData.intensity,
        text: emotionData.text,
        time_of_day: getTimeOfDay(),
        request_id: Math.random().toString(36)        // Unique ID to prevent caching
    };
    
    console.log('📦 Emotion Assessment payload:', emotionPayload);
    console.log('Mits',JSON.stringify(emotionPayload));
    
    try {
        // Try direct connection first (without CORS proxy)
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emotionPayload)
        });
        
        if (directResponse.ok) {
            // FIXED: Get response as text first, then try to parse as JSON
            const responseText = await directResponse.text();
            console.log('✅ Emotion Assessment success (raw):', responseText);
            
            let responseData;
            try {
                // Try to parse as JSON
                responseData = JSON.parse(responseText);
                console.log('✅ Parsed JSON response:', responseData);
            } catch (parseError) {
                console.log('ℹ️ Response is not JSON, using as text:', responseText);
                // If not JSON, create a simple object with the text
                responseData = { 
                    status: 'success', 
                    message: responseText || 'Emotion assessment completed' 
                };
            }
            
            // Display the ORA response in the chat
            displayOraResponse(responseData);
            
            return true;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed, trying CORS proxy:', directError.message);
    }
    
    // Fallback to CORS proxy with flattened payload
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const response = await fetch(corsProxyUrl + encodeURIComponent(makeWebhookUrl), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emotionPayload)
        });
        
        const responseText = await response.text();
        console.log('✅ Proxy response:', responseText);
        
        try {
            // Try to parse the response as JSON
            const responseData = JSON.parse(responseText);
            console.log('✅ Parsed response data:', responseData);
            
            // Display the ORA response in the chat
            displayOraResponse(responseData);
            
            return true;
        } catch (parseError) {
            console.log('⚠️ Could not parse response as JSON:', responseText);
            // Even if parsing fails, try to display something
            displayOraResponse({response: responseText});
            return true;
        }
    } catch (error) {
        console.error('❌ Failed to send to proxy:', error);
        return false;
    }
}

// Function to send chat messages (WELLNESS COACHING)
async function sendChatMessage(messageText) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('💬 Sending WELLNESS COACHING message:', messageText);
    
    // Create payload for WELLNESS COACHING
    const chatPayload = {
        user_id: chatId,
        session_id: chatId,
        timestamp: new Date().toISOString(),
        message_type: "wellness_coaching",            // KEY: This tells Make.com it's ongoing coaching
        emotion: window.currentEmotion || 'neutral',  // Keep context of detected emotion
        intensity: window.emotionIntensity || 0.7,
        text: messageText,
        time_of_day: getTimeOfDay(),
        request_id: Math.random().toString(36)        // Unique ID to prevent caching
    };
    
    console.log('📦 Wellness Coaching payload:', chatPayload);
    
    try {
        // Try direct connection first
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(chatPayload)
        });
        
        if (directResponse.ok) {
            // FIXED: Get response as text first, then try to parse as JSON
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
            body: JSON.stringify(chatPayload)
        });
        
        const responseText = await response.text();
        console.log('✅ Chat proxy response:', responseText);
        
        try {
            const responseData = JSON.parse(responseText);
            displayOraResponse(responseData);
            return true;
        } catch (parseError) {
            console.log('⚠️ Could not parse chat response as JSON:', responseText);
            displayOraResponse({response: responseText});
            return true;
        }
    } catch (error) {
        console.error('❌ Failed to send chat message:', error);
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

// UPDATED Function to display ORA's response in the chat - SIMPLIFIED VERSION
function displayOraResponse(responseData) {
    console.log("Raw response received:", responseData);
    
    // Show the chat section
    const chatDiv = document.getElementById("chat");
    if (chatDiv) {
        chatDiv.style.display = "block";
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
        // Handle the 'message' field from Make.com
        message = responseData.message;
    } else if (responseData && responseData.response) {
        // Handle the 'response' field
        message = responseData.response;
    } else if (responseData && responseData.status === "success") {
        // Generic success message if no specific response
        message = "I hear you. How can I support your wellness journey today?";
    } else {
        // Fallback for unexpected response format
        message = "I'm here to support you. Please share more about how you're feeling.";
        console.log("Unexpected response format:", responseData);
    }
    
    // Add the message to chat history
    if (message) {
        chatHistory.innerHTML += `<div class="assistant">🧘 <strong>ORA:</strong> ${message}</div>`;
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
    
    // Calculate intensity based on emotion detection and keywords found
    let intensity = 0.7; // Default intensity
    if (maxCount > 0) {
      intensity = Math.min(0.6 + (maxCount * 0.2), 1.0); // Higher intensity for more emotion keywords
    }
    
    // Update global variables for visualization
    window.currentEmotion = detectedEmotion;
    window.emotionIntensity = intensity; // Use calculated intensity instead of speech confidence
    
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
    
    // Send to Make.com webhook with intensity instead of confidence
    const emotionData = {
      emotion: detectedEmotion,
      intensity: intensity,  // Use intensity instead of confidence
      text: text,
      sessionId: chatId
    };
    
    // Send to Make.com webhook
    const success = await sendEmotionToMake(emotionData);
    
    if (success) {
      console.log('✅ Emotion data sent successfully to Make.com');
    } else {
      console.error('❌ Failed to send emotion data to Make.com');
      statusText.textContent = "Error sending data to Make.com";
    }
  }
  
  // Send chat message function
  function sendMessage() {
    const messageText = userMessage.value.trim();
    if (!messageText) return;
    
    // Add user message to chat
    chatHistory.innerHTML += `<div class="user">🧑 ${messageText}</div>`;
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Clear input
    userMessage.value = "";
    
    // Send to Make.com
    sendChatMessage(messageText);
  }
});





