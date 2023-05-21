""" A toy example of self playing for Zole
"""
import envs
from defined_agents import get_random_agent, get_human_agent
from games.zole.utils.action_event import PlayCardAction

import argparse
import torch

import rlcard
from rlcard.utils.utils import print_card
from rlcard.utils import set_seed


def get_env():
    seed_id = 2
    set_seed(seed_id)

    return rlcard.make(
        'zole',
        {'seed': seed_id}
    )


def start_game_loop(args):
    print('>> Zole human agent')

    env = get_env()
    env.set_agents([
        get_human_agent(env),
        get_random_agent(env),
        torch.load(args.agent_path)
    ])

    while True:
        print('>> Start a new game')

        trajectories, payoffs = env.run(is_training=False)

        if len(trajectories[0]) != 0:
            final_state = []
            action_record = []

            for i in range(3):
                final_state.append(trajectories[i][-1])
                action_record = final_state[i]['action_record']

            print('\n=============   Last Trick  ===============')
            current_trick_card_list = [None, None, None]
            if isinstance(action_record[-1][1], PlayCardAction):
                for pair in action_record[-3:]:
                    current_trick_card_list[pair[0]] = pair[1].card
                print_card(current_trick_card_list)
            else:
                print('Everyone passed')

        print('===============     Result     ===============')
        print(payoffs)

        input('Press any key to continue...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Game loop as human with random and trained agent')
    parser.add_argument(
        '--agent_path',
        type=str,
        default='samples/dmc/2_137897600.pth',
    )

    args = parser.parse_args()

    start_game_loop(args)
