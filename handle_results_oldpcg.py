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


results={}
for i in range(1,(repetitions+1)):
    agent1 = f'macropcg{i}/evaluations.npz'
    e = np.load(agent1)
    timesteps = e["timesteps"]
    mean_r = e["results"].mean(axis=1) #calc mean reward per timestep
    results[f"macropcg{i}"]= {"timesteps": timesteps,"mean": mean_r} #save mean reward in results

for controller, values in results.items():
    smooth_mean = smooth_ema(values["mean"])
    plt.plot(values["timesteps"], smooth_mean, label=controller)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation Rewards Macro PCG")
plt.legend()
plt.grid(True)
plt.savefig("results_macropcg.png")
plt.clf()

results={}
for i in range(1,(repetitions+1)):
    agent2 = f'controllerpcg{i}/evaluations.npz'
    e = np.load(agent2)
    timesteps = e["timesteps"]
    mean_r = e["results"].mean(axis=1) #calc mean reward per timestep
    results[f"controllerpcg{i}"]= {"timesteps": timesteps,"mean": mean_r} #save mean reward in results

for controller, values in results.items():
    smooth_mean = smooth_ema(values["mean"])
    plt.plot(values["timesteps"], smooth_mean, label=controller)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation Rewards Controller PCG")
plt.legend()
plt.grid(True)
plt.savefig("results_controllerpcg.png")
