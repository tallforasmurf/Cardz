'''
Module suit_card_deck defines classes for Suit, Card, Deck, and Pile objects.

Note that the code herein has a dependency on the assumption that a "deck of
cards" contains 52 cards in four suits. It does not support jokers or decks
with other than the conventional 52 cards.

            LICENSE INFORMATION

This work is licensed under the Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International License. To view a
copy of this license, visit
http://creativecommons.org/licenses/by-nc-sa/4.0/.

'''

'''

The __all__ global defines the set of names that are returned by

from suit_card_deck import *

'''
__all__ = [ 'Suit', 'Card', 'Rank', 'Deck', 'Pile', 'Hand',
           'CLUB', 'DIAMOND', 'HEART', 'SPADE',
           'EmptyDeckError',
           'MismatchedDeckError', 'PilingError' ]

'''
Declare the exceptions raised herein.
'''

class EmptyDeckError( IndexError ) :
    pass

class MismatchedDeckError( ValueError ) :
    pass

class ShallowCutError( ValueError ):
    pass

class PilingError( ValueError ) :
    pass

'''
    Imports

    IntEnum for card ranks
    random for shuffle
    typing for typing
'''
from enum import IntEnum
import random
from typing import List

class Suit():

    '''
    Objects of the Suit class represent the four suits of the deck.

    One object of each suit is instantiated as a global name below,
    and these specific objects are incorporated by all objects of
    the Card class. Thus the suit of a diamond card "is" DIAMOND
    as well as being equal-to DIAMOND and to Suit(1).

    Properties: are all implemented as methods, not attributes.

    color(): string, "black" or "red"

    name(): string, "Club", "Diamond", "Heart" or "Spade"

    plural(): string, the value of name() + "s"

    initial(): string, "C" "D" "H" or "S"

    rank(): integer, 0 (Club) to 3 (Spade)

    image(): one-character string, a unicode symbol ♠ ♣ ♥ ♦ (&spades;&clubs;&hearts;&diams;)

    '''

    colors = ( 'black', 'red', 'red', 'black' )
    names = ( 'Club', 'Diamond', 'Heart', 'Spade' )
    images = '♣♦♥♠'

    __slots__ = '_r'

    def __init__( self, rank:int ) :
        assert 0 <= rank and rank <= 3
        self._r = rank

    def color( self ) -> str :
        return Suit.colors[ self._r ]

    def name( self ) -> str :
        return Suit.names[ self._r ]

    def initial( self ) -> str :
        return Suit.names[ self._r ][ 0 ]

    def plural( self ) -> str :
        return Suit.names[ self._r ] + 's'

    def rank( self ) -> int :
        return self._r

    def image( self ) -> str :
        return Suit.images[ self._r ]

    def __repr__( self ) -> str :
        return 'Suit({})'.format( self._r )

    def __str__( self ) -> str :
        return self.name()


'''
The four Suits, defined here as constants, for comparison elsewhere.
'''

CLUB = Suit(0)
DIAMOND = Suit(1)
HEART = Suit(2)
SPADE = Suit(3)

class Rank(IntEnum):

    '''
    An intenum representing the relative rank of a Card
    '''

    r2 = 2 ; r3 = 3 ; r4 = 4 ; r5 = 5;
    r6 = 6 ; r7 = 7 ; r8 = 8 ; r9 = 9;
    rT = 10
    rJ = 11
    rQ = 12
    rK = 13
    rA = 14

