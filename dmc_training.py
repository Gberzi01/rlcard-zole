from envs.zole import ZoleEnv

import argparse

from rlcard.agents.dmc_agent import DMCTrainer
from rlcard.utils import set_seed


def train(args):
    config = {
        'allow_step_back': False,
        'seed': args.seed,
        'large_win_incentive': args.large_win_incentive,
    }
    set_seed(args.seed)

    env = ZoleEnv(config)

    trainer = DMCTrainer(
        env=env,
        save_interval=args.save_interval,
        load_model=True,
        xpid=args.xpid
    )

    trainer.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser('DMC example in RLCard')

    parser.add_argument(
        '--seed',
        type=int,
        default=2,
    )

    parser.add_argument(
        '--save_interval',
        type=int,
        default=10,
    )

    parser.add_argument(
        '--xpid',
        type=str,
        default='zole',
    )

    parser.add_argument(
        '--large_win_incentive',
        type=int,
        default=0,
    )

    args = parser.parse_args()

    train(args)
