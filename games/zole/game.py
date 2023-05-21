"""
    File name: zole/game.py
"""

from typing import List

from games.zole.judger import ZoleJudger
from games.zole.round import ZoleRound
from games.zole.utils.action_event import ActionEvent, CallActionEvent, PlayCardAction

import numpy as np


class ZoleGame:
    """ Game class. This class will interact with outer environment.
    """

    def __init__(self, allow_step_back=False):
        """Initialize the class ZoleGame
        """
        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState(1)
        self.judger: ZoleJudger = ZoleJudger(game=self)
        self.actions: [ActionEvent] = []  # must reset in init_game
        self.round: ZoleRound or None = None  # must reset in init_game
        self.num_players: int = 3

    def init_game(self):
        """ Initialize all characters in the game and start round 1
        """
        board_id = self.np_random.choice([1, 2, 3])
        self.actions: List[ActionEvent] = []
        self.round = ZoleRound(num_players=self.num_players, board_id=board_id, np_random=self.np_random)

        self._deal_cards()

        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def _deal_cards(self):
        self._deal_player_cards()
        self.round.dealer.deal_table_cards(table=self.round.table, num=2)
        self._deal_player_cards()

    def _deal_player_cards(self):
        first_person_after_dealer = self.round.get_person_after_dealer()
        self.round.dealer.deal_cards(player=first_person_after_dealer, num=4)

        second_person_after_dealer = self.round.get_second_person_after_dealer()
        self.round.dealer.deal_cards(player=second_person_after_dealer, num=4)

        dealer = self.round.players[self.round.dealer_id]
        self.round.dealer.deal_cards(player=dealer, num=4)

    def step(self, action: ActionEvent):
        """ Perform game action and return next player number, and the state for next player
        """
        if isinstance(action, CallActionEvent):
            self.round.make_call(action=action)
        elif isinstance(action, PlayCardAction):
            self.round.play_card(action=action)
        else:
            raise Exception(f'Unknown step action={action}')
        self.actions.append(action)
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def get_num_players(self) -> int:
        """ Return the number of players in the game
        """
        return self.num_players

    @staticmethod
    def get_num_actions() -> int:
        """ Return the number of possible actions in the game
        """
        return ActionEvent.get_num_actions()

    def get_player_id(self):
        """ Return the current player that will take actions soon
        """
        return self.round.current_player_id

    def is_over(self) -> bool:
        """ Return whether the current game is over
        """
        return self.round.is_over()

    def get_state(self, player_id: int):  # wch: not really used
        """ Get player's state

        Return:
            state (dict): The information of the state
        """
        return {
            'player_id': player_id,
            'current_player_id': self.round.current_player_id,
            'hand': self.round.players[player_id].hand
        }