class Card():

    '''
    The class of playing card objects.

    Properties: (all implemented as methods not attributes)

    suit(): class Suit, "is" one of CLUB, DIAMOND, HEART or SPADE

    suit_rank(): int from suit.rank(), the rank of its suit

    rank(): IntEnum of 2, 3, ... 14

    count(): int, 2-10 or 11 for Ace

    name(): one-letter string, '2' ... '9', 'T', 'J', 'Q', 'K', 'A'

    position(): int from 0..51, the raw standing of this card in an
        unshuffled deck of 52, from which suit, rank etc are derived

    __str__(): a suit symbol plus name, as "♣9" or "♥Q"

    __repr__(): string "Card(n)" where n == position()

    A Card which is dealt from a Deck knows its source Deck object.
    Card objects from different Decks (or from no Deck) are not comparable!

    The Card class implements the comparison operators based on the card Rank;
    thus two 9's are equal, Ace > Jack, etc. Because Rank is an IntEnum
    it is legal also to compare a Card to an int in the range 2..14.

    If you want the Suit to figure in the comparison of two Cards (as in
    Bridge or Hearts), the suit must be tested separately.

    Card objects are hashable, so can be used as keys in a set or dict. The
    hash value is the card's position in an unshuffled deck, e.g. 13 for the
    deuce of diamonds, modified by the Card's Deck. So a set can contain
    multiple Cards of the same Suit and Rank but from different Decks; but a
    set will only contain one instance of a given card from a given Deck.

    '''

    Suits = ( CLUB, DIAMOND, HEART, SPADE )
    Points = ( 2,3,4,5,6,7,8,9,10,10,10,10,11 )
    Names = ( '2', '3', '4', '5', '6', '7', '8',
              '9', 'T', 'J', 'Q', 'K', 'A' )

    #__slots__ = ['_r', '_p', '_deck' ]

    def __init__( self, position, deck = None ) :
        assert 0 <= position and position <= 51
        self._pos = position
        self._r, self._p = divmod( position, 13 )
        self._deck = deck

    def suit_rank( self ) -> int :
        return Card.Suits[ self._r ].rank()

    def suit( self ) -> Suit :
        return Card.Suits[ self._r ]

    def rank( self ) -> Rank :
        return Rank( 2+self._p )

    def point_count( self ) -> int :
        return Card.Points[ self._p ]

    def name( self ) -> str :
        return Card.Names[ self._p ]

    def position( self ) -> int :
        return self._pos

    def __repr__( self ) -> str :
        return 'Card( {} )'.format( self._pos )

    def __str__( self ) -> str :
        return '{}{}'.format( self.suit().image(), self.name() )

    def __lt__( self, other ) -> bool :
        if isinstance( other, Card ) :
            return self.rank() < other.rank()
        elif isinstance( other, int) and 1 < other < 15 :
            return self.rank() < Rank( other )
        else :
            return NotImplemented

    def __eq__( self, other ) -> bool :
        if isinstance( other, Card ) :
            return self.rank() == other.rank()
        elif isinstance( other, int) and 1 < other < 15 :
            return self.rank() == Rank( other )
        else :
            return NotImplemented

    def __gt__( self, other ) -> bool :
        if isinstance( other, Card ) :
            return self.rank() > other.rank()
        elif isinstance( other, int) and 1 < other < 15 :
            return self.rank() > Rank( other )
        else :
            return NotImplemented

    def __le__( self, other ) -> bool :
        return self.__lt__( other ) or self.__eq__( other )

    def __ge__( self, other ) -> bool :
        return self.__gt__( other ) or self.__eq__( other )

    def __ne__( self, other ) -> bool :
        return self.__gt__( other ) or self.__lt__( other )

    def __hash__( self ) :
        return self._pos +id(self._deck)

