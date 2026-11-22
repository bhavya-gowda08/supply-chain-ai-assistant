
import json

# Manually verified relevance labels.
# Document IDs:
# doc_0 = supply_chain_policy.pdf
# doc_1 = test_document.txt
# doc_2 = test_inventory.csv
# doc_3 = test_inventory.xlsx

evaluation_data = [
    {
        "question": "What is supply chain management?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "What activities are involved in supply chain management?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "What is inventory management?",
        "relevant_docs": ["doc_0", "doc_1"]
    },
    {
        "question": "Which products are included in the inventory?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What is the reorder level for Soap?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What is the reorder level for Shampoo?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What is the reorder level for Detergent?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What is the reorder level for Toothpaste?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What is the reorder level for Cooking Oil?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "What should happen when stock reaches the reorder level?",
        "relevant_docs": ["doc_0", "doc_1"]
    },
    {
        "question": "When should replenishment be initiated?",
        "relevant_docs": ["doc_0", "doc_1"]
    },
    {
        "question": "Which warehouse locations does the company operate?",
        "relevant_docs": ["doc_0", "doc_2", "doc_3"]
    },
    {
        "question": "What are the responsibilities of warehouses?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "How are suppliers evaluated?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "What factors are considered in supplier management?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "What is demand planning?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "Which factors are used to estimate future product requirements?",
        "relevant_docs": ["doc_0"]
    },
    {
        "question": "How should inventory be monitored?",
        "relevant_docs": ["doc_0", "doc_1"]
    },
    {
        "question": "What should happen to low-stock products?",
        "relevant_docs": ["doc_0", "doc_1"]
    },
    {
        "question": "What is the available stock of Soap?",
        "relevant_docs": ["doc_2", "doc_3"]
    },
    {
        "question": "Which warehouse stores Shampoo?",
        "relevant_docs": ["doc_2", "doc_3"]
    },
    {
        "question": "What is the available stock of Detergent?",
        "relevant_docs": ["doc_2", "doc_3"]
    },
    {
        "question": "Which products have stock below their reorder level?",
        "relevant_docs": ["doc_2", "doc_3"]
    },
    {
        "question": "What inventory details are recorded in the spreadsheet?",
        "relevant_docs": ["doc_2", "doc_3"]
    },
    {
        "question": "How does effective supply chain management benefit a company?",
        "relevant_docs": ["doc_0"]
    }
]

# Save the evaluation dataset
with open("evaluation_dataset.json", "w", encoding="utf-8") as file:
    json.dump(evaluation_data, file, indent=4)

print("Evaluation dataset created successfully!")
print("Total evaluation questions:", len(evaluation_data))
print("\nQuestions:")

for index, item in enumerate(evaluation_data, start=1):
    print(f"{index}. {item['question']}")

print("\nSaved as evaluation_dataset.json")
