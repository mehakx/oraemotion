// Voice-only conversation with ORA
// No text interface - pure voice-to-voice

let chatId = null;
let isRecording = false;
let recognition = null;

// Initialize when DOM is fully loaded
window.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const statusText = document.getElementById("status");
  
  // Initialize chat ID
  chatId = Date.now().toString();
  console.log('🆔 Chat ID initialized:', chatId);
  
  // Hide text interface completely
  const userMessage = document.getElementById("userMessage");
  const sendBtn = document.getElementById("sendBtn");
  if (userMessage) userMessage.style.display = "none";
  if (sendBtn) sendBtn.style.display = "none";
  
  // Set up event listeners
  if (recordBtn) {
    recordBtn.addEventListener("click", startRecording);
  }
  
  if (stopBtn) {
    stopBtn.addEventListener("click", stopRecording);
  }
  
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
      statusText.textContent = "✨ Listening...";
      recordBtn.style.display = "none";
      stopBtn.style.display = "inline-block";
      stopBtn.disabled = false;
      console.log('🎤 Recording started');
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      
      console.log('🗣️ Speech recognized:', transcript);
      
      // Send to Make.com for voice response
      sendVoiceMessage(transcript);
    };
    
    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      statusText.textContent = `Error: ${event.error}`;
      resetRecording();
    };
    
    recognition.onend = () => {
      if (isRecording) {
        statusText.textContent = "✨ Ready to listen";
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
  
  // Send voice message to Make.com
  async function sendVoiceMessage(transcript) {
    const makeWebhookUrl = "https://hook.eu2.make.com/t3fintf1gaxjumlyj7v357rleon0idnh";
    
    console.log('🎤 Sending voice message:', transcript);
    
    const payload = {
      user_id: chatId,
      timestamp: new Date().toISOString(),
      text: transcript,
      request_id: Math.random().toString(36)
    };
    
    statusText.textContent = "🤖 ORA is thinking...";
    
    try {
      const response = await fetch(makeWebhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        const responseText = await response.text();
        console.log('✅ Raw response:', responseText);
        
        let responseData;
        try {
          responseData = JSON.parse(responseText);
          console.log('✅ Parsed response:', responseData);
        } catch (parseError) {
          console.log('⚠️ Response is not JSON:', responseText);
          responseData = { message: responseText };
        }
        
        // Play the voice response
        playVoiceResponse(responseData);
        
      } else {
        console.error('❌ Response not ok:', response.status);
        statusText.textContent = "❌ Failed to get response";
      }
      
    } catch (error) {
      console.error('❌ Failed to send message:', error);
      statusText.textContent = "❌ Connection failed";
    }
  }
  
  // Play voice response (NO TEXT DISPLAY)
  function playVoiceResponse(responseData) {
    console.log('🔍 Looking for audio in response:', responseData);
    
    // Extract audio URL
    let audioUrl = "";
    
    if (responseData) {
      // Check multiple possible locations for audio URL
      audioUrl = responseData.audio_url || 
                responseData.audioUrl || 
                responseData.Audio_File || 
                responseData.audio_file ||
                "";
    }
    
    console.log('🎵 Audio URL found:', audioUrl);
    
    if (audioUrl && audioUrl.trim() !== "") {
      console.log('🔊 Playing audio:', audioUrl);
      statusText.textContent = "🔊 ORA is speaking...";
      
      const audio = new Audio(audioUrl);
      
      audio.onloadstart = () => {
        console.log('🔄 Audio loading...');
      };
      
      audio.oncanplay = () => {
        console.log('✅ Audio ready to play');
      };
      
      audio.onended = () => {
        console.log('✅ Audio playback completed');
        statusText.textContent = "✨ Ready to listen";
      };
      
      audio.onerror = (error) => {
        console.error('❌ Audio playback failed:', error);
        statusText.textContent = "❌ Audio playback failed";
      };
      
      // Play the audio
      audio.play().catch(error => {
        console.error('❌ Audio play failed:', error);
        statusText.textContent = "❌ Could not play audio";
      });
      
    } else {
      console.log('❌ No audio URL found in response');
      console.log('📋 Full response structure:', JSON.stringify(responseData, null, 2));
      statusText.textContent = "❌ No audio received";
    }
  }
});





