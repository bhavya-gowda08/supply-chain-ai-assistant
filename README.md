# Enterprise AI Demand Planning & Supply Chain Intelligence Assistant

## Project Overview

The Enterprise AI Demand Planning & Supply Chain Intelligence Assistant is an AI-powered application designed to support supply chain operations through intelligent document retrieval, inventory analysis, and business insights.

The project combines Advanced Retrieval-Augmented Generation (RAG), SQL analytics, and Google's Gemini LLM to answer supply chain-related questions.

## Key Features

- AI-powered supply chain chatbot.
- Inventory and warehouse dashboard.
- Structured data analysis using MySQL.
- Document upload and processing.
- Advanced RAG with hybrid retrieval.
- Semantic search and BM25 keyword search.
- Cross-encoder reranking.
- Conversation memory.
- Source references for document-based answers.
- CSV report generation.
- Embedding model evaluation.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Frontend |
| MySQL | Relational database |
| ChromaDB | Vector database |
| Google Gemini | LLM |
| Sentence Transformers | Text embeddings |
| BM25 | Keyword retrieval |
| Cross-Encoder | Reranking |
| Pandas | Data processing |
| Plotly | Dashboard visualizations |

## Project Structure

```text
supply-chain-ai-assistant/
│
├── app.py
├── database.py
├── rag.py
├── vector_store.py
├── intent_router.py
├── sql_analytics.py
├── report_generator.py
├── requirements.txt
├── README.md
│
├── data/
├── documents/
├── reports/
├── docs/
│   ├── architecture.md
│   ├── architecture_diagram.md
│   └── technical_documentation.md
│
└── RAG_Evaluation_Report.pdf
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/bhavya-gowda08/supply-chain-ai-assistant.git
cd supply-chain-ai-assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Configure your Gemini API key and database connection details using environment variables. Do not commit API keys or passwords to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

## RAG Evaluation

Two embedding models were evaluated:

- all-MiniLM-L6-v2
- all-mpnet-base-v2

Evaluation metrics:

- Precision@3
- Recall@3
- Mean Reciprocal Rank (MRR)
- Average Retrieval Time

The preliminary evaluation results are available in `advanced_evaluation_v2_results.csv` and `RAG_Evaluation_Report.pdf`.

## Documentation

Refer to the `docs/` directory for:
- System architecture.
- Architecture diagram.
- Technical documentation.

## Project Goal

To build an intelligent supply chain assistant that combines structured database analytics and document-based question answering to support better operational decision-making.