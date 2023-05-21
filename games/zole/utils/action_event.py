"""
    File name: zole/utils/action_event.py
"""

from games.zole.utils.zole_card import ZoleCard


# ====================================
# Action_ids:
#       0 -> deal_cards
#       1 -> pass_table
#       2 -> take_table
#       3 to 28 -> bury_card
#       29 to 54 -> play_card
# ====================================

class ActionEvent(object):  # Interface
    deal_cards_action_id = 0
    pass_table_action_id = 1
    take_table_action_id = 2
    first_bury_card_action_id = 3
    first_play_card_action_id = 29

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def from_action_id(action_id: int):
        if action_id == ActionEvent.pass_table_action_id:
            return PassTableAction()
        elif action_id == ActionEvent.take_table_action_id:
            return TakeTableAction()
        elif ActionEvent.first_bury_card_action_id <= action_id < ActionEvent.first_play_card_action_id:
            card_id = action_id - ActionEvent.first_bury_card_action_id
            card = ZoleCard.card(card_id=card_id)
            return BuryCardAction(card=card)
        elif ActionEvent.first_play_card_action_id <= action_id < ActionEvent.first_play_card_action_id + 26:
            card_id = action_id - ActionEvent.first_play_card_action_id
            card = ZoleCard.card(card_id=card_id)
            return PlayCardAction(card=card)
        else:
            raise Exception(f'ActionEvent from_action_id: invalid action_id={action_id}')

    @staticmethod
    def get_num_actions():
        """ Return the number of possible actions in the game
        """
        return 3 + 26 + 26  # deal_card, pass_table, take_table + bury_cards + take_cards


class CallActionEvent(ActionEvent):  # Interface
    pass


class PassTableAction(CallActionEvent):
    def __init__(self):
        super().__init__(action_id=ActionEvent.pass_table_action_id)

    def __str__(self):
        return 'pass'

    def __repr__(self):
        return 'pass'


class TakeTableAction(CallActionEvent):
    def __init__(self):
        super().__init__(action_id=ActionEvent.take_table_action_id)

    def __str__(self):
        return 'pick up'

    def __repr__(self):
        return 'pick up'


class BuryCardAction(CallActionEvent):
    def __init__(self, card: ZoleCard):
        play_card_action_id = ActionEvent.first_bury_card_action_id + card.card_id
        super().__init__(action_id=play_card_action_id)
        self.card: ZoleCard = card

    def __str__(self):
        return f'{self.card}'

    def __repr__(self):
        return f'{self.__str__()}'


class PlayCardAction(ActionEvent):
    def __init__(self, card: ZoleCard):
        play_card_action_id = ActionEvent.first_play_card_action_id + card.card_id
        super().__init__(action_id=play_card_action_id)
        self.card: ZoleCard = card

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"{self.card}"
