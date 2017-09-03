'''

Simple emulation of the solitaire game "Klondike by Threes"

PTUI (plain terminal user interface)

On each turn displays the layout as (for example)

pack(21) ♣4
 ♣  ♦  ♥  ♠  1(1)  2(2)  3(3)  4(4)  5(5)  6(6)  7(7)
 -  -  -  -   ♠6    ♥J    ♥K    ♣T    ♥5    ♦J    ♣A
  >>

and awaits an order of the form: source target
and the sources and targets are:

1, 2, 3, 4, 5, 6, 7: the piles in the tableau
C, D, H, S: the ace-piles by suit
P the pack

As above, valid orders might be:
  P5 (top of pack, club 4, to pile 5, on the heart 5)
  42 (top of pile 4, club ten, onto pile 2, the heart jack)
  7C (top of pile 7, club Ace, to the Club ace pile)

A null order (return only) means, turn up the next card.
If the deck has been completely turned over, return means,
invert it and turn it.

Exercises the suit_card_deck module.

    LICENSE

This work is licensed under the Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc-sa/4.0/.

'''

from suit_card_deck import *
from typing import List

ACES = [] # type: List[Pile]

TABLEAU = [] # type: List[Pile]

DECK = Deck() # type: Deck

PACK = Pile() # type: Pile

def new_game():
    '''
    Initialize game apparatus: create fresh copies of the ace piles,
    the seven tableau piles, the deck and the pack. Shuffle and deal.
    '''
    global ACES, TABLEAU, DECK, PACK

    ACES = [ Pile(), Pile(), Pile(), Pile() ]
    TABLEAU = [ Pile(), Pile(), Pile(), Pile(), Pile(), Pile(), Pile() ]
    DECK = Deck()
    PACK = Pile()

    DECK.shuffle( times=5 )

    for j in range(7) :
        for p in range( j, 7 ) :
            TABLEAU[ p ].receive( DECK.deal() )

KEEP_ON = True # type: bool

def ask_another() :
    '''
    prompt user if another game is wanted, return True if so,
    False if not.
    '''
    print()
    try:

        ans = input('\t Another game? [Yn] ' )
        if not len( ans ) :
            ans = 'y'
        return ans.lower()[0] == 'y'

    except EOFError as e :
        print() # force a newline on ^D
        return False

while KEEP_ON :

    print('picture a game here')

    KEEP_ON = ask_another()