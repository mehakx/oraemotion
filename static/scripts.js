// Emotion Analyzer - Abstract Digital Visualization
// Main variables
let recognition;
let isListening = false;
let confidences = { sad: 0, fear: 0, anger: 0, anxiety: 0, neutral: 1, excitement: 0, joy: 0 };
let lastTranscript = '';
let chatId = null;

// Visualization variables
let currentEmotion = "neutral";
let lastEmotion = "neutral";
let emotionIntensity = 30;
let particleSystem = [];
let waveAmplitude = 10;
let waveFrequency = 0.02;
let waveSpeed = 0.01;
let wavePhase = 0;
let center = { x: 0, y: 0 };
let eyeSize = 200;
let pulseSize = 1;
let pulseDirection = 0.01;
let noiseOffset = 0;

// Error handling
let recognitionTimeout = null;
let consecutiveErrors = 0;
let maxConsecutiveErrors = 3;
let backoffTime = 1000;
let textInputActive = false;

// Colors for different emotions
const emotionColors = {
  sad: { primary: '#0066cc', secondary: '#001a33', accent: '#66a3ff' },
  fear: { primary: '#6600cc', secondary: '#1a0033', accent: '#cc99ff' },
  anger: { primary: '#cc0000', secondary: '#330000', accent: '#ff6666' },
  anxiety: { primary: '#cc6600', secondary: '#331a00', accent: '#ffcc66' },
  neutral: { primary: '#666666', secondary: '#1a1a1a', accent: '#cccccc' },
  excitement: { primary: '#ffcc00', secondary: '#332b00', accent: '#ffee99' },
  joy: { primary: '#00cc00', secondary: '#003300', accent: '#99ff99' },
  confused: { primary: '#ff00ff', secondary: '#330033', accent: '#ff99ff' },
  tired: { primary: '#336699', secondary: '#0d1a26', accent: '#99c2ff' },
  hungry: { primary: '#ff9900', secondary: '#332600', accent: '#ffd699' }
};

function setup() {
  let canvas = createCanvas(windowWidth, windowHeight);
  canvas.parent('visual-container');
  colorMode(HSB, 360, 100, 100, 1);
  
  // Set center point
  center = { x: width/2, y: height/2 };
  
  // Create initial particles
  createParticles(50);
  
  // Setup speech recognition
  setupSpeechRecognition();
  setupChatInterface();
  
  // Begin speech recognition immediately
  startListening();
  
  console.log('setup done');
}

function createParticles(count) {
  for (let i = 0; i < count; i++) {
    let angle = random(TWO_PI);
    let radius = random(eyeSize * 0.5, eyeSize * 2);
    
    particleSystem.push({
      pos: { 
        x: center.x + cos(angle) * radius, 
        y: center.y + sin(angle) * radius 
      },
      vel: { x: random(-1, 1), y: random(-1, 1) },
      size: random(2, 8),
      color: color(random(360), 80, 90, random(0.5, 0.9)),
      angle: angle,
      radius: radius,
      speed: random(0.005, 0.02),
      noiseOffset: random(1000),
      lifespan: 255
    });
  }
}

function setupChatInterface() {
  const chatToggle = document.getElementById('chat-toggle');
  const chatContainer = document.getElementById('chat-container');
  const sendButton = document.getElementById('send-button');
  const messageInput = document.getElementById('message-input');
  
  // Set up chat toggle
  chatToggle.addEventListener('click', () => {
    const isVisible = chatContainer.style.display === 'block';
    chatContainer.style.display = isVisible ? 'none' : 'block';
  });
  
  // Set up send button
  sendButton.addEventListener('click', sendChatMessage);
  
  // Set up enter key to send message
  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      sendChatMessage();
    }
  });
}

function sendChatMessage() {
  const messageInput = document.getElementById('message-input');
  const text = messageInput.value.trim();
  
  if (!text) return;
  
  // Clear input field
  messageInput.value = '';
  
  // Add message to chat history
  addMessageToChat(text, 'user');
  
  // If we don't have a chat session yet, we need to respond to the message and create one
  if (!chatId) {
    processEmotionAndRespond(text);
  } else {
    // Continue existing chat session
    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, message: text })
    })
    .then(response => response.json())
    .then(data => {
      addMessageToChat(data.reply, 'assistant');
    })
    .catch(error => {
      console.error('Error in chat:', error);
      addMessageToChat('Sorry, there was an error processing your message.', 'assistant', true);
    });
  }
}

function addMessageToChat(message, sender, isError = false) {
  const chatHistory = document.getElementById('chat-history');
  const messageElement = document.createElement('div');
  
  messageElement.classList.add('chat-message');
  messageElement.classList.add(sender + '-message');
  
  if (isError) {
    messageElement.classList.add('error-message');
  }
  
  messageElement.textContent = message;
  chatHistory.appendChild(messageElement);
  
  // Scroll to bottom
  chatHistory.scrollTop = chatHistory.scrollHeight;
  
  // Make chat container visible if it's not already
  document.getElementById('chat-container').style.display = 'block';
}