class Pile() :

    '''
    The class of a set of 0 or more cards that have been dealt from a single Deck.

    A Pile can be used as a "hand" or as a discard heap, or as one element
    of a solitaire tableau.

    A Pile does **NOT** enforce the rule that its cards should all be from a
    single Deck. Thus you could in principle pile up Cards from different Decks,
    and if you did that, you might find duplicate Card values in a Pile.

    when a Pile is returned to a Deck, the Deck enforces the rule that every Card
    must have come from that Deck.

    Properties:

    __len__(): int, the number of cards in the Pile

    A Pile supports indexing:

        apile[n] returns the Nth Card in the Pile

        apile[x:y] returns a list of Cards

    Indexing a Pile makes it easy to access the top Card in a Pile to display
    it or test its value; or to display all the cards in the Pile (for C in
    apile[:]) and so on.

    Note that indexing does not remove cards from the Pile, so if you do anything
    with the returned Cards other than test or display them (for example if you
    put them back in a deck or in another Pile) you risk raising errors later.

    sort( reverse=False ): sorts the cards in the pile into ascending
        or descending (reverse==True) order, by rank within suit.
        Returns the number of cards in the pile.

    turn_over() : inverts the pile. Lets you correct for the fact that when
        you deal one card at a time to a pile, the cards are inverted
        from their deck sequence.
        Returns the number of cards in the pile.

    receive() accepts a Card which goes on top of the Pile

    receive_pile() accepts another Pile, removes all cards from it and
    stacks them on this Pile.

    remove() returns the Card from the top of the Pile and removes it.

    remove_pile( n ) removes n cards from the top of the Pile and returns
        a new Pile containing those cards.

    The Pile does not support comparison. It does support default hashing
    so you can have a dictionary or set of Piles.

    '''

    def __init__( self ) :
        self._cards = [] # Type: List( Card )

    def __len__( self ) -> int :
        return len( self._cards )

    def __getitem__( self, key ) :
        ''' implement indexing '''
        return self._cards.__getitem__( key )

    def sort( self, reverse:bool = False ) -> int :
        self._cards.sort( key = Card.position, reverse=reverse )
        return len( self._cards )

    def turn_over( self ) :
        self._cards = list( reversed( self._cards ) )
        return len( self._cards )

    def receive( self, card: Card ) -> int :
        ''' add a Card to this Pile
        Args:
            card: class Card, required
        Returns:
            int, number of Cards now in the Pile
        State:
            extends contents of self._cards
        Raises:
            ValueError when card isn't one
            PilingError when card is already in Pile
        Note that "card in self._cards" uses the __eq__ method of Card,
        which only compares card-rank. We need to compare positions.
        '''
        if isinstance( card, Card ) :
            for c in self._cards :
                if c.position() == card.position() :
                    raise PilingError( "Card already in Pile" )
            self._cards.insert( 0, card )
            return len( self._cards )
        else :
            raise ValueError

    def receive_pile ( self, pile ) -> int :
        ''' add a Pile to this Pile.

        Note we can't type-check the argument "pile:Pile" because the
        name Pile has not been defined yet -- we are inside its def.

        Note we can't loop using self.receive( pile.remove() ) because
        that would put the cards on top in reverse order. We need to
        remove them, then add them in reverse order. Fortunately the
        builtin reversed() function returns an iterator.

        In fact this operation is exactly analogous to what you might
        do to move N cards from one pile to another: deal them off the
        top into a pile, then deal the pile onto the receiving pile.

        Args:
            pile: class Pile, required, may be empty
        Returns:
            int, number of Cards now in this Pile
        State:
            extends contents of self._cards
            empties the contents of pile (side effect! not Functional!)
        Raises:
            ValueError if pile isn't one
            calls self.receive, so possibly PilingError if a Card
            existed in both piles.
        '''
        if isinstance( pile, Pile ) :
            pile_cards = []
            while len( pile ) :
                pile_cards.append( pile.remove() )
            for card in reversed( pile_cards ) :
                self.receive( card )
        else :
            raise ValueError

    def remove( self ) -> Card :
        ''' remove the top Card of the Pile
        Returns:
            a Card object
        State:
            shortens contents of self._cards
        Raises:
            PilingError when Pile is empty
        '''
        if len( self._cards ) :
            return self._cards.pop( 0 )
        else :
            raise PilingError( 'taking card from empty pile')

    def remove_pile( self, cards_to_take: int = 1 ) :
        '''Remove top n cards from this Pile and return them as a new Pile.
        As with receive_pile() we have reverse the order of the cards.

        As above, we can't type-note the return "-> Pile" because that
        class name does not exist yet.

        Args:
            cards_to_take: int must be <= len(self._cards)
        Returns:
            a Pile object
        State:
            creates a new object
            shortens self._cards
        Raises:
            PilingError when cards_to_take is too large
        '''
        if cards_to_take <= len( self._cards ) :
            new_pile = Pile()
            pile_cards = []
            for j in range( cards_to_take ) :
                pile_cards.append( self.remove() )
            for card in reversed( pile_cards ) :
                new_pile.receive( card )
            return new_pile
        else:
            raise PilingError( "taking more cards than exist in Pile" )

class Hand( Pile ): # an alias
    pass

