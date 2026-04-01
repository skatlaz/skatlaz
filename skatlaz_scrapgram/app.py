import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from skatlaz_scrapgram.routes import users, chat, groups, forum, files, giphy
from skatlaz_scrapgram.admin.routes import bp as admin_bp
from skatlaz_scrapgram.websocket import socketio, init_socket
from skatlaz_scrapgram.config import Config

app = Flask(__name__)
app.config["SECRET_KEY"] = "skatlaz"
app.config.from_object(Config)

app.register_blueprint(users.bp)
app.register_blueprint(chat.bp)
app.register_blueprint(groups.bp)
app.register_blueprint(forum.bp)
app.register_blueprint(files.bp)
app.register_blueprint(giphy.bp)
app.register_blueprint(admin_bp)

init_socket(app)

if __name__ == "__main__":
    # Usar porta 5001 em vez de 5000
    socketio.run(app, debug=True, port=5001)
