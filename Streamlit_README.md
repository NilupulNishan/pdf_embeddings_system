Here’s a clean and professional **README.md** for your project:

---

# 📘 PDF Query System (Streamlit UI)

A **production-grade PDF Query System** built with **Streamlit** that enables intelligent querying over PDF collections using a Retrieval-Augmented Generation (RAG) pipeline.

This UI allows you to:

* 🔎 Query a single collection or all collections
* 💬 Chat with your PDFs
* 📚 View source references
* 🧱 Build or refresh the vector index directly from the UI (optional)

---

## 🚀 Features

### ✅ Collection Selection

* Select a specific PDF collection
* Or search across **ALL collections**
* Dynamically initializes the correct retriever:

  * `SmartRetriever` (single collection)
  * `MultiCollectionRetriever` (all collections)

### 💬 Chat Interface

* Interactive Streamlit chat UI
* Maintains session-based chat history
* Clean light theme UI

### 📚 Source Display

* Shows referenced source chunks
* Expandable "Sources" section per answer
* Uses `SourceFormatter` for structured formatting

### 🧱 Optional Index Builder

* "Build Index" button in sidebar
* Runs `scripts/process_pdfs.py`
* Refreshes collections automatically after processing

---

## 🏗️ Project Structure (Relevant Parts)

```
project_root/
│
├── src/
│   ├── retriever.py
│   ├── storage_manager.py
│   └── source_formatter.py
│
├── scripts/
│   └── process_pdfs.py
│
└── streamlit_app.py   ← (This UI file)
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd <your-project>
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure your requirements include:

* streamlit
* your vector DB dependencies
* embedding model dependencies
* any LLM libraries used internally

---

## 🧠 Build the Index (First Time Setup)

Before querying, you must process PDFs:

```bash
python scripts/process_pdfs.py
```

Or use the **🧱 Build Index** button inside the UI (if enabled).

---

## ▶️ Run the Application

```bash
streamlit run streamlit_app.py
```

Then open:

```
http://localhost:8501
```

---

## 🧩 How It Works

### 1️⃣ StorageManager

* Lists available vector collections
* Manages stored embeddings

### 2️⃣ SmartRetriever

* Used when a single collection is selected
* Executes `query()`

### 3️⃣ MultiCollectionRetriever

* Used when searching across all collections
* Executes `query_best()`

### 4️⃣ SourceFormatter

* Formats retrieved chunks
* Displays clean source metadata in UI

---

## 🔁 Query Flow

1. User selects collection (or ALL)
2. User asks question
3. Retriever searches embeddings
4. Best chunks retrieved
5. LLM generates answer
6. Sources displayed under expandable section

---

## 🎨 UI Design

* Light theme
* Wide layout
* Sidebar collection manager
* Clean chat bubbles
* Expandable source viewer
* Session-based message history

---

## 🛠 Configuration Notes

* Ensure your vector database directory exists
* Ensure embeddings are already built
* If no collections are found:

  * Run `scripts/process_pdfs.py`
  * Then click **Refresh**

---

## 🧪 Example Query

```
How do I reset the device?
```

---

## ❗ Troubleshooting

### No collections found

Run:

```bash
python scripts/process_pdfs.py
```

### Build Index button disabled

Ensure this import works:

```python
from scripts.process_pdfs import main as process_main
```

---

## 📌 Future Improvements (Optional)

* Add authentication
* Add PDF upload from UI
* Add streaming responses
* Add conversation export
* Add analytics dashboard
* Dockerize deployment

---

## 👨‍💻 Author

Built as a **Production-grade PDF Query System with Streamlit + RAG Architecture**

---

If you want, I can also generate:

* 🔹 A shorter README (for internal repo)
* 🔹 A more enterprise-style README
* 🔹 A GitHub-ready version with badges
* 🔹 A Docker deployment README
* 🔹 A resume-friendly project description 🚀
Here’s a clean and professional **README.md** for your project:

---

# 📘 PDF Query System (Streamlit UI)

A **production-grade PDF Query System** built with **Streamlit** that enables intelligent querying over PDF collections using a Retrieval-Augmented Generation (RAG) pipeline.

This UI allows you to:

* 🔎 Query a single collection or all collections
* 💬 Chat with your PDFs
* 📚 View source references
* 🧱 Build or refresh the vector index directly from the UI (optional)

---

## 🚀 Features

### ✅ Collection Selection

* Select a specific PDF collection
* Or search across **ALL collections**
* Dynamically initializes the correct retriever:

  * `SmartRetriever` (single collection)
  * `MultiCollectionRetriever` (all collections)

### 💬 Chat Interface

* Interactive Streamlit chat UI
* Maintains session-based chat history
* Clean light theme UI

### 📚 Source Display

* Shows referenced source chunks
* Expandable "Sources" section per answer
* Uses `SourceFormatter` for structured formatting

### 🧱 Optional Index Builder

* "Build Index" button in sidebar
* Runs `scripts/process_pdfs.py`
* Refreshes collections automatically after processing

---

## 🏗️ Project Structure (Relevant Parts)

```
project_root/
│
├── src/
│   ├── retriever.py
│   ├── storage_manager.py
│   └── source_formatter.py
│
├── scripts/
│   └── process_pdfs.py
│
└── streamlit_app.py   ← (This UI file)
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd <your-project>
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure your requirements include:

* streamlit
* your vector DB dependencies
* embedding model dependencies
* any LLM libraries used internally

---

## 🧠 Build the Index (First Time Setup)

Before querying, you must process PDFs:

