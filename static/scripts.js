// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to Make.com webhook
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/mg0z2u8k9gv069uo14pj1exbil0a6q17";
    
    console.log('🚀 Attempting to send to Make.com webhook:', emotionData);
    
    // Create enhanced payload structure to match Make.com scenario
    const enhancedPayload = {
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        emotion_data: {
            primary_emotion: emotionData.emotion,
            confidence_score: emotionData.confidence,
            secondary_emotions: [],
            voice_indicators: []
        },
        context: {
            activity: "voice recording",
            location: "app",
            time_of_day: getTimeOfDay()
        },
        raw_text: emotionData.text
    };
    
    console.log('📦 Enhanced payload:', enhancedPayload);
    
    try {
        // Try direct connection first (without CORS proxy)
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(enhancedPayload)
        });
        
        if (directResponse.ok) {
            // Parse and handle the response from Make.com
            const responseData = await directResponse.json();
            console.log('✅ Direct Make.com webhook success:', responseData);
            
            // Display the ORA response in the chat
            displayOraResponse(responseData);
            
            return true;
        }
        
    } catch (directError) {
        console.log('⚠️ Direct connection failed, trying CORS proxy:', directError.message);
    }
    
    // Fallback to CORS proxy with enhanced payload
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const response = await fetch(corsProxyUrl + encodeURIComponent(makeWebhookUrl), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(enhancedPayload)
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
        }
        
        return true;
    } catch (error) {
        console.error('❌ Failed to send to proxy:', error);
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

// Function to display ORA's response in the chat
function displayOraResponse(responseData) {
    const chatHistory = document.getElementById("chatHistory");
    if (!chatHistory) return;
    
    // Check if we have a response object
    if (responseData && responseData.response) {
        try {
            // Try to parse the response if it's a string
            const response = typeof responseData.response === 'string' 
                ? JSON.parse(responseData.response) 
                : responseData.response;
            
            // Add ORA's response components to chat
            chatHistory.innerHTML += `
                <div class="assistant">
                    <div class="ora-header">🧘 ORA Wellness Response</div>
                    <div class="ora-section"><strong>Acknowledgment:</strong> ${response.acknowledgment}</div>
                    <div class="ora-section"><strong>Mindfulness Practice:</strong> ${response.mindfulness_practice}</div>
                    <div class="ora-section"><strong>Mind-Body Exercise:</strong> ${response.mind_body_exercise}</div>
                    <div class="ora-section"><strong>Empowering Reflection:</strong> ${response.empowering_reflection}</div>
                    <div class="ora-section"><strong>Physical Action:</strong> ${response.physical_action}</div>
                </div>
            `;
        } catch (error) {
            // If parsing fails, display the raw response
            chatHistory.innerHTML += `<div class="assistant">🧘 ${responseData.response}</div>`;
        }
    } else if (responseData && responseData.status === "success") {
        // Generic success message if no specific response
        chatHistory.innerHTML += `<div class="assistant">🧘 ORA has processed your emotion data.</div>`;
    }
    
    // Scroll chat to bottom
    chatHistory.scrollTop = chatHistory.scrollHeight;
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
    
    // Add user's speech to chat history
    if (chatHistory) {
      chatHistory.innerHTML += `<div class="user">🧑 "${text}"</div>`;
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
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
      if (chatHistory) {
        chatHistory.innerHTML += `<div class="assistant error">⚠️ Unable to connect to ORA wellness agent.</div>`;
      }
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
    
    // Process the text as an emotion input
    processEmotion(text, 0.8); // Using a default confidence score
  }
});