function setupSpeechRecognition() {
  if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
    document.getElementById('status').innerText = 'Speech not supported. Please type.';
    showTextInputFallback('Type your message below.');
    return;
  }
  
  recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onresult = e => {
    const transcript = e.results[e.results.length-1][0].transcript.trim();
    console.log('Transcript:', transcript);
    if (transcript && transcript !== lastTranscript) {
      lastTranscript = transcript;
      processEmotionAndRespond(transcript);
      consecutiveErrors = 0;
      backoffTime = 1000;
    }
  };
  
  recognition.onerror = e => {
    console.error('Speech error', e.error);
    consecutiveErrors++;
    clearTimeout(recognitionTimeout);
    if (consecutiveErrors >= maxConsecutiveErrors) showTextInputFallback('Speech failing — type instead.');
    recognitionTimeout = setTimeout(startListening, backoffTime);
  };
  
  recognition.onend = () => {
    console.log('Speech ended, restarting...');
    if (!recognitionTimeout) recognitionTimeout = setTimeout(startListening, backoffTime);
  };
  
  window.addEventListener('mousedown', startListening);
}

function startListening() {
  try { 
    recognition.start(); 
    isListening = true;
    document.getElementById('status').innerText = 'Listening. Just start speaking...';
  } catch { 
    recognitionTimeout = setTimeout(startListening, 1000); 
  }
}

function showTextInputFallback(msg) {
  if (textInputActive) return;
  textInputActive = true;
  const c = document.createElement('div'); 
  c.id = 'text-input-container';
  if (msg) {
    const m = document.createElement('div');
    m.textContent = msg;
    c.appendChild(m);
  }
  
  const inp = document.createElement('input'); 
  inp.placeholder = 'Type here...'; 
  inp.style.padding = '8px'; 
  inp.style.margin = '5px';
  
  const btn = document.createElement('button'); 
  btn.textContent = 'Go'; 
  btn.onclick = () => {
    const text = inp.value.trim();
    if (text) {
      processEmotionAndRespond(text);
      inp.value = '';
    }
  };
  
  c.append(inp, btn);
  document.body.appendChild(c);
}

function processEmotionAndRespond(text) {
  processText(text);
  
  // Don't create a chat session for very short utterances
  if (text.length < 5) return;
  
  // Also get an empathetic response
  fetch('/respond', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text })
  })
  .then(response => response.json())
  .then(data => {
    chatId = data.chat_id;
    addMessageToChat(text, 'user');
    addMessageToChat(data.message, 'assistant');
    document.getElementById('chat-container').style.display = 'block';
  })
  .catch(error => {
    console.error('Error getting response:', error);
  });
}

function processText(text) {
  fetch('/classify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  .then(r => r.json())
  .then(data => {
    confidences = data.confidences || {};
    lastEmotion = currentEmotion;
    currentEmotion = data.emotion.toLowerCase();
    emotionIntensity = Math.abs(data.intensity);
    
    // Visual response to emotion change
    waveAmplitude = map(emotionIntensity, 0, 100, 5, 30);
    waveFrequency = map(emotionIntensity, 0, 100, 0.01, 0.05);
    pulseSize = 1.5;  // Expand the eye
    
    // Add new particles on emotion change
    if (currentEmotion !== lastEmotion) {
      createParticles(30);
    }
    
    // Update the status display
    const statusEl = document.getElementById('status');
    const statusText = `Detected: ${data.emotion} (intensity: ${data.intensity})`;
    statusEl.innerText = statusText;
    
    // Update the emotion panel
    document.getElementById('emotion-label').textContent = data.emotion.toLowerCase();
    
    // Set color of emotion label based on emotion
    const colors = emotionColors[currentEmotion] || emotionColors.neutral;
    document.getElementById('emotion-label').style.color = colors.primary;
    
    // Update intensity bar
    document.getElementById('intensity-fill').style.width = `${emotionIntensity}%`;
    document.getElementById('intensity-fill').style.background = `repeating-linear-gradient(
      45deg,
      ${colors.primary}88,
      ${colors.primary}88 5px,
      ${colors.accent} 5px,
      ${colors.accent} 10px
    )`;
    
    // Create a visual flash for emotion change
    if (currentEmotion !== lastEmotion) {
      const flashEl = document.createElement('div');
      Object.assign(flashEl.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        backgroundColor: colors.primary,
        opacity: '0.2',
        pointerEvents: 'none',
        transition: 'opacity 0.5s',
        zIndex: '999'
      });
      document.body.appendChild(flashEl);
      setTimeout(() => {
        flashEl.style.opacity = '0';
        setTimeout(() => flashEl.remove(), 500);
      }, 100);
    }
  })
  .catch(e => {
    console.error(e);
    document.getElementById('status').innerText = 'Error analyzing.';
  });
}