class Deck():

    '''
    Class of an array of 52 Cards which can be dealt in a certain sequence.

    The array of Cards is itself never permuted. The sequence in which Cards
    are dealt is determined by an array of indices. To access Card N, we
    return self._cards[self._access[N]].

    Initially the access array is [0..51], so that _access[N]==N and thus an
    un-shuffled deck will be dealt in sequence from 0 (Club 2) to 51 (Spade Ace).

    A Deck has a top Card. To "deal" from a deck is to output the top card,
    i.e. self._cards[self._access[self._top]], and then to increment the top
    pointer, making the next Card in access sequence the new top Card.

    Cards that have not yet been dealt are those indexed by _access[_top:].
    Those that have been dealt are indexed by _access[:_top]. (Slices are nices!)

    The Deck is empty when self._top > 51. Dealing from an empty Deck ()
    raises an exception.

    Deck supports len() returning the number of cards undealt.

    A Deck may be cut(). By default a cut must select and leave at least
    five cards, but this is a parameter.

    A single card that has been dealt from this deck can be returned to the
    deck, where it is put on the bottom. This decrements _top.

    All the cards of a Pile can be returned to the Deck from which the Pile
    was dealt. The cards are added to the bottom of the Deck. Note this
    operation has the side-effect that it empties the Pile.

    To shuffle a Deck is to permute the array of indices in self._access
    which describe undealt cards. A non-empty deck can be shuffled at any
    time. This makes possible the type of game where a discard Pile is
    returned to the deck and the deck re-shuffled.

    If you want to get the identical sequence of cards, you need to call
    random.seed() before calling Deck.shuffle(). Also note the following
    remark in the random.shuffle documentation,

        ...for even rather small len(x), the total number of permutations of x is
        larger than the period of most random number generators; this implies
        that most permutations of a long sequence can never be generated.

    To get around this limitation, and for better versimilitude in shuffled
    decks, shuffle multiple times before dealing. To assist this we provide a
    times argument to shuffle, defaulting to once.

    '''
    __slots__ = ( '_access', '_cards', '_top' )
    ex_text_1 = 'dealing from empty deck'
    ex_text_2 = 'shuffling empty deck'
    ex_text_3 = 'returning card to different deck'
    ex_text_4 = 'returning card that has not been dealt'
    ex_text_5 = 'cut takes or leaves fewer than minimum'

    def __init__( self ) :

        ''' Initialize a Deck with 52 cards in natural sequence '''

        # Python 3 coding tid-bit: the expression [ range(52) ] does NOT
        # return a list of 52 integers! but the expression list( range(52) )
        # does, which is what is wanted here.

        self._access = list( range(52) )
        self._cards = [ Card(p, self) for p in self._access ]
        self._top = 0

    def _cards_left ( self ) :
        '''factor out a simple calculation'''
        return len( self._access ) - self._top

    def __len__ ( self ) :
        return self._cards_left()

    def deal( self ) -> Card :
        '''
        Return the topmost card of the Deck.

        Returns:
            Card

        State:
            increments self._top

        Raises:
            EmptyDeckError
        '''
        if self._top > 51 :
            raise EmptyDeckError( Deck.ex_text_1 )
        C = self._cards[ self._access[ self._top ] ]
        self._top += 1
        return C

    def shuffle( self, times:int = 1 ) :
        '''
        Permute the access array for the undealt portion of the Deck

        Args:
            times: int, default 1, number of times to shuffle
        Raises:
            EmptyDeckError
        State:
            permutes the values in self._access
        '''

        if self._top > 51 :
            raise EmptyDeckError( Deck.ex_text_2 )

        if self._top == 51 :
            return # "shuffle" of one-card deck is a no-op

        if self._top :
            # shuffle remaining cards in partially-dealt deck.
            remaining_deck = self._access[ self._top : ]
            for count in range( times ) :
                random.shuffle( remaining_deck )
            self._access[ self._top : ] = remaining_deck
        else :
            # _top is 0, no cards dealt, save a little time
            # by not doing the slice operations.
            for count in range( times ) :
                random.shuffle( self._access ) # shuffle whole deck

    def cut( self, cards_to_take:int = None, minimum_cut:int = 5 ) :
        '''
        Cut the deck.
        Args:
            cards_to_take: if None, "about" half the cards are taken,
                if given, must be greater than minimum_cut and
                less than or equal (self._cards_left - minimum_cut)

            minimum_cut: int, fewest cards that can be taken or left
                by the cut. 5 is the convention for Poker.

        Raises:
            EmptyDeckError

        State:
            Modifies contents of self._access for undealt portion.

        '''

        middle_of_the_pack = self._cards_left() - (2 * minimum_cut )

        if middle_of_the_pack  < 0 :
            # there are not 2*minimum_cut cards in the deck
            raise EmptyDeckError( Deck.ex_text_5 )

        if cards_to_take is None : # "are" None?
            cards_to_take = minimum_cut + random.randint( 0, middle_of_the_pack )
        else :
            if cards_to_take < minimum_cut \
            or cards_to_take > ( self._cards_left() - minimum_cut ) :
                # cut would take or leave less than the minimum
                raise EmptyDeckError( Deck.ex_text_5 )

        # yeah, this could be done in one statement. bite me.
        already_dealt_cards = self._access[ : self._top ]
        cut_pile = self._access[ self._top : self._top + cards_to_take ]
        left_pile = self._access[ self._top + cards_to_take : ]
        self._access = already_dealt_cards + left_pile + cut_pile

    def put_back_card( self, card: Card ) -> int :
        '''
        Return a single Card dealt from this Deck, to the bottom.

        Args:
            card: Card object dealt from this Deck
        Raises:
            MismatchedDeckError if card not from this Deck
            MismatchedDeckError if card has not been dealt
        Returns:
            int: number of Cards now in Deck
        '''

        if card._deck is not self :
            raise MismatchedDeckError( Deck.ex_text_3 )

        # Has it been dealt?
        C = card.position()
        if C in self._access[ self._top : ] :
            # value C is somewhere >= top in _access, ergo, not yet dealt
            # or perhaps being returned a second time?
            raise MismatchedDeckError( Deck.ex_text_4 )

        # Remove value C from _access, append it to the end, and
        # adjust top. This puts card C at the bottom of the deck.
        self._access.remove( C )
        self._access.append( C )
        self._top -= 1
        return self._cards_left()

    def put_back_pile( self, pile: Pile ) -> int :
        '''
        Return all Cards of a Pile to this Deck, provided they were
        dealt from it.

        Args:
            pile: Pile object
        Returns:
            number of undealt Cards now in the Deck
        State:
            changes self._access and self._top
            also empties all Cards from the given pile
             (not very "functional" is it)
        '''

        while len( pile ) :
            self.put_back_card( pile.remove() )
        return self._cards_left()

