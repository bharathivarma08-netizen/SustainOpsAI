from pathlib import Path
import chromadb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
CHROMA_DIR = PROJECT_ROOT / "outputs" / "chroma_db"

COLLECTION_NAME = "sustainops_knowledge"


def load_knowledge_documents():
    """
    Load all Markdown documents from the knowledge directory.
    """
    documents = []

    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        documents.append({
            "filename": path.name,
            "text": text
        })

    return documents


def split_into_chunks(text):
    """
    Split a Markdown document into meaningful sections.

    Each Markdown heading starts a new chunk.
    """
    lines = text.splitlines()

    chunks = []
    current_chunk = []

    for line in lines:

        if line.startswith("#") and current_chunk:

            chunk_text = "\n".join(current_chunk).strip()

            if chunk_text:
                chunks.append(chunk_text)

            current_chunk = []

        current_chunk.append(line)

    if current_chunk:

        chunk_text = "\n".join(current_chunk).strip()

        if chunk_text:
            chunks.append(chunk_text)

    return chunks


def create_vector_database():
    """
    Create or refresh the ChromaDB knowledge collection.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    documents = load_knowledge_documents()

    chunk_documents = []
    chunk_ids = []
    chunk_metadata = []

    for document in documents:

        chunks = split_into_chunks(
            document["text"]
        )

        for index, chunk in enumerate(chunks):

            chunk_id = (
                f"{Path(document['filename']).stem}"
                f"_chunk_{index}"
            )

            chunk_documents.append(chunk)
            chunk_ids.append(chunk_id)

            chunk_metadata.append({
                "filename": document["filename"],
                "chunk_index": index
            })

    # Refresh the collection so it reflects
    # the current knowledge files.
    if collection.count() > 0:

        existing = collection.get()

        if existing["ids"]:
            collection.delete(
                ids=existing["ids"]
            )

    collection.add(
        ids=chunk_ids,
        documents=chunk_documents,
        metadatas=chunk_metadata
    )

    return collection


def get_collection():
    """
    Open the existing SustainOps knowledge collection.

    If it does not exist yet, create it.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    if collection.count() == 0:
        collection = create_vector_database()

    return collection


def retrieve_knowledge(query, top_k=3):
    """
    Retrieve the most relevant knowledge chunks.

    Returns structured results containing:
    - source filename
    - chunk index
    - retrieved text
    """

    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    retrieved_results = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_results.append({
            "source": metadata["filename"],
            "chunk": metadata["chunk_index"],
            "text": document,
            "distance": distance
        })

    return retrieved_results


if __name__ == "__main__":

    print("\n========== SUSTAINOPS RAG QUERY INTERFACE ==========\n")

    collection = create_vector_database()

    print(
        f"Knowledge chunks stored: "
        f"{collection.count()}"
    )

    query = (
        "Could HVAC operation explain "
        "an unusual electricity anomaly?"
    )

    print("\n--- Query ---")
    print(query)

    results = retrieve_knowledge(
        query,
        top_k=3
    )

    print("\n--- Retrieved Evidence ---")

    for index, result in enumerate(
        results,
        start=1
    ):

        print(f"\nResult {index}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk']}")
        print(f"Distance: {result['distance']:.4f}")
        print("Text:")
        print(result["text"])

    print("\n=====================================================\n")