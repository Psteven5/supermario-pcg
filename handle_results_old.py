import numpy as np
import matplotlib.pyplot as plt



repetitions = 5

results={}
for i in range(1,(repetitions+1)):
    agent1 = f'macro{i}/evaluations.npz'
    e = np.load(agent1)
    timesteps = e["timesteps"]
    mean_r = e["results"].mean(axis=1) #calc mean reward per timestep
    results[f"macro{i}"]= {"timesteps": timesteps,"mean": mean_r} #save mean reward in results

for controller, values in results.items():
    plt.plot(values["timesteps"], values["mean"], label=controller)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation Rewards")
plt.legend()
plt.grid(True)
plt.savefig("results_macro.png")
plt.clf()

results={}
for i in range(1,(repetitions+1)):
    agent2 = f'controller{i}/evaluations.npz'
    e = np.load(agent2)
    timesteps = e["timesteps"]
    mean_r = e["results"].mean(axis=1) #calc mean reward per timestep
    results[f"controller{i}"]= {"timesteps": timesteps,"mean": mean_r} #save mean reward in results

for controller, values in results.items():
    plt.plot(values["timesteps"], values["mean"], label=controller)

plt.xlabel("Timesteps")
plt.ylabel("Mean Reward")
plt.title("Evaluation Rewards")
plt.legend()
plt.grid(True)
plt.savefig("results_controller.png")
