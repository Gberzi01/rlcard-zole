"""
    File name: envs/zole.py
"""

import numpy as np
from collections import OrderedDict

from rlcard.envs import Env

from games.zole import Game
from games.zole.game import ZoleGame
from games.zole.round import ZoleRound
from games.zole.utils.action_event import ActionEvent


class ZoleEnv(Env):
    """ Zole Environment
    """

    def __init__(self, config):
        self.name = 'zole'
        self.game = Game()
        super().__init__(config=config)
        self.zolePayoffDelegate = DefaultZolePayoffDelegate()
        self.zoleStateExtractor = DefaultZoleStateExtractor()
        self.zolePerformanceTracker = DefaultZolePerformanceTracker(config.get('display_performance_interval', 500))
        state_shape_size = self.zoleStateExtractor.get_state_shape_size()
        self.state_shape = [[1, state_shape_size] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]
        self.large_win_incentive: int = config.get('large_win_incentive', 0)

    def reset(self):
        self.zolePerformanceTracker.track_round(self.game.round)
        return super().reset()    

    def get_payoffs(self):
        """ Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        """
        return self.zolePayoffDelegate.get_payoffs(game=self.game, large_win_incentive=self.large_win_incentive)

    def get_perfect_information(self):
        """ Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        """
        raise NotImplementedError

    def _extract_state(self, state):  # wch: don't use state 211126
        """ Extract useful information from state for RL.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        """
        extracted_state = self.zoleStateExtractor.extract_state(game=self.game)
        extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def _decode_action(self, action_id):
        """ Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (ActionEvent): The action that will be passed to the game engine.
        """
        return ActionEvent.from_action_id(action_id=action_id)

    def _get_legal_actions(self):
        """ Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.
        """
        raise NotImplementedError  # wch: not needed


class ZolePayoffDelegate(object):
    def get_payoffs(self, game: ZoleGame, large_win_incentive: int):
        """ Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        """
        raise NotImplementedError


class DefaultZolePayoffDelegate(ZolePayoffDelegate):
    def get_payoffs(self, game: ZoleGame, large_win_incentive: int):
        """ Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        """

        large_player_id = game.round.large_player_id
        if large_player_id is not None:
            won_trick_points = game.round.won_trick_points
            [large_player_score, small_player_score] = _points_to_score(
                won_trick_points[0],
                won_trick_points[1],
                large_win_incentive
            )
            payoffs = []
            for player_id in range(3):
                payoff = large_player_score if player_id == large_player_id else small_player_score
                payoffs.append(payoff)
        else:
            payoffs = [0, 0, 0]
        return np.array(payoffs)


class ZoleStateExtractor(object):  # interface
    def get_state_shape_size(self) -> int:
        raise NotImplementedError

    def extract_state(self, game: ZoleGame):
        """ Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            game (ZoleGame): The game

        Returns:
            (numpy.array): The extracted state
        """
        raise NotImplementedError

    @staticmethod
    def get_legal_actions(game: ZoleGame):
        """ Get all legal actions for current state.

        Returns:
            (OrderedDict): A OrderedDict of legal actions' id.
        """
        legal_actions = game.judger.get_legal_actions()
        legal_actions_ids = {action_event.action_id: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)


