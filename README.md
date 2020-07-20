## Python code to emulate decks of cards and play simple games

Coded in good style, using type annotations, with lots of unit tests.

### Base library: suit_card_deck.py

Implements classes for
* Suit
* Card
* Deck
* Pile (aka Hand)
with appropriate behaviors

### API Documentation

Recommended use: `from suit_card_deck import *`
This defines the following names:

```
__all__ = [ 'Suit', 'Card', 'Rank', 'Deck', 'Pile', 'Hand',
           'CLUB', 'DIAMOND', 'HEART', 'SPADE',
           'EmptyDeckError',
           'MismatchedDeckError', 'PilingError' ]`
```

## Suit

An object that represents one of the four suits.
Four global objects named CLUB, DIAMOND, HEART and SPADE are instantiated and can be
used for comparisons, as in `card.suit() is CLUB` or `card.suit() < SPADE`

Properties of a suit are usually accessed via a card, unicode `card.suit()`.

`card.suit().color()` returns a string `black` or `red`.

`card.suit().name()` returns a string, one of 'Club', 'Diamond', 'Heart', 'Spade'
This is also the `str()` form of a suit.

`card.suit().plural()` returns the `name()` with `s`, for example `DIAMONDS`

`card.suit().initial()` returns a string, one of 'C', 'D', 'H', 'S'.

`card.suit().rank()` (also `card.suit_rank()`) returns an int, 0 1 2 or 3.

`card.suit().symbol()` returns a one-character unicode string ♠ ♣ ♥ ♦ (&spades;&clubs;&hearts;&diams;).
These characters are available as a four-character string as `Suit.symbols`.

## Card

An object that represents one card of a particular value and suit, dealt from a deck.

`card = Card(p)` where `p` is an int from 0 to 51, the position of this card in an
unshuffled deck of 52. 0 is deuce of Clubs; 51 is ace of Spades.
Typically a card is created as part of a Deck and dealt from that Deck.
In that case, the card "knows" its original deck object.
Returning a card to another deck raises an error.
A card created using `card = Card(p)` has no deck reference.

All properties of a card are accessed as methods.
Besides the suit-related methods (above) the card offers:

`card.position()` returns the `p` value of its creation, 0..51.

`card.color()` is the same as `card.suit().color()`.

`card.rank()` returns one of an IntEnum `Rank` with values from `Rank.r2` (2) to `Rank.r9` (9)
and `Rank.rT` (10), `Rank.rJ` (11), `Rank.rQ` (12), `Rank.rK` (13) and `Rank.rA` (14).

`card.nrank()` returns an int from 0 to 12, where an Ace is 0 and a King is 12.

`card.point_count()` is an int in 2,3,4,5,6,7,8,9,10,10,10,10,11, depending on rank.

`card.honor()` (also `card.honour()`) is True for cards of `Rank.rT` and above.

`card.name()` returns a one-character string '2' ... '9' 'T', 'J', 'Q', 'K', 'A'.

`str(card)` returns a two-character string, the name plus its suit symbol, for example `♣K` or `♦4`

## Deck

An object that represents a standard pack of 52 playing cards. It can be "shuffled" then "dealt"
into Piles (hands, tableau, etc.) and the Piles can be returned to the deck.

`deck = Deck()` Creates a new deck.

`len(deck)` Returns the number of cards not yet dealt, initally 52.

`deck.shuffle(times=1)` Shuffle the undealt cards in the deck 1 or more times (5 recommended).

`deck.cut(taking=None, minimum=5)` Cuts the deck taking a specified number from the top to the bottom.
If `taking` is omitted, approximately half the cards are taken. Taking all the cards or
leaving less than the minimum raises `EmptyDeckError`. (5 is the normal minimum for a Poker cut.)

`deck.deal()->Card` Removes the top card of the deck and returns it.
Dealing from an empty deck raises `EmptyDeckError`.

`deck.deal_pile(count)->Pile` Removes `count` cards from the deck and returns them as a Pile.
Can raise `EmptyDeckError`.

`deck.deal_to_pile(count, pile)->int` Removes `count` cards from the deck and adds them to the given Pile.
Returns the length of the pile after dealing.
Can raise `EmptyDeckError`.

`deck.put_back_card(card)->int` Puts a single card back on the bottom of the deck.
Returns the count of cards now in the deck.
If the card was not dealt from this deck, raises `MismatchedDeckError`.

`deck.put_back_pile(pile)->int` Removes all cards from a Pile and puts them on the bottom of the deck
in the same sequence. The Pile will be empty. Returns the count of cards now in the deck.
If a card was not dealt from this deck, raises `MismatchedDeckError`.

## Pile or Hand

Each object of class Pile (or Hand, which is an alias for the same class)
represents a group of zero or more cards dealt from a Deck.
A Pile can be used to represent a hand in a game,
or a discard pile,
or the pack in Solitaire, or any other group of cards that are played or handled together.

A Pile can be created by dealing cards from a Deck (`east = deck.deal_pile(13)`) but piles can
also be added to other piles, or cards can be taken from a pile and put on another pile.
Piles retain the sequence of cards as they are added, so there is a "top" and a "bottom" card.

When all the cards in a Pile come from the same deck, there will never be a duplicate.
However a Pile will accept cards from different decks, and if you mix cards from
different decks, a Pile might contain duplicates (and might raise an error if it is returned
to one deck).

A Pile can be created passing a "flag" value, any object: `east = Pile('E')`
This makes it easier for code to keep track of which pile is which, as in

```
    if pile.flag() == 'F' : # playing to a Foundation
```

A Pile object can have its length taken as `len(pile)`.
A pile can be indexed, as `pile[0]` (top card) or `pile[-1]` (bottom card).
You can slice a pile `pile[1:-1]` to access a range of cards.
These actions should be done only to test or display the indexed Card, as:

```
    if discard[0].color() == 'red' and discard[0].name() == '3' :
        # canasta discards frozen when red 3 on top
```

The indexed cards remain in the Pile.
To move a card out of a pile, or from one pile to another, you must call a method to remove it.

The properties of a Pile are all accessed as methods.

`pile.flag()` returns whatever value was passed in on creation (None when the pile is
created by a Deck).

`pile.sort( reverse=False )` arranges the cards in the pile by their position (i.e. 2 of clubs
to Ace of Spades), either ascending or descending. Returns the length of the pile.

`pile.turn_over()` reverses the order of cards in the pile. Exactly as you would do
when turning over a discard pile in Rummy.

`pile.receive(card)` puts the given card on top of the pile.
Returns the length of the pile.

`pile.receive_pile(other_pile)` removes the cards from `other_pile` and stacks them on this pile,
retaining their sequence. So if `pile==[1,2]` and `other_pile==[3,4]` the result is `[3,4,1,2]`.
As a side-effect, `other_pile` is emptied of cards.

`pile.remove()` removes the top card of the pile and returns it.
Raises `PilingError` if the pile is empty.

`pile.remove_pile(taking=1)` removes `taking` cards from the top and returns them in the same order,
as a new Pile.
Can raise `PilingError`.

### Game: Klondike by threes

Simple curses-based Klondike solitaire using the base library.

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png" /></a><br /><span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">Cardz: playing card emulation in Python</span> by <a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/tallforasmurf/Cardz" property="cc:attributionName" rel="cc:attributionURL">David Cortesi</a> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
