"""
    File name: zole/dealer.py
"""

from typing import List

from games.zole.player import ZolePlayer, ZoleTable
from games.zole.utils.zole_card import ZoleCard


class ZoleDealer:
    """ Initialize a ZoleDealer dealer class
    """

    def __init__(self, np_random):
        """ set shuffled_deck, set stock_pile
        """
        self.np_random = np_random
        self.shuffled_deck: List[ZoleCard] = ZoleCard.get_deck()  # keep a copy of the shuffled cards at start of round
        self.np_random.shuffle(self.shuffled_deck)
        self.stock_pile: List[ZoleCard] = self.shuffled_deck.copy()

    def deal_cards(self, player: ZolePlayer, num: int):
        """ Deal some cards from stock_pile to one player

        Args:
            player (ZolePlayer): The ZolePlayer object
            num (int): The number of cards to be dealt
        """
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())

    def deal_table_cards(self, table: ZoleTable, num: int):
        """ Deal some cards from stock_pile to table

        Args:
            table (ZoleTable): The ZoleTable object
            num (int): The number of cards to be dealt
        """
        for _ in range(num):
            table.hand.append(self.stock_pile.pop())
