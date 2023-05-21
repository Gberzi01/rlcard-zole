"""
    File name: zole/judger.py
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .game import ZoleGame

from games.zole.utils.action_event import ActionEvent, PlayCardAction, PassTableAction, TakeTableAction, BuryCardAction
from games.zole.utils.zole_card import ZoleCard
from games.zole.player import ZolePlayer


class ZoleJudger:
    """
        Judger decides legal actions for current player
    """

    def __init__(self, game: 'ZoleGame'):
        """ Initialize the class ZoleJudger
        :param game: ZoleGame
        """
        self.game: ZoleGame = game

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        if self.game.is_over():
            return []

        current_player = self.game.round.get_current_player()
        if not self.game.round.is_bidding_over():
            return self._get_bidding_legal_action(current_player)

        return self._get_trick_legal_actions(current_player)

    def _get_trick_legal_actions(self, current_player: ZolePlayer) -> List[ActionEvent]:
        legal_cards = self._get_legal_cards(current_player)

        return [PlayCardAction(card=card) for card in legal_cards]

    def _get_legal_cards(self, current_player: ZolePlayer) -> List[ZoleCard]:
        trick_moves = self.game.round.get_trick_moves()
        hand = current_player.hand

        if trick_moves and len(trick_moves) < 3:
            led_card: ZoleCard = trick_moves[0].card
            cards_of_led_suit = [card for card in hand if led_card.is_matching_strength(card.card_id)]
            if cards_of_led_suit:
                return cards_of_led_suit

        return hand

    @staticmethod
    def _get_bidding_legal_action(current_player: ZolePlayer) -> List[ActionEvent]:
        if len(current_player.hand) > 8:
            return [BuryCardAction(card=card) for card in current_player.hand]

        return [
            PassTableAction(),
            TakeTableAction()
        ]
