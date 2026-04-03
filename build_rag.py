import hashlib
import os
from get_similar_docs import PINECONE_API_KEY
import pinecone
from langchain_community.document_loaders import DirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, GEMINI_API_KEY, PINECONE_NAMESPACE

DATA_DIR = "./data"
EXTENSIONS = {".txt", ".pdf", ".md", ".docx", ".html", ".csv"}
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
EMBEDDING_DIM = 1024

def get_key(path):
  # Use deterministic hashing so IDs remain stable across runs.
  return hashlib.sha1(path.encode("utf-8")).hexdigest()[:16]


def ingest_one(index, embeddings, rel_path):
  file_key = get_key(rel_path)
  meta_id = f"meta::{file_key}"

  existing = index.fetch(ids=[meta_id], namespace=PINECONE_NAMESPACE).get("vectors", {}).get(meta_id)
  if existing:
    print(f"Skip existing: {rel_path}")
    return "skipped"
  print(f"Index new: {rel_path}")

  docs = DirectoryLoader(DATA_DIR, glob=rel_path).load()
  chunks = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
  ).split_documents(docs)

  for i, chunk in enumerate(chunks):
    chunk.metadata.update({"source": rel_path, "chunk_index": i})

  if chunks:
    ids = [f"doc::{file_key}::{i}" for i in range(len(chunks))]
    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings.embed_documents(texts, output_dimensionality=EMBEDDING_DIM)
    payload = []
    for i, vec in enumerate(vectors):
      meta = dict(chunks[i].metadata)
      meta["text"] = texts[i]
      payload.append((ids[i], vec, meta))
    index.upsert(vectors=payload, namespace=PINECONE_NAMESPACE)

  meta_vector = embeddings.embed_query(
    f"meta {rel_path}", output_dimensionality=EMBEDDING_DIM
  )
  index.upsert(
    vectors=[
      (
        meta_id,
        meta_vector,
        {"type": "ingest_meta", "source": rel_path, "chunk_count": len(chunks)},
      )
    ],
    namespace=PINECONE_NAMESPACE,
  )
  return "indexed"


def main():
  if not os.path.isdir(DATA_DIR):
    print(f"Missing directory: {DATA_DIR}")
    return

  if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    print("Set PINECONE_API_KEY and PINECONE_INDEX_NAME.")
    return

  pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
  index = pc.Index(PINECONE_INDEX_NAME)
  # Use a model that supports embedContent (see https://ai.google.dev/gemini-api/docs/embeddings)
  # Text-only: gemini-embedding-001. Multimodal: gemini-embedding-2-preview
  embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=GEMINI_API_KEY,
  )

  # Enforce dimension match to avoid quality loss from truncation/padding.
  probe_vector = embeddings.embed_query(
    "dimension_check", output_dimensionality=EMBEDDING_DIM
  )
  embedding_dim = len(probe_vector)
  index_dim = pc.describe_index(PINECONE_INDEX_NAME).dimension
  if index_dim != embedding_dim:
    print(
      f"Dimension mismatch: index={index_dim}, embeddings={embedding_dim}. "
      f"Create/use a Pinecone index with dimension {embedding_dim}."
    )
    return

  files = []
  for root, _, names in os.walk(DATA_DIR):
    for name in names:
      if os.path.splitext(name)[1].lower() in EXTENSIONS:
        files.append(os.path.relpath(os.path.join(root, name), DATA_DIR))

  indexed = 0
  skipped = 0
  for rel_path in files:
    try:
      status = ingest_one(index, embeddings, rel_path)
      indexed += status == "indexed"
      skipped += status == "skipped"
    except Exception as e:
      print(f"Error loading {rel_path}: {e}")

  print(f"Done. Indexed: {indexed}, Skipped(existing): {skipped}, Total: {len(files)}")


if __name__ == "__main__":
  main()
