<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ORA - Your Wellness Companion</title>
  <style>
    body, html {
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background-color: #f8f9fa;
      height: 100%;
    }
    
    .navbar {
      background: #007bff;
      color: white;
      padding: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .logo {
      width: 50px;
      margin-right: 10px;
    }
    
    .container {
      max-width: 800px;
      margin: 20px auto;
      padding: 20px;
      background: white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      border-radius: 8px;
      text-align: center;
    }
    
    h1, h2 {
      color: #007bff;
      margin-bottom: 30px;
    }
    
    .controls {
      margin-bottom: 20px;
    }
    
    button {
      padding: 12px 24px;
      margin: 0 10px;
      border: none;
      border-radius: 50px;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
      transition: background-color 0.3s;
    }
    
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    #recordBtn {
      background-color: #ffdb58;
      color: #333;
    }
    
    #recordBtn:hover:not(:disabled) {
      background-color: #f0c030;
    }
    
    #stopBtn {
      background-color: #e0e0e0;
      color: #333;
    }
    
    #stopBtn:hover:not(:disabled) {
      background-color: #d0d0d0;
    }
    
    .btn {
      background-color: #007bff;
      color: white;
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    
    .btn.success {
      background-color: #28a745;
    }
    
    .btn:hover {
      opacity: 0.8;
    }
    
    #status {
      margin: 15px 0;
      font-size: 18px;
      color: #555;
      min-height: 25px;
    }
    
    #visualization-container {
      width: 100%;
      height: 400px;
      margin: 20px 0;
      border-radius: 10px;
      overflow: hidden;
      position: relative;
      background-color: #1a1a1a;
    }
    
    #emotion-panel {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      width: 200px;
      text-align: center;
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      border-radius: 8px;
      padding: 10px;
      z-index: 10;
    }
    
    #emotion-label {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 8px;
      text-transform: lowercase;
    }
    
    #intensity-bar {
      height: 15px;
      width: 100%;
      background-color: #333;
      border-radius: 10px;
      overflow: hidden;
      margin-top: 5px;
    }
    
    #intensity-fill {
      height: 100%;
      width: 0%;
      background: repeating-linear-gradient(
        45deg,
        #555,
        #555 5px,
        #777 5px,
        #777 10px
      );
      transition: width 0.5s, background 0.5s;
    }
    
    /* Chat Interface Styles */
    #chat {
      display: none;
      margin-top: 30px;
      border-top: 2px solid #007bff;
      padding-top: 20px;
      text-align: left;
    }
    
    #chat h3 {
      text-align: center;
      color: #007bff;
      margin-bottom: 20px;
    }
    
    .chat-history {
      margin-bottom: 15px;
      max-height: 300px;
      overflow-y: auto;
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 8px;
      border: 1px solid #dee2e6;
    }
    
    .chat-history div {
      margin-bottom: 15px;
      padding: 12px;
      border-radius: 8px;
      line-height: 1.4;
    }
    
    .chat-history .user {
      background-color: #007bff;
      color: white;
      margin-left: 20px;
      text-align: right;
      border-radius: 15px 15px 5px 15px;
    }
    
    .chat-history .assistant {
      background-color: #e9ecef;
      color: #333;
      margin-right: 20px;
      border-radius: 15px 15px 15px 5px;
    }
    
    .chat-history .assistant-content {
      background-color: #d4edda;
      color: #155724;
      margin-right: 20px;
      border-radius: 15px 15px 15px 5px;
      border-left: 4px solid #28a745;
    }
    
    .chat-history .error {
      background-color: #f8d7da;
      color: #721c24;
      border-left: 4px solid #dc3545;
    }
    
    .chat-input {
      display: flex;
      gap: 10px;
      margin-top: 15px;
    }
    
    .chat-input input {
      flex-grow: 1;
      padding: 12px;
      border: 2px solid #dee2e6;
      border-radius: 25px;
      font-size: 16px;
      outline: none;
      transition: border-color 0.3s;
    }
    
    .chat-input input:focus {
      border-color: #007bff;
    }
    
    .chat-input button {
      padding: 12px 20px;
      background-color: #28a745;
      color: white;
      border: none;
      border-radius: 25px;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.3s;
    }
    
    .chat-input button:hover {
      background-color: #218838;
    }
    
    /* p5.js canvas */
    #p5-canvas {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
    }
    
    /* Animation for emotion change flash */
    @keyframes emotion-flash {
      0% { opacity: 0; }
      50% { opacity: 0.5; }
      100% { opacity: 0; }
    }
    
    .emotion-flash {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 100;
      animation: emotion-flash 0.5s ease-out;
    }
    
    /* Responsive adjustments */
    @media (max-width: 600px) {
      .container {
        margin: 10px;
        padding: 15px;
      }
      
      #visualization-container {
        height: 300px;
      }
      
      button {
        padding: 10px 20px;
        font-size: 14px;
      }
      
      .chat-history {
        max-height: 200px;
      }
    }
  </style>
  <!-- Load p5.js before our scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.6.0/p5.min.js"></script>
</head>
<body>
  <div class="navbar">
    <img src="/static/logo.png" alt="ORA Logo" class="logo">
    <h1>ORA - Your Wellness Companion</h1>
  </div>
  
  <div class="container">
    <h2>Emotion Analyzer</h2>
    
    <div class="controls">
      <button id="recordBtn">🎤 Record</button>
      <button id="stopBtn" disabled>⏹ Stop</button>
    </div>
    
    <p id="status">Ready to record</p>
    
    <div id="visualization-container">
      <!-- p5.js will create canvas here -->
      <div id="p5-canvas"></div>
      
      <!-- Emotion panel overlay -->
      <div id="emotion-panel">
        <div id="emotion-label">waiting...</div>
        <div id="intensity-bar">
          <div id="intensity-fill"></div>
        </div>
      </div>
    </div>
    
    <!-- Chat Interface (hidden until after first analysis) -->
    <div id="chat">
      <h3>💬 Continue Your Wellness Journey with ORA</h3>
      <div id="chatHistory" class="chat-history"></div>
      <div class="chat-input">
        <input type="text" id="userMessage" placeholder="Share more about how you're feeling, or ask ORA for guidance..." />
        <button id="sendBtn">Send</button>
      </div>
    </div>
  </div>
  
  <!-- Load our scripts in the correct order -->
  <script src="{{ url_for('static', filename='scripts.js') }}"></script>
  <script src="{{ url_for('static', filename='p5-sketch.js') }}"></script>
</body>
</html>
