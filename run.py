from app import create_app, socketio
import os

app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 80))
    socketio.run(app, debug=app.config['DEBUG'], host=host, port=port, allow_unsafe_werkzeug=True)