from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

repetitions = 5
target_length = 10_000  # max 10,000 timesteps


def get_results(file: Path) -> dict[str, np.ndarray]:
    e = np.load(file)

    sum = e.sum(axis=0)
    mean = sum.mean()
    std = sum.std()

    return {"mean": mean, "std": std}


evaluation_path = Path("evaluation")

model = None
for file in evaluation_path.iterdir():
    model = file.name.split("_")[0]
    break
seeds = set()
for file in evaluation_path.iterdir():
    if not file.name.startswith(model):
        continue
    seeds.add(int(file.name.split("_")[1].split(".")[0]))
seeds = list(seeds)
seeds.sort()

results = {}
for file in evaluation_path.iterdir():
    model = file.name.split("_")[0]
    seed = int(file.name.split("_")[1].split(".")[0])
    lvl = seeds.index(seed)
    if lvl not in results:
        results[lvl] = {}
    results[lvl][f"{model}"] = get_results(file)

for level, resses in results.items():
    for model, values in resses.items():
        plt.bar(model, values["mean"], yerr=values["std"], label=model)

    plt.xlabel("Model")
    plt.ylabel("Average Total Reward")
    plt.title(f"Average Total Reward for PCG Level {level+1}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"bar_{level+1}.png")
    plt.clf()
