import argparse
import pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

PINECONE_API_KEY = ""
PINECONE_INDEX_NAME = ""
PINECONE_NAMESPACE = "default"
GEMINI_API_KEY = ""
EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 1024


def build_query_vector(query_text):
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )
    return embeddings.embed_query(
        query_text,
        output_dimensionality=EMBEDDING_DIM,
    )


def search_similar(query_text, top_k):
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    query_vector = build_query_vector(query_text)
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=PINECONE_NAMESPACE,
        include_metadata=True,
    )
    return results.get("matches", [])


def main():
    parser = argparse.ArgumentParser(description="Search similar document chunks in Pinecone.")
    parser.add_argument("query", type=str, help="Natural language query text")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    args = parser.parse_args()

    matches = search_similar(args.query, args.top_k)
    if not matches:
        print("No matches found.")
        return

    print(f"Top {len(matches)} matches for: {args.query}")
    for i, match in enumerate(matches, 1):
        metadata = match.get("metadata", {})
        source = metadata.get("source", "unknown")
        chunk_index = metadata.get("chunk_index", "n/a")
        text = metadata.get("text", "")
        score = match.get("score", 0.0)
        snippet = text[:300].replace("\n", " ").strip()

        print(f"\n{i}. score={score:.4f} | source={source} | chunk={chunk_index}")
        if snippet:
            print(f"   {snippet}")


if __name__ == "__main__":
    main()
