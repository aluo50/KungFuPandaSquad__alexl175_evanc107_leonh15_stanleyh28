// Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
// KungFuPandaSquad
// SoftDev
// P02: Makers Makin' It, Act I
// 2025-1-9
// Time spent: 51

// On load, if in middle of game continue or else open up bet modal
$(document).ready(function () {
    let bet_amount = parseInt($("#bet").text());
    if (bet_amount != 0){
        startGameSequence();
    } else {
        openBetModal();
    }
});

// Translated from Python logic
function calculateHandValue(cards) {
    let total = 0;
    let aces = 0;

    for (const card of cards) {
        const rank = card % 13; 
        if (rank === 0) { 
            total += 11;
            aces++;
        } else if (rank >= 10) { 
            total += 10;
        } else { 
            total += rank + 1;
        }
    }
    while (total > 21 && aces > 0) {
        total -= 10;
        aces--;
    }
    return total;
}

// Updates the scores of player and dealer
function updateScore(card, position) {
    if (position === "player") {
        // Add the new card to the player's array
        initialPlayerCards.push(card);

        // Recalculate player's score
        let newScore = calculateHandValue(initialPlayerCards);

        // Update player score
        $("#player-score").text(newScore);

      } else if (position === "dealer") {
        // Add the new card to the dealer's array
        initialDealerCards.push(card);

        // Recalculate dealer's score
        let newScore = calculateHandValue(initialDealerCards);

        // Update dealer score
        $("#dealer-score").text(newScore);
    }
}

// Shuffle + Deal Initial Cards
function startGameSequence() {
    // Shuffle animation
    $("#deck .card").addClass("shuffling");

    // Makes copies of the arrays
    firstPlayerCards = initialPlayerCards.slice();
    firstDealerCards = initialDealerCards.slice();

    initialPlayerCards = [];
    initialDealerCards = [];

    // Deal
    setTimeout(() => {
        $("#deck .card").removeClass("shuffling");
        dealInitialCards(firstPlayerCards, firstDealerCards);
    }, 2000);
    
    // If Blackjack autostand
    if (calculateHandValue(firstPlayerCards) === 21) {
        setTimeout(() => stand(), 6000);
    }

    // If in middle of game continue
    if (firstPlayerCards.length > 2) {
        setTimeout(() => {
            for (i=2; i<firstPlayerCards.length; i++) {
                hit(card=firstPlayerCards[i]);
            }
        }, 6000);
    }

    // If game is over autostand
    if (game_over === true) {
        setTimeout(() => stand(firstDealerCards.slice(2)), 6000 + (firstPlayerCards.length-2) * 600);
    }
}


// Deal 2 face-up cards to player, 1 face-up + 1 face-down to dealer.
function dealInitialCards(player_cards, dealer_cards) {
    // Player 1st card (face-up)
    dealCard("player", "face-up", getCardImage(player_cards[0]));
    updateScore(player_cards[0], "player");
    
    // Player 2nd card (face-up)
    setTimeout(() => {
        dealCard("player", "face-up", getCardImage(player_cards[1]));
        updateScore(player_cards[1], "player");
    }, 600);
    
    // Dealer 1st card (face-up)
    setTimeout(() => {
        dealCard("dealer", "face-up", getCardImage(dealer_cards[0]));
        updateScore(dealer_cards[0], "dealer");
    }, 1200);
    
    // Dealer 2nd card (face-down)
    setTimeout(() => {
        dealCard("dealer", "face-down", getCardImage(dealer_cards[1]));
    }, 1800);
}

// Return the path to the PNG file for a given card integer (for display on site)
function getCardImage(cardNum) {
    return "/static/images/cards/" + cardNum + ".png";
}

// Animates a card from the deck to player/dealer area.
function dealCard(target, faceState, cardUrl) {
    // Create a new card element with size of 80px (otherwise too big)
    const newCard = $("<div>")
        .addClass("card moving")
        .addClass(faceState)
        .css({ 
            width: "80px",
            height: "auto" 
        })
        .append(
            $("<img>").attr(
                "src",
                faceState === "face-down"
                    ? "/static/images/cards/back.png"
                    : cardUrl
            ).css({ 
                width: "100%", 
                height: "auto" 
            })
        );

    // Append card temporarily to body for animation
    $("body").append(newCard);

    // Deck position (start) and target position (end)
    const deckOffset = $("#deck").offset();
    const targetOffset =
        target === "player"
            ? $("#player-cards").offset()
            : $("#dealer-cards").offset();

    // Position the card at the deck
    newCard.css({
        position: "absolute",
        top: deckOffset.top,
        left: deckOffset.left,
        zIndex: 9999
    });

    // Animate card movement to target area
    newCard.animate(
        {
            top: targetOffset.top,
            left: targetOffset.left + 50 
        },
        1500,
        "swing",
        function () {
            newCard.removeClass("moving");
            newCard.css({ 
                top: 0, 
                left: 0, 
                position: "relative", 
                zIndex: "auto"
            });
            $("#" + target + "-cards").append(newCard);
        }
    );
}

