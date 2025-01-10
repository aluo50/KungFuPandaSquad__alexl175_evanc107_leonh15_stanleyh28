# Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
# KungFuPandaSquad
# SoftDev
# P02: Makers Makin' It, Act I
# 2025-1-9
# Time spent: x

import random

def get_card(num):
    quotient = num//13
    card_value = num%13

    card_value += 1
    if card_value == 1:
        ace = True
        type = None
    else:
        if card_value >= 11:
            if card_value == 11:
                type = "J"
            elif card_value == 12:
                type = "Q"
            else:
                type = "K"

            card_value = 10
        else:
            type = None
        ace = False
    return quotient, card_value, ace, type

def play_game():
    game = True
    cards = [i for i in range(52)]
    bot_hand = 0
    player_hand = 0
    bet_amount = None
    while bet_amount == None:
        try:
            bet_amount = int(input("How much would you like to bet in this game? "))
        except:
            print("Invalid input. Input an integer.")
            bet_amount = None
    #while game == True: