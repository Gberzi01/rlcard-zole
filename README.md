## Project setup:
Create virtual environment
```bash
python3 -m venv venv
```

Enter virtual environment
```bash
source venv/bin/activate
```

Install project dependencies
```bash
pip install -r requirements.txt
```

## Agent training
Train DMC agents, trained model and agents will appear in `experiments/dmc_result/zole`
```bash
python dmc_training.py
```

Train NFSP/DQN agents, trained model and agents will appear in `experiments/{algorithm}_result/zole/{agent_id}`,
Agent directories need to be created before launching
```bash
python rl_training.py --algorithm=dqn
```

## Play as human
Play as human vs random agent and one trained agent, trained agent path required as argument
```bash
python zole_human.py --agent_path=samples/dmc/2_137897600.pth
```

## Run tournament with an agent

```bash
python zole_tournament.py --agent_path=samples/dmc/2_137897600.pth --nr_games=2000
```

## Run agent evaluation

```bash
python agent_evaluate_multiple.py
```
