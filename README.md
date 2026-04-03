# 🌌 Universe QA: RAG vs. LLM Comparison

Welcome to **Universe QA**, a specialized exploration tool designed to answer your deepest questions about the cosmos. This project serves as a practical laboratory to learn and compare the performance of a standard Large Language Model (LLM) against a Retrieval-Augmented Generation (RAG) system.

---

## 🎯 Project Purpose

The goal of this project is to visualize the difference between "parametric memory" (what an LLM knows from training) and "external knowledge" (specific data provided to the model). By comparing the two modes, you can observe how grounding an AI in factual documents reduces hallucinations and increases technical accuracy.

### 📚 The Knowledge Base
The RAG system is fueled by official scientific data.
* **Source:** Technical documents and research papers curated from **NASA**.
* **Location:** All source files are stored in the `/data` directory.

---

## ⚙️ Operational Modes

| Mode | Description |
| :--- | :--- |
| **LLM Only** | The model answers based on its original training data. Best for general theories and broad concepts. |
| **RAG Mode** | The model searches the `/data` directory for NASA documents to find specific facts before answering. Best for mission specifics and recent data. |

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python installed (3.11) and the required libraries (Streamlit, and your chosen LLM/Vector DB framework) configured in your environment. Run requirements.txt!

### 2. Adding keys
Add Pinecone and Gemini keys in config.py

### 3. Build RAG
Build the RAG system, run:

```bash
python build_rag.py
```

### 4. Running the App
The interface is built using **Streamlit** for a seamless, interactive experience. To launch the frontend and do Q/A, run:

```bash
streamlit run ui_frontend/app.py
