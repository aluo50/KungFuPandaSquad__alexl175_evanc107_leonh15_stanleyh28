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

if __name__ == "__main__":
    app.run(debug=True)