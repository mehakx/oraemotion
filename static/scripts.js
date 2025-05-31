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
    const flattenedPayload = {
        user_id: chatId || 'anonymous',
        session_id: emotionData.sessionId || 'default',
        timestamp: new Date().toISOString(),
        primary_emotion: emotionData.emotion || 'neutral',
        confidence_score: Math.round((emotionData.confidence || 0) * 100), // Convert to percentage
        raw_text: emotionData.text || '',
        time_of_day: getTimeOfDay()
    };
    
    console.log('📦 Flattened payload:', flattenedPayload);
    
    try {
        // Try direct connection first with better error handling
        console.log('🔄 Attempting direct connection to Make.com...');
        const directResponse = await fetch(makeWebhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload),
            // Add timeout to prevent hanging
            signal: AbortSignal.timeout(10000) // 10 second timeout
        });
        
        console.log('📡 Direct response status:', directResponse.status);
        console.log('📡 Direct response ok:', directResponse.ok);
        console.log('📡 Direct response headers:', Object.fromEntries(directResponse.headers.entries()));
        
        if (directResponse.ok) {
            // Parse and handle the response from Make.com
            const responseText = await directResponse.text();
            console.log('✅ Direct response text:', responseText);
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
                console.log('✅ Direct Make.com webhook success (parsed JSON):', responseData);
            } catch (parseError) {
                console.log('⚠️ Response is not JSON, treating as text');
                responseData = { response: responseText, status: 'success' };
            }
            
            // Display the ORA response in the chat
            displayOraResponse(responseData);
            return true;
        } else {
            // Log the error response for debugging
            const errorText = await directResponse.text();
            console.error('❌ Direct connection failed with status:', directResponse.status);
            console.error('❌ Error response:', errorText);
            throw new Error(`HTTP ${directResponse.status}: ${errorText}`);
        }
        
    } catch (directError) {
        console.log('❌ Direct connection error details:');
        console.log('   Error type:', directError.constructor.name);
        console.log('   Error message:', directError.message);
        console.log('   Full error:', directError);
        
        // Better CORS detection
        if (directError.message.includes('CORS') || 
            directError.message.includes('cross-origin') ||
            directError.message.includes('Access-Control-Allow-Origin')) {
            console.log('🚫 Confirmed: This is a CORS error');
        } else if (directError.name === 'TypeError' && directError.message.includes('Failed to fetch')) {
            console.log('🚫 This looks like a CORS or network error (TypeError: Failed to fetch)');
        } else if (directError.name === 'AbortError') {
            console.log('⏰ Request timed out after 10 seconds');
        } else {
            console.log('🤔 This is a different type of error:', directError.name);
        }
        
        console.log('🔄 Trying CORS proxy as fallback...');
    }
    
    // Fallback to CORS proxy with better error handling
    try {
        const corsProxyUrl = "https://api.allorigins.win/raw?url=";
        const proxyUrl = corsProxyUrl + encodeURIComponent(makeWebhookUrl);
        console.log('🌐 Proxy URL:', proxyUrl);
        
        const response = await fetch(proxyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(flattenedPayload),
            signal: AbortSignal.timeout(15000) // 15 second timeout for proxy
        });
        
        console.log('🌐 Proxy response status:', response.status);
        console.log('🌐 Proxy response ok:', response.ok);
        
        if (response.ok) {
            const responseText = await response.text();
            console.log('✅ Proxy response text:', responseText);
            
            // Handle the common "Oops... Request Timeout." from allorigins
            if (responseText.includes('Request Timeout') || responseText.includes('Oops')) {
                console.log('⚠️ Proxy service timed out or failed');
                throw new Error('Proxy service timeout');
            }
            
            try {
                // Try to parse the response as JSON
                const responseData = JSON.parse(responseText);
                console.log('✅ Parsed proxy response data:', responseData);
                displayOraResponse(responseData);
                return true;
            } catch (parseError) {
                console.log('⚠️ Proxy response not JSON, treating as text');
                // Even if parsing fails, display something
                displayOraResponse({response: responseText, status: 'success'});
                return true;
            }
        } else {
            const errorText = await response.text();
            console.error('❌ Proxy failed with status:', response.status, errorText);
            throw new Error(`Proxy error: ${response.status}`);
        }
        
    } catch (proxyError) {
        console.error('❌ Proxy method failed:');
        console.log('   Error type:', proxyError.constructor.name);
        console.log('   Error message:', proxyError.message);
        console.log('   Full error:', proxyError);
        
        // Final fallback: Show error to user
        console.error('❌ All connection methods failed');
        displayErrorMessage('Unable to connect to wellness agent. Please check your internet connection and try again.');
        return false;
    }
}

// Helper function to display error messages
function displayErrorMessage(message) {
    const chatHistory = document.getElementById("chatHistory");
    if (chatHistory) {
        chatHistory.innerHTML += `<div class="assistant error">⚠️ ${message}</div>`;
        chatHistory.scrollTop = chatHistory.scrollHeight;
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