'''
Test code, pure tedium
'''

if __name__ == '__main__' :

    '''
    Test suite for Suit. (Sweet!)
    n.b. this found FOUR BUGS in the first-draft code. Sheesh.
    '''
    assert CLUB.color() == 'black'
    assert SPADE.color() == CLUB.color()
    assert DIAMOND.color() != CLUB.color()
    assert HEART.color() == DIAMOND.color()
    assert CLUB.name() == 'Club'
    assert HEART.name() == 'Heart'
    assert SPADE.name() == 'Spade'
    for S in (CLUB,DIAMOND,HEART,SPADE) :
        assert S.plural() == S.name()+'s'
    assert SPADE.rank() == 3
    assert SPADE.rank() > HEART.rank()
    assert HEART.rank() > DIAMOND.rank()
    assert DIAMOND.rank() > CLUB.rank()
    assert DIAMOND.image() == '♦'
    assert SPADE.image() == '♠'
    '''
    Testing Card Bugs 1 2 3
    '''
    cd = Card(12)
    assert cd.suit_rank() == 0
    assert cd.suit() is CLUB
    assert cd.rank() == Rank.rA
    assert cd.point_count() == 11
    assert cd.name() == 'A'
    assert cd.position() == 12
    assert cd.__repr__() == 'Card( 12 )'
    assert str(cd) == '♣A'
    C = [ Card( p ) for p in range(52) ]
    #for s in ( 0, 13, 26, 39 ) :
        #for x in range(13) :
            #print( ' ', C[ s+x ], end=' ')
        #print()
    #print()
    assert C[0] < C[1] # deuce less than trey
    assert C[5] < 8 # seven less than Rank(8)
    assert C[0] == C[13] # deuces are equal
    assert C[12] > C[24] # C Ace beats D King
    assert C[8] >= C[8+13]
    assert C[8] >= C[7+13]
    assert C[8] <= C[8+13]
    assert C[8] <= C[9+13]
    assert not C[0] > C[1] # test that they do return false
    assert not C[5] > 8
    assert not C[0] == C[1]
    '''
    Testing Deck, Bugs: 1 2
    '''
    D0 = Deck()
    for j in range(52) :
        assert D0.deal() == C[j]
    # D0 is now an empty deck
    try :
        x = D0.deal()
        assert False
    except EmptyDeckError as e:
        assert str(e) == Deck.ex_text_1

    try :
        D0.shuffle()
        assert False
    except EmptyDeckError as e:
        assert str(e) == Deck.ex_text_2

    D0 = Deck() # new deck
    try :
        D0.cut() # default cut
    except Exception as e :
        assert False
    for j in range(42) : # deal all but 10 cards
        C = D0.deal()
    assert len(D0) == 10
    try :
        D0.cut() # should work
    except Exception as e :
        assert False
    C = D0.deal()
    try :
        D0.cut() # has 9 cards, should fail
        assert False
    except EmptyDeckError as e :
        assert str(e) == Deck.ex_text_5
    try :
        D0.cut( minimum_cut = 4 )
    except Exception as e :
        assert False

    try :
        D0.cut( cards_to_take = 6, minimum_cut = 4 )
        assert False
    except EmptyDeckError as e :
        assert str(e) == Deck.ex_text_5

    D0 = Deck()
    D0.cut( cards_to_take = 13 )
    C0 = D0.deal()
    assert C0.suit() is DIAMOND
    assert C0.rank() == Rank.r2

    D0 = Deck()
    C0 = D0.deal()
    try :
        assert len(D0) == 51
        assert 52 == D0.put_back_card( C0 )
    except Exception as e :
        assert False
    C0 = D0.deal()
    D1 = Deck()
    C1 = D1.deal()
    try :
        D0.put_back_card( C1 )
        assert False
    except MismatchedDeckError as e :
        assert str(e) == Deck.ex_text_3
    try :
        D0.put_back_card( C0 ) # this should work
    except Exception as e :
        assert False
    try :
        D0.put_back_card( C0 ) # this should not
    except MismatchedDeckError as e :
        assert str(e) == Deck.ex_text_4

    D1 = Deck()
    D2 = Deck()
    random.seed(4095)
    D1.shuffle()
    random.seed(4095)
    D2.shuffle()
    for j in range(52):
        cd = D1.deal()
        n = D1.put_back_card( cd )
        assert n == 52
    for j in range(52):
        c1 = D1.deal()
        c2 = D2.deal()
        assert c1 == c2 and c1.suit() == c2.suit()
    D3 = Deck()
    '''
    Testing Pile and Deck
    '''
    D0 = Deck()
    east = Pile()
    north = Pile()
    west = Pile()
    south = Pile()
    for j in range(13) : # deal a hand of bridge
        east.receive( D0.deal() )
        north.receive( D0.deal() )
        west.receive( D0.deal() )
        south.receive( D0.deal() )
    assert south[0] == Card(51)
    assert east[-1] == Card(0)
    D0.put_back_pile( east )
    assert len(east) == 0
    assert len(D0) == 13

    D1 = Deck()
    C1 = D1.deal()
    P0 = Pile()
    P0.receive(C1)
    try :
        P0.receive( C1 )
        assert False
    except PilingError as p :
        pass
    try :
        P0.receive( 50 )
        assert False
    except ValueError as v :
        pass
    try :
        P0.receive_pile( 'what?' )
        assert False
    except ValueError as v :
        pass
    try :
        x = P0.remove_pile( 2 )
        assert False
    except PilingError as p :
        pass

    D1 = Deck()
    P0 = Pile()
    for j in range(13) :
        # deal 13 clubs, last is pos. 13
        P0.receive( D1.deal() )
    P1 = P0.remove_pile( 6 ) # take off the top 6
    assert 6 == len(P1)
    assert 7 == len(P0)
    # empty P1 into temp Pile, put cards back in P0,
    # discard temp Pile
    P0.receive_pile( P1.remove_pile(6) )
    assert 0 == len(P1) # now empty
    assert 13 == len(P0) # now back to 13
    assert 12 == P0[0].position() # top card is former top card
    assert 7 == P0[5].position()
    assert 0 == P0[12].position()

    def dump_pile( p:Pile ) :
        for c in p :
            print( c, end=' ' )
        print()

    D2 = Deck()
    D2.shuffle( times=5 )
    P2 = Pile()
    for j in range(13) : P2.receive( D2.deal() )
    #dump_pile(P2)
    P2.sort()
    #dump_pile(P2)
    for j in range(1,13) :
        assert P2[j].position() > P2[j-1].position()
    P2.sort( reverse=True )
    #dump_pile(P2)
    for j in range(1,13) :
        assert P2[j].position() < P2[j-1].position()
    P2.turn_over()
    #dump_pile(P2)
    for j in range(1,13) :
        assert P2[j].position() > P2[j-1].position()
