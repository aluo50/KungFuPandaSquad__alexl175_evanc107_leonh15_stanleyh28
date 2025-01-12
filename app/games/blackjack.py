# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

from flask import session
import random

def get_card(num):
    quotient = num // 13
    card_value = num % 13 + 1
    
    if card_value == 1:
        ace = True
        card_type = 'A'
        card_value = 11
    elif card_value >= 11:
        card_type = ['J', 'Q', 'K'][card_value - 11]
        card_value = 10
        ace = False
    else:
        card_type = None
        ace = False

    return quotient, card_value, ace, card_type

def calculate_hand_value(cards):
    total = 0
    aces = 0
    for card in cards:
        suit, value, ace, card_type = get_card(card)
        total += value
        if ace:
            aces += 1
    
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    
    return total

def initialize_game():
    session['deck'] = [i for i in range(52)]
    session['player_hand'] = random.sample(session['deck'], 2)
    for card in session['player_hand']:
        session['deck'].remove(card)

    session['dealer_hand'] = random.sample(session['deck'], 2)
    for card in session['dealer_hand']:
        session['deck'].remove(card)

def player_hit():
    card = random.sample(session['deck'], 1)[0]
    session['player_hand'].append(session['deck'].pop(session['deck'].index(card)))
    session.modified = True

def dealer_play():
    while calculate_hand_value(session['dealer_hand']) < 17:
        card = random.sample(session['deck'], 1)[0]
        session['dealer_hand'].append(session['deck'].pop(session['deck'].index(card)))
        session.modified = True
        
def double_down():
    player_hit()
    # Double bet amount
    session.modified = True

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
        user_info = database.return_user(session['username'])
        user_id = user_info['user_id']
        if outcome in ['win', 'blackjack']:
            database.update_balance(user_id, "blackjack", +50)
        elif outcome in ['lose', 'bust']:
            database.update_balance(user_id, "blackjack", -50)
    
    return outcome

    
