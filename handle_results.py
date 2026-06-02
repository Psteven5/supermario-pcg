import numpy as np
import matplotlib.pyplot as plt



repetitions = 5

def smooth_ema(data, weight=0.8):
    """
    Exponential Moving Average smoothing.
    """
    smoothed = np.zeros_like(data)
    if len(data) > 0:
        smoothed[0] = data[0]
        for i in range(1, len(data)):
            smoothed[i] = smoothed[i-1] * weight + data[i] * (1 - weight)
    return smoothed

def get_results(agent: str) -> dict[str, np.ndarray]:
    first = np.load(f"{agent}1/evaluations.npz")
    timesteps = first["timesteps"]
    all_results = first["results"]
    for i in range(2,(repetitions+1)):
        data = f'{agent}{i}/evaluations.npz'
        e = np.load(data)
        all_results = np.concatenate((all_results, e["results"]), axis=1)

    mean_r = all_results.mean(axis=1) #calc mean reward per timestep
    std_r = all_results.std(axis=1) #calc std per timestep

    return {"timesteps": timesteps,"mean": mean_r, "std": std_r}

results = {}
results["macro"] = get_results("macro")
results["controller"] = get_results("controller")

for controller, values in results.items():
    smooth_mean = smooth_ema(values["mean"])
    smooth_std = smooth_ema(values["std"])
    plt.plot(values["timesteps"], smooth_mean, label=controller)
    plt.fill_between(values["timesteps"], smooth_mean - smooth_std, smooth_mean + smooth_std, alpha=0.3)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation During Training on Level 1-1")
plt.legend()
plt.grid(True)
plt.savefig("results.png")
