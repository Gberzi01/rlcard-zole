import envs
from defined_agents import get_random_agent

import argparse
import torch

import rlcard
from rlcard.utils import set_seed, tournament


def get_env(seed_id: int):
    set_seed(seed_id)

    return rlcard.make(
        'zole',
        {'seed': seed_id}
    )


def start(args):
    env = get_env(args.seed_id)
    env.set_agents([
        get_random_agent(env),
        get_random_agent(env),
        torch.load(args.agent_path)
    ])

    rewards = tournament(env, args.nr_games)
    print(f'Points per game {rewards}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run tournament with agents')
    parser.add_argument(
        '--agent_path',
        type=str,
        default='samples/dmc/2_137897600.pth',
    )

    parser.add_argument(
        '--nr_games',
        type=int,
        default=2000,
    )

    parser.add_argument(
        '--seed_id',
        type=int,
        default=14,
    )

    args = parser.parse_args()

    start(args)