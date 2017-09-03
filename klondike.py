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
  P5 (club 4 to pile 5, on the heart 5)
  42 (club ten onto the heart jack)
  7C (club Ace to its ace pile)

a null order (return only) means, turn up the next card.

Exercises the suit_card_deck module.

'''

from suit_card_deck import *

