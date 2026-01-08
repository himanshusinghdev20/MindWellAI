import os
import sys
from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
from datetime import datetime
import secrets
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET') or secrets.token_hex(16)

# Enable error logging
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

client = OpenAI()

conversation_store = {}
user_names = {}
# Simple in-memory user database (in production, use a real database)
users_db = {}

# Emotion-based exercises and suggestions
EMOTION_EXERCISES = {
    'sadness': {
        'breathing': {
            'name': '4-7-8 Breathing',
            'description': 'Breathe in for 4 counts, hold for 7, exhale for 8. Repeat 4 times.',
            'steps': ['Sit comfortably', 'Inhale through nose (4 counts)', 'Hold breath (7 counts)', 'Exhale through mouth (8 counts)', 'Repeat 3 more times']
        },
        'quote': 'Every storm runs out of rain. This feeling is temporary, and brighter days are ahead.',
        'music': 'https://www.youtube.com/watch?v=1ZYbU82GVz4',
        'tips': ['Reach out to a friend or loved one', 'Write down three things you\'re grateful for', 'Take a gentle walk outside', 'Allow yourself to feel without judgment']
    },
    'stress': {
        'breathing': {
            'name': 'Box Breathing',
            'description': 'Equal counts of breathing in, holding, breathing out, and holding.',
            'steps': ['Breathe in (4 counts)', 'Hold (4 counts)', 'Breathe out (4 counts)', 'Hold (4 counts)', 'Repeat for 5 minutes']
        },
        'quote': 'You are stronger than you think. Take it one step at a time.',
        'music': 'https://www.youtube.com/watch?v=lFcSrYw-ARY',
        'tips': ['Break tasks into smaller steps', 'Practice the 5-4-3-2-1 grounding technique', 'Take regular breaks', 'Prioritize sleep and hydration']
    },
    'anxiety': {
        'breathing': {
            'name': 'Diaphragmatic Breathing',
            'description': 'Deep belly breathing to activate the relaxation response.',
            'steps': ['Place hand on belly', 'Breathe deeply into belly', 'Feel belly rise and fall', 'Breathe slowly for 5 minutes', 'Focus on the rhythm']
        },
        'quote': 'This too shall pass. You have survived 100% of your worst days.',
        'music': 'https://www.youtube.com/watch?v=z6X5oEIg6Ak',
        'tips': ['Use the 5-4-3-2-1 sensory technique', 'Challenge anxious thoughts', 'Practice progressive muscle relaxation', 'Limit caffeine intake']
    },
    'anger': {
        'breathing': {
            'name': 'Cooling Breath',
            'description': 'Calming technique to reduce anger and tension.',
            'steps': ['Breathe in deeply through nose', 'Hold for 3 counts', 'Exhale slowly through mouth', 'Visualize tension leaving', 'Repeat 10 times']
        },
        'quote': 'Between stimulus and response there is a space. In that space is your power to choose.',
        'music': 'https://www.youtube.com/watch?v=UfcAVejslrU',
        'tips': ['Take a timeout before responding', 'Express feelings with "I" statements', 'Physical activity to release energy', 'Practice counting to 10']
    },
    'happiness': {
        'breathing': {
            'name': 'Energizing Breath',
            'description': 'Breathing exercise to maintain and enhance positive energy.',
            'steps': ['Stand tall', 'Take quick, energizing breaths', 'Raise arms overhead', 'Feel the positive energy', 'Smile and breathe']
        },
        'quote': 'Joy is not in things; it is in us. Keep nurturing this beautiful feeling!',
        'music': 'https://www.youtube.com/watch?v=ZbZSe6N_BXs',
        'tips': ['Share your joy with others', 'Document this moment in a journal', 'Practice gratitude', 'Engage in activities you love']
    },
    'neutral': {
        'breathing': {
            'name': 'Mindful Breathing',
            'description': 'Simple awareness of breath for presence and calm.',
            'steps': ['Sit comfortably', 'Focus on your natural breath', 'Notice inhale and exhale', 'If mind wanders, gently return', 'Continue for 5 minutes']
        },
        'quote': 'Peace comes from within. Take time to nurture your inner calm.',
        'music': 'https://www.youtube.com/watch?v=jPpUNAFHgxM',
        'tips': ['Practice mindfulness meditation', 'Maintain healthy routines', 'Connect with nature', 'Stay hydrated and eat well']
    }
}

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    error_trace = traceback.format_exc()
    print(f"\n\n===== ERROR =====\n{error_trace}\n================\n", flush=True)
    app.logger.error(f"Exception occurred: {e}\n{error_trace}")
    return f"Error: {str(e)}\n\n{error_trace}", 500

@app.route('/favicon.ico')
def favicon():
    """Serve favicon to prevent 404 errors"""
    return '', 204

@app.route('/')
def landing():
    """Landing page with sign in/sign up"""
    return render_template('landing.html')