class DefaultZoleStateExtractor(ZoleStateExtractor):
    def get_state_shape_size(self) -> int:
        state_shape_size = 0
        state_shape_size += 3 * 26  # hands_rep_size
        state_shape_size += 3 * 26  # trick_rep_size
        state_shape_size += 26  # hidden_cards_rep_size
        state_shape_size += 3  # dealer_rep_size
        state_shape_size += 3  # large_player_rep_size
        state_shape_size += 3  # current_player_rep_size
        state_shape_size += 1  # is_bidding_rep_size
        return state_shape_size

    def extract_state(self, game: ZoleGame):
        """ Extract useful information from state for RL.

        Args:
            game (ZoleGame): The game

        Returns:
            (numpy.array): The extracted state
        """
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player_id = game.round.get_current_player().player_id
        large_player_id = game.round.large_player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(26, dtype=int) for _ in range(3)]
        if not game.is_over():
            for card in game.round.players[current_player_id].hand:
                hands_rep[current_player_id][card.card_id] = 1

        # construct trick_pile_rep
        trick_pile_rep = [np.zeros(26, dtype=int) for _ in range(3)]
        if game.round.is_bidding_over() and not game.is_over():
            trick_moves = game.round.get_trick_moves()
            for move in trick_moves:
                player = move.player
                card = move.card
                trick_pile_rep[player.player_id][card.card_id] = 1

        hidden_cards_rep = self._construct_hidden_cards_rep(game, current_player_id, large_player_id)

        # construct large_player_rep
        large_player_rep = np.zeros(3, dtype=int)
        if large_player_id is not None:
            large_player_rep[large_player_id] = 1

        # construct dealer_rep
        dealer_rep = np.zeros(3, dtype=int)
        dealer_rep[game.round.tray.dealer_id] = 1

        # construct current_player_rep
        current_player_rep = np.zeros(3, dtype=int)
        current_player_rep[current_player_id] = 1

        # construct is_bidding_rep
        is_bidding_rep = np.array([1] if game.round.is_bidding_over() else [0])

        rep = []
        rep += hands_rep
        rep += trick_pile_rep
        rep.append(hidden_cards_rep)
        rep.append(dealer_rep)
        rep.append(large_player_rep)
        rep.append(current_player_rep)
        rep.append(is_bidding_rep)

        obs = np.concatenate(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = obs
        extracted_state['raw_hands_rep'] = hands_rep[current_player_id]
        extracted_state['raw_large_player_rep'] = large_player_rep

        return extracted_state

    @staticmethod
    def _construct_hidden_cards_rep(game: ZoleGame, current_player_id: int, large_player_id: int) -> np.ndarray:
        hidden_cards_rep = np.zeros(26, dtype=int)
        if game.is_over():
            return hidden_cards_rep

        # opponent hands
        for player in game.round.players:
            if player.player_id != current_player_id:
                for card in player.hand:
                    hidden_cards_rep[card.card_id] = 1

        # table cards or large player buried cards
        if game.round.is_bidding_over():
            if current_player_id != large_player_id:
                for card in game.round.buried_cards:
                    hidden_cards_rep[card.card_id] = 1
        else:
            for card in game.round.table.hand:
                hidden_cards_rep[card.card_id] = 1

        return hidden_cards_rep


class DefaultZolePerformanceTracker(object):
    def __init__(self, display_performance_interval: int):
        self.pick_up_table_counts = np.zeros(3, dtype=int)
        self.won_games_large = np.zeros(3, dtype=int)
        self.won_games_small = np.zeros(3, dtype=int)
        self.round_counter: int = 1
        self.display_performance_interval = display_performance_interval

    def track_round(self, round: ZoleRound or None):
        if round:
            self._count_performance(round)
            if self.round_counter % self.display_performance_interval == 0:
                self.display_performance()

        self.round_counter += 1

    def _count_performance(self, round: ZoleRound):
        if round.large_player_id is not None:
            self.pick_up_table_counts[round.large_player_id] += 1
            if round.won_trick_points[0] > 61:
                self.won_games_large[round.large_player_id] += 1
            else:
                for player_id in range(3):
                    if player_id == round.large_player_id:
                        continue
                    self.won_games_small[player_id] += 1

    def display_performance(self):
        large_percent_wins = []
        small_percent_wins = []
        games_as_large = []
        for played_id in range(3):
            games_as_large.append(self.get_games_as_large(played_id))
            large_percent_wins.append(self.get_large_percent_wins(played_id))
            small_percent_wins.append(self.get_small_percent_wins(played_id))

        print(f'Rounds played #{self.round_counter}')
        print(f'Pickup table counts {self.pick_up_table_counts}')
        print(f'Games won as large {large_percent_wins}')
        print(f'Games won as small {small_percent_wins}')
        print(f'Games played as large {games_as_large}')

    def get_large_percent_wins(self, played_id):
        return f'{self.won_games_large[played_id] / self.pick_up_table_counts[played_id]:.3f}'
    
    def get_small_percent_wins(self, played_id):
        games_played = sum(self.pick_up_table_counts)
        return f'{self.won_games_small[played_id] / (games_played - self.pick_up_table_counts[played_id]):.3f}'
    
    def get_games_as_large(self, played_id):
        return f'{self.pick_up_table_counts[played_id] / self.round_counter:.3f}'


def _points_to_score(large_player_points: int, small_player_points: int, large_win_incentive: int):
    if large_player_points + small_player_points != 120:
        raise ValueError

    points = large_player_points

    if points == 120:
        return [6 + large_win_incentive * 2, -3 - large_win_incentive]
    elif points >= 91:
        return [4 + large_win_incentive * 2, -2 - large_win_incentive]
    elif points >= 61:
        return [2 + large_win_incentive * 2, -1 - large_win_incentive]
    elif points > 31:
        return [-4, 2]
    elif points > 1:
        return [-6, 3]
    else:  # points == 0: Technically not correct, should check for won tricks
        return [-8, 4]
