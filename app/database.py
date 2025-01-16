# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

from flask import request, flash, session
import sqlite3
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'steakco.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # USER LOGIN TABLE
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            balance INTEGER NOT NULL DEFAULT 1000
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game TEXT,
            change INTEGER,
            new_balance INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS blackjack_in_progress (
            user_id INTEGER NOT NULL,
            bet_amount INTEGER,
            player_hand TEXT,
            dealer_hand TEXT,
            game_over INT
        );
    ''')
    
    conn.commit()
    conn.close()

def add_user():
    create_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        pw_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash,))
        conn.commit()
        conn.close()

        session['username'] = username
        flash('Registration successful!', 'success')

    except sqlite3.IntegrityError:
        flash('Username already Exists', 'error')

def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        # Retrieve hashed password for the given username
        cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        user_row = cur.fetchone()
        conn.close()

        # Checks hashed user password against database
        if user_row and check_password_hash(user_row['password_hash'], password):
            session['username'] = username
            flash('Login successful!', 'success')
        else:
            flash('Invalid username or password!', 'error')


def get_user(user):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (user,))
    user_info = cur.fetchone()
    conn.close()
    return user_info

# adds 'amount' to user's balance and records transactions
def update_balance(user_id, game_name, amount):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    new_balance = row['balance'] + amount 
    cur.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    cur.execute(
        "INSERT INTO transactions(user_id, game, change, new_balance) VALUES (?, ?, ?, ?)",
        (user_id, game_name, amount, new_balance)
    )
    conn.commit()
    conn.close()
    return new_balance

# loads stored blackjack session returns dict with deck, hands, bet
def load_blackjack(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM blackjack_in_progress WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return{
            'bet': row['bet_amount'],
            'player_hand': json.loads(row['player_hand']),
            'dealer_hand': json.loads(row['dealer_hand']),
            'game_over': row['game_over']
        }
    return None

# update blackjack_sessions row with latest game state
def save_blackjack(user_id, bet, player_hand, dealer_hand, game_over):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE blackjack_in_progress SET bet_amount=?, player_hand=?, dealer_hand=?, game_over=? WHERE user_id=?", (bet, json.dumps(player_hand), json.dumps(dealer_hand), game_over, user_id))

    conn.commit()
    conn.close()

    
def add_blackjack_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO blackjack_in_progress (user_id, bet_amount, player_hand, dealer_hand, game_over) VALUES (?, ?, ?, ?, ?)", (user_id, 0, json.dumps([]), json.dumps([]), 0))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, balance FROM users ORDER BY balance DESC;")
    results = cur.fetchall()
    conn.close()

    leaderboard = []
    rank = 1
    prev_balance = None
    for i, row in enumerate(results):
        if prev_balance is not None and row['balance'] != prev_balance:
            rank = i+1
        leaderboard.append({'rank': rank, 'username': row['username'], 'balance':row['balance']})
        prev_balance = row['balance']
    return leaderboard

def get_transaction_history(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT game, change, new_balance
        FROM transactions
        WHERE user_id = ?
        ORDER by transaction_id DESC
    """, (user_id,)
    )
    rows=cur.fetchall()
    conn.close()
    return rows