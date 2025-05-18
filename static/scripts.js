window.addEventListener("DOMContentLoaded", () => {
  const recordBtn  = document.getElementById("recordBtn");
  const stopBtn    = document.getElementById("stopBtn");
  const status     = document.getElementById("status");
  const chatDiv    = document.getElementById("chat");
  const chatHistory = document.getElementById("chatHistory");
  const userMessage = document.getElementById("userMessage");
  const sendBtn     = document.getElementById("sendBtn");

  // Web Speech API
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    status.textContent = "⚠️ SpeechRecognition not supported.";
    recordBtn.disabled = true;
    return;
  }
  const recog = new SR();
  recog.lang = "en-US";
  recog.interimResults = false;
  recog.maxAlternatives = 1;

  let chatId = null;

  recordBtn.onclick = () => {
    status.textContent = "Listening…";
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    recog.start();
  };

  stopBtn.onclick = () => {
    recog.stop();
  };

  recog.onresult = async (e) => {
    const text = e.results[0][0].transcript;
    status.textContent = `You said: “${text}” – detecting emotion…`;
    stopBtn.disabled = true;

    try {
      // Classify emotion
      let res = await fetch("/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      let { emotion } = await res.json();

      status.textContent = `Emotion: ${emotion} – generating reply…`;

      // Get empathetic reply
      res = await fetch("/respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emotion, text })
      });
      let { message, chat_id } = await res.json();

      // Show chat UI
      chatId = chat_id;
      chatHistory.innerHTML = `
        <div class="assistant">🤖 ${message}</div>
      `;
      chatDiv.classList.remove("hidden");
      status.textContent = "Done";

    } catch (err) {
      console.error(err);
      status.textContent = "⚠️ Error – see console.";
    } finally {
      recordBtn.disabled = false;
    }
  };

  recog.onerror = (e) => {
    status.textContent = `⚠️ Speech error: ${e.error}`;
    recordBtn.disabled = false;
    stopBtn.disabled = true;
  };

  // Send user chat messages
  sendBtn.onclick = sendMessage;
  userMessage.addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    const text = userMessage.value.trim();
    if (!text || !chatId) return;
    chatHistory.innerHTML += `<div class="user">🧑 ${text}</div>`;
    userMessage.value = "";

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, message: text })
      });
      const { reply } = await res.json();
      chatHistory.innerHTML += `<div class="assistant">🤖 ${reply}</div>`;
    } catch (err) {
      console.error(err);
      chatHistory.innerHTML += `<div class="assistant error">⚠️ Chat failed.</div>`;
    }
  }
});
