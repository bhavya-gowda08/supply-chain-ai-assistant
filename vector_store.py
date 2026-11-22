
import os
import re
import json
import hashlib
import shutil
import uuid
from datetime import datetime

import pandas as pd
import chromadb

from pypdf import PdfReader
from docx import Document as DocxDocument

from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi


# =========================================================
# 1. CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
ARCHIVE_DIR = os.path.join(DOCUMENTS_DIR, "archive")

CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")
PARENT_STORE_PATH = os.path.join(DATA_DIR, "parent_store.json")
VERSION_PATH = os.path.join(DATA_DIR, "document_versions.json")

COLLECTION_NAME = "supply_chain_documents"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

RETRIEVAL_COUNT = 5
FINAL_RESULT_COUNT = 3

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)


# =========================================================
# 2. LOAD MODELS
# =========================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

if hasattr(embedding_model, "get_embedding_dimension"):
    actual_dimension = embedding_model.get_embedding_dimension()
else:
    actual_dimension = embedding_model.get_sentence_embedding_dimension()

if actual_dimension != EMBEDDING_DIMENSION:
    raise RuntimeError(
        f"Expected embedding dimension {EMBEDDING_DIMENSION}, "
        f"received {actual_dimension}"
    )

print("Embedding model loaded.")

print("Loading reranker...")

reranker = CrossEncoder(RERANKER_MODEL_NAME)

print("Reranker loaded.")


# =========================================================
# 3. CHROMADB CONNECTION
# =========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


def create_collection():
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


collection = create_collection()


def ensure_collection_dimension():
    global collection

    try:
        if collection.count() == 0:
            return True

        result = collection.get(
            limit=1,
            include=["embeddings"]
        )

        embeddings = result.get("embeddings")

        if embeddings is None or len(embeddings) == 0:
            return True

        dimension = len(embeddings[0])

        if dimension != EMBEDDING_DIMENSION:
            raise RuntimeError(
                f"Existing ChromaDB dimension is {dimension}, "
                f"but the model produces {EMBEDDING_DIMENSION}. "
                "Do not delete the database automatically. "
                "Back it up and re-index documents if necessary."
            )

        return True

    except RuntimeError:
        raise
    except Exception as error:
        raise RuntimeError(
            f"ChromaDB dimension check failed: {error}"
        )


ensure_collection_dimension()


# =========================================================
# 4. JSON STORAGE
# =========================================================

def load_json(path):
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            result = json.load(file)

        return result if isinstance(result, dict) else {}

    except (json.JSONDecodeError, OSError) as error:
        print("JSON loading error:", error)
        return {}


def save_json(path, data):
    temporary_path = path + ".tmp"

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(temporary_path, path)


def load_parent_store():
    return load_json(PARENT_STORE_PATH)


def save_parent_store(parent_store):
    save_json(PARENT_STORE_PATH, parent_store)


def load_document_versions():
    return load_json(VERSION_PATH)


def save_document_versions(data):
    save_json(VERSION_PATH, data)


# =========================================================
# 5. DOCUMENT EXTRACTION
# =========================================================

def extract_pdf_pages(file_path):
    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        content = page.extract_text() or ""

        if content.strip():
            pages.append({
                "page": page_number,
                "content": content
            })

    return pages


def extract_docx_pages(file_path):
    document = DocxDocument(file_path)
    parts = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text.strip())

    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            )

            if row_text:
                parts.append(row_text)

    content = "\n".join(parts)

    if not content.strip():
        return []

    return [{
        "page": 1,
        "content": content
    }]


def load_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf_pages(file_path)

    if extension == ".docx":
        return extract_docx_pages(file_path)

    if extension == ".txt":
        with open(
            file_path,
            "r",
            encoding="utf-8-sig"
        ) as file:
            content = file.read()

        return [{"page": 1, "content": content}] if content.strip() else []

    if extension == ".csv":
        dataframe = pd.read_csv(file_path)

        return [{
            "page": 1,
            "content": dataframe.to_string(index=False)
        }]

    if extension in [".xlsx", ".xls"]:
        sheets = pd.read_excel(
            file_path,
            sheet_name=None
        )

        pages = []

        for page_number, (sheet_name, dataframe) in enumerate(
            sheets.items(),
            start=1
        ):
            content = (
                f"Sheet Name: {sheet_name}\n"
                f"{dataframe.to_string(index=False)}"
            )

            pages.append({
                "page": page_number,
                "content": content
            })

        return pages

    raise ValueError(
        f"Unsupported document format: {extension}"
    )


# =========================================================
# 6. TEXT CHUNKING
# =========================================================

