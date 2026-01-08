const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const voiceBtn = document.getElementById('voice-btn');
const voiceOutputToggle = document.getElementById('voice-output-toggle');
const exercisesBtn = document.getElementById('exercises-btn');
const loading = document.getElementById('loading');
const emotionDisplay = document.getElementById('current-emotion');
const intensityFill = document.getElementById('intensity-fill');
const signoutBtn = document.getElementById('signout-btn');

const nameModal = document.getElementById('name-modal');
const nameInput = document.getElementById('name-input');
const nameSubmit = document.getElementById('name-submit');
const nameSkip = document.getElementById('name-skip');

const exercisesModal = document.getElementById('exercises-modal');
const closeExercises = document.getElementById('close-exercises');
const exercisesContainer = document.getElementById('exercises-container');

let isRecording = false;
let recognition = null;
let currentEmotion = 'neutral';
let userName = null;

// Show name modal on page load
window.addEventListener('load', () => {
    nameModal.classList.remove('hidden');
});

// Handle name submission
nameSubmit.addEventListener('click', async () => {
    const name = nameInput.value.trim();
    if (name) {
        try {
            const response = await fetch('/set-name', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await response.json();
            if (data.status === 'success') {
                userName = name;
                nameModal.classList.add('hidden');
                addMessage(data.message, 'bot');
            }
        } catch (error) {
            console.error('Error setting name:', error);
            nameModal.classList.add('hidden');
        }
    }
});

// Handle name skip
nameSkip.addEventListener('click', () => {
    nameModal.classList.add('hidden');
});

// Enter key for name input
nameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        nameSubmit.click();
    }
});

// Show exercises modal
exercisesBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/get-exercises', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emotion: currentEmotion })
        });
        const data = await response.json();
        if (data.status === 'success') {
            displayExercises(data.exercises, data.emotion);
            exercisesModal.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error fetching exercises:', error);
    }
});

// Close exercises modal
closeExercises.addEventListener('click', () => {
    exercisesModal.classList.add('hidden');
});

// Close modal when clicking outside
exercisesModal.addEventListener('click', (e) => {
    if (e.target === exercisesModal) {
        exercisesModal.classList.add('hidden');
    }
});

// Sign out functionality
signoutBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to sign out?')) {
        try {
            await fetch('/auth/signout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            window.location.href = '/';
        } catch (error) {
            console.error('Error signing out:', error);
            window.location.href = '/';
        }
    }
});

function displayExercises(exercises, emotion) {
    const emotionEmojis = {
        sadness: '😢',
        stress: '😰',
        anxiety: '😟',
        anger: '😠',
        happiness: '😊',
        neutral: '😌'
    };
    
    exercisesContainer.innerHTML = `
        <div class="exercise-section">
            <h3>${emotionEmojis[emotion] || '😌'} For ${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</h3>
        </div>
        
        <div class="exercise-section">
            <h4>🫁 Breathing Exercise</h4>
            <div class="exercise-card">
                <h5>${exercises.breathing.name}</h5>
                <p>${exercises.breathing.description}</p>
                <ol>
                    ${exercises.breathing.steps.map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
        </div>
        
        <div class="exercise-section">
            <h4>💭 Motivational Quote</h4>
            <div class="exercise-card quote-card">
                <p>"${exercises.quote}"</p>
            </div>
        </div>
        
        <div class="exercise-section">
            <h4>🎵 Relaxing Music</h4>
            <div class="exercise-card">
                <a href="${exercises.music}" target="_blank" class="music-link">
                    🎧 Listen to Calming Music
                </a>
            </div>
        </div>
        
        <div class="exercise-section">
            <h4>✨ Self-Care Tips</h4>
            <div class="exercise-card">
                <ul>
                    ${exercises.tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="red" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="8"></circle>
            </svg>
        `;
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    };
    
    recognition.onend = () => {
        isRecording = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
        `;
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isRecording = false;
        voiceBtn.classList.remove('recording');
    };
} else {
    voiceBtn.style.display = 'none';
    console.warn('Speech recognition not supported');
}

// Voice input button
voiceBtn?.addEventListener('click', () => {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser.');
        return;
    }
    
    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
    }
});

// Text-to-speech function
async function speakText(text) {
    if (!voiceOutputToggle.checked) return;
    
    try {
        // Try OpenAI TTS first
        const response = await fetch('/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        const contentType = response.headers.get('content-type');
        
        // Check if response is JSON (error/fallback) or audio
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            if (data.fallback) {
                // Silently fall back to browser speech
                console.log('TTS unavailable:', data.message);
                useBrowserSpeech(text);
                return;
            }
            throw new Error(data.error || 'Failed to generate speech');
        }
        
        if (!response.ok) {
            throw new Error('Failed to generate speech');
        }
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play();
        
        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
        };
    } catch (error) {
        console.error('OpenAI TTS failed, falling back to browser speech:', error);
        // Fallback to browser's built-in text-to-speech
        useBrowserSpeech(text);
    }
}

function useBrowserSpeech(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Configure voice settings
        utterance.rate = 0.9;  // Slightly slower for clarity
        utterance.pitch = 1;   // Normal pitch
        utterance.volume = 1;  // Full volume
        
        // Try to use a more natural voice if available
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice => 
            voice.name.includes('Google') || 
            voice.name.includes('Microsoft') ||
            voice.lang.startsWith('en')
        );
        
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('Speech synthesis not supported in this browser');
    }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';
    
    sendBtn.disabled = true;
    loading.classList.remove('hidden');
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        addMessage(data.response, 'bot', data.sentiment.emotions);
        
        updateEmotionDisplay(data.sentiment.emotions);
        
        // Speak the bot's response
        speakText(data.response);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('I apologize, but I encountered an error. Please try again.', 'bot');
    } finally {
        loading.classList.add('hidden');
        sendBtn.disabled = false;
        userInput.focus();
    }
});

userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

clearBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear the conversation?')) {
        try {
            await fetch('/clear', { method: 'POST' });
            
            chatMessages.innerHTML = `
                <div class="bot-message">
                    <div class="message-bubble bot">
                        <p>Hello! I'm here to listen and support you. How are you feeling today?</p>
                        <span class="timestamp">Just now</span>
                    </div>
                </div>
            `;
            
            emotionDisplay.textContent = 'Neutral';
            intensityFill.style.width = '50%';
        } catch (error) {
            console.error('Error clearing conversation:', error);
        }
    }
});

function addMessage(text, sender, emotions = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let emotionTag = '';
    if (sender === 'user' && emotions) {
        const emotionClass = `emotion-${emotions.primary.toLowerCase()}`;
        emotionTag = `<span class="emotion-tag ${emotionClass}">${emotions.primary} (${emotions.intensity}/10)</span>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-bubble ${sender}">
            <p>${escapeHtml(text)}</p>
            ${emotionTag}
            <span class="timestamp">${timestamp}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateEmotionDisplay(emotions) {
    currentEmotion = emotions.primary.toLowerCase();
    emotionDisplay.textContent = emotions.primary;
    emotionDisplay.className = `emotion-value emotion-${emotions.primary.toLowerCase()}`;
    
    const intensityPercent = (emotions.intensity / 10) * 100;
    intensityFill.style.width = `${intensityPercent}%`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

userInput.focus();