// Determines game result based on scores
function determineGameResult(dealer_score, player_score) {
    if (dealer_score > 21) {
        if (player_score === 21) {
            return 'blackjack';
        } else {
            return 'win';
        }
    } else if (dealer_score === player_score) {
        return 'tie';
    } else if (player_score > dealer_score) {
        return 'win';
    } else {
        return 'lose';
    }
}

// Hit function
function hit(card=null) {
    // Not resuming a game
    if (card===null) {
        $.post("/hit", function (data) {
            // Animate the newly drawn card
            dealCard("player", "face-up", getCardImage(data.new_card));

            // Update player's score
            updateScore(data.new_card, "player");

            // If there's a result (bust, etc.), show end screen
            setTimeout(() => {
                if (data.result) {
                    showEndScreen(data.result);
                }
            }, 1200);
        });
        
    // This called when resuming a game and player has hit at least once during the game
    } else {
        // Animate the newly drawn card
        dealCard("player", "face-up", getCardImage(card));

        // Update player's score
        updateScore(card, "player");

        // If there's a result (bust, etc.), show end screen
        setTimeout(() => {
          if (calculateHandValue(initialPlayerCards) > 21) {
            showEndScreen('bust');
          }
        }, 1200);
    }    
}

// Stand function
function stand(cards=[]) {
  // Not resuming a game
  if (cards.length === 0) {
      $.post("/stand", function (data) {
          // Flip the second card dealer face down card (data.dealer_hand[1])
          flipDealerFaceDownCard(data.dealer_hand[1]);

          setTimeout(() => {
              // Animate additional dealer draws if needed
              if (data.dealer_hand.length > 2) {
                  // Start from index 2
                  animateDealerDraws(data.dealer_hand.slice(2));
              }
          }, 600);

          // Show result
          setTimeout(() => showEndScreen(data.result, data.amount), 200 + 600 * data.dealer_hand.length);
      });
      
  // Resuming game
  } else {
    // Flip the second card dealer face down card
    flipDealerFaceDownCard(firstDealerCards[1]);

    setTimeout(() => animateDealerDraws(cards), 600);

    // Show result
    setTimeout(() => {
        dealer_score = calculateHandValue(initialDealerCards);
        player_score = calculateHandValue(initialPlayerCards);

        let result = determineGameResult(dealer_score, player_score);
        showEndScreen(result);
        
    }, 400 + 600 * cards.length);
  }
}

// Double down function
function doubleDown() {
    // Similar to hit
    $.post("/double_down", function (data) {
        if (data.new_card != false) {
            // Animates the new bet
            animateBalanceChange(data.amount);
            animateBet(data.bet);
            
            // Deals player 1 card and gets new score
            dealCard("player", "face-up", getCardImage(data.new_card));
            updateScore(data.new_card, "player");
            
            // If player busts, just display result and dealer doesn't need to draw
            if (calculateHandValue(initialPlayerCards) > 21) {
                setTimeout(() => showEndScreen('bust'), 1200);
            } else {
                setTimeout(() => {
                    // Autostand to finish the game
                    stand()
                }, 1200);
            }
        } else {
            // Flash error message
            showFlashMessage(data.message, "error");
        }
    });
}

// Dealer Logic
function flipDealerFaceDownCard(faceDownCardNum) {
    // Find the face-down card in #dealer-cards and flip it over
    const faceDownDiv = $("#dealer-cards .face-down").first();
    if (faceDownDiv.length) {
        faceDownDiv.removeClass("face-down").addClass("face-up");
        faceDownDiv.find("img").attr("src", getCardImage(faceDownCardNum));
        updateScore(faceDownCardNum, "dealer");
    }
}

// Animate dealer's turn
function animateDealerDraws(drawnCards) {
    let delay = 0;
    drawnCards.forEach((cardNum) => {
        setTimeout(() => {
            dealCard("dealer", "face-up", getCardImage(cardNum));
            updateScore(cardNum, "dealer");
        }, delay);
        delay += 600;
    });
}

// End Screen
function showEndScreen(resultText, amount=0) {
    let message = "";
    // End screen messages
    if (resultText === "win"){
        message = "You Win!";
        animateBalanceChange(amount * 2);
    } else if (resultText === "lose") {
        message = "Dealer Wins!";
    } else if (resultText === "tie") {
        message = "Push!";
        animateBalanceChange(amount);
    } else if (resultText === "bust") {
        message = "Bust!";
    } else if (resultText === "blackjack") {
        message = "Blackjack!";
        animateBalanceChange(amount * 2.5);
    }

    // Display message as end screen fades in
    $("#final-result").text(message);
    $("#end-screen").fadeIn();
    // Resets bet to 0
    animateBet(0);
}