def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    return splitter.split_text(text)


# =========================================================
# 7. ID AND METADATA HELPERS
# =========================================================

def generate_id(value):
    return hashlib.md5(
        value.encode("utf-8")
    ).hexdigest()


def identify_section(text):
    for line in text.splitlines():
        line = line.strip()

        if re.match(
            r"^(\d+[\.)]\s+|[A-Z][A-Z\s]{5,}$)",
            line
        ):
            return line[:150]

    return "General Supply Chain Policy"


def prepare_metadata(metadata, source, page):
    metadata = metadata or {}

    return {
        "source": str(source),
        "page": int(page),
        "document_type": os.path.splitext(source)[1].replace(".", "").upper(),
        "product": str(metadata.get("product") or "").strip(),
        "sku": str(metadata.get("sku") or "").strip(),
        "factory": str(metadata.get("factory") or "").strip(),
        "warehouse": str(metadata.get("warehouse") or "").strip().upper(),
        "supplier": str(metadata.get("supplier") or "").strip(),
        "region": str(metadata.get("region") or "").strip(),
        "department": str(metadata.get("department") or "").strip(),
        "sop_version": str(metadata.get("sop_version") or "").strip(),
        "effective_date": str(metadata.get("effective_date") or "").strip(),
        "section": "General Supply Chain Policy"
    }


# =========================================================
# 8. DOCUMENT DELETION
# =========================================================

def delete_document_by_source(source_name):
    try:
        result = collection.get(
            where={"source": source_name},
            include=["metadatas"]
        )

        ids = result.get("ids") or []

        if ids:
            collection.delete(ids=ids)

        parent_store = load_parent_store()

        parent_ids = [
            parent_id
            for parent_id, parent_data in parent_store.items()
            if (
                isinstance(parent_data, dict)
                and parent_data.get("source") == source_name
            )
        ]

        for parent_id in parent_ids:
            parent_store.pop(parent_id, None)

        save_parent_store(parent_store)

        return True

    except Exception as error:
        print("Document deletion error:", error)
        return False


# =========================================================
# 9. DOCUMENT VERSION MANAGEMENT
# =========================================================

def get_document_version_history(source_name):
    versions = load_document_versions()
    return versions.get(source_name, [])


def archive_document(source_name, file_path, metadata=None):
    if not os.path.exists(file_path):
        return None

    versions = load_document_versions()
    history = versions.get(source_name, [])

    next_version = max(
        [item.get("version", 0) for item in history] or [0]
    ) + 1

    extension = os.path.splitext(file_path)[1]

    archive_filename = (
        f"{uuid.uuid4().hex}_V{next_version}{extension}"
    )

    archive_path = os.path.join(
        ARCHIVE_DIR,
        archive_filename
    )

    shutil.copy2(file_path, archive_path)

    record = {
        "version": next_version,
        "source": source_name,
        "archive_path": archive_path,
        "metadata": metadata or {},
        "created_at": datetime.now().isoformat()
    }

    history.append(record)
    versions[source_name] = history

    save_document_versions(versions)

    return record


# =========================================================
# 10. PROCESS AND INDEX DOCUMENT
# =========================================================

