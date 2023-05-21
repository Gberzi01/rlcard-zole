import envs
from defined_agents import get_random_agent
from logger import Logger

import os

import rlcard
from rlcard.utils import set_seed, tournament
import torch


nr_games = 2000
seed_id = 14


def get_nfsp_evaluatable_agents():
    evaluatable_agents = []
    nfsp_files = os.listdir('experiments/trained/nfsp/')
    nfsp_files.sort()

    for file in nfsp_files:
        evaluatable_agents.append(torch.load(f'experiments/trained/nfsp/{file}'))

    return evaluatable_agents


def get_dqn_evaluatable_agents():
    evaluatable_agents = []
    dqn_files = os.listdir('experiments/trained/dqn/')
    dqn_files.sort()

    for file in dqn_files:
        evaluatable_agents.append(torch.load(f'experiments/trained/dqn/{file}'))

    return evaluatable_agents


def get_dmc_evaluatable_agents():
    evaluatable_agents = []
    dmc_files = [
        '2_9600.pth',
        '2_2905600.pth',
        '2_5782400.pth',
        '2_8646400.pth',
        '2_11516800.pth',
        '2_14393600.pth',
        '2_17260800.pth',
        '2_20131200.pth',
        '2_23001600.pth',
        '2_25865600.pth',
        '2_28739200.pth',
        '2_31612800.pth',
        '2_34489600.pth',
        '2_37360000.pth',
        '2_40240000.pth',
        '2_43116800.pth',
        '2_46000000.pth',
        '2_48883200.pth',
        '2_51744000.pth',
        '2_54608000.pth',
        '2_57472000.pth',
        '2_60332800.pth',
        '2_63206400.pth',
        '2_66076800.pth',
        '2_68953600.pth',
        '2_71840000.pth',
        '2_74713600.pth',
        '2_77600000.pth',
        '2_80480000.pth',
        '2_83363200.pth',
        '2_86243200.pth',
        '2_89129600.pth',
        '2_92009600.pth',
        '2_94873600.pth',
        '2_97753600.pth',
        '2_100627200.pth',
        '2_103513600.pth',
        '2_106396800.pth',
        '2_109267200.pth',
        '2_112118400.pth',
        '2_114976000.pth',
        '2_117840000.pth',
        '2_120694400.pth',
        '2_123520000.pth',
        '2_126400000.pth',
        '2_129276800.pth',
        '2_132163200.pth',
        '2_135030400.pth',
        '2_137897600.pth',
        '2_137907200.pth',
        '2_140684800.pth',
        '2_143475200.pth',
        '2_146272000.pth',
        '2_149062400.pth',
        '2_151865600.pth',
        '2_154684800.pth',
        '2_157494400.pth',
        '2_160291200.pth',
        '2_163094400.pth',
        '2_165888000.pth',
        '2_168688000.pth',
        '2_171488000.pth',
        '2_174310400.pth',
        '2_177126400.pth',
        '2_179952000.pth',
        '2_182771200.pth',
        '2_185600000.pth',
        '2_188416000.pth',
        '2_191244800.pth',
        '2_194051200.pth',
        '2_196854400.pth',
        '2_199660800.pth',
        '2_202486400.pth',
        '2_205305600.pth',
        '2_208128000.pth',
        '2_210956800.pth',
        '2_213785600.pth',
        '2_216604800.pth',
        '2_219427200.pth',
        '2_222236800.pth',
        '2_225049600.pth',
        '2_227868800.pth',
        '2_230694400.pth',
        '2_233513600.pth',
        '2_236339200.pth',
        '2_239145600.pth',
        '2_241964800.pth',
        '2_244784000.pth',
        '2_247596800.pth',
        '2_250409600.pth',
        '2_253216000.pth',
        '2_256025600.pth',
        '2_258828800.pth',
        '2_261622400.pth',
        '2_264476800.pth',
        '2_267273600.pth',
        '2_270000000.pth',
    ]

    for file in dmc_files:
        evaluatable_agents.append(torch.load(f'experiments/trained/dmc/{file}'))

    return evaluatable_agents


def get_env(): 
    set_seed(seed_id)
    return rlcard.make(
        'zole',
        {
            'seed': seed_id,
            'display_performance_interval': nr_games
        }
    )


def evaluate():
    opponents = [
        'vs_dmc',
        'vs_dqn',
        'vs_nfsp',
        'vs_dmc_t',
    ]

    # evaluatable_agents = get_dmc_evaluatable_agents()
    # evaluatable_agents = get_dqn_evaluatable_agents()
    evaluatable_agents = get_nfsp_evaluatable_agents()

    baselines = [
        # ['random', 'random']
        ['experiments/trained/720/dmc_0_137897600.pth', 'experiments/trained/720/dmc_1_137897600.pth'],
        ['experiments/trained/720/dqn_0_20230518_0425.pth', 'experiments/trained/720/dqn_1_20230518_0425.pth'],
        ['experiments/trained/720/nfsp_0_20230519_0033.pth', 'experiments/trained/720/nfsp_1_20230519_0033.pth'],
        ['experiments/trained/1440/0_270000000.pth', 'experiments/trained/1440/1_270000000.pth']
    ]

    for index, baseline in enumerate(baselines):
        agent_0 = torch.load(baseline[0])
        agent_1 = torch.load(baseline[1])
        # with Logger(f'performance/trained/nfsp/vs_random') as logger:
        with Logger(f'performance/trained/nfsp/{opponents[index]}') as logger:
            for agent_index, agent in enumerate(evaluatable_agents):
                env = get_env()
                env.set_agents([
                    # get_random_agent(env),
                    # get_random_agent(env),
                    agent_0,
                    agent_1,
                    agent
                ])

                rewards = tournament(env, nr_games)
                print(f'Finished {index} {agent_index}')

                large_wins = [
                    env.zolePerformanceTracker.get_large_percent_wins(0),
                    env.zolePerformanceTracker.get_large_percent_wins(1),
                    env.zolePerformanceTracker.get_large_percent_wins(2),
                ]

                small_wins = [
                    env.zolePerformanceTracker.get_small_percent_wins(0),
                    env.zolePerformanceTracker.get_small_percent_wins(1),
                    env.zolePerformanceTracker.get_small_percent_wins(2),
                ]

                as_large = [
                    env.zolePerformanceTracker.get_games_as_large(0),
                    env.zolePerformanceTracker.get_games_as_large(1),
                    env.zolePerformanceTracker.get_games_as_large(2),
                ]

                logger.log_performance(
                    large_wins,
                    small_wins,
                    as_large,
                    rewards,
                )


evaluate()
