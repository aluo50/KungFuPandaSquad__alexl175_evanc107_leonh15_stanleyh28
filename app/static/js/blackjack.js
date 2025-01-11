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


// Shuffle + Deal Initial Cards
function startGameSequence() {
  // Shuffle animation
  $("#deck .card").addClass("shuffling");

  // deal
  setTimeout(() => {
    $("#deck .card").removeClass("shuffling");
    dealInitialCards(initialPlayerCards, initialDealerCards);
  }, 2000);
  if (calculateHandValue(initialPlayerCards) == 21) {
      setTimeout(() => stand(), 6000);
  }
}


// Deal 2 face-up cards to player, 1 face-up + 1 face-down to dealer.
function dealInitialCards(player_cards, dealer_cards) {
  // Player 1st card (face-up)
  dealCard("player", "face-up", getCardImage(player_cards[0]));
  // Player 2nd card (face-up)
  setTimeout(() => {
    dealCard("player", "face-up", getCardImage(player_cards[1]));
  }, 600);
  // Dealer 1st card (face-up)
  setTimeout(() => {
    dealCard("dealer", "face-up", getCardImage(dealer_cards[0]));
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
        1500, // Slower animation for more realism
        "swing",
        function () {
            // After animation, reset size and move card to target container
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
    dealCard("player", "face-up", getCardImage(data.new_card));

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
  }
}

function animateDealerDraws(drawnCards) {
  // Animate each newly drawn card (face-up)
  let delay = 0;
  drawnCards.forEach((cardNum) => {
    setTimeout(() => {
      dealCard("dealer", "face-up", getCardImage(cardNum));
    }, delay);
    delay += 600; // 600 ms delay in between draws
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

function playAgain() {
  $("#end-screen").fadeOut(() => {
    // Clear existing cards
    $("#player-cards").empty();
    $("#dealer-cards").empty();

    // resets game setup
    $.post("/play_again", function (data) {
      dealInitialCards(data.player_cards, data.dealer_cards);
    });
  });
}