'''

Simple emulation of the solitaire game "Klondike by Threes" to exercise the
suit_card_deck module.


PTUI (plain terminal user interface) (TODO: rewrite for curses)

On each turn displays the layout as (for example)

pack(21) ♦3                    ♣ -  ♦ A  ♥ -  ♠ -
 (1) (2) (3) (4) (5) (6) (7)
  ♣K  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆
      ♠Q  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆
          ♥7  ⁅⁆  ⁅⁆  ⁅⁆  ⁅⁆
          ♠6  ♥6  ♥K  ♦5  ⁅⁆
              ♣5  ♠Q  ♣4  ⁅⁆
              ♦4  ♦J      ⁅⁆
              ♣3  ♠T      ♥J

and awaits an order of the form: source target
The sources are:
    P, the pack, and 1, 2, 3, 4, 5, 6, 7, the piles in the tableau
The targets are:
    C, D, H, S: the ace-piles by suit, and the tableau 1..7.

In the above tableau (from an actual game) the only valid orders are
p6 (♦3 from pack to ♣4) and 63 (♦5/♣4 from pile 6 to ♠6 on pile 2)

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

class Klondike():
    '''
    Implement the apparatus and the rules of the game.

    For the Tableau we have seven piles which are initialized with
    one to seven cards. For each pile we keep a "face-up count" which
    is the number of cards at the top of the pile that are face-up
    and visible. Initially that is 1. Later, when cards are moved to a
    pile, that goes up by the number of cards.

    The pile cards that are face-up are pile[:faceup]. The cards that
    are still face-down are pile[faceup:]. The index of the deepest
    face-up card is pile[faceup-1].

    '''
    import sys

    _header_line = ' (1) (2) (3) (4) (5) (6) (7)'

    def __init__( self ) :
        '''
        Initialize game apparatus: create fresh copies of the ace piles,
        the seven tableau piles, the deck and the pack. Shuffle and deal.
        '''
        self.aces = [] # type: List[Pile]
        self.tableau = [] # type: List[Pile]
        self.deck = Deck() # type: Deck
        self.pack = Pile() # type: Pile
        self.aces = [ Pile(), Pile(), Pile(), Pile() ]
        self.tableau = [ Pile(), Pile(), Pile(), Pile(), Pile(), Pile(), Pile() ]
        self.deck = Deck()
        self.pack = Pile()

        self.deck.shuffle( times=5 )

        for j in range(7) :
            for p in range( j, 7 ) :
                self.tableau[ p ].receive( self.deck.deal() )
        self.faceup_count = [1] * 7

    '''

    Write the current game state to a stream IO device, stdout
    by default. Return the number of lines written, as this can
    vary with height of the tableau.

    Note that None, the default for dest, causes print() to use
    sys.stdout as the destination.

    '''
    def display( self, dest=None ) :

        # first line: "pack(nn) sv", some spaces, Aces

        print( "pack({}) {}".format( len(self.pack),
                                     self.pack[0] if len(self.pack) else '--'
                                     )
                , file=dest, end='' )
        print( "   "
                , file=dest, end='' )
        for s in range(4) :
            dash_or_rank = '-' if 0==len(self.aces[s]) else self.aces[s][0].name()
            print( Suit(s).initial() + ':' + dash_or_rank
                , file=dest, end=' ' )
        print( file=dest ) # end that line

        # second line: tableau column header line
        print( self._header_line, file=dest )

        # third-to-nth lines:
        #   determine depth of the deepest pile, that is our loop count
        #   for row in range(depth), i.e. while any pile has unprinted cards,
        #      for each tableau pile 1-7,
        #         if it has at least row cards,
        #            the card to display is its len minus row minus 1,
        #            e.g. if it has 3 cards and row is 0, display pile[2]
        #            if that card is face-up, display the card image
        #            else display []
        #         else display '  '

        max_depth = max( [ len(p) for p in self.tableau ] )

        for row in range( max_depth ) : # 0..max_depth-1
            for pile in range( 7) :
                len_pile = len( self.tableau[ pile ] )
                if len_pile > row :
                    card = len_pile - row - 1
                    if card < self.faceup_count[ pile ] :
                        out = str( self.tableau[ pile ][ card ] )
                    else :
                        out = '[]'
                else :
                    out = '  '
                print( ' ', out, end='', file=dest )
            # end for piles...
            print( file=dest ) # end that line

        return max_depth + 2



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

#def perform( command: str ) :
    #global ACES, TABLEAU, DECK, PACK

    #'''
    #Carry out the user's wishes based on the two letters received.
    #'''
    #if command == 'NN' :
        ## NN: turn the deck. If no cards remain in the deck, return the pack
        ## to the deck. Deal three cards (if available) from the deck onto the
        ## pack.
        #if 0 == len( DECK ) :
            #if len( PACK ) :
                #PACK.turn_over()
                #DECK.put_back_pile( PACK ) # empties PACK
            #else:
                #print( "no cards remain" )
            #return
        #for k in range( min( 3, len( DECK ) ) ) :
            #PACK.receive( DECK.deal() )
        #return
    ## command is SD, move card from source to dest.
    #source_letter = command[0]
    #dest_letter = command[1]
    #if source_letter == 'P' :
        #source_pile = PACK
    #else : # source is 1..7
        #source_pile = TABLEAU[ int( source_letter ) - 1 ]

    ## any source might be empty; diagnose
    #if 0 == len( source_pile ) :
        #print('No cards in pile {}'.format( source_letter ) )
        #return

    ## source is ok, choose destination and validate move
    #source_card = source_pile[0]
    #if dest_letter in 'CDHS' :
        #suit_rank = 'CDHS'.index( dest_letter )
        #dest_pile = ACES[ suit_rank ]
        #if source_card.suit_rank() == suit_rank and \
            #(
                #( source_card.rank() == Rank.rA and 0 == len( dest_pile ) )
            #or
                #( source_card.position() == ( dest_pile[0].position()+1 ) )
            #or
                #( source_card.rank() == Rank.r2 and dest_pile[0].rank() == Rank.rA )
            #) :
            #dest_pile.receive( source_pile.remove() )
        #else:
            #print( "invalid move: {} to {}".format( str(source_card), dest_letter ) )
    #else :
        #dest_pile = TABLEAU[ int( dest_letter ) - 1 ]
        #source_color = source_card.suit().color()
        #source_rank = source_card.rank()
        #if ( \
            #(
                #0 == len(dest_pile)
                #and source_card.rank() == Rank.rK
            #)
            #or
            #(
                #source_color != dest_pile[0].suit().color()
                #and dest_pile[0].rank() == (source_rank + 1)
            #)
           #) :
            #dest_pile.receive( source_pile.remove() )
        #else :
            #print( "invalid move: {} to {}".format( str(source_card), dest_letter ) )

while KEEP_ON :

    game = Klondike()

    game.display()

    #while True :
        #display_tableau()
        #command = get_command()
        #if command == 'XX' :
            ## user hit ^C
            #break
        #perform( command )

    KEEP_ON = ask_another()