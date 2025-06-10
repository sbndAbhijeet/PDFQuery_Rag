# PDFQuery Retrieval System

A Python-based question answering system built on top of gemini-2.0-flash and PDF document parsing. This application allows users to ask questions based only on the context retrieved from the provided PDF file, ensuring accurate, referenceable answers.

---

## ✨ Features

* Extracts text from PDF
* Splits and chunks text for vector embedding
* Uses `GoogleGenerativeAIEmbeddings` and `QdrantDB` vector store for semantic search
* Retrieves relevant context and feeds it to GPT for accurate, context-bound answers
* Prevents hallucination by using only retrieved context

---

## 📂 Directory Structure

```
.
├── main.py
├── vector_db.py
├── streamlit_app.py
├── .gitignore
├── requirements.txt
├── README.md
├── uploaded_pdfs/
└── .env
```

---

## ⚡ Quickstart

### 1. Clone Repository

```bash
git clone https://github.com/sbndAbhijeet/PDFQuery_Rag
cd PDFQuery_Rag
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```


### 3. Run Script

```bash
streamlit run streamlit_app.py
```
Then you will be directed to streamlit interface, where you can upload a document, process it and ask questions related to it.
---

## 🤖 How It Works

### ✍️ Document Parsing
Uses LangChain PyPDF and extracts the pdf data.

### 🧰 Embedding & Indexing

Uses Google embedding model (`models/embedding-001`) and `QdrantDB` to index vector chunks.


---

## 🔒 Prompt Structure

### System Prompt:

```
You are a helpful assistant that gives detailed clear answers based only on the provided document excerpts.
Use only the content from the retrieved context and do not make up facts.
If relevant info is found, answer clearly and concisely. At the end, list page numbers.
If not found, respond: "I couldn’t find the answer in the provided documents."
```

### User Prompt Template:

```
Use the following context to answer the question.

Context:
<context>

Question: <user_question>
```

---

## 🚀 Future Enhancements

* Add metadata search (e.g., chapter titles)
* PDF viewer alongside answer
* Highlighting relevant text
* Multilingual PDF support

---

## ✨ Example

```
Question: Who are the three men in the story?

Answer: George, Harris, and Jerome (the narrator) are the three men in the story.

Pages: 1, 3, 5
```
---

## 💼 License

MIT License