def process_document(file_path, metadata=None):
    if not os.path.exists(file_path):
        print("File not found:", file_path)
        return False

    source_name = os.path.basename(file_path)
    metadata = metadata or {}

    try:
        print("Processing document:", source_name)

        pages = load_document(file_path)

        if not pages:
            print("No readable content found.")
            return False

        chunks = []
        chunk_ids = []
        chunk_metadata = []
        parent_records = {}

        for page_data in pages:
            page_number = int(page_data.get("page", 1))
            page_content = page_data.get("content", "")

            if not page_content.strip():
                continue

            parent_id = generate_id(
                f"{source_name}_{page_number}"
            )

            parent_records[parent_id] = {
                "content": page_content,
                "source": source_name,
                "page": page_number
            }

            for chunk_index, chunk in enumerate(
                split_text(page_content)
            ):
                if not chunk.strip():
                    continue

                chunk_id = generate_id(
                    f"{source_name}_{page_number}_{chunk_index}_{chunk}"
                )

                current_metadata = prepare_metadata(
                    metadata,
                    source_name,
                    page_number
                )

                current_metadata.update({
                    "parent_id": parent_id,
                    "chunk_index": int(chunk_index),
                    "section": identify_section(chunk)
                })

                chunks.append(chunk)
                chunk_ids.append(chunk_id)
                chunk_metadata.append(current_metadata)

        if not chunks:
            print("No text chunks created.")
            return False

        embeddings = embedding_model.encode(
            chunks,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        if embeddings.shape[1] != EMBEDDING_DIMENSION:
            raise ValueError("Embedding dimension mismatch.")

        # Archive the upload before updating the index.
        archive_record = archive_document(
            source_name,
            file_path,
            metadata
        )

        if archive_record is None:
            return False

        # Remove the previous indexed copy of this filename.
        if not delete_document_by_source(source_name):
            print("Could not replace previous indexed document.")
            return False

        collection.add(
            ids=chunk_ids,
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=chunk_metadata
        )

        parent_store = load_parent_store()
        parent_store.update(parent_records)
        save_parent_store(parent_store)

        print("Document indexed successfully:", source_name)
        print("Chunks created:", len(chunks))

        return True

    except Exception as error:
        print("Document processing error:", error)
        return False


# =========================================================
# 11. DOCUMENT LISTING
# =========================================================

def get_indexed_documents():
    try:
        result = collection.get(
            include=["metadatas"]
        )

        metadatas = result.get("metadatas") or []
        documents = {}

        for metadata in metadatas:
            if not isinstance(metadata, dict):
                continue

            source = metadata.get("source")

            if not source:
                continue

            if source not in documents:
                documents[source] = {
                    "source": source,
                    "warehouse": metadata.get("warehouse", ""),
                    "product": metadata.get("product", ""),
                    "supplier": metadata.get("supplier", ""),
                    "region": metadata.get("region", ""),
                    "department": metadata.get("department", ""),
                    "sop_version": metadata.get("sop_version", ""),
                    "document_type": metadata.get("document_type", ""),
                    "chunks": 0
                }

            documents[source]["chunks"] += 1

        return list(documents.values())

    except Exception as error:
        print("Document listing error:", error)
        return []


# =========================================================
# 12. UPDATE DOCUMENT METADATA
# =========================================================

def update_document_metadata(source_name, updated_metadata):
    try:
        result = collection.get(
            where={"source": source_name},
            include=["metadatas"]
        )

        ids = result.get("ids") or []
        old_metadatas = result.get("metadatas") or []

        if not ids:
            return False

        allowed_fields = [
            "product",
            "sku",
            "factory",
            "warehouse",
            "supplier",
            "region",
            "department",
            "sop_version",
            "effective_date"
        ]

        new_metadatas = []

        for old_metadata in old_metadatas:
            # Convert ChromaDB metadata to a normal Python dictionary.
            current = dict(old_metadata or {})

            for field in allowed_fields:
                if field in updated_metadata:
                    value = updated_metadata[field]

                    if field == "warehouse":
                        value = str(value or "").upper()
                    else:
                        value = str(value or "")

                    current[field] = value

            new_metadatas.append(current)

        collection.update(
            ids=ids,
            metadatas=new_metadatas
        )

        return True

    except Exception as error:
        print("Metadata update error:", error)
        return False


# =========================================================
# 13. DELETE DOCUMENT COMPLETELY
# =========================================================

def delete_document(source_name):
    if not source_name:
        return False

    return delete_document_by_source(source_name)


def delete_document_completely(source_name):
    try:
        if not delete_document_by_source(source_name):
            return False

        versions = load_document_versions()
        history = versions.pop(source_name, [])

        for record in history:
            archive_path = record.get("archive_path")

            if archive_path and os.path.exists(archive_path):
                os.remove(archive_path)

        save_document_versions(versions)

        return True

    except Exception as error:
        print("Complete document deletion error:", error)
        return False


# =========================================================
# 14. VECTOR STORE STATUS
# =========================================================

def get_vector_store_status():
    try:
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks": collection.count(),
            "embedding_model": EMBEDDING_MODEL_NAME,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "status": "Connected"
        }

    except Exception as error:
        return {
            "collection_name": COLLECTION_NAME,
            "total_chunks": 0,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "status": str(error)
        }


# =========================================================
# 15. QUERY EXPANSION
# =========================================================

def expand_query(query):
    if not query or not query.strip():
        return []

    queries = [query.strip()]

    replacements = {
        "inventory": ["stock", "warehouse inventory"],
        "reorder": ["replenishment", "stock replenishment"],
        "supplier": ["vendor", "supplier management"],
        "shipment": ["delivery", "logistics"],
        "demand": ["sales demand", "demand forecasting"],
        "production": ["manufacturing", "production planning"],
        "quality": ["quality inspection", "quality control"],
        "warehouse": ["storage facility", "warehouse operations"]
    }

    for keyword, alternatives in replacements.items():
        if keyword in query.lower():
            for alternative in alternatives:
                expanded = re.sub(
                    re.escape(keyword),
                    alternative,
                    query,
                    count=1,
                    flags=re.IGNORECASE
                )

                if expanded not in queries:
                    queries.append(expanded)

    return queries[:4]


