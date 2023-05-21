"""
    File name: zole/round.py
"""

from typing import List

from games.zole.dealer import ZoleDealer
from games.zole.player import ZolePlayer, ZoleTable

from games.zole.utils.move import ZoleMove, DealHandMove, MakePassMove, PlayCardMove, CallMove, MakeTakeMove, BuryCardMove
from games.zole.utils.action_event import PassTableAction, CallActionEvent, TakeTableAction, PlayCardAction, BuryCardAction
from games.zole.utils.tray import Tray
from games.zole.utils.zole_card import ZoleCard


class ZoleRound:

    @property
    def dealer_id(self) -> int:
        return self.tray.dealer_id

    @property
    def board_id(self) -> int:
        return self.tray.board_id

    @property
    def large_player_id(self) -> int or None:
        if self.contract_take_move:
            return self.contract_take_move.player.player_id
        return None

    @property
    def round_phase(self):
        if self.is_over():
            return 'game over'
        elif self.is_bidding_over():
            return 'play card'
        else:
            return 'choose table'

    def __init__(self, num_players: int, board_id: int, np_random):
        """ Initialize the round class

            The round class maintains the following instances:
                1) dealer: the dealer of the round; dealer has trick_pile
                2) players: the players in the round; each player has his own hand_pile
                3) current_player_id: the id of the current player who has the move
                4) play_card_count: count of PlayCardMoves
                5) move_sheet: history of the moves of the players (including the deal_hand_move)
                6) won_trick_points: points already gained for each team during the round

        Args:
            num_players: int
            board_id: int
            np_random
        """
        tray = Tray(board_id=board_id)
        dealer_id = tray.dealer_id
        self.tray = tray
        self.np_random = np_random
        self.dealer: ZoleDealer = ZoleDealer(self.np_random)
        self.players: List[ZolePlayer] = []
        self.table: ZoleTable = ZoleTable(np_random=self.np_random)
        for player_id in range(num_players):
            self.players.append(ZolePlayer(player_id=player_id, np_random=self.np_random))
        self.current_player_id: int = self.get_person_after_dealer().player_id
        self.play_card_count: int = 0
        self.contract_take_move: MakeTakeMove or None = None
        self.won_trick_points = [0, 0]  # count of won points by side
        self.won_trick_cards = [[], []]  # count of won cards by side
        self.move_sheet: List[ZoleMove] = []
        self.move_sheet.append(DealHandMove(dealer=self.players[dealer_id], shuffled_deck=self.dealer.shuffled_deck))
        self.buried_cards: List[ZoleCard] = []

    def is_bidding_over(self) -> bool:
        """ Return whether the current bidding is over
        """
        last_make_pass_moves: List[MakePassMove] = []
        last_bury_card_moves: List[BuryCardMove] = []

        for move in reversed(self.move_sheet):
            if isinstance(move, PlayCardMove):
                return True
            elif isinstance(move, MakePassMove):
                last_make_pass_moves.append(move)
                if len(last_make_pass_moves) == 3:
                    return True
            elif isinstance(move, MakeTakeMove):
                return False
            elif isinstance(move, BuryCardMove):
                last_bury_card_moves.append(move)
                if len(last_bury_card_moves) == 2:
                    return True
            elif isinstance(move, DealHandMove):
                return False
            else:
                raise NotImplementedError
        return False

    def is_over(self) -> bool:
        """ Return whether the current game is over
        """
        if not self.is_bidding_over():
            return False

        if not self.contract_take_move:
            return True

        for player in self.players:
            if player.hand:
                return False

        return True

    def get_current_player(self) -> ZolePlayer:
        return self.players[self.current_player_id]

    def get_person_after_dealer(self) -> ZolePlayer:
        return self.players[(self.dealer_id + 1) % 3]

    def get_second_person_after_dealer(self) -> ZolePlayer:
        return self.players[(self.dealer_id + 2) % 3]

    def get_trick_moves(self) -> List[PlayCardMove]:
        trick_moves: List[PlayCardMove] = []
        if self.is_bidding_over():
            if self.play_card_count > 0:
                trick_pile_count = self.play_card_count % 3
                if trick_pile_count == 0:
                    trick_pile_count = 3  # wch: note this
                for move in self.move_sheet[-trick_pile_count:]:
                    if isinstance(move, PlayCardMove):
                        trick_moves.append(move)
                if len(trick_moves) != trick_pile_count:
                    raise Exception(f'get_trick_moves: count of trick_moves={[str(move.card) for move in trick_moves]} does not equal {trick_pile_count}')
        return trick_moves

    def make_call(self, action: CallActionEvent):
        # when current_player takes CallActionEvent step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        if isinstance(action, PassTableAction):
            self.move_sheet.append(MakePassMove(current_player))
        elif isinstance(action, TakeTableAction):
            take_table_move = MakeTakeMove(current_player, action)
            current_player = self.players[self.current_player_id]
            current_player.take_table(self.table.hand)
            self.contract_take_move = take_table_move
            self.move_sheet.append(take_table_move)
            return  # prevent current player rotation
        elif isinstance(action, BuryCardAction):
            buried_card: ZoleCard = action.card
            bury_card_move = BuryCardMove(current_player, action)
            current_player = self.players[self.current_player_id]

            current_player.remove_card_from_hand(card=buried_card)
            self.won_trick_points[0] += buried_card.card_to_points()
            self.won_trick_cards[0].append(buried_card)
            self.move_sheet.append(bury_card_move)
            self.buried_cards.append(buried_card)

            if len(current_player.hand) > 8:
                return  # prevent current player rotation
        if self.is_bidding_over():
            if not self.is_over():
                self.current_player_id = self.get_person_after_dealer().player_id
        else:
            self.current_player_id = (self.current_player_id + 1) % 3

    def play_card(self, action: PlayCardAction):
        # when current_player takes PlayCardAction step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(PlayCardMove(current_player, action))

        card = action.card
        current_player.remove_card_from_hand(card=card)
        self.play_card_count += 1

        trick_moves = self.get_trick_moves()

        if len(trick_moves) == 3:
            winning_card = trick_moves[0].card
            trick_winner = trick_moves[0].player
            trick_points = winning_card.card_to_points()
            trick_cards = [winning_card]
            for move in trick_moves[1:]:
                trick_card = move.card
                trick_cards.append(trick_card)
                trick_player = move.player
                trick_points += trick_card.card_to_points()
                if winning_card.is_same_suit_or_trump(trick_card.card_id):
                    if trick_card.card_id > winning_card.card_id:
                        winning_card = trick_card
                        trick_winner = trick_player

            self.current_player_id = trick_winner.player_id
            if self.current_player_id == self.contract_take_move.player.player_id:
                self.won_trick_cards[0].extend(trick_cards)
                self.won_trick_points[0] += trick_points
            else:
                self.won_trick_cards[1].extend(trick_cards)
                self.won_trick_points[1] += trick_points
        else:
            self.current_player_id = (self.current_player_id + 1) % 3

    def print_scene(self):
        print(f'===== Board: {self.tray.board_id} move: {len(self.move_sheet)} player: {self.players[self.current_player_id]} phase: {self.round_phase} =====')
        print(f'dealer={self.players[self.tray.dealer_id]}')
        if not self.is_bidding_over() or self.play_card_count == 0:
            last_move = self.move_sheet[-1]
            last_call_text = f'{last_move}' if isinstance(last_move, CallMove) else 'None'
            print(f'last call: {last_call_text}')
        if self.is_bidding_over() and self.contract_take_move:
            print(f'big player: {self.contract_take_move.player}')
        for player in self.players:
            print(f'{player}: {[str(card) for card in player.hand]}')
        print(f'Table: {[str(card) for card in self.table.hand]}')
        if self.is_bidding_over():
            trick_pile = ['None', 'None', 'None']
            for trick_move in self.get_trick_moves():
                trick_pile[trick_move.player.player_id] = trick_move.card
            print(f'trick_pile: {[str(card) for card in trick_pile]}')
