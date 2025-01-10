# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad 
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

from flask import request, flash, session
import sqlite3
import os
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
            password_hash TEXT NOT NULL
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
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user, pw_hash,))
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


def return_user(user):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (user,))
    user_info = cur.fetchone()
    conn.close()
    return user_info