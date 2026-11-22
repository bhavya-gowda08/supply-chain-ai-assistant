
import pandas as pd
import matplotlib.pyplot as plt

# Load evaluation results
df = pd.read_csv("advanced_evaluation_results.csv")

print("Evaluation Results:")
print(df.to_string(index=False))

# --------------------------------
# Chart 1: Average Precision
# --------------------------------

plt.figure(figsize=(8, 5))

plt.bar(
    df["Model"],
    df["Average Precision"]
)

plt.title("Embedding Model Comparison - Average Precision")
plt.xlabel("Embedding Models")
plt.ylabel("Average Precision")
plt.ylim(0, 1)

plt.tight_layout()
plt.savefig("embedding_precision_comparison.png")
plt.show()

# --------------------------------
# Chart 2: Average Retrieval Time
# --------------------------------

plt.figure(figsize=(8, 5))

plt.bar(
    df["Model"],
    df["Average Retrieval Time"]
)

plt.title("Embedding Model Comparison - Retrieval Time")
plt.xlabel("Embedding Models")
plt.ylabel("Retrieval Time (seconds)")

plt.tight_layout()
plt.savefig("embedding_retrieval_time.png")
plt.show()

print("\nCharts saved successfully!")
print("1. embedding_precision_comparison.png")
print("2. embedding_retrieval_time.png")
