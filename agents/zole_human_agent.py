from rlcard.utils.utils import print_card
from games.zole.utils.zole_card import ZoleCard
from games.zole.utils.action_event import ActionEvent, PlayCardAction


class HumanAgent(object):
    """ A human agent for Zole. It can be used to play alone for understand how the Zole code runs
    """

    def __init__(self, num_actions):
        """ Initialize the human agent

        Args:
            num_actions (int): the size of the output action space
        """
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state):
        """ Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        """
        state['raw_legal_actions'].sort()

        _print_state(
            state['raw_legal_actions'],
            state['raw_hands_rep'],
            state['action_record'],
            state['raw_large_player_rep'],
        )
        
        action = int(input('>> You choose action (integer): '))
        while action < 0 or action >= len(state['legal_actions']):
            print('Action illegal...')
            action = int(input('>> Re-choose action (integer): '))
        return ActionEvent.from_action_id(state['raw_legal_actions'][action])

    def eval_step(self, state):
        """ Predict the action given the current state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action chosen by the human agent
        """
        return self.step(state), {}


def _print_state(raw_legal_actions, raw_hand_rep, action_record, raw_large_player_rep):
    """ Print out the state
    """

    print('\n=============   Player Large   ===============')
    print(raw_large_player_rep)

    play_card_list = []
    for pair in action_record:
        if isinstance(pair[1], PlayCardAction):
            play_card_list.append(pair)

    trick_count = len(play_card_list) // 3

    last_trick_card_list = [None, None, None]
    if trick_count > 0:
        print('\n=============   Last Trick  ===============')
        for pair in play_card_list[(trick_count - 1) * 3:trick_count * 3]:
            last_trick_card_list[pair[0]] = pair[1].card
        print_card(last_trick_card_list)

    print('\n=============   Current Trick  ===============')
    current_trick_card_list = [None, None, None]
    for pair in play_card_list[trick_count * 3:]:
        current_trick_card_list[pair[0]] = pair[1].card
    print_card(current_trick_card_list)

    print('\n=============   Your Hand   ===============')
    _hand_card_list = []
    for card_id in range(0, 26):
        if raw_hand_rep[card_id] == 1:
            _hand_card_list.append(ZoleCard.card(card_id=card_id))
    print_card(_hand_card_list)

    print('\n=========== Actions You Can Choose ===========')
    _action_list = []
    for index, action_id in enumerate(raw_legal_actions):
        action_event = ActionEvent.from_action_id(action_id=action_id)
        _action_list.append(f'{index}: {action_event}')
    print(', '.join(_action_list))
