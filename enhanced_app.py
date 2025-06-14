<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ora - Enhanced Admin Dashboard</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #6dd5ed, #2193b0 );
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        .card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            border: none;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            background: rgba(255, 255, 255, 0.2);
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            font-weight: bold;
            color: #fff;
        }
        .btn-primary {
            background-color: #007bff;
            border-color: #007bff;
        }
        .btn-primary:hover {
            background-color: #0056b3;
            border-color: #0056b3;
        }
        .btn-success {
            background-color: #28a745;
            border-color: #28a745;
        }
        .btn-success:hover {
            background-color: #218838;
            border-color: #218838;
        }
        .btn-danger {
            background-color: #dc3545;
            border-color: #dc3545;
        }
        .btn-danger:hover {
            background-color: #c82333;
            border-color: #bd2130;
        }
        textarea {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #fff;
            resize: vertical;
        }
        textarea::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        .instructions {
            font-style: italic;
            margin-top: 10px;
            color: rgba(255, 255, 255, 0.8);
        }
        .emotion-display {
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 10px;
        }
        .emotion-display span {
            margin-right: 15px;
        }
        .emotion-display .intensity {
            font-size: 0.8em;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="text-center mb-4">Ora - Enhanced Admin Dashboard</h2>

        <div class="card">
            <div class="card-header">Speech Recognition & Emotion Analysis</div>
            <div class="card-body">
                <div class="form-group">
                    <label for="note-textarea">Your Conversation/Note:</label>
                    <textarea id="note-textarea" class="form-control" rows="6" placeholder="Start speaking or type your note here..."></textarea>
                </div>
                <div class="text-center">
                    <button id="start-record-btn" class="btn btn-primary mr-2"><i class="fas fa-microphone"></i> Start Recording</button>
                    <button id="pause-record-btn" class="btn btn-danger"><i class="fas fa-pause"></i> Stop Recording</button>
                    <button id="read-note-btn" class="btn btn-success ml-2"><i class="fas fa-volume-up"></i> Read Note</button>
                </div>
                <p id="recording-instructions" class="instructions text-center mt-3">Click "Start Recording" to begin.</p>
                <div id="emotion-output" class="emotion-display text-center mt-3">
                    <!-- Emotion analysis will appear here -->
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">AI Insights & Contextual Memory</div>
            <div class="card-body">
                <p>This section will display AI-generated insights, contextual memory recall, and family wellness patterns based on the recorded conversations.</p>
                <div id="ai-insights">
                    <!-- AI insights will be dynamically loaded here -->
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        $(document ).ready(function() {
            var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
            var recognition = new SpeechRecognition();

            // --- IMPORTANT: Suggested Settings ---
            recognition.continuous = true;   // Keep listening until explicitly stopped
            recognition.interimResults = true; // Get results as they come (optional, but good for UX)
            recognition.lang = 'en-US';      // Set the language (e.g., 'en-US', 'en-GB, 'es-ES')

            var noteTextarea = $('#note-textarea');
            var instructions = $('#recording-instructions');
            var emotionOutput = $('#emotion-output');
            var noteContent = '';

            // Function to simulate emotion analysis (replace with actual API call later)
            function analyzeEmotion(text) {
                if (!text.trim()) {
                    emotionOutput.html('');
                    return;
                }
                // Simple dummy analysis for demonstration
                let emotion = 'Neutral';
                let intensity = 0;
                if (text.toLowerCase().includes('happy') || text.toLowerCase().includes('joy')) {
                    emotion = 'Happy';
                    intensity = Math.floor(Math.random() * 3) + 7; // 7-9
                } else if (text.toLowerCase().includes('sad') || text.toLowerCase().includes('depressed')) {
                    emotion = 'Sad';
                    intensity = Math.floor(Math.random() * 3) + 7; // 7-9
                } else if (text.toLowerCase().includes('angry') || text.toLowerCase().includes('frustrated')) {
                    emotion = 'Angry';
                    intensity = Math.floor(Math.random() * 3) + 7; // 7-9
                } else if (text.toLowerCase().includes('stress') || text.toLowerCase().includes('anxious')) {
                    emotion = 'Anxious';
                    intensity = Math.floor(Math.random() * 3) + 7; // 7-9
                } else {
                    intensity = Math.floor(Math.random() * 5) + 1; // 1-5
                }
                emotionOutput.html(`<span>Emotion: ${emotion}</span> <span class="intensity">Intensity: ${intensity}/10</span>`);
            }

            /*-----------------------------
                  Speech Recognition
            -------------------------------*/

            recognition.onstart = function() {
                instructions.text('Voice recognition activated. Speak into the microphone.');
                emotionOutput.html(''); // Clear previous emotion
            };

            recognition.onspeechend = function() {
                // This event fires when speech stops. If continuous is true, recognition might still be active.
                // You might want to adjust this message or remove it if continuous is true.
                // instructions.text('You were quiet for a while. Recognition may have paused.');
                console.log('Speech has ended.');
            };

            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event); // Log the full event for debugging
                if (event.error == 'no-speech') {
                    instructions.text('No speech was detected. Please try again. Ensure your microphone is working and access is allowed.');
                } else if (event.error == 'audio-capture') {
                    instructions.text('No microphone was found. Ensure that a microphone is installed and that microphone access is enabled in your browser and OS settings.');
                } else if (event.error == 'not-allowed' || event.error == 'service-not-allowed') {
                    instructions.text('Microphone access was denied. Please allow microphone access in your browser settings and reload the page.');
                } else {
                    instructions.text('An error occurred during recognition: ' + event.error);
                }
            };

            recognition.onresult = function(event) {
                var current = event.resultIndex;
                var transcript = '';
                // Loop through all results to get the full transcript, including interim ones
                for (var i = current; i < event.results.length; ++i) {
                    // Only append final results to the noteContent
                    if (event.results[i].isFinal) {
                        transcript += event.results[i][0].transcript;
                    }
                    // You could also display interim results in a separate temporary area for real-time feedback
                }

                if (transcript) {
                    noteContent += transcript + ' '; // Add a space after each final transcript
                    noteTextarea.val(noteContent);
                    analyzeEmotion(noteContent); // Analyze emotion of the current note content
                }
            };

            /*-----------------------------
                  App buttons and input
            -------------------------------*/

            $('#start-record-btn').on('click', function(e) {
                if (noteTextarea.val()) {
                    noteContent = noteTextarea.val();
                    if (noteContent.slice(-1) !== ' ') { // Add space if last char isn't one
                         noteContent += ' ';
                    }
                } else {
                    noteContent = '';
                }
                recognition.start();
                instructions.text('Voice recognition started. Speak now.');
            });

            $('#pause-record-btn').on('click', function(e) {
                recognition.stop();
                instructions.text('Voice recognition paused.');
            });

            $('#read-note-btn').on('click', function(e) {
                var note = noteTextarea.val();
                if (note) {
                    var speech = new SpeechSynthesisUtterance();
                    speech.text = note;
                    speech.volume = 1;
                    speech.rate = 1;
                    speech.pitch = 1;
                    window.speechSynthesis.speak(speech);
                }
            });

            noteTextarea.on('input', function() {
                noteContent = $(this).val();
                analyzeEmotion(noteContent); // Analyze emotion as user types
            });
        });
    </script>
</body>
</html>
