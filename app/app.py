from flask import Blueprint, Flask, render_template, jsonify, request, redirect, url_for
from flask_prometheus_metrics import register_metrics
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, func
import logging
import time

# Prometheus metrics
REQUEST_COUNTER = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# Logging configuration
logging.basicConfig(filename='/app-log/app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

CONFIG = {"version": "v0.1.2", "config": "staging"}
MAIN = Blueprint("main", __name__)

# Initialize SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comments.db'
db = SQLAlchemy(app)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()

def get_comments():
    return Comment.query.order_by(Comment.id.desc()).all()   

@MAIN.route("/", methods=['GET', 'POST'])
def index():
    start_time = time.time()  # Record start time for latency calculation
    
    if request.method == 'POST':
        text = request.form.get('comment_text')
        if text:
            new_comment = Comment(text=text)
            db.session.add(new_comment)
            db.session.commit()
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            logging.info(f'|flask-app|Comment added for game: {text}|{elapsed_time:.5f}|{request.user_agent.string}|Comment')
            comments = get_comments()
            return jsonify({"success": True, "comments": [comment.text for comment in comments]})
        return jsonify({"success": False})

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    logging.info(f'|flask-app|Index page displayed|{elapsed_time:.5f}|{request.user_agent.string}|Index')
    comments = get_comments()
    main_page_image_url = "https://clubrunner.blob.core.windows.net/00000001374/Images/Game_Night_Logo_Color.png"
    return render_template('index.html', comments=comments, main_page_image_url=main_page_image_url)

@MAIN.route("/scrabble")
def scrabble():
    start_time = time.time()  # Record start time for latency calculation
    logging.info('|flask-app|Scrabble information requested|{:.5f}|{}|{}|'.format(time.time() - start_time, request.user_agent.string,"Scrabble"))
    game_data = {
        "description": "Scrabble is a word game in which two to four players score points by placing tiles, each bearing a single letter, onto a game board divided into a 15×15 grid of squares. The tiles must form words that, in crossword fashion, read left to right in rows or downward in columns and are included in a standard dictionary or lexicon.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Scrabble_game_in_progress.jpg"
    }
    return jsonify(game_data)

@MAIN.route("/monopoly")
def monopoly():
    start_time = time.time()  # Record start time for latency calculation
    logging.info('|flask-app|Monopoly information requested|{:.5f}|{}|{}|'.format(time.time() - start_time, request.user_agent.string,"Monopoly"))
    game_data = {
        "description": "Monopoly is a multiplayer economics-themed board game. In the game, players roll two dice to move around the game board, buying and trading properties and developing them with houses and hotels.",
        "image_url": "https://miro.medium.com/v2/resize:fit:1400/0*BaQs4MaCPgxibQdE.jpg"
    }
    return jsonify(game_data)

@MAIN.route("/uno")
def uno():
    start_time = time.time()  # Record start time for latency calculation
    logging.info('|flask-app|UNO information requested|{:.5f}|{}|{}|'.format(time.time() - start_time, request.user_agent.string, "UNO"))
    game_data = {
        "description": "Uno (/ˈuːnoʊ/; from Spanish and Italian for 'one'), stylized as UNO, is a proprietary American shedding-type card game originally developed in 1971 by Merle Robbins.",
        "image_url": "https://omsapts.com/wp-content/uploads/2022/03/spicy-uno-for-game-night.jpg"
    }
    return jsonify(game_data)

@MAIN.route("/rummy")
def rummy():
    start_time = time.time()  # Record start time for latency calculation
    logging.info('|flask-app|Rummy information requested|{:.5f}|{}|{}|'.format(time.time() - start_time, request.user_agent.string,"Rummy"))
    game_data = {
        "description": "fRummy is a tile-based game for 2 to 4 players, combining elements of the card game rummy and mahjong. There are 106 tiles in the game, including 104 numbered tiles (valued 1 to 13 in four different colors, two copies of each) and two jokers.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Rummikub_Tiles.jpg/1200px-Rummikub_Tiles.jpg"
    }
    return jsonify(game_data)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    start_time = time.time()  # Record start time for latency calculation
    text = request.form.get('comment_text')
    if text:
        new_comment = Comment(text=text)
        db.session.add(new_comment)
        db.session.commit()
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        logging.info(f'|flask app|Comment added for game:{text}|{elapsed_time:.5f}|{request.user_agent.string}|Comment|')
        comments = get_comments()
        return jsonify({"success": True, "comments": [comment.text for comment in comments]})
    return jsonify({"success": False})
def register_blueprints(app):
    app.register_blueprint(MAIN)

def create_app(config):  
    register_blueprints(app)
    register_metrics(app, app_version=config["version"], app_config=config["config"])
    return app

def create_dispatcher() -> DispatcherMiddleware:
    main_app = create_app(config=CONFIG)
    return DispatcherMiddleware(main_app.wsgi_app, {"/metrics": make_wsgi_app()})

if __name__ == "__main__":
    run_simple(
        "0.0.0.0",
        5000,
        create_dispatcher(),
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
    )