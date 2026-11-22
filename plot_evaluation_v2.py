
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("advanced_evaluation_v2_results.csv")

metrics = [
    ("Precision@3", "Precision Comparison"),
    ("Recall@3", "Recall Comparison"),
    ("MRR", "Mean Reciprocal Rank Comparison")
]

for column, title in metrics:

    plt.figure(figsize=(8, 5))

    plt.bar(df["Model"], df[column])

    plt.title(title)
    plt.xlabel("Embedding Model")
    plt.ylabel(column)
    plt.ylim(0, 1)

    plt.tight_layout()

    filename = column.lower().replace("@", "_") + "_v2.png"
    plt.savefig(filename)

    plt.show()

# Retrieval time chart
plt.figure(figsize=(8, 5))

plt.bar(
    df["Model"],
    df["Average Retrieval Time (seconds)"]
)

plt.title("Average Retrieval Time Comparison")
plt.xlabel("Embedding Model")
plt.ylabel("Time (seconds)")

plt.tight_layout()
plt.savefig("retrieval_time_v2.png")
plt.show()

print("All four evaluation charts generated successfully!")
