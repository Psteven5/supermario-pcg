import matplotlib.pyplot as plt

data = {
    "Q1": [3,4,4,4,4,5],
    "Q2": [4,4,4,4,5,5],
    "Q3": [3,3,4,4,4,5],
    "Q4": [3,3,4,4,5,5],
    "Q5": [3,4,4,5,5,5],
}

labels = list(data.keys())
values = list(data.values())
plt.figure(figsize=(10, 6))
plt.boxplot(values, tick_labels=labels)
plt.title("User Study Results")
plt.xlabel("Questions")
plt.ylabel("Ratings (1-5)")
plt.ylim(1, 5)
plt.grid(True)
plt.savefig("user_study_results.png")

