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

To evaluate specific agents on different PCG levels, the models and parameters can be chosen inside `./evaluate_best.py` and the evaluation can be run using:
```bash
uv run evaluate_best.py
```

All python files beginning with `handle_results*.py` can be run to create various plots based on the results of `main.py` or `evaluate_best.py`