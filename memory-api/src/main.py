import os
import sys
import sqlite3
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from src.routes.memory import memory_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'ora-memory-secret-key-2024'

# Register memory routes
app.register_blueprint(memory_bp, url_prefix='/api/memory')

# [Rest of the code I provided earlier]