```bash
python scripts/process_pdfs.py
```

Or use the **🧱 Build Index** button inside the UI (if enabled).

---

## ▶️ Run the Application

```bash
streamlit run streamlit_app.py
```

Then open:

```
http://localhost:8502
```

---

## 🧩 How It Works

### 1️⃣ StorageManager

* Lists available vector collections
* Manages stored embeddings

### 2️⃣ SmartRetriever

* Used when a single collection is selected
* Executes `query()`

### 3️⃣ MultiCollectionRetriever

* Used when searching across all collections
* Executes `query_best()`

### 4️⃣ SourceFormatter

* Formats retrieved chunks
* Displays clean source metadata in UI

---

## 🔁 Query Flow

1. User selects collection (or ALL)
2. User asks question
3. Retriever searches embeddings
4. Best chunks retrieved
5. LLM generates answer
6. Sources displayed under expandable section

---

## 🎨 UI Design

* Light theme
* Wide layout
* Sidebar collection manager
* Clean chat bubbles
* Expandable source viewer
* Session-based message history

---

## 🛠 Configuration Notes

* Ensure your vector database directory exists
* Ensure embeddings are already built
* If no collections are found:

  * Run `scripts/process_pdfs.py`
  * Then click **Refresh**

---

## 🧪 Example Query

```
How do I reset the device?
```

---

## ❗ Troubleshooting

### No collections found

Run:

```bash
python scripts/process_pdfs.py
```

### Build Index button disabled

Ensure this import works:

```python
from scripts.process_pdfs import main as process_main
```

---

## 📌 Future Improvements (Optional)

* Add authentication
* Add PDF upload from UI
* Add streaming responses
* Add conversation export
* Add analytics dashboard
* Dockerize deployment

---

## 👨‍💻 Author

Built as a **Production-grade PDF Query System with Streamlit + RAG Architecture**

---

If you want, I can also generate:

* 🔹 A shorter README (for internal repo)
* 🔹 A more enterprise-style README
* 🔹 A GitHub-ready version with badges
* 🔹 A Docker deployment README
* 🔹 A resume-friendly project description 🚀
---
# 📘 PDF Query System (Streamlit UI)

A **production-grade PDF Query System** built with **Streamlit** that enables intelligent querying over PDF collections using a Retrieval-Augmented Generation (RAG) pipeline.

This UI allows you to:

* 🔎 Query a single collection or all collections
* 💬 Chat with your PDFs
* 📚 View source references
* 🧱 Build or refresh the vector index directly from the UI (optional)

---

## 🚀 Features

### ✅ Collection Selection

* Select a specific PDF collection
* Or search across **ALL collections**
* Dynamically initializes the correct retriever:

  * `SmartRetriever` (single collection)
  * `MultiCollectionRetriever` (all collections)

### 💬 Chat Interface

* Interactive Streamlit chat UI
* Maintains session-based chat history
* Clean light theme UI

### 📚 Source Display

* Shows referenced source chunks
* Expandable "Sources" section per answer
* Uses `SourceFormatter` for structured formatting

### 🧱 Optional Index Builder

* "Build Index" button in sidebar
* Runs `scripts/process_pdfs.py`
* Refreshes collections automatically after processing

---

## 🏗️ Project Structure (Relevant Parts)

```
project_root/
│
├── src/
│   ├── retriever.py
│   ├── storage_manager.py
│   └── source_formatter.py
│
├── scripts/
│   └── process_pdfs.py
│
└── streamlit_app.py   ← (This UI file)
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd <your-project>
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure your requirements include:

* streamlit
* your vector DB dependencies
* embedding model dependencies
* any LLM libraries used internally

---

## 🧠 Build the Index (First Time Setup)

Before querying, you must process PDFs:

```bash
python scripts/process_pdfs.py
```

Or use the **🧱 Build Index** button inside the UI (if enabled).

---

## ▶️ Run the Application

```bash
streamlit run streamlit_app.py
```

Then open:

```
http://localhost:8501
```

---

## 🧩 How It Works

### 1️⃣ StorageManager

* Lists available vector collections
* Manages stored embeddings

### 2️⃣ SmartRetriever

* Used when a single collection is selected
* Executes `query()`

### 3️⃣ MultiCollectionRetriever

* Used when searching across all collections
* Executes `query_best()`

### 4️⃣ SourceFormatter

* Formats retrieved chunks
* Displays clean source metadata in UI

---

## 🔁 Query Flow

1. User selects collection (or ALL)
2. User asks question
3. Retriever searches embeddings
4. Best chunks retrieved
5. LLM generates answer
6. Sources displayed under expandable section

---

## 🎨 UI Design

* Light theme
* Wide layout
* Sidebar collection manager
* Clean chat bubbles
* Expandable source viewer
* Session-based message history

---

## 🛠 Configuration Notes

* Ensure your vector database directory exists
* Ensure embeddings are already built
* If no collections are found:

  * Run `scripts/process_pdfs.py`
  * Then click **Refresh**

---

## 🧪 Example Query

```
How do I reset the device?
```

---

## ❗ Troubleshooting

### No collections found

Run:

```bash
python scripts/process_pdfs.py
```

### Build Index button disabled

Ensure this import works:

```python
from scripts.process_pdfs import main as process_main
```

---

## 📌 Future Improvements (Optional)

* Add authentication
* Add PDF upload from UI
* Add streaming responses
* Add conversation export
* Add analytics dashboard
* Dockerize deployment

---

## 👨‍💻 Author

Built as a **Production-grade PDF Query System with Streamlit + RAG Architecture**

---