@app.route('/chat')
def index():
    """Main chat interface"""
    try:
        print(f"Chat route called")
        print(f"App secret key exists: {bool(app.secret_key)}")
        print(f"Session before: {dict(session)}")
        
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            print(f"Created new session_id: {session['session_id']}")
        
        if session['session_id'] not in conversation_store:
            conversation_store[session['session_id']] = []
        
        if session['session_id'] not in user_names:
            user_names[session['session_id']] = None
        
        print(f"About to render template")
        return render_template('index.html')
    except Exception as e:
        print(f"ERROR in chat route: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.route('/auth/signup', methods=['POST'])
def signup():
    """Handle user sign up"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not name or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Store user (in production, hash the password!)
        user_id = str(uuid.uuid4())
        users_db[email] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': password  # In production, use hashing!
        }
        
        # Create session
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['session_id'] = str(uuid.uuid4())
        
        # Initialize user data
        user_names[session['session_id']] = name
        conversation_store[session['session_id']] = []
        
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully',
            'user': {'name': name, 'email': email}
        })
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return jsonify({'error': 'Sign up failed'}), 500

@app.route('/auth/signin', methods=['POST'])
def signin():
    """Handle user sign in"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check credentials
        user = users_db.get(email)
        if not user or user['password'] != password:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create session
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['name']
        session['session_id'] = str(uuid.uuid4())
        
        # Initialize user data
        user_names[session['session_id']] = user['name']
        if session['session_id'] not in conversation_store:
            conversation_store[session['session_id']] = []
        
        return jsonify({
            'status': 'success',
            'message': 'Signed in successfully',
            'user': {'name': user['name'], 'email': user['email']}
        })
    except Exception as e:
        print(f"Error in signin: {str(e)}")
        return jsonify({'error': 'Sign in failed'}), 500

@app.route('/auth/signout', methods=['POST'])
def signout():
    """Handle user sign out"""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Signed out successfully'})

@app.route('/set-name', methods=['POST'])
def set_name():
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        user_names[session_id] = name
        
        return jsonify({
            'status': 'success',
            'message': f'Nice to meet you, {name}! How can I support you today?'
        })
    except Exception as e:
        print(f"Error setting name: {str(e)}")
        return jsonify({'error': 'Failed to set name'}), 500

@app.route('/get-exercises', methods=['POST'])
def get_exercises():
    try:
        data = request.json
        emotion = data.get('emotion', 'neutral').lower()
        
        exercises = EMOTION_EXERCISES.get(emotion, EMOTION_EXERCISES['neutral'])
        
        return jsonify({
            'status': 'success',
            'emotion': emotion,
            'exercises': exercises
        })
    except Exception as e:
        print(f"Error getting exercises: {str(e)}")
        return jsonify({'error': 'Failed to get exercises'}), 500

@app.route('/analyze', methods=['POST'])
def analyze_message():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'Invalid request'}), 400
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        if session_id not in conversation_store:
            conversation_store[session_id] = []
        
        conversation_history = conversation_store[session_id]
        user_name = user_names.get(session_id)
        
        sentiment_result = analyze_sentiment(user_message, conversation_history)
        
        bot_response = generate_empathetic_response(
            user_message, 
            sentiment_result, 
            conversation_history,
            user_name
        )
        
        conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'emotions': sentiment_result['emotions']
        })
        conversation_history.append({
            'role': 'assistant',
            'content': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(conversation_history) > 20:
            conversation_store[session_id] = conversation_history[-20:]
        
        return jsonify({
            'response': bot_response,
            'sentiment': sentiment_result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error in analyze_message: {str(e)}")
        return jsonify({'error': 'An error occurred processing your message'}), 500

def analyze_sentiment(message, conversation_history):
    try:
        system_prompt = """You are an expert emotional intelligence AI that analyzes text to detect emotional states.
        
Analyze the given message and provide:
1. Primary emotion (sadness, stress, anger, anxiety, happiness, neutral)
2. Intensity level (low: 1-3, medium: 4-6, high: 7-10)
3. Secondary emotions if present
4. Brief emotional context

Respond in this exact JSON format:
{
  "primary_emotion": "emotion_name",
  "intensity": 7,
  "secondary_emotions": ["emotion1", "emotion2"],
  "context": "brief explanation"
}"""

        context = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]
            context = "\n\nRecent conversation context:\n"
            for msg in recent_messages:
                role = "User" if msg['role'] == 'user' else "Bot"
                context += f"{role}: {msg['content']}\n"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this message:{context}\n\nCurrent message: {message}"}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content in response")
        sentiment_data = json.loads(content)
        
        return {
            'emotions': {
                'primary': sentiment_data.get('primary_emotion', 'neutral'),
                'intensity': sentiment_data.get('intensity', 5),
                'secondary': sentiment_data.get('secondary_emotions', [])
            },
            'context': sentiment_data.get('context', '')
        }
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error in sentiment analysis: {error_msg}")
        
        # Provide more specific fallback context
        if 'connection' in error_msg.lower() or 'getaddrinfo' in error_msg.lower():
            context = 'Network connection issue - using neutral sentiment'
        elif 'quota' in error_msg.lower() or '429' in error_msg:
            context = 'API quota exceeded - using neutral sentiment'
        else:
            context = 'Unable to analyze sentiment'
        
        return {
            'emotions': {
                'primary': 'neutral',
                'intensity': 5,
                'secondary': []
            },
            'context': context
        }

def generate_empathetic_response(user_message, sentiment_result, conversation_history, user_name=None):
    try:
        primary_emotion = sentiment_result['emotions']['primary']
        intensity = sentiment_result['emotions']['intensity']
        
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'want to die', 'no reason to live']
        is_crisis = any(keyword in user_message.lower() for keyword in crisis_keywords)
        
        name_prefix = f"{user_name}, " if user_name else ""
        
        if is_crisis or (primary_emotion in ['sadness', 'anxiety'] and intensity >= 8):
            crisis_message = f"""{name_prefix}I'm really concerned about what you're sharing with me. Your feelings are valid, but I want you to know that help is available:

🆘 **Crisis Resources:**
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

Please reach out to a mental health professional or one of these crisis services. You don't have to face this alone."""
            return crisis_message
        
        emotion_guidelines = {
            'sadness': 'Be gentle, validating, and offer comfort. Acknowledge their pain without minimizing it.',
            'stress': 'Be calming and supportive. Offer perspective and coping strategies.',
            'anger': 'Be understanding and non-judgmental. Help them process their feelings constructively.',
            'anxiety': 'Be reassuring and grounding. Help them feel safe and heard.',
            'happiness': 'Share in their joy genuinely. Reinforce positive feelings.',
            'neutral': 'Be warm and conversational. Listen actively and be supportive.'
        }
        
        guideline = emotion_guidelines.get(primary_emotion, emotion_guidelines['neutral'])
        
        name_context = f"\nUser's name: {user_name} (use their name occasionally to make responses more personal)" if user_name else ""
        
        system_prompt = f"""You are a compassionate mental health support chatbot. Your role is to provide emotional support, active listening, and empathy.

Current emotional state: {primary_emotion} (intensity: {intensity}/10)
Guidance: {guideline}{name_context}

Important guidelines:
- Show genuine empathy and understanding
- Validate their feelings without judgment
- Ask thoughtful follow-up questions when appropriate
- Offer gentle coping suggestions if relevant
- Be warm, supportive, and human-like
- Keep responses conversational and natural (2-4 sentences typically)
- Never diagnose or replace professional therapy
- If they're in crisis, direct them to professional resources
- Use the user's name occasionally (if provided) to make the conversation more personal

Respond in a caring, supportive way that addresses their emotional needs."""

        from typing import cast
        from openai.types.chat import ChatCompletionMessageParam
        
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append(cast(ChatCompletionMessageParam, {
                    "role": msg['role'],
                    "content": msg['content']
                }))
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content in response")
        return content.strip()
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating response: {error_msg}")
        
        # Provide more specific fallback based on error type
        if 'connection' in error_msg.lower() or 'getaddrinfo' in error_msg.lower():
            return "I'm experiencing connection issues, but I'm here to support you. Please check your internet connection and try again."
        elif 'quota' in error_msg.lower() or '429' in error_msg:
            return "I'm currently unavailable due to service limits. Please try again in a few moments."
        
        return "I'm here to listen and support you. Could you tell me more about how you're feeling?"

@app.route('/clear', methods=['POST'])
def clear_conversation():
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in conversation_store:
            conversation_store[session_id] = []
    return jsonify({'status': 'success'})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Use OpenAI's text-to-speech API
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Warm, empathetic voice
            input=text
        )
        
        # Stream the audio response
        from flask import Response
        import io
        
        audio_data = io.BytesIO()
        for chunk in response.iter_bytes():
            audio_data.write(chunk)
        audio_data.seek(0)
        
        return Response(audio_data.read(), mimetype='audio/mpeg')
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error in text-to-speech: {error_msg}")
        
        # Check for specific error types
        if 'quota' in error_msg.lower() or '429' in error_msg:
            return jsonify({
                'error': 'Text-to-speech quota exceeded',
                'fallback': True,
                'message': 'Using browser voice instead'
            }), 200
        elif 'connection' in error_msg.lower() or 'getaddrinfo' in error_msg.lower():
            return jsonify({
                'error': 'Network connection issue',
                'fallback': True,
                'message': 'Using browser voice instead'
            }), 200
        
        return jsonify({
            'error': 'Text-to-speech unavailable',
            'fallback': True,
            'message': 'Using browser voice instead'
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