// Resets game
function playAgain() {
    $("#end-screen").fadeOut(() => {
        // Clears everything and makes bet modal reappear to submit new bet
        $("#player-cards").empty();
        $("#dealer-cards").empty();
        $("#player-score").text(0);
        $("#dealer-score").text(0);
        initialDealerCards = [];
        initialPlayerCards = [];   
        openBetModal();
    });
}

// Animates coins
function animateBalanceChange(amount) {
    const balanceElement = document.getElementById("balance");
    let currentBalance = parseInt(balanceElement.innerText);
    let targetBalance = currentBalance + amount;
    
    // Limits increments and animated coins
    let increment = amount / 20;
    let coinsToAnimate = Math.min(Math.abs(amount), 100);
    const coinContainer = document.createElement('div');
    coinContainer.id = 'coin-animation-container';
    document.body.appendChild(coinContainer);
    
    // Constants used later to figure out positioning
    const balanceOffset = balanceElement.getBoundingClientRect();
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;

    // Create and animate coins
    for (let i = 0; i < coinsToAnimate; i++) {
        setTimeout(() => {
            // Coin png
            const coin = document.createElement('div');
            coin.classList.add('coin-animation');
            coin.style.position = "fixed";
            coin.style.backgroundImage = "url('/static/images/coin.png')";
            document.body.appendChild(coin);

            // Figures out where coin starts
            if (amount > 0) {
                coin.style.left = `${centerX}px`;
                coin.style.top = `${centerY}px`;
            } else {
                coin.style.left = `${balanceOffset.left}px`;
                coin.style.top = `${balanceOffset.top}px`;
            }

            // Delays each coin animation
            setTimeout(() => {
                coin.style.transition = "transform 1.5s ease-out, opacity 1s ease-out";
                if (amount > 0) {
                    // Move coins towards the balance from center
                    coin.style.transform = `translate(${balanceOffset.left - centerX}px, ${balanceOffset.top - centerY}px)`;
                } else {
                    // Move coins from balance to the center
                    coin.style.transform = `translate(${centerX - balanceOffset.left}px, ${centerY - balanceOffset.top}px)`;
                }
                coin.style.opacity = "0";
            }, 50);

            // Ends animation
            setTimeout(() => {
                coin.remove();
            }, 1600);
        }, i * (1000 / coinsToAnimate));
    }

    // Counter animation for balance change
    setTimeout(() => {
        let counter = setInterval(() => {
            if ((increment > 0 && currentBalance < targetBalance) ||
                (increment < 0 && currentBalance > targetBalance)) {
                currentBalance += increment;
                balanceElement.innerText = Math.round(currentBalance);
            } else {
                clearInterval(counter);
                balanceElement.innerText = targetBalance;
            }
        }, 50);
    }, 1200);
}

// Function to animate bet counter
function animateBet(target) {
    const betElement = document.getElementById("bet");
    let currentBet = parseInt(betElement.innerText);
    let increment = (target-currentBet) / 20;
    setTimeout(() => {
        let counter = setInterval(() => {
            if ((increment > 0 && currentBet < target) ||
                (increment < 0 && currentBet > target)) {
                currentBet += increment;
                betElement.innerText = Math.round(currentBet);
            } else {
                clearInterval(counter);
                betElement.innerText = target;
            }
        }, 50);
    }, 1200);
}

// Display bet modal to submit bets
function openBetModal() {
    $("#betModal").show();
}

// Submits bet and starts the game
function submitBet(betValue=null) {
    // If not resuming, if resuming already have betValue passed in
    if (betValue === null) {
        var betValue = parseInt($("#betAmountInput").val());
        if (isNaN(betValue) || betValue <= 0) {
            showFlashMessage("Please enter a valid bet amount!", 'error');
            return;
        }
    }

    // Post the bet to the server 
    $.post("/set_bet", { bet: betValue }, function(data) {
        if (data.success) {
            // Close modal and starts new game
            $("#betModal").hide();
            bet_amount = data.bet;
            amount = data.amount;
            showFlashMessage(data.message, 'success')
            dealInitialCards(data.player_cards, data.dealer_cards);
            animateBalanceChange(amount);
            animateBet(bet_amount);
            if (calculateHandValue(initialPlayerCards) == 21) {
              setTimeout(() => stand(), 5000);
            }
        } else {
            showFlashMessage(data.message, 'error')
        }
    });
}

// Goes all in
function allIn() {
    const balanceElement  = document.getElementById("balance");
    let currentBalance = parseInt(balanceElement.innerText);
    // Check they have money first
    if (currentBalance <= 0){
        showFlashMessage("You don't have enough money to bet!", 'error');
        return;
    } else {
        submitBet(currentBalance);
    }
}

// Flashing messges so user doesn't have to reload to see
function showFlashMessage(message, category) {
    const $newFlash = $(
        `<div class="flash-message ${category}">${message}</div>`
    );

    $(".flash-messages").append($newFlash);

    // Auto-fade and remove after 3 seconds
    setTimeout(() => {
        $newFlash.fadeOut(500, () => {
            $newFlash.remove();
        });
    }, 3000);
}