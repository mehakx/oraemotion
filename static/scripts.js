// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

// Function to send emotion data to Make.com webhook
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('🚀 Attempting to send to Make.com webhook:', emotionData);
    
    // Create FLATTENED payload structure to match Make.com scenario
    // This avoids nested objects which Make.com has trouble parsing
    const flattenedPayload = {
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        primary_emotion: emotionData.emotion,
        intensity_level: emotionData.intensity,  // Changed from confidence_score to intensity_level
        raw_text: emotionData.text,
        time_of_day: getTimeOfDay()
    };
    
    console.log('📦 Flattened payload:', flattenedPayload);
    
    try {
        // Try direct connection first (without CORS proxy)
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload)
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
    
    // Fallback to CORS proxy with flattened payload
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const response = await fetch(corsProxyUrl + encodeURIComponent(makeWebhookUrl), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload)
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
    
    // Display something no matter what
    chatHistory.innerHTML += `<div class="assistant">🧘 ORA Wellness Response received.</div>`;
    
    // Try to display structured response if available
    try {
        if (responseData && responseData.response) {
            let response = responseData.response;
            
            // If response is a string, try to parse it as JSON
            if (typeof response === 'string') {
                try {
                    response = JSON.parse(response);
                } catch (e) {
                    // If parsing fails, just display the string
                    chatHistory.innerHTML += `<div class="assistant-content">${response}</div>`;
                    return;
                }
            }
            
            // If we have a structured response object
            if (response.acknowledgment || response.mindfulness_practice) {
                chatHistory.innerHTML += `
                    <div class="assistant-content">
                        ${response.acknowledgment ? `<p><strong>Acknowledgment:</strong> ${response.acknowledgment}</p>` : ''}
                        ${response.mindfulness_practice ? `<p><strong>Mindfulness Practice:</strong> ${response.mindfulness_practice}</p>` : ''}
                        ${response.mind_body_exercise ? `<p><strong>Mind-Body Exercise:</strong> ${response.mind_body_exercise}</p>` : ''}
                        ${response.empowering_reflection ? `<p><strong>Empowering Reflection:</strong> ${response.empowering_reflection}</p>` : ''}
                        ${response.physical_action ? `<p><strong>Physical Action:</strong> ${response.physical_action}</p>` : ''}
                    </div>
                `;
            }
        } else if (responseData && responseData.status === "success") {
            // Generic success message if no specific response
            chatHistory.innerHTML += `<div class="assistant-content">ORA has processed your emotion data.</div>`;
        } else {
            // Fallback for unexpected response format
            chatHistory.innerHTML += `<div class="assistant-content">Received response from ORA.</div>`;
            console.log("Unexpected response format:", responseData);
        }
    } catch (error) {
        console.error("Error displaying ORA response:", error);
        chatHistory.innerHTML += `<div class="assistant error">⚠️ Error displaying ORA response.</div>`;
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
    
    // Process the text as an emotion input with default intensity
    processEmotion(text, 0.8); // Using a default confidence score (not used for intensity calculation)
  }
});
