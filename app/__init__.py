# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import sqlite3
import os
import database
import json
from database import save_blackjack, load_blackjack, update_balance, login_user, add_user
from games.blackjack import (
    calculate_hand_value,
    initialize_game,
    player_hit,
    dealer_play,
    determine_winner,
    double_down,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)

database.create_db()

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    if "username" in session:
        user_info = database.return_user(session["username"])
        balance = user_info["balance"]
        conn = database.get_db_connection()
        cur=conn.cursor()
        cur.execute("SELECT game_id, game_type, status FROM game WHERE user_id=? AND status='in-progress'",
        (user_info["user_id"],))
        saved_games = cur.fetchall()
        conn.close()
        return render_template("home.html", username=session["username"], balance=balance, saved_games=saved_games)
    else:
        return render_template("home.html", username=None, balance=None, saved_games=[])

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        database.login_user()
        if "username" in session:
            return redirect(url_for("home"))
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    if "username" in session:
        user = session.pop("username")
        flash(f"{user}, you have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        database.add_user()
        if "username" in session:
            return redirect(url_for("home"))
        return redirect(url_for("register"))
    return render_template("login.html")

@app.route("/resume_game", methods=["POST"])
def resume_game():
    game_id = request.form.get("game_id")
    blackjack_state = database.load_blackjack(game_id)

    if blackjack_state:
        session['db_game_id'] = game_id
        session['deck'] = blackjack_state['deck']
        session['player_hand'] = blackjack_state['player_hand']
        session['dealer_hand'] = blackjack_state['dealer_hand']

        flash("Resumed saved game", "info")
        return redirect(url_for("play_blackjack"))
    else:
        flash("couldn't find selected game")
        return redirect(url_for("home"))
    

# blackjack game
@app.route("/blackjack", methods=["GET"])
def play_blackjack():
    if "username" in session: 
        from database import load_blackjack, create_blackjack, save_blackjack
        user_info = database.return_user(session["username"])
        user_id = user_info['user_id']

        conn = database.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT game_id FROM game WHERE user_id=? AND game_type ='blackjack' AND status='in-progress' ORDER BY game_id DESC LIMIT 1",
        (user_id,))
        existing_game = cur.fetchone()
        conn.close()

        if existing_game:
            game_id = existing_game['game_id']
            session['db_game_id'] = game_id 
            blackjack_state=load_blackjack(game_id)

            session['deck'] = blackjack_state['deck']
            session['player_hand'] = blackjack_state['player_hand']
            session['dealer_hand'] = blackjack_state['dealer_hand']
        
        else:
            game_id = create_blackjack(user_id)
            session['db_game_id'] = game_id
            initialize_game()
            save_blackjack(game_id, session['deck'], session['player_hand'],session['dealer_hand'],0)
    else:
        flash('Login to play!', 'error')
        print(True)
#         return redirect(url_for("home"))
    # Initialize if no deck in session
    if "deck" not in session:
        initialize_game()
    
    # Retrieve the current hands from session
    player_cards = session.get("player_hand", [])
    dealer_cards = session.get("dealer_hand", [])
    
    player_score = calculate_hand_value(session["player_hand"])
    dealer_score = calculate_hand_value([session["dealer_hand"][0]])
    
    if player_score == 21:
        stand()
    return render_template(
        "blackjack.html",
        player_cards=player_cards,
        dealer_cards=dealer_cards,
        dealer_score=dealer_score,
        player_score=player_score
    )

# hit
@app.route("/hit", methods=["POST"])
def hit():
    """
    Player requests a hit.
    The server draws one card for the player (player_hit),
    returns the new card so front end can animate it.
    """
    player_hit()
    new_card = session["player_hand"][-1]  # the newly drawn card

    # Check if the player busted
    player_value = calculate_hand_value(session["player_hand"])
    result = None
    if player_value == 21:
        stand()
    elif player_value > 21:
        # If busted, figure out if lose or tie, etc.
        result = determine_winner()

    return jsonify({
        "new_card": new_card,
        "result": result
    })

# stand
@app.route("/stand", methods=["POST"])
def stand():
    dealer_play()
    result = determine_winner()

    return jsonify({
        "dealer_hand": session["dealer_hand"],  # the final dealer hand
        "result": result
    })

@app.route("/double_down", methods=["POST"])
def double_down_route():
    double_down()
    result = determine_winner()
    new_card = session["player_hand"][-1]

    return jsonify({
        "new_card": new_card,
        "result": result
    })

# resets blackjack, starts new round
@app.route("/play_again", methods=["POST"])
def play_again():
    initialize_game()
    session.modified = True

    if 'username' in session and 'db_game_id' in session:
        from database import save_blackjack
        game_id = session['db_game_id']
        save_blackjack(game_id, session['deck'], session['player_hand'],session['dealer_hand'],0)

    return jsonify({
        "player_cards": session["player_hand"],
        "dealer_cards": session["dealer_hand"]
    })

if __name__ == "__main__":
    app.run(debug=True)
