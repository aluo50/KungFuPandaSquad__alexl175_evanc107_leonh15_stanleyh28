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
from database import save_blackjack, load_blackjack, update_balance, login_user, add_user, get_user, add_blackjack_user
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
        user_info = database.get_user(session["username"])
        balance = user_info["balance"]
        session['balance'] = balance
        return render_template("home.html", username=session["username"], balance=balance)
    else:
        return render_template("home.html", username=None, balance=None)

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
    
# blackjack game
@app.route("/blackjack", methods=["GET"])
def play_blackjack():
    if "username" in session: 
        user_info = get_user(session["username"])
        user_id = user_info['user_id']

        result = load_blackjack(user_id)

        if result != None:
            session['bet'] = result['bet']
            session['balance'] -= session['bet']
            player_hand = result['player_hand']
            dealer_hand = result['dealer_hand']
            session['player_hand'] = player_hand
            session['dealer_hand'] = dealer_hand
            game_over = result['game_over']
            cards = [i for i in range(52)]
            for card in player_hand:
                cards.remove(card)
            for card in dealer_hand:
                cards.remove(card)
            session['deck'] = cards
            flash('Resumed game!','success')
        
        else:
            initialize_game(bet)
            add_blackjack_user(user_id)
            save_blackjack(user_id, 100, session['player_hand'],session['dealer_hand'], 0)
            game_over = False
    else:
        flash('Login to play!', 'error')
        return redirect(url_for("home"))
    
    # Retrieve the current hands from session
    player_cards = session.get("player_hand", [])
    dealer_cards = session.get("dealer_hand", [])
    
    return render_template(
        "blackjack.html",
        player_cards=player_cards,
        dealer_cards=dealer_cards,
        game_over=game_over
    )

# hit
@app.route("/hit", methods=["POST"])
def hit():
    player_hit()
    new_card = session["player_hand"][-1]  # the newly drawn card
    
    user_id = get_user(session['username'])['user_id']
    
    save_blackjack(user_id, session['bet'], session['player_hand'], session['dealer_hand'], 0)

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
    
    user_id = get_user(session['username'])['user_id']
    
    save_blackjack(user_id, 100, session['player_hand'],session['dealer_hand'], 1)

    return jsonify({
        "dealer_hand": session["dealer_hand"],  # the final dealer hand
        "result": result
    })

@app.route("/double_down", methods=["POST"])
def double_down_route():
    balance = session['balance']
    if session['bet'] > balance:
        # fix flash
        flash("You don't have enough money to double down!", 'error')
        return jsonify({
            "new_card": False
        })
    else:
        session['balance'] -= session['bet']
        session['bet'] *= 2
        double_down()
        result = determine_winner()
        new_card = session["player_hand"][-1]
        
        user_id = get_user(session['username'])['user_id']
        
        save_blackjack(user_id, session['bet'], session['player_hand'],session['dealer_hand'], 1)

        return jsonify({
            "new_card": new_card,
            "result": result
        })

# resets blackjack, starts new round
@app.route("/play_again", methods=["POST"])
def play_again():
    initialize_game(100)
    session.modified = True

    if 'username' in session:
        user_id = get_user(session['username'])['user_id']
        save_blackjack(user_id, 100, session['player_hand'],session['dealer_hand'], 0)

    return jsonify({
        "player_cards": session["player_hand"],
        "dealer_cards": session["dealer_hand"]
    })

@app.route("/plinko")
def plinko():
    if "username" not in session:
        flash("Login to play Plinko!", "error")
        return redirect(url_for("login"))
    return render_template("plinko.html")

if __name__ == "__main__":
    app.run(debug=True)
