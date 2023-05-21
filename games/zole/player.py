"""
    File name: zole/player.py
"""

from typing import List

from games.zole.utils.zole_card import ZoleCard


class ZolePlayer:

    def __init__(self, player_id: int, np_random):
        """ Initialize a ZolePlayer player class

        Args:
            player_id (int): id for the player
        """
        if player_id < 0 or player_id > 2:
            raise Exception(f'ZolePlayer has invalid player_id: {player_id}')
        self.np_random = np_random
        self.player_id: int = player_id
        self.hand: List[ZoleCard] = []

    def remove_card_from_hand(self, card: ZoleCard):
        self.hand.remove(card)

    def take_table(self, table_cards: List[ZoleCard]):
        self.hand.extend(table_cards)

    def __str__(self):
        return ['N', 'E', 'S'][self.player_id]


class ZoleTable:

    def __init__(self, np_random):
        """ Initialize a ZoleTable table class
        """
        self.np_random = np_random
        self.hand: List[ZoleCard] = []

    def __str__(self):
        return 'T'


if __name__ == '__main__':
    player = ZolePlayer(0, 1)
    print(player)
