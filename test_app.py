from flask import Flask
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    print("Starting minimal Flask app...")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
