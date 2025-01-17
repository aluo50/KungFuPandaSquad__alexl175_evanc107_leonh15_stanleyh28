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
from database import save_blackjack, load_blackjack, update_balance, login_user, add_user, get_user, add_blackjack_user, get_leaderboard, get_transaction_history
from games.blackjack import (
    calculate_hand_value,
    initialize_game,
    player_hit,
    dealer_play,
    determine_winner
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

        transactions = get_transaction_history(user_info["user_id"])

        return render_template("home.html", username=session["username"], balance=balance, transactions=transactions)
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

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if "username" in session:
        user = session.pop("username")
        flash(f"{user}, you have been logged out.", "success")
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
            player_hand = result['player_hand']
            dealer_hand = result['dealer_hand']
            session['player_hand'] = player_hand
            session['dealer_hand'] = dealer_hand
            game_over = result['game_over']
            if game_over == True:
                session['balance'] = get_user(session['username'])['balance']
            else:
                session['balance'] = get_user(session['username'])['balance'] - session['bet']
            cards = [i for i in range(52)]
            for card in player_hand:
                cards.remove(card)
            for card in dealer_hand:
                cards.remove(card)
            session['deck'] = cards
            flash('Resumed game!','success')
            # Retrieve the current hands from session
            player_cards = session.get("player_hand", [])
            dealer_cards = session.get("dealer_hand", [])

            return render_template(
                "blackjack.html",
                body_class="blackjack-body",
                player_cards=player_cards,
                dealer_cards=dealer_cards,
                game_over=game_over,
                username=session["username"],
                balance=session["balance"],
                bet=session["bet"]
            )
        
        else:
            add_blackjack_user(user_id)

            return render_template(
                "blackjack.html",
                body_class="blackjack-body",
                player_cards=[],
                dealer_cards=[],
                game_over=0,
                username=session["username"],
                balance=session["balance"],
                bet=0
            )
    else:
        flash('Login to play!', 'error')
        return redirect(url_for("home"))

# Hit route
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

# Stand route
@app.route("/stand", methods=["POST"])
def stand():
    dealer_play()
    result = determine_winner()
    
    user_id = get_user(session['username'])['user_id']

    save_blackjack(user_id, session['bet'], session['player_hand'],session['dealer_hand'], 1)

    return jsonify({
        "dealer_hand": session["dealer_hand"],  # the final dealer hand
        "result": result,
        "amount": session["bet"]
    })

# Double down route
@app.route("/double_down", methods=["POST"])
def double_down_route():
    balance = session['balance']
    if session['bet'] > balance:
        # fix flash
        msg = "You don't have enough money to double down!"
        return jsonify({
            "new_card": False,
            "message": msg
        })
    else:
        session['balance'] -= session['bet']
        session['bet'] *= 2
        player_hit()
        new_card = session["player_hand"][-1]
        
        session.modified = True
        
        user_id = get_user(session['username'])['user_id']
        
        save_blackjack(user_id, session['bet'], session['player_hand'],session['dealer_hand'], 1)

        return jsonify({
            "new_card": new_card,
            "amount": -session["bet"]//2,
            "bet": session["bet"]
        })

# Sets the bet amount
@app.route("/set_bet", methods=["POST"])
def set_bet():
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in."}), 403

    bet = int(request.form["bet"])
    user_info = get_user(session['username'])
    current_balance = user_info['balance']

    if bet > current_balance:
        return jsonify({"success": False, "message": "Insufficient balance."})

    initialize_game(bet)
    session.modified = True

    if 'username' in session:
        user_id = get_user(session['username'])['user_id']
        save_blackjack(user_id, bet, session['player_hand'], session['dealer_hand'], 0)

    return jsonify({
        "success": True, 
        "message": f"Bet set at {session['bet']}!",
        "player_cards": session["player_hand"],
        "dealer_cards": session["dealer_hand"],
        "amount": -session["bet"],
        "bet": session["bet"]
    })

@app.route("/plinko")
def plinko():
    if "username" not in session:
        flash("Login to play Plinko!", "error")
        return redirect(url_for("login"))

    user_info = get_user(session["username"])
    balance = user_info["balance"]
    session["balance"] = balance 

    return render_template("plinko.html",username=session["username"], balance=balance)
    
@app.route("/plinko_drop", methods=["POST"])
def plinko_drop():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = get_user(session['username'])['user_id']
    bet_amount = 50
    new_balance = update_balance(user_id, "plinko", -bet_amount)
    session["balance"] = new_balance

    return jsonify({"message": "dropped ball", "balance": new_balance})

@app.route("/plinko_result", methods=["POST"])
def plinko_result():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    #data=request.json
    multiplier_str = request.form.get("multiplier", "1.0")  
    multiplier = float(multiplier_str)

    user_id = get_user(session['username'])['user_id']

    bet_amount = 50
    winnings = int(bet_amount * float(multiplier))

    new_balance = update_balance(user_id,"plinko", winnings)
    session["balance"] = new_balance

    return jsonify({"balance":new_balance, "winnings":winnings})


@app.route("/mines")
def mines():
    if "username" not in session:
        flash("Login to play Mines!", "error")
        return redirect(url_for("login"))

    user_info = get_user(session["username"])
    balance = user_info["balance"]
    session["balance"] = balance 

    bet_amount = 50
    
    if 'accumulated' not in session:
        session['accumulated'] = 0

    return render_template("mines.html",username=session["username"], balance=balance, bet=bet_amount, accumulated=session['accumulated'])

@app.route("/mines_increment", methods=["POST"])
def mines_increment():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    increment_amount = 10  

    if 'accumulated' not in session:
        session['accumulated'] = 0

    session['accumulated'] += increment_amount

    return jsonify({
        "accumulated": session['accumulated']
    })

@app.route("/mines_lose", methods=["POST"])
def mines_lose():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = get_user(session['username'])['user_id']
    bet_amount = 50
    new_balance = update_balance(user_id, "mines", -bet_amount)
    session["balance"] = new_balance

    session['accumulated'] = 0

    return jsonify({"message": "lost", "balance": new_balance, "accumulated": session['accumulated']})

@app.route("/mines_win", methods=["POST"])
def mines_win():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = get_user(session['username'])['user_id']
    bet_amount = 50
    new_balance = update_balance(user_id, "mines", bet_amount)
    session["balance"] = new_balance

    accumulated = session.get('accumulated', 0)
    
    return jsonify({"message": "won", "balance": new_balance, "accumulated": accumulated})

@app.route("/mines_cashout", methods=["POST"])
def mines_cashout():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    user_id = get_user(session['username'])['user_id']

    accumulated = session.get('accumulated', 0)
    new_balance = update_balance(user_id, "mines", accumulated)
    session["balance"] = new_balance
    session['accumulated'] = 0

    return jsonify({"message": "Cashed out successfully.","balance": new_balance,"accumulated": session['accumulated']})

@app.route("/leaderboard", methods=["GET"])
def show_leaderboard():
    results = get_leaderboard()
    if 'username' in session:
        username = session['username']
    else:
        username=None
    return render_template("leaderboard.html", leaderboard=results, username=username)
 
if __name__ == "__main__":
    app.run(debug=True)
