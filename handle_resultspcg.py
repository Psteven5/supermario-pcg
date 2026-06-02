import numpy as np
import matplotlib.pyplot as plt



repetitions = 5

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
results["macro pcg"] = get_results("macropcg")
results["controller pcg"] = get_results("controllerpcg")

for controller, values in results.items():
    plt.plot(values["timesteps"], values["mean"], label=controller)
    plt.fill_between(values["timesteps"], values["mean"] - values["std"], values["mean"] + values["std"], alpha=0.3)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation Rewards")
plt.legend()
plt.grid(True)
plt.savefig("results_pcg.png")
