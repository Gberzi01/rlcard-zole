"""
    File name: zole/utils/zole_card.py
"""

from rlcard.games.base import Card


class ZoleCard(Card):
    cards = [
        # Hearts
        '9H',
        'KH',
        'TH',
        'AH',

        # Spades
        '9S',
        'KS',
        'TS',
        'AS',

        # Clubs
        '9C',
        'KC',
        'TC',
        'AC',

        # Trumps
        '7D',
        '8D',
        '9D',
        'KD',
        'TD',
        'AD',
        'JD',
        'JH',
        'JS',
        'JC',
        'QD',
        'QH',
        'QS',
        'QC',
    ]

    card_points = [
        # Hearts
        0,
        4,
        10,
        11,

        # Spades
        0,
        4,
        10,
        11,

        # Clubs
        0,
        4,
        10,
        11,

        # Trumps
        0,
        0,
        0,
        4,
        10,
        11,
        2,
        2,
        2,
        2,
        3,
        3,
        3,
        3,
    ]

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> [Card]:
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        self.card_id = self.cards.index(f'{self.rank}{self.suit}')

    def is_trump_card(self):
        return self.card_id > 11

    def card_to_points(self):
        return self.card_points[self.card_id]

    def is_same_suit_or_trump(self, card_id):
        if 12 <= card_id:
            return True
        elif 8 <= card_id < 12:
            return 8 <= self.card_id < 12
        elif 4 <= card_id < 8:
            return 4 <= self.card_id < 8
        else:  # 0 <= card_id < 4
            return self.card_id < 4

    def is_matching_strength(self, card_id):
        if 0 <= self.card_id < 4:
            return 0 <= card_id < 4
        elif 4 <= self.card_id < 8:
            return 4 <= card_id < 8
        elif 8 <= self.card_id < 12:
            return 8 <= card_id < 12
        elif self.card_id >= 12:
            return card_id >= 12
        return False

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'


'''
    deck is always in order from
    9H, KH, TH, AH, 9S, KS, TS, AS, 9C, KC, TC, AC,
    7D, 8D, 9D, KD, TD, AD, JD, JH, JS, JC, QD, QH, QS, QC
'''
_deck = [ZoleCard(suit=card[1], rank=card[0]) for [*card] in ZoleCard.cards]

if __name__ == '__main__':
    print(_deck)
