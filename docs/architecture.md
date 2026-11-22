# Enterprise AI Demand Planning & Supply Chain Intelligence Assistant

## 1. Project Overview

This project is an AI-powered Supply Chain Intelligence Assistant that helps users analyze inventory, monitor stock levels, retrieve supply chain policies, and answer business-related questions.

It combines Advanced Retrieval-Augmented Generation (RAG), SQL analytics, and Gemini LLM to provide intelligent responses.

## 2. System Architecture

The project consists of the following components:

### A. Frontend Layer
- Streamlit web application.
- Interactive dashboard.
- AI chatbot interface.
- Document upload facility.
- Inventory and supply chain visualizations.
- Report generation and download.

### B. Application Layer
- Python-based application logic.
- Intent detection and query routing.
- Conversation memory.
- Report generation.
- SQL analytics integration.

### C. Advanced RAG Layer
- Document loading and extraction.
- Recursive text chunking.
- Metadata-based retrieval.
- Query expansion and multi-query retrieval.
- Hybrid search using semantic search and BM25.
- Reciprocal Rank Fusion.
- Cross-encoder reranking.
- Context compression.
- Source citations.

### D. AI and Embedding Layer
- Gemini LLM for response generation.
- Sentence Transformers for document embeddings.
- all-MiniLM-L6-v2 embedding model.
- all-mpnet-base-v2 for embedding evaluation.

### E. Database Layer
- MySQL for structured supply chain information.
- ChromaDB for vector storage and semantic retrieval.

## 3. Data Sources

### Structured Data
- Products
- Inventory
- Warehouses
- Suppliers
- Sales transactions

### Unstructured Data
- Supply chain policy documents.
- Inventory management documents.
- PDF, DOCX, TXT, CSV and Excel files.

## 4. Query Processing Workflow

1. User enters a question in the Streamlit chatbot.
2. Intent router identifies the query type.
3. SQL queries are processed through the SQL analytics module.
4. Document-related questions are processed through the Advanced RAG pipeline.
5. Relevant information is retrieved from MySQL or ChromaDB.
6. Gemini generates the response.
7. The chatbot displays the answer with source references when available.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Relational Database | MySQL |
| Retrieval | Semantic Search and BM25 |
| Reranking | Cross-Encoder |
| Data Processing | Pandas |
| Visualization | Plotly |
| PDF Report | ReportLab |

## 6. Evaluation

Two embedding models are compared using:

- Precision@3
- Recall@3
- Mean Reciprocal Rank (MRR)
- Average Retrieval Time

The initial evaluation results are documented in RAG_Evaluation_Report.pdf.

## 7. Expected Benefits

- Faster access to supply chain information.
- Improved inventory monitoring.
- Easier retrieval of company policies.
- Data-driven business decisions.
- Reduced manual document searching.