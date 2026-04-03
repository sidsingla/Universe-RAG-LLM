import argparse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from get_similar_docs import search_similar, GEMINI_API_KEY

LLM_MODEL = "gemini-2.5-flash"


def build_context(matches):
    blocks = []
    for i, match in enumerate(matches, 1):
        metadata = match.get("metadata", {})
        source = metadata.get("source", "unknown")
        chunk_index = metadata.get("chunk_index", "n/a")
        text = metadata.get("text", "")
        if text:
            blocks.append(f"[{i}] source={source}, chunk={chunk_index}\n{text}")
    return "\n\n".join(blocks)


def _make_llm(temperature=0.2):
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
    )


def answer_question_no_rag(question):
    """Answer using Gemini only (no document retrieval)."""
    prompt = ChatPromptTemplate.from_template(
        "You are a knowledgeable assistant. Answer clearly and helpfully.\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )
    chain = prompt | _make_llm(temperature=0.4)
    response = chain.invoke({"question": question})
    return response.content


def answer_question(question, top_k=5, use_rag=True):
    """
    If use_rag is True: retrieve from Pinecone, then answer from context.
    If False: answer with the LLM alone (no RAG).
    """
    if not use_rag:
        return answer_question_no_rag(question)

    matches = search_similar(question, top_k)
    if not matches:
        return "I could not find relevant context in the vector index."

    context = build_context(matches)

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful RAG assistant.\n"
        "Use only the provided context to answer.\n"
        "If the context is insufficient, say you are not sure.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    chain = prompt | _make_llm(temperature=0.2)
    response = chain.invoke({"context": context, "question": question})
    return response.content


def main():
    parser = argparse.ArgumentParser(description="Question answering over Pinecone using Gemini + LangChain.")
    parser.add_argument("question", type=str, help="Question to ask")
    parser.add_argument("--top_k", type=int, default=5, help="Number of retrieved chunks (RAG only)")
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Answer with Gemini only (no vector retrieval).",
    )
    args = parser.parse_args()

    answer = answer_question(args.question, top_k=args.top_k, use_rag=not args.no_rag)
    print(answer)


if __name__ == "__main__":
    main()
