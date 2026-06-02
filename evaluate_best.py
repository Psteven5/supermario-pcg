import random
import torch
import numpy as np
from pathlib import Path

Path("evaluation").mkdir(exist_ok=True)
Path("evaluation_determ").mkdir(exist_ok=True)

torch.random.manual_seed(42)
random.seed(42)
np.random.seed(42)

best_models = ["controller3", "controllerpcg1", "macro2", "macropcg3"]
num_levels = 5

render = True
num_frames = 4
frame_skip = 4
rl = True
use_pcg = True
pcg_seeds = [random.randint(0, 4_294_967_295) for _ in range(num_levels)]

if not render:
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
from source.main import evaluate

if __name__=='__main__':
    for model in best_models:
        for pcg_seed in pcg_seeds:
            use_macro = model.startswith("macro")
            res = evaluate(render, num_frames, frame_skip, 5, rl, use_macro, use_pcg, pcg_seed, model, False)
            np.save(f"evaluation/{model}_{pcg_seed}.npy", res)

    pg.quit()
