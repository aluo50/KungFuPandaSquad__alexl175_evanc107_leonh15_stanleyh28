# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: 55

from flask import session
import random
from database import get_user, update_balance

# Gets value of the card, returns the value and whether or not it is an ace
def get_card(num):
    card_value = num % 13 + 1
    
    if card_value == 1:
        ace = True
        card_value = 11
    elif card_value >= 11:
        card_value = 10
        ace = False
    else:
        ace = False
        
    return card_value, ace

# Calculates hand value, maximizes point value without busting
def calculate_hand_value(cards):
    total = 0
    aces = 0
    for card in cards:
        value, ace = get_card(card)
        total += value
        if ace:
            aces += 1
    
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    
    return total

# Initializes the game
def initialize_game(bet):
    # Sets bet and new balance
    session['bet'] = bet
    session['balance'] -= bet
    
    # Initializes deck 
    # Player's cards
    session['deck'] = [i for i in range(52)]
    session['player_hand'] = random.sample(session['deck'], 2)
    for card in session['player_hand']:
        session['deck'].remove(card)
    
    # Dealer's cards
    session['dealer_hand'] = random.sample(session['deck'], 2)
    for card in session['dealer_hand']:
        session['deck'].remove(card)

# Function to hit, randomly gets a card from the deck
def player_hit():
    card = random.sample(session['deck'], 1)[0]
    session['player_hand'].append(session['deck'].pop(session['deck'].index(card)))
    session.modified = True

# Stand function
def dealer_play():
    while calculate_hand_value(session['dealer_hand']) < 17:
        card = random.sample(session['deck'], 1)[0]
        session['dealer_hand'].append(session['deck'].pop(session['deck'].index(card)))
        session.modified = True

# Determines winner of game and returns the result
def determine_winner():
    player_value = calculate_hand_value(session['player_hand'])
    dealer_value = calculate_hand_value(session['dealer_hand'])

    if player_value > 21:
        outcome = 'bust'
    elif dealer_value > 21 or player_value > dealer_value:
        if player_value == 21:
            outcome = 'blackjack'
        else:
            outcome = 'win'
    elif player_value == dealer_value:
        outcome = 'tie'
    else:
        outcome = 'lose'
    
    if 'username' in session:
        user_info = get_user(session['username'])
        user_id = user_info['user_id']
        if outcome == 'win':
            session['balance'] += session['bet'] * 2
            update_balance(user_id, "blackjack", session['bet'])
        elif outcome == 'blackjack':
            session['balance'] += session['bet'] * 2.5
            update_balance(user_id, "blackjack", session['bet']*1.5)
        elif outcome == 'lose' or outcome == 'bust':
            update_balance(user_id, "blackjack", -session['bet'])
        else:
            session['balance'] += session['bet']
            update_balance(user_id, "blackjack", 0)
    
    return outcome
