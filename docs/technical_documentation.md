# Technical Documentation

## 1. Introduction

The Enterprise AI Demand Planning & Supply Chain Intelligence Assistant is a Python-based application that combines Advanced Retrieval-Augmented Generation (RAG), SQL analytics, and Generative AI to support supply chain operations.

## 2. Project Modules

### 2.1 app.py – Frontend Application
- Provides the Streamlit user interface.
- Displays inventory and supply chain dashboards.
- Provides an AI chatbot.
- Supports document uploads.
- Displays charts and reports.

### 2.2 database.py – Database Connectivity
- Establishes a connection with MySQL.
- Supports structured data retrieval.
- Provides database access to other application modules.

### 2.3 intent_router.py – Query Classification
- Identifies the user's query intent.
- Routes SQL-related questions to SQL Analytics.
- Routes document-related questions to the RAG module.
- Identifies report-generation requests.

### 2.4 rag.py – RAG Orchestration
- Processes user questions.
- Manages conversation memory.
- Connects the retriever with Gemini.
- Generates answers using retrieved context.
- Provides source references when available.

### 2.5 vector_store.py – Document Retrieval
- Loads supported documents.
- Extracts and splits document content.
- Generates vector embeddings.
- Stores document chunks in ChromaDB.
- Performs semantic and keyword retrieval.
- Applies hybrid search and reranking.
- Retrieves parent context and compresses retrieved information.

### 2.6 sql_analytics.py – SQL Analytics
- Executes database queries.
- Retrieves inventory information.
- Analyzes sales and stock details.
- Supports structured business questions.

### 2.7 report_generator.py – Report Generation
- Generates reports from available analytics.
- Exports report data into CSV format.

## 3. Advanced RAG Workflow

The RAG pipeline follows these stages:

1. Document loading.
2. Text extraction.
3. Recursive text chunking.
4. Metadata extraction and assignment.
5. Embedding generation.
6. Vector storage in ChromaDB.
7. Query expansion.
8. Multi-query retrieval.
9. Semantic and BM25 keyword search.
10. Reciprocal Rank Fusion.
11. Cross-encoder reranking.
12. Context compression.
13. Gemini-based response generation.
14. Source citation.

## 4. Embedding Models

The project evaluates two embedding models:

- all-MiniLM-L6-v2
- all-mpnet-base-v2

The models are compared using Precision@3, Recall@3, Mean Reciprocal Rank (MRR), and average retrieval time.

## 5. Database Design

The MySQL database is named `supply_chain_db`.

The implemented tables include:

- products
- inventory
- warehouses
- suppliers
- sales

ChromaDB stores document embeddings for semantic retrieval.

## 6. Supported Document Formats

The document processing module supports:

- PDF
- DOCX
- TXT
- CSV
- XLSX
- XLS

## 7. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Streamlit | User interface |
| MySQL | Structured data storage |
| ChromaDB | Vector database |
| Gemini | Language model |
| Sentence Transformers | Embedding generation |
| BM25 | Keyword retrieval |
| Cross-Encoder | Reranking |
| Pandas | Data processing |
| ReportLab | PDF report generation |

## 8. Evaluation

The embedding comparison results are saved in `advanced_evaluation_v2_results.csv`.

The evaluation report is available as `RAG_Evaluation_Report.pdf`.

The evaluation is an initial document-level experiment using four documents and manually assigned relevance labels. Its results should not be interpreted as production-level performance.

## 9. Conclusion

The project integrates structured database analytics and document-based question answering into a single supply chain intelligence application. It helps users access business information, retrieve relevant policies, and make more informed operational decisions.