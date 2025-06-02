// Main variables
// Make these global so p5-sketch.js can access them
window.currentEmotion = "neutral";
window.emotionIntensity = 0;
let chatId = null;

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

  .assistant-content {
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
    
    .user, .assistant-content {
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

// Function to send emotion data to Make.com webhook (EXACT WORKING VERSION)
async function sendEmotionToMake(emotionData) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('🚀 Attempting to send to Make.com webhook:', emotionData);
    
    // Create FLATTENED payload structure to match Make.com scenario
    // This avoids nested objects which Make.com has trouble parsing
    const flattenedPayload = {
        user_id: chatId,
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        emotion: emotionData.emotion,              // CHANGED: was primary_emotion
        intensity: emotionData.intensity,          // CHANGED: was intensity_level
        text: emotionData.text,                    // CHANGED: was raw_text
        time_of_day: getTimeOfDay()
    };
    
    console.log('📦 Flattened payload:', flattenedPayload);
    console.log('Mits',JSON.stringify(flattenedPayload));
    
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
            // FIXED: Get response as text first, then try to parse as JSON
            const responseText = await directResponse.text();
            console.log('✅ Direct Make.com webhook success (raw):', responseText);
            
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
                    message: responseText || 'Data received successfully' 
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

// Function to send chat messages (EXACT WORKING VERSION)
async function sendChatMessage(messageText) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('💬 Sending chat message:', messageText);
    
    // Create payload for chat message - SAME FORMAT as emotion data
    const chatPayload = {
        user_id: chatId,
        session_id: chatId,
        timestamp: new Date().toISOString(),
        emotion: window.currentEmotion || 'neutral',    // CHANGED: was primary_emotion
        intensity: window.emotionIntensity || 0.7,      // CHANGED: was intensity_level
        text: messageText,                              // CHANGED: was raw_text
        time_of_day: getTimeOfDay()
        // Removed message_type to keep same format as working emotion data
    };
    
    console.log('📦 Chat payload:', chatPayload);
    
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
            console.log('✅ Chat message success (raw):', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('✅ Parsed JSON response:', responseData);
            } catch (parseError) {
                console.log('ℹ️ Response is not JSON, using as text:', responseText);
                responseData = { 
                    status: 'success', 
                    message: responseText || 'Message sent successfully' 
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

// Function to display ORA's response in the chat (EXACT WORKING VERSION)
function displayOraResponse(responseData) {
    const chatHistory = document.getElementById("chatHistory");
    if (!chatHistory) return;
    
    console.log("Raw response received:", responseData);
    
    // Show chat interface after first response
    const chatDiv = document.getElementById("chat");
    if (chatDiv && chatDiv.style.display === "none") {
        chatDiv.style.display = "block";
    }
    
    // Try to display structured response if available
    try {
        if (responseData && responseData.message) {
            // Handle the 'message' field from Make.com
            let message = responseData.message;
            chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> ${message}</div>`;
        } else if (responseData && responseData.response) {
            let response = responseData.response;
            
            // If response is a string, try to parse it as JSON
            if (typeof response === 'string') {
                try {
                    response = JSON.parse(response);
                } catch (e) {
                    // If parsing fails, just display the string
                    chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> ${response}</div>`;
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                    return;
                }
            }
            
            // If we have a structured response object
            if (response.acknowledgment || response.mindfulness_practice) {
                chatHistory.innerHTML += `
                    <div class="assistant-content">
                        🧘 <strong>ORA Wellness Guidance:</strong><br>
                        ${response.acknowledgment ? `<p><strong>💝 Acknowledgment:</strong> ${response.acknowledgment}</p>` : ''}
                        ${response.mindfulness_practice ? `<p><strong>🧠 Mindfulness Practice:</strong> ${response.mindfulness_practice}</p>` : ''}
                        ${response.mind_body_exercise ? `<p><strong>🧘 Mind-Body Exercise:</strong> ${response.mind_body_exercise}</p>` : ''}
                        ${response.empowering_reflection ? `<p><strong>💪 Empowering Reflection:</strong> ${response.empowering_reflection}</p>` : ''}
                        ${response.physical_action ? `<p><strong>🏃 Physical Action:</strong> ${response.physical_action}</p>` : ''}
                    </div>
                `;
            } else {
                chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> ${response}</div>`;
            }
        } else if (responseData && responseData.status === "success") {
            // Generic success message if no specific response
            chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> I hear you. How can I support your wellness journey today?</div>`;
        } else {
            // Fallback for unexpected response format
            chatHistory.innerHTML += `<div class="assistant-content">🧘 <strong>ORA:</strong> I'm here to support you. Please share more about how you're feeling.</div>`;
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
        happy: "linear-gradient(90deg, #FFD700, #FFA500)",
        sad: "linear-gradient(90deg, #4169E1, #1E90FF)",
        angry: "linear-gradient(90deg, #FF4500, #DC143C)",
        fear: "linear-gradient(90deg, #9370DB, #8A2BE2)",
        surprise: "linear-gradient(90deg, #FF69B4, #FF1493)",
        disgust: "linear-gradient(90deg, #32CD32, #228B22)",
        neutral: "linear-gradient(90deg, #ff6b9d, #c471ed, #12c2e9)"
      };
      
      intensityFill.style.background = emotionColors[detectedEmotion] || emotionColors.neutral;
    }
    
    console.log(`🎯 Emotion detected: ${detectedEmotion} (intensity: ${intensity})`);
    
    // Send to Make.com
    const emotionData = {
      emotion: detectedEmotion,
      intensity: intensity,
      text: text,
      confidence: confidence,
      sessionId: chatId
    };
    
    statusText.textContent = "Sending data to Make.com...";
    
    const success = await sendEmotionToMake(emotionData);
    
    if (success) {
      console.log('✅ Emotion data sent successfully to Make.com');
      statusText.textContent = "Data sent successfully to Make.com";
    } else {
      console.log('❌ Failed to send emotion data to Make.com');
      statusText.textContent = "Failed to send emotion data to Make.com";
    }
  }
  
  // Send chat message function
  async function sendMessage() {
    const messageText = userMessage.value.trim();
    if (!messageText) return;
    
    console.log('💬 User message:', messageText);
    
    // Clear input
    userMessage.value = '';
    
    // Send to Make.com
    const success = await sendChatMessage(messageText);
    
    if (success) {
      console.log('✅ Chat message sent successfully');
    } else {
      console.log('❌ Failed to send chat message');
    }
  }
});



