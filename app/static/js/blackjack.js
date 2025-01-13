// Alex Luo, Evan Chan, Leon Huang, Stanley Hoo
// KungFuPandaSquad
// SoftDev
// P02: Makers Makin' It, Act I
// 2025-1-9
// Time spent: x

$(document).ready(function () {
  startGameSequence();
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

function updateScore(card, position) {
  if (position === "player") {
    // Add the new card to the player's array
    initialPlayerCards.push(card);

    // Recalculate player's score
    let newScore = calculateHandValue(initialPlayerCards);

    // Update the DOM
    $("#player-score").text(newScore);

  } else if (position === "dealer") {
    // Add the new card to the dealer's array
    initialDealerCards.push(card);

    // Recalculate dealer's score
    let newScore = calculateHandValue(initialDealerCards);

    // Update the DOM
    $("#dealer-score").text(newScore);
  }
}

// Shuffle + Deal Initial Cards
function startGameSequence() {
  // Shuffle animation
  $("#deck .card").addClass("shuffling");
    
  firstPlayerCards = initialPlayerCards.slice();
  firstDealerCards = initialDealerCards.slice();
    
  initialPlayerCards = [];
  initialDealerCards = [];

  // deal
  setTimeout(() => {
    $("#deck .card").removeClass("shuffling");
    dealInitialCards(firstPlayerCards, firstDealerCards);
  }, 2000);
  if (calculateHandValue(firstPlayerCards) == 21) {
      setTimeout(() => stand(), 6000);
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

// Return the path to the PNG file for a given card integer.
function getCardImage(cardNum) {
  return "/static/images/cards/" + cardNum + ".png";
}

// Animates a card from the deck to player/dealer area.
function dealCard(target, faceState, cardUrl) {
    // Create a new card element with controlled size
    const newCard = $("<div>")
        .addClass("card moving")
        .addClass(faceState)
        .css({ 
            width: "60px",
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

    // Position the card at the deck initially with absolute positioning
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

// stand function
function stand() {
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

    // show result
    setTimeout(() => showEndScreen(data.result), 200 + 600 * data.dealer_hand.length);
  });
}

// hit function
function hit() {
  $.post("/hit", function (data) {
    // Animate the newly drawn card
    dealCard("player", "face-up", getCardImage(data.new_card));

    // Update player's score with the new card
    updateScore(data.new_card, "player");

    // If there's a result (bust, etc.), show end screen
    setTimeout(() => {
      if (data.result) {
        showEndScreen(data.result);
      }
    }, 1200);
  });
}

function doubleDown() {
  // Similar to hit
  $.post("/double_down", function (data) {
    dealCard("player", "face-up", getCardImage(data.new_card));
    updateScore(data.new_card, "player");
    // If player busts, just display result and dealer doesn't need to draw
    if (data.result === 'bust') {
        setTimeout(() => showEndScreen(data.result), 1200);
    } else {
        setTimeout(() => {
          stand(data)
        }, 1200);
    }
  });
}

// Dealer Logic
function flipDealerFaceDownCard(faceDownCardNum) {
  // Find the first face-down card in #dealer-cards
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
function showEndScreen(resultText) {
  let message = "";
  if (resultText === "win") message = "You Win!";
  else if (resultText === "lose") message = "Dealer Wins!";
  else if (resultText === "tie") message = "Push!";
  else if (resultText === "bust") message = "Bust!";
  else if (resultText == "blackjack") message = "Blackjack!";

  $("#final-result").text(message);
  $("#end-screen").fadeIn();
}

// Resets game
function playAgain() {
  $("#end-screen").fadeOut(() => {
    // Clear existing cards
    $("#player-cards").empty();
    $("#dealer-cards").empty();

    // resets game setup
    $.post("/play_again", function (data) {
      initialPlayerCards = [];
      initialDealerCards = [];
      $("#player-score").text(0);
      $("#dealer-score").text(0);
      dealInitialCards(data.player_cards, data.dealer_cards);
    });
      
    if (calculateHandValue(initialPlayerCards) == 21) {
      setTimeout(() => stand(), 5000);
    }
  });
}