function draw() {
  // Set background color based on current emotion
  const colors = emotionColors[currentEmotion] || emotionColors.neutral;
  background(colors.secondary);
  
  // Update wave phase
  wavePhase += waveSpeed;
  
  // Update pulse animation
  pulseSize += pulseDirection;
  if (pulseSize > 1.2 || pulseSize < 0.9) {
    pulseDirection *= -1;
  }
  
  // Update noise offset for particle movement
  noiseOffset += 0.01;
  
  // Draw outer waves
  drawWaves(colors.primary, colors.accent);
  
  // Draw the central eye
  drawAbstractEye(colors.primary, colors.accent);
  
  // Update and draw particles
  updateParticles(colors.primary);
  
  // Draw pupil
  drawPupil(colors.secondary);
}

function drawWaves(primaryColor, accentColor) {
  noFill();
  stroke(primaryColor);
  strokeWeight(2);
  
  // Draw concentric waves
  for (let i = 0; i < 5; i++) {
    let size = eyeSize * 1.5 + i * 50;
    beginShape();
    for (let a = 0; a < TWO_PI; a += 0.1) {
      let xoff = map(cos(a), -1, 1, 0, 2);
      let yoff = map(sin(a), -1, 1, 0, 2);
      let r = size + waveAmplitude * sin(waveFrequency * size + wavePhase);
      let x = center.x + r * cos(a);
      let y = center.y + r * sin(a);
      vertex(x, y);
    }
    endShape(CLOSE);
  }
  
  // Draw radiating lines
  stroke(accentColor);
  strokeWeight(1);
  let lineCount = 12;
  for (let i = 0; i < lineCount; i++) {
    let angle = i * TWO_PI / lineCount;
    let startX = center.x + eyeSize * 0.7 * cos(angle);
    let startY = center.y + eyeSize * 0.7 * sin(angle);
    let endX = center.x + (eyeSize * 2 + waveAmplitude * sin(wavePhase)) * cos(angle);
    let endY = center.y + (eyeSize * 2 + waveAmplitude * sin(wavePhase)) * sin(angle);
    
    line(startX, startY, endX, endY);
  }
}

function drawAbstractEye(primaryColor, accentColor) {
  // Draw iris
  noStroke();
  fill(primaryColor);
  ellipse(center.x, center.y, eyeSize * pulseSize, eyeSize * pulseSize);
  
  // Draw iris detail
  stroke(accentColor);
  strokeWeight(1);
  noFill();
  for (let i = 0; i < 3; i++) {
    ellipse(center.x, center.y, 
            eyeSize * 0.8 * pulseSize - i * 15, 
            eyeSize * 0.8 * pulseSize - i * 15);
  }
  
  // Draw light reflection
  noStroke();
  fill(255, 180);
  let reflectionX = center.x + eyeSize * 0.25;
  let reflectionY = center.y - eyeSize * 0.2;
  ellipse(reflectionX, reflectionY, eyeSize * 0.2, eyeSize * 0.15);
}

function drawPupil(secondaryColor) {
  fill(secondaryColor);
  noStroke();
  
  // Determine pupil size based on emotion intensity
  let pupilSize = map(emotionIntensity, 0, 100, eyeSize * 0.2, eyeSize * 0.5);
  ellipse(center.x, center.y, pupilSize, pupilSize);
  
  // Draw pupil detail
  fill(0);
  ellipse(center.x, center.y, pupilSize * 0.8, pupilSize * 0.8);
  
  // Small white reflection in pupil
  fill(255, 200);
  ellipse(center.x - pupilSize * 0.15, center.y - pupilSize * 0.15, pupilSize * 0.1, pupilSize * 0.1);
}

function updateParticles(primaryColor) {
  noStroke();
  
  for (let i = particleSystem.length - 1; i >= 0; i--) {
    let p = particleSystem[i];
    
    // Noise-based movement
    let noiseX = noise(p.noiseOffset, 0, noiseOffset) * 2 - 1;
    let noiseY = noise(0, p.noiseOffset, noiseOffset) * 2 - 1;
    
    // Angular movement
    p.angle += p.speed * (emotionIntensity / 50);
    p.radius += sin(frameCount * 0.05) * 0.5;
    
    // Combine noise and circular movement
    p.pos.x = center.x + cos(p.angle) * p.radius + noiseX * 10;
    p.pos.y = center.y + sin(p.angle) * p.radius + noiseY * 10;
    
    // Decrease lifespan
    p.lifespan -= 0.5;
    
    // Draw the particle
    let particleColor = color(hue(p.color), saturation(p.color), brightness(p.color), p.lifespan / 255);
    fill(particleColor);
    ellipse(p.pos.x, p.pos.y, p.size, p.size);
    
    // Remove dead particles
    if (p.lifespan <= 0) {
      particleSystem.splice(i, 1);
    }
  }
  
  // Add new particles occasionally
  if (frameCount % 30 === 0) {
    createParticles(1);
  }
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
  center = { x: width/2, y: height/2 };
}
