# Super Marios Bros PCG

# Requirements
The uv command:
uv can be installed using pip:
```bash
pip install uv
```
or using curl:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

# How to run the project
To run the agent training:
```bash
uv run main.py
```
parameters can be changed inside `main()` of `./source/main.py`. And rendering of the game can be enabled by setting `render=True` in `./main.py`.

The following settings are present in `./source/main.py`:

    num_frames = 4                 # setting for neural network, determine how many frames are given at the timestep to the agent.
    frame_skip = 4                 # determine how many (game) frames are skipped in between timesteps.
    runs = 5                       # how many repetitions per training of RL agent.
    rl = True                      # If True, the player is not able to give inputs and the RL agents are trained. If false, the player can play the game.
    use_macro = False              # determine if the macro RL agent is used or the controll RL agent.
    run_without_learning = False   # If true, the best macro1 model runs without training (demonstration). 
    use_pcg = False                # If False, level 1-1 is loaded. If True, the PCG level is generated.
    pcg_seed = None                # Set a seed for the PCG speciffically, making PCG deterministic. This only happens when the value is not None.

To evaluate specific agents on different PCG levels, the models and parameters can be chosen inside `./evaluate_best.py` and the evaluation can be run using:
```bash
uv run evaluate_best.py
```

All python files beginning with `handle_results*.py` can be run to create various plots based on the results of `main.py` or `evaluate_best.py`