# =========================================================
# 16. SEMANTIC SEARCH
# =========================================================

def semantic_search(query, where=None):
    if not query or not query.strip():
        return []

    try:
        total_count = collection.count()

        if total_count == 0:
            return []

        query_embedding = embedding_model.encode(
            [query],
            convert_to_numpy=True
        )[0].tolist()

        if isinstance(where, dict) and where:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(RETRIEVAL_COUNT, total_count),
                where=where,
                include=["documents", "metadatas", "distances"]
            )
        else:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(RETRIEVAL_COUNT, total_count),
                include=["documents", "metadatas", "distances"]
            )

        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]
        ids = results.get("ids") or [[]]

        output = []

        for index, content in enumerate(documents[0]):
            output.append({
                "id": ids[0][index],
                "content": content,
                "metadata": metadatas[0][index] or {},
                "distance": distances[0][index]
            })

        return output

    except Exception as error:
        print("Semantic search error:", error)
        return []


# =========================================================
# 17. BM25 KEYWORD SEARCH
# =========================================================

def keyword_search(query, where=None):
    if not query or not query.strip():
        return []

    try:
        if isinstance(where, dict) and where:
            results = collection.get(
                where=where,
                include=["documents", "metadatas"]
            )
        else:
            results = collection.get(
                include=["documents", "metadatas"]
            )

        documents = results.get("documents") or []
        metadatas = results.get("metadatas") or []
        ids = results.get("ids") or []

        if not documents:
            return []

        corpus = [
            re.findall(r"\w+", document.lower())
            for document in documents
        ]

        query_tokens = re.findall(
            r"\w+",
            query.lower()
        )

        if not query_tokens:
            return []

        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        output = []

        for index in ranked_indices[:RETRIEVAL_COUNT]:
            if scores[index] <= 0:
                continue

            output.append({
                "id": ids[index],
                "content": documents[index],
                "metadata": metadatas[index] or {},
                "bm25_score": float(scores[index])
            })

        return output

    except Exception as error:
        print("BM25 search error:", error)
        return []


# =========================================================
# 18. RECIPROCAL RANK FUSION
# =========================================================

def reciprocal_rank_fusion(
    semantic_results,
    keyword_results,
    k=60
):
    fused_scores = {}
    document_map = {}

    for rank, document in enumerate(semantic_results, start=1):
        document_id = document.get("id")

        if not document_id:
            continue

        fused_scores[document_id] = (
            fused_scores.get(document_id, 0)
            + 1 / (k + rank)
        )

        document_map[document_id] = document

    for rank, document in enumerate(keyword_results, start=1):
        document_id = document.get("id")

        if not document_id:
            continue

        fused_scores[document_id] = (
            fused_scores.get(document_id, 0)
            + 1 / (k + rank)
        )

        if document_id not in document_map:
            document_map[document_id] = document

    ranked_ids = sorted(
        fused_scores,
        key=lambda item: fused_scores[item],
        reverse=True
    )

    output = []

    for document_id in ranked_ids:
        document = dict(document_map[document_id])
        document["fusion_score"] = fused_scores[document_id]
        output.append(document)

    return output


# =========================================================
# 19. CROSS-ENCODER RERANKING
# =========================================================

def rerank_documents(query, documents):
    if not documents:
        return []

    valid_documents = [
        document for document in documents
        if document.get("content")
    ]

    if not valid_documents:
        return []

    pairs = [
        [query, document["content"]]
        for document in valid_documents
    ]

    try:
        scores = reranker.predict(pairs)
        output = []

        for document, score in zip(valid_documents, scores):
            updated = dict(document)
            updated["rerank_score"] = float(score)
            output.append(updated)

        output.sort(
            key=lambda item: item.get("rerank_score", 0),
            reverse=True
        )

        return output

    except Exception as error:
        print("Reranking error:", error)
        return valid_documents


# =========================================================
# 20. HYBRID SEARCH
# =========================================================

def hybrid_search(query, where=None):
    semantic_results = semantic_search(
        query,
        where=where
    )

    keyword_results = keyword_search(
        query,
        where=where
    )

    fused_results = reciprocal_rank_fusion(
        semantic_results,
        keyword_results
    )

    return rerank_documents(
        query,
        fused_results
    )


# =========================================================
# 21. MULTI-QUERY SEARCH
# =========================================================

