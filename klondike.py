#!/usr/bin/python
# -*- coding: UTF8 -*-
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
p6 (♦3 from pack to ♣4) and 63 (♦5/♣4 from pile 6 to ♠6 on pile 3)

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

    For the Tableau we have seven piles which are initialized with one to
    seven cards. For each pile we keep a faceup_count value which is the
    number of cards at the top of the pile that are face-up and so should be
    visible when the pile is displayed.

    Initially faceup_count is 1. When cards are moved onto a pile, that goes
    up by the number of cards.

    The pile cards that are face-up are pile[:faceup_count]. The cards that
    are still face-down are pile[faceup_count:]. Visible cards by the rules
    must decrease in value. The index of the deepest (thus, highest-ranked)
    face-up card is pile[faceup_count-1].

    It works out conveniently to store the Pack as the 8th Tableau pile.

    '''
    import sys

    _header_line = ' (1) (2) (3) (4) (5) (6) (7)'


    def __init__( self, seed:int=None ) :
        '''
        Initialize game apparatus: create fresh copies of the ace piles,
        the seven tableau piles, the deck and the pack. Shuffle and deal.
        '''
        # create the four foundations, each a pile tagged with its suit
        self.aces = [ Pile('C'), Pile('D'), Pile('H'), Pile('S') ] # four foundations
        # create seven unique tableaux, each tagged with a 'T'
        self.tableau = [ Pile('T') for _ in range(7) ]
        self.deck = Deck()
        self.pack = Pile('P')
        if seed : # user wants a certain game
            import random
            random.seed(seed)
        self.deck.shuffle( times=5 )

        for j in range(7) : # deal the tableaux
            for p in range( j, 7 ) :
                self.tableau[ p ].receive( self.deck.deal() )
        self.faceup_count = [1] * 7 # turn over the top card of each tableau pile

    def game_over( self ) -> bool :
        return 52 == sum( [ len(x) for x in self.aces ] )

    '''
    Turn the deck, that is, deal the top 3 cards onto the pack, so one can be
    played.

    If the deck is exhausted:
        if the pack has any cards:
            turn the pack over and put it back in the deck
        else
            all cards have been played, do nothing and return
    Deal the top 3 cards, or 2 or 1 as available, from deck to the pack.
    '''
    def turn_the_deck( self ) :
        if 0 == len( self.deck ) :
            if len( self.pack ) :
                self.pack.turn_over()
                self.deck.put_back_pile( self.pack )
            else :
                return
        for k in range( min( 3, len( self.deck ) ) ) :
            self.pack.receive( self.deck.deal() )

    '''
    Execute a move command give a source in 'P1234567' and a destination in
    'CDHS1234567'. (Assumes that only a valid source and dest will be passed.)

    A valid move will involve a sequence of one or more cards. First verify
    that the source has any cards left, and raise an error if not (it is up
    to the caller to display errors).

    Next, set the indices of the first and last cards to be moved from the
    source.

    When the source and destination are both the tableau, the user probably
    wants to move the whole sequence of face-up cards from the source pile to
    the destination pile. Verify if that is possible, i.e. the deepest face
    up card in the source can be received by the top of the destination. If
    so, note first and last as the indices of all face up cards in the
    source.

    Otherwise, i.e. when the above test fails, or the source is the Pack, or
    the destination is an Ace pile, the intent must be to move only the top
    (smallest) face up card of the source to the destination top. Verify that
    is a valid move and raise an error if not. Set first and last to the same
    index of the top card of the source.

    Carry out the move. Then, if the source has any cards left, deduct the
    count of cards moved from its faceup_count. If that reduces the face-up
    count to zero, and it has any cards left, turn up a card by setting face-up to 1.
    '''

    def can_play_to( self, card:Card, dest:Pile ) -> bool :
        '''
        Can card be played on dest? The rules ain't simple.

        Can play to a tableau if the tableau is not empty and the card
        is of the other color and rank one higher, or if the tableau is
        empty and the card is a King.

        Can play to a foundation if the foundation is not empty and the
        card is the same suit and one higher in numeric rank, or the
        foundation is empty and the card is the correct Ace.
        '''
        if dest.flag() == 'T' : # playing to a tableau
            #dbg = [ len(dest), card.rank(), card.suit().color() ]
            #if len(dest) : dbg.append([ dest[0].suit().color(), dest[0].rank() ] )
            return \
                (
                    len(dest)
                    and card.rank() < Rank.rA
                    and card.suit().color() != dest[0].suit().color()
                    and dest[0].rank() == ( card.rank() + 1 )
                ) or \
                (
                    0 == len(dest)
                    and card.rank() == Rank.rK
                )
        else : # assume dest.flag in 'CDHS', playing to a foundation
            #dbg = [ len(dest), card.suit(), card.nrank()]
            #if len(dest) : dbg.append( [dest[0].suit(), dest[0].nrank()] )
            return \
                (
                    len(dest)
                    and card.suit() == dest[0].suit()
                    and card.nrank() == dest[0].nrank()+1
                ) or \
                (
                    0 == len(dest)
                    and card.suit().initial() == dest.flag()
                    and card.rank() == Rank.rA
                )

    def move( self, source_letter:str, dest_letter:str ) :

        dest_is_tableau = source_is_tableau = False
        cards_moved = 0
        if source_letter == 'P' :
            source_pile = self.pack
        else :
            source_number = '1234567'.index( source_letter )
            source_pile = self.tableau[ source_number ]
            source_is_tableau = True

        if 0 == len(source_pile) :
            raise ValueError( 'No cards in source '+source_letter )

        if dest_letter in 'CDHS' : # foundation
            dest_number = 'CDHS'.index( dest_letter )
            dest_pile = self.aces[ dest_number ]
        else :
            dest_number = '1234567'.index( dest_letter )
            dest_pile = self.tableau[ dest_number ]
            dest_is_tableau = True

        if dest_pile == source_pile :
            raise ValueError( 'Source and destination are the same' )

        if dest_is_tableau and source_is_tableau :
            # Can the dest receive all source face up cards?
            source_faceup_count = self.faceup_count[source_number]
            source_high_card = source_pile[source_faceup_count-1]
            if self.can_play_to( source_high_card, dest_pile ) :
                # dest can receive all source face up cards.
                dest_pile.receive_pile( source_pile.remove_pile(source_faceup_count) )
                cards_moved = source_faceup_count
            elif self.can_play_to( source_pile[0], dest_pile ) :
                # dest can receive the top face up card
                dest_pile.receive( source_pile.remove() )
                cards_moved = 1
            else:
                # not a valid move
                raise ValueError( 'Invalid move' )
        else :
            # pack->tableau, pack->foundation, tableau->foundation
            if self.can_play_to( source_pile[0], dest_pile ) :
                dest_pile.receive( source_pile.remove() )
            else :
                raise ValueError( 'Invalid move' )
            cards_moved = 1
        if dest_is_tableau :
            self.faceup_count[dest_number] += cards_moved
        if source_is_tableau :
            self.faceup_count[source_number] -= cards_moved
            if self.faceup_count[ source_number ] == 0 \
            and len(source_pile) :
                # turn over top card of source tableau
                self.faceup_count[source_number] = 1


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
        print("kay, byeee") # force a newline on ^D
        return False
    except KeyboardInterrupt as k :
        print("yeet!") # force a newline on ^C/Delete
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
            if input_text.lower() == "q" : raise EOFError
        except EOFError as e :
            print() # force a newline on ^D
            return 'XX'
        except KeyboardInterrupt as k :
            print() # force a newline on ^C/Delete
            return 'XX'

        # strip commas and whitespace internal as well as outside
        input_text.replace(',','')
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


# FOR DEVELOPMENT SET A FIXED SEED, OTHERWISE NONE
# seed 319649 is a complete game
# GAME_SEED = 319649
GAME_SEED = None

game = Klondike(GAME_SEED)
while True:
    game.display()
    command = get_command()
    if command == 'XX' :
        # user hit ^C
        break
    elif command == 'NN' :
        game.turn_the_deck()
    else :
        try:
            game.move( command[0], command[1] )
        except ValueError as VE:
            print( str(VE) )
    if not game.game_over() :
        continue
    if ask_another() :
        game = Klondike(GAME_SEED)
    else :
        break
