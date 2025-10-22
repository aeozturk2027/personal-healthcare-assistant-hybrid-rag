🏥 Personal Healthcare Assistant – Hybrid RAG + Knowledge Graph System

🎯 Overview

The Personal Healthcare Assistant is a Hybrid RAG (Retrieval-Augmented Generation) system that combines a Neo4j Knowledge Graph for structured personal data with a FAISS vector store for general medical knowledge.
It uses GPT-4o-mini for smart intent classification and adaptive response generation.

The system automatically decides where to retrieve information from — the personal knowledge graph, the general RAG source, or both — based on the intent of the user’s question.

🔬 Hybrid Architecture – 3-Way Intent Classification
Mode	Data Source	Technology	Usage
🔒 Personal	Neo4j Knowledge Graph	Graph Query (Cypher)	Personal health data only
🌐 Generic	FAISS + MedQuad Dataset	RAG (Vector Search + LLM)	General medical knowledge
🎯 Hybrid	Neo4j + FAISS	Graph + RAG Combined	Personalized medical advice using both sources

🤖 Intent Detection (LLM-based):

Uses GPT-4o-mini instead of keyword matching for smart, context-aware classification

Supports three intent types: PERSONAL, GENERIC, and HYBRID

Includes fallback logic for uninterrupted performance

Why it’s a Hybrid RAG system:

Structured Data: Retrieved via Neo4j and Cypher queries

Unstructured Data: Retrieved via FAISS vector search and GPT summarization

Intent-Aware Routing: The model dynamically decides which data source(s) to use

Hybrid Mode: Combines both personal graph data and external medical knowledge

✨ Key Features

🔍 Transparent Demo Interface

Neo4j results and graph data are fully visible for personal queries

RAG responses include similarity scores and document sources

A detailed execution trace shows all processing steps

Designed for maximum transparency and auditability

👤 Personal Health Management

📅 Appointment tracking and reminders

💊 Medication and dosage management

🩺 Condition monitoring with severity levels

🔬 Test results and trend analysis

👨‍⚕️ Doctor profiles and visit notes

🎯 Intelligent Intent Classification

Automatically detects whether a query is personal, generic, or hybrid

Combines both knowledge sources when needed

Generates context-aware, personalized responses

🎨 Modern, Insightful UI

Intent badges (Personal / Generic / Hybrid)

Color-coded similarity scores

Detailed source explanations (with question & answer)

Sidebar dashboard summarizing personal data

Real-time execution trace visualization

⚙️ Advanced RAG Pipeline

Sentence Transformers for embeddings

FAISS for high-speed cosine similarity search

Dynamic thresholds for flexible personalization

Powered by GPT-4o-mini for efficient generation

📊 Dataset
MedQuad – Medical Question-Answer Dataset

Source: Kaggle - MedQuad Dataset

Statistics:

16,461 Q&A pairs

47 medical conditions and topics

Verified sources: NIH, Mayo Clinic, CDC, FDA, and MPlusHealthTopics

Usage:
This dataset powers the generic medical knowledge base.
Documents are embedded using Sentence Transformers and stored in FAISS for similarity-based retrieval.

⚡ Quick Start (for Demos or Judges)

Set up and run in under 5 minutes:

# 0. Download the MedQuad dataset (if not available)
# Place medquad.csv in the ./data folder

# 1. Start Neo4j via Docker
docker run --name neo4j -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/12345678 neo4j:latest

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install --upgrade pip wheel
pip install -r requirements.txt

# 4. Set up environment variables (.env)
OPENAI_API_KEY=sk-proj-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345678

# 5. Build FAISS vector index
python build_index.py

# 6. Load demo data (auto-adjusted dynamic dates)
python setup_demo_data_enhanced.py

# 7. Launch the Streamlit app
streamlit run app_hybrid.py


Example Questions

🔒 Personal: "Do I have any appointments today?"
🌐 Generic:  "What is high blood pressure?"
🎯 Hybrid:   "Should I be concerned about my blood pressure given my hypertension?"

🧩 Why Hybrid?

Most RAG systems only use unstructured documents for retrieval.
This system goes further by combining a personal structured graph (Neo4j) with unstructured medical text (FAISS).

The graph provides accurate, contextualized health records.

The RAG component provides expert-level general knowledge.

The LLM merges both for personalized, evidence-based answers.

Example hybrid query:

“Should I be worried about my blood sugar levels given my test results?”
→ The system retrieves your HbA1c test data from Neo4j and diabetes guidelines from MedQuad to produce a tailored medical insight.

🧠 System Architecture
User Question
     ↓
LLM Intent Classifier (GPT-4o-mini)
     ↓
 ┌────────────┬────────────┬────────────┐
 │  Personal  │   Generic  │   Hybrid   │
 │  (Neo4j)   │   (FAISS)  │ Neo4j+FAISS│
 └────────────┴────────────┴────────────┘
     ↓
Response Generation (GPT-4o-mini)
     ↓
User Answer + Source Transparency

🗂️ Project Structure
project_root/
├── src/
│   ├── data_processor.py         # Dataset loader
│   ├── embeddings.py             # Sentence Transformer utilities
│   ├── vector_store.py           # FAISS integration
│   ├── chatbot.py                # LLM orchestration
│   ├── neo4j_client.py           # Graph database operations
│   ├── intent_classifier.py      # 3-way classification
│   ├── hybrid_context.py         # Neo4j + FAISS coordinator
│   └── date_tools.py             # Date utilities
│
├── data/medquad.csv              # Medical Q&A dataset
├── build_index.py                # Embedding and index builder
├── setup_demo_data_enhanced.py   # Dynamic demo data generator
├── app_hybrid.py                 # Streamlit UI
├── requirements.txt
├── .env
└── README.md

🖥️ UI Highlights

Intent Badges: Clearly shows whether a response is Personal, Generic, or Hybrid

Similarity Scores: Cosine similarity with color-coded confidence levels

Neo4j Transparency: Displays queried graph nodes and relationships

Sidebar Dashboard: Quick summary of user conditions, medications, and appointments

Execution Trace: Step-by-step breakdown of all backend actions

⚙️ Technical Details

Vector Search

FAISS (Cosine Similarity)

1–2 ms retrieval time (16k documents)

LLM

Model: GPT-4o-mini

~500–800 tokens per response

Cost-effective and fast

Graph Queries

Neo4j, indexed

Average query latency < 10 ms

🔮 Roadmap

Phase 2: Authentication

JWT-based login

Role-based access (Patient / Doctor / Admin)

Phase 3: Analytics

Visual health trends

Predictive health alerts

Drug–interaction checks

Phase 4: Production

HTTPS + SSL

Data backup & audit logs

HIPAA compliance

🏆 Tech Stack
Component	Technology
Backend	Python 3.8+
Frontend	Streamlit
LLM	OpenAI GPT-4o-mini
Embeddings	Sentence Transformers (all-MiniLM-L6-v2)
Vector DB	FAISS
Graph DB	Neo4j
Dataset	MedQuad (Q&A Dataset – Kaggle)
📜 License

MIT License — Free for educational and commercial use.

🙏 Credits

MedQuad Dataset (NIH, Mayo Clinic, CDC, FDA)

Sentence Transformers by Hugging Face

FAISS by Meta AI

Neo4j Graph Database

OpenAI GPT-4o-mini API

📞 Support

If you encounter issues:

Check your .env configuration

Verify that Neo4j is running (docker ps)

Rebuild FAISS index if needed (python build_index.py)

Review the troubleshooting section

Enjoy your Personal Healthcare Assistant! 🚀
Last updated: October 22, 2025
