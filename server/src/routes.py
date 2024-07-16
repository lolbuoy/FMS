from app import app

@app.route('/')
def index():
    print(app.config)
    return 'Hello, Flask-SocketIO!'
