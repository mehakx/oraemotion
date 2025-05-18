// Main variables
let currentEmotion = "neutral";
let emotionIntensity = 0;
let chatId = null;

// Initialize when DOM is fully loaded
window.addEventListener("DOMContentLoaded", () => {
  const recordBtn = document.getElementById("recordBtn");
  const stopBtn = document.getElementById("stopBtn");
  const status = document.getElementById("status");
  const chatDiv = document.getElementById("chat");
  const chatHistory = document.getElementById("chatHistory");
  const userMessage = document.getElementById("userMessage");
  const sendBtn = document.getElementById("sendBtn");
  
  // Web Speech API
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    status.textContent = "⚠️ SpeechRecognition not supported.";
    recordBtn.disabled = true;
    return;
  }
  
  const recognition = new SR();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  
  // Set up record button
  recordBtn.onclick = () => {
    status.textContent = "Listening…";
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    recognition.start();
  };
  
  // Set up stop button
  stopBtn.onclick = () => {
    recognition.stop();
    status.textContent = "Stopped listening";
    stopBtn.disabled = true;
    recordBtn.disabled = false;
  };
  
  // Handle speech recognition results
  recognition.onresult = async (e) => {
    const text = e.results[0][0].transcript;
    status.textContent = `You said: "${text}" – detecting emotion…`;
    stopBtn.disabled = true;
    recordBtn.disabled = false;
    
    try {
      // Classify emotion
      let res = await fetch("/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      let data = await res.json();
      
      // Update status with detected emotion
      status.textContent = `Emotion: ${data.emotion} – generating reply…`;
      
      // Update the visualization
      updateVisualization(data.emotion, data.intensity);
      
      // Get empathetic reply
      res = await fetch("/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emotion: data.emotion, text })
      });
      let { message, chat_id } = await res.json();
      
      // Show chat UI
      chatId = chat_id;
      chatHistory.innerHTML = `
        <div class="assistant">🤖 ${message}</div>
      `;
      chatDiv.style.display = "block";
      status.textContent = "Ready to record again";
    } catch (err) {
      console.error(err);
      status.textContent = "⚠️ Error – see console.";
      recordBtn.disabled = false;
    }
  };
  
  // Handle speech recognition errors
  recognition.onerror = (e) => {
    status.textContent = `⚠️ Speech error: ${e.error}`;
    recordBtn.disabled = false;
    stopBtn.disabled = true;
  };
  
  // Set up send button for chat
  sendBtn.onclick = sendMessage;
  userMessage.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });
  
  // Function to send chat messages
  async function sendMessage() {
    const text = userMessage.value.trim();
    if (!text || !chatId) return;
    
    // Add user message to chat
    chatHistory.innerHTML += `<div class="user">🧑 ${text}</div>`;
    userMessage.value = "";
    
    try {
      // Send message to server
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