def multi_query_search(query, where=None):
    expanded_queries = expand_query(query)
    all_results = {}

    for expanded_query in expanded_queries:
        results = hybrid_search(
            expanded_query,
            where=where
        )

        for document in results:
            document_id = document.get("id")

            if not document_id:
                continue

            previous = all_results.get(document_id)

            if (
                previous is None
                or document.get("rerank_score", 0)
                > previous.get("rerank_score", 0)
            ):
                all_results[document_id] = document

    output = list(all_results.values())

    output.sort(
        key=lambda item: item.get("rerank_score", 0),
        reverse=True
    )

    return output


# =========================================================
# 22. PARENT DOCUMENT RETRIEVAL
# =========================================================

def retrieve_parent_documents(documents):
    if not documents:
        return []

    parent_store = load_parent_store()
    output = []
    seen_parent_ids = set()

    for document in documents:
        metadata = document.get("metadata", {}) or {}
        parent_id = metadata.get("parent_id")

        if not parent_id:
            output.append(document)
            continue

        if parent_id in seen_parent_ids:
            continue

        seen_parent_ids.add(parent_id)

        parent_data = parent_store.get(parent_id)

        if not isinstance(parent_data, dict):
            output.append(document)
            continue

        parent_content = parent_data.get("content", "")

        if not parent_content:
            output.append(document)
            continue

        updated = dict(document)
        updated["content"] = parent_content

        updated_metadata = dict(metadata)

        for key in [
            "source",
            "page",
            "product",
            "sku",
            "factory",
            "warehouse",
            "supplier",
            "region",
            "department",
            "sop_version",
            "effective_date",
            "document_type"
        ]:
            if key in parent_data:
                updated_metadata[key] = parent_data[key]

        updated["metadata"] = updated_metadata
        output.append(updated)

    return output


# =========================================================
# 23. CONTEXT COMPRESSION
# =========================================================

def compress_context(query, documents):
    if not documents:
        return []

    query_words = set(
        re.findall(r"\w+", query.lower())
    )

    output = []

    for document in documents:
        content = document.get("content", "")

        if not content:
            continue

        sentences = re.split(
            r"(?<=[.!?])\s+",
            content
        )

        relevant_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_words = set(
                re.findall(r"\w+", sentence.lower())
            )

            if query_words.intersection(sentence_words):
                relevant_sentences.append(sentence)

        compressed_content = (
            " ".join(relevant_sentences)
            if relevant_sentences
            else content
        )

        updated = dict(document)
        updated["content"] = compressed_content
        output.append(updated)

    return output


# =========================================================
# 24. METADATA FILTER BUILDER
# =========================================================

def build_metadata_filter(filters):
    if not isinstance(filters, dict) or not filters:
        return None

    conditions = []

    for key, value in filters.items():
        if value is None:
            continue

        if isinstance(value, str) and not value.strip():
            continue

        conditions.append({key: value})

    if not conditions:
        return None

    if len(conditions) == 1:
        return conditions[0]

    return {"$and": conditions}


# =========================================================
# 25. MAIN RAG SEARCH FUNCTION
# =========================================================

def search_documents_with_metadata(
    query,
    top_k=FINAL_RESULT_COUNT,
    where=None
):
    if not query or not query.strip():
        return []

    try:
        if collection.count() == 0:
            print("No documents are indexed.")
            return []

        # Ignore invalid non-dictionary filters.
        metadata_filter = (
            where if isinstance(where, dict) else None
        )

        print("Advanced RAG retrieval started.")

        retrieved_documents = multi_query_search(
            query,
            where=metadata_filter
        )

        if not retrieved_documents:
            return []

        parent_documents = retrieve_parent_documents(
            retrieved_documents
        )

        reranked_documents = rerank_documents(
            query,
            parent_documents
        )

        compressed_documents = compress_context(
            query,
            reranked_documents
        )

        final_count = max(1, int(top_k))

        final_documents = compressed_documents[:final_count]

        print(
            "Documents returned:",
            len(final_documents)
        )

        return final_documents

    except Exception as error:
        print("Document retrieval error:", error)
        return []


# =========================================================
# 26. TEST VECTOR STORE
# =========================================================

if __name__ == "__main__":
    print("\nVECTOR STORE STATUS")
    print(get_vector_store_status())

    print("\nINDEXED DOCUMENTS")
    print(get_indexed_documents())

    results = search_documents_with_metadata(
        "What is the inventory reorder policy?",
        top_k=3
    )

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Content:")
        print(result.get("content", "")[:500])
        print("Metadata:")
        print(result.get("metadata", {}))
        print("Rerank score:")
        print(result.get("rerank_score"))
