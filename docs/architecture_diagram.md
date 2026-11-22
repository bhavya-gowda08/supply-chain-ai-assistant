
# System Architecture Diagram

```mermaid
flowchart TD
    A[User] --> B[Streamlit Frontend]

    B --> C[Python Backend]
    C --> D[Intent Router]

    D -->|Document Questions| E[Advanced RAG Pipeline]
    D -->|Data Questions| F[SQL Analytics]
    D -->|Report Requests| G[Report Generator]

    E --> H[Document Processing]
    H --> I[Text Extraction and Chunking]
    I --> J[Embedding Generation]
    J --> K[ChromaDB Vector Database]

    E --> L[Hybrid Retrieval]
    L --> M[Semantic Search]
    L --> N[BM25 Keyword Search]
    M --> O[Reciprocal Rank Fusion]
    N --> O
    O --> P[Cross Encoder Reranking]
    P --> Q[Context Compression]

    Q --> R[Gemini LLM]
    F --> S[MySQL Database]
    G --> S

    R --> T[Generated Answer with Sources]
    S --> T
    T --> B
