'''

Simple emulation of the solitaire game "Klondike by Threes" to exercise the
suit_card_deck module.


PTUI (plain terminal user interface) (TODO: rewrite for curses)

On each turn displays the layout as (for example)

pack(21) ♦3
 ♣  ♦  ♥  ♠  (1) (2) (3) (4) (5) (6) (7)
 A  -  -  -   ♣K  ♦7  --  --  --  --  --
              ♦Q      --  --  --  --  --
                      ♥7  --  --  --  --
                      ♠6  ♥6  ♥K  ♦5  --
                          ♣5  ♠Q  ♣4  --
                          ♦4  ♦J      ♥J
                          ♣3  ♠T

and awaits an order of the form: source target
The sources are:
    P, the pack, and 1, 2, 3, 4, 5, 6, 7, the piles in the tableau
The targets are:
    C, D, H, S: the ace-piles by suit, and the tableau 1..7.

In the above tableau (from an actual game) the only valid orders are
p6 (♦3 from pack to ♣4) and 62 (♦5/♣4 from pile 6 to ♦7 on pile 2)

A null order (return only) means, turn up the next card. If the deck has been
completely turned over, return means, invert it and turn it.

    LICENSE

This work is licensed under the Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International License.
To view a copy of this license, visit
http://creativecommons.org/licenses/by-nc-sa/4.0/.

'''

from suit_card_deck import *
from typing import List, Union
import string

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

def ask_another() -> str :
    '''
    prompt user if another game is wanted, return True if so,
    False if not. Take ^c, ^d as a "no".
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
    except KeyboardInterrupt as k :
        print() # force a newline on ^C/Delete
        return False

def display_tableau() :
    '''
    Display the current state of the game, to this template:

    pack(4) ♣4
    ♣  ♦  ♥  ♠  1(0)  2(2)  3(1)  4(4)  5(5)  6(6)  7(7)
    A  -  3  -   --    ♥J    ♥K    ♣T    ♥5    ♦J    ♦3

    Numbers in parens are the counts of cards in that pile.

    '''
    def name_count( name:str, pile:Union[Pile,Deck] ) :
        '''
        return a name of a pile (or deck) and the count of cards in parens,
        as "2(2)" or "pack(17)"
        '''
        return '{}({})'.format( name, len( pile ) )

    def top_card( pile: Pile ) :
        '''
        return the str of the top card of a pile, or "--" if the pile is empty.
        '''
        return str( pile[0] ) if len( pile ) else "--"

    def top_rank( pile: Pile ) :
        '''
        return the rank character of the top card of a pile, or "-"
        '''
        return pile[0].name() if len( pile ) else "-"

    # first line: pack(n) sr
    print( name_count( "pack", DECK ), top_card( PACK ) )

    # second line, first part: four suit symbols via the Suit class
    for s in range(4) :
        print( Suit(s).image(), end='  ' )

    # second line, part deux: print the 7 tableau piles sizes, and return
    for p in range(6) :
        print( name_count( str(p+1), TABLEAU[p] ), end='  ' )
    print( name_count( '7', TABLEAU[6] ) )

    # third line, part 1: print name of top card in each ace-pile
    for s in range(4) :
        print( top_rank( ACES[s]), end='  ' )

    # third line, finish: print top card in each tableau pile
    for p in range(7) :
        print( '', top_card( TABLEAU[p] ), end='   ' )
    print()

def get_command() -> str :
    '''
    Prompt the user for a move command, ensure it is two characters for
    source-target, and return it.

    If the command (after stripping) is null, return NN
    If the user hits ^D or ^C, return XX

    Allow manual "q" response because ^d doesn't work in Wing i/o window.
    '''
    sources = '1234567P'
    destinations = '1234567CDHS'
    while True :
        try:
            input_text = input( "source, target: " )
            if input_text.upper() == "q" : raise EOFError
        except EOFError as e :
            print() # force a newline on ^D
            return 'XX'
        except KeyboardInterrupt as k :
            print() # force a newline on ^C/Delete
            return 'XX'

        # strip all whitespace internal as well as outside
        command = input_text.translate( { ord(c):None for c in string.whitespace } )
        # if nothing left after removing whitespace, return null command
        if 0 == len( command) :
            return 'NN'
        # make uppercase
        command = command.upper()
        if len( command ) == 2 and \
           command[0] in sources and \
           command[1] in destinations and \
           command[0] != command[1] :
            break

        print( "Enter return to deal three more cards," )
        print( "Enter a source, 1 - 7 or P for the pack, and" )
        print( "a destination, C D H or S or 1-7, to move a card." )
    # end input loop
    return command

def perform( command: str ) :
    global ACES, TABLEAU, DECK, PACK

    '''
    Carry out the user's wishes based on the two letters received.
    '''
    if command == 'NN' :
        # NN: turn the deck. If no cards remain in the deck, return the pack
        # to the deck. Deal three cards (if available) from the deck onto the
        # pack.
        if 0 == len( DECK ) :
            if len( PACK ) :
                PACK.turn_over()
                DECK.put_back_pile( PACK ) # empties PACK
            else:
                print( "no cards remain" )
            return
        for k in range( min( 3, len( DECK ) ) ) :
            PACK.receive( DECK.deal() )
        return
    # command is SD, move card from source to dest.
    source_letter = command[0]
    dest_letter = command[1]
    if source_letter == 'P' :
        source_pile = PACK
    else : # source is 1..7
        source_pile = TABLEAU[ int( source_letter ) - 1 ]

    # any source might be empty; diagnose
    if 0 == len( source_pile ) :
        print('No cards in pile {}'.format( source_letter ) )
        return

    # source is ok, choose destination and validate move
    source_card = source_pile[0]
    if dest_letter in 'CDHS' :
        suit_rank = 'CDHS'.index( dest_letter )
        dest_pile = ACES[ suit_rank ]
        if source_card.suit_rank() == suit_rank and \
            (
                ( source_card.rank() == Rank.rA and 0 == len( dest_pile ) )
            or
                ( source_card.position() == ( dest_pile[0].position()+1 ) )
            or
                ( source_card.rank() == Rank.r2 and dest_pile[0].rank() == Rank.rA )
            ) :
            dest_pile.receive( source_pile.remove() )
        else:
            print( "invalid move: {} to {}".format( str(source_card), dest_letter ) )
    else :
        dest_pile = TABLEAU[ int( dest_letter ) - 1 ]
        source_color = source_card.suit().color()
        source_rank = source_card.rank()
        if ( \
            (
                0 == len(dest_pile)
                and source_card.rank() == Rank.rK
            )
            or
            (
                source_color != dest_pile[0].suit().color()
                and dest_pile[0].rank() == (source_rank + 1)
            )
           ) :
            dest_pile.receive( source_pile.remove() )
        else :
            print( "invalid move: {} to {}".format( str(source_card), dest_letter ) )

while KEEP_ON :

    new_game()

    while True :
        display_tableau()
        command = get_command()
        if command == 'XX' :
            # user hit ^C
            break
        perform( command )

    KEEP_ON = ask_another()