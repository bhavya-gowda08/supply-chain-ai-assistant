
import time
import pandas as pd
import rag

# Questions for evaluating document-based RAG
evaluation_data = [
    {
        "question": "What should happen when stock reaches the reorder level?",
        "keywords": ["reorder", "replenishment"]
    },
    {
        "question": "What is the purpose of monitoring warehouse inventory?",
        "keywords": ["inventory", "warehouse", "stock"]
    },
    {
        "question": "What information is available about inventory products?",
        "keywords": ["product", "stock", "quantity"]
    },
    {
        "question": "What details are recorded in the inventory spreadsheet?",
        "keywords": ["inventory", "product", "warehouse"]
    },
    {
        "question": "What information is available in the sales data?",
        "keywords": ["sales", "quantity", "amount"]
    }
]

results = []

print("========== RAG EVALUATION STARTED ==========")

for index, item in enumerate(evaluation_data, start=1):

    question = item["question"]
    keywords = item["keywords"]

    print(f"\nQuestion {index}: {question}")

    start_time = time.perf_counter()

    try:
        answer = rag.ask_question(question)
        elapsed = time.perf_counter() - start_time

        answer_text = str(answer)
        intent = rag.last_intent or "Unknown"
        citations = getattr(rag, "last_sources", [])

        matched_keywords = [
            word for word in keywords
            if word.lower() in answer_text.lower()
        ]

        relevance_score = (
            len(matched_keywords) / len(keywords)
            if keywords else 0
        )

        results.append({
            "Question": question,
            "Detected Intent": intent,
            "Answer": answer_text,
            "Matched Keywords": len(matched_keywords),
            "Answer Relevance Score": round(relevance_score, 4),
            "Citation Count": len(citations),
            "Response Time (seconds)": round(elapsed, 4),
            "Status": "Success"
        })

        print("Intent:", intent)
        print("Citation count:", len(citations))
        print("Answer relevance:", round(relevance_score, 4))
        print("Response time:", round(elapsed, 4), "seconds")

    except Exception as error:
        results.append({
            "Question": question,
            "Detected Intent": "Error",
            "Answer": str(error),
            "Matched Keywords": 0,
            "Answer Relevance Score": 0,
            "Citation Count": 0,
            "Response Time (seconds)": 0,
            "Status": "Failed"
        })

        print("Evaluation error:", error)

# Save results
df = pd.DataFrame(results)

df.to_csv("rag_evaluation_results.csv", index=False)

successful = df[df["Status"] == "Success"]

print("\n========== FINAL RAG EVALUATION ==========")
print("Total questions:", len(df))
print("Successful questions:", len(successful))

if not successful.empty:
    print(
        "Average answer relevance:",
        round(successful["Answer Relevance Score"].mean(), 4)
    )
    print(
        "Average response time:",
        round(successful["Response Time (seconds)"].mean(), 4),
        "seconds"
    )
    print(
        "Average citation count:",
        round(successful["Citation Count"].mean(), 2)
    )

print("\nResults saved to rag_evaluation_results.csv")
