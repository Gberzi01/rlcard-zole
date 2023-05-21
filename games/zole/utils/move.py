"""
    File name: zole/utils/move.py

    These classes are used to keep a move_sheet history of the moves in a round.
"""

from games.zole.utils.action_event import ActionEvent, PlayCardAction, PassTableAction, TakeTableAction
from games.zole.utils.zole_card import ZoleCard
from games.zole.player import ZolePlayer


class ZoleMove(object):  # Interface
    pass


class PlayerMove(ZoleMove):  # Interface
    def __init__(self, player: ZolePlayer, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action


class CallMove(PlayerMove):  # Interface
    def __init__(self, player: ZolePlayer, action: ActionEvent):
        super().__init__(player=player, action=action)


class DealHandMove(ZoleMove):
    def __init__(self, dealer: ZolePlayer, shuffled_deck: [ZoleCard]):
        super().__init__()
        self.dealer = dealer
        self.shuffled_deck = shuffled_deck

    def __str__(self):
        shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
        return f'{self.dealer} deal shuffled_deck=[{shuffled_deck_text}]'


class MakePassMove(CallMove):
    def __init__(self, player: ZolePlayer):
        super().__init__(player=player, action=PassTableAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeTakeMove(CallMove):
    def __init__(self, player: ZolePlayer, take_action: TakeTableAction):
        super().__init__(player=player, action=take_action)
        self.action = take_action  # Note: keep type as TakeTableAction rather than ActionEvent

    def __str__(self):
        return f'{self.player} took table {self.action}'


class BuryCardMove(CallMove):
    def __init__(self, player: ZolePlayer, action: ActionEvent):
        super().__init__(player=player, action=action)
        self.action = action

    def __str__(self):
        return f'{self.player} buried {self.action}'


class PlayCardMove(PlayerMove):
    def __init__(self, player: ZolePlayer, action: PlayCardAction):
        super().__init__(player=player, action=action)
        self.action = action  # Note: keep type as PlayCardAction rather than ActionEvent

    @property
    def card(self):
        return self.action.card

    def __str__(self):
        return f'{self.player} plays {self.action}'
