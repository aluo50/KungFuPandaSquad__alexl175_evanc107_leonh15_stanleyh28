# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad 
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

from flask import Flask, request, render_template, redirect, url_for, flash, session
import sqlite3
import os
import database
from games.blackjack import calculate_hand_value, initialize_game, player_hit, dealer_play, determine_winner, double_down

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)

database.create_db()

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    if 'username' in session:
        return render_template("home.html", username=session['username'])
    return render_template("home.html", username=None)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        database.login_user()
        if 'username' in session:
            return redirect(url_for("home"))
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():
    if 'username' in session:
        user=session.pop('username')
        flash(f"{user}, you have been logged out.", 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        database.add_user()
        if 'username' in session:
            return redirect(url_for('home'))
        return redirect(url_for('register'))
    
    return render_template("login.html")

@app.route('/blackjack', methods=["GET", "POST"])
def play_blackjack():
    # Only initialize if 'deck' is not in session,
    # meaning there's no active game yet.
    if 'deck' not in session:
        initialize_game()
    return render_template('blackjack.html')

@app.route('/hit', methods=["POST"])
def hit():
    player_hit()
    player_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['player_hand']]
    )
    dealer_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['dealer_hand']]
    )
    if calculate_hand_value(session['player_hand']) > 21:
        result = determine_winner()
        return {"player_cards": player_cards_html, "dealer_cards": dealer_cards_html, "result": result}
    else:
        return {"player_cards": player_cards_html, "dealer_cards": dealer_cards_html}

@app.route('/stand', methods=["POST"])
def stand():
    dealer_play()
    result = determine_winner()
    player_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['player_hand']]
    )
    dealer_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['dealer_hand']]
    )
    return {"player_cards": player_cards_html, "dealer_cards": dealer_cards_html, "result": result}

@app.route('/double_down', methods=["POST"])
def double_down_route():
    double_down()
    result = determine_winner()
    player_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['player_hand']]
    )
    dealer_cards_html = ''.join(
        [f'<img src="{url_for("static", filename="images/cards/" + str(card) + ".png")}">' for card in session['dealer_hand']]
    )
    return {"player_cards": player_cards_html, "dealer_cards": dealer_cards_html, "result": result}

@app.route('/play_again', methods=["POST"])
def play_again():
    initialize_game()
    session.modified = True  

    # Send the new cards back to the frontend
    player_cards_html = ''.join(
        [f'<img src="{url_for('static', filename='images/cards/' + str(card) + '.png')}">' for card in session['player_hand']]
    )
    dealer_cards_html = ''.join(
        [f'<img src="{url_for('static', filename='images/cards/' + str(card) + '.png')}">' for card in session['dealer_hand']]
    )

    return {"player_cards": player_cards_html, "dealer_cards": dealer_cards_html}

if __name__ == "__main__":
    app.run(debug=True)