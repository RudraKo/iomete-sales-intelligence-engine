# The Living Sales Intelligence Engine (IOMETE)
> **Sovereign Lakehouse B2B Sales Intelligence powered by Groq (`llama-3.3-70b-versatile`) and Streamlit**

Built for the hackCBS IOMETE track. Solves B2B enterprise sales friction by transforming complex technical documentation about IOMETE (a sovereign data lakehouse built on Apache Spark, Apache Iceberg, and Kubernetes running on customer infrastructure) into instant, verified, context-aware sales briefs, objection handlers, and follow-up memos.

---

## ⚡ Setup in Under 5 Commands

```bash
# 1. Clone & navigate to the repository
cd IOMETE

# 2. Create and activate a Python virtual environment
python3 -m venv venv && source venv/bin/activate

# 3. Install core dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env

# 5. Launch the Streamlit application
streamlit run frontend/app.py
```

*(Note: In step 4, ensure you add your `GROQ_API_KEY` to `.env` or input it directly in the Streamlit UI sidebar)*

---

## 📁 Project Structure (Phase 1 Initialized)

```
IOMETE/
├── .env.example            # Environment configuration template
├── requirements.txt        # Core dependencies (streamlit, groq, pydantic, requests)
├── README.md               # Clean setup documentation
├── backend/                # Phase 2: RAG, embeddings & retrieval services
├── frontend/               # Streamlit application UI & interactive views
│   └── app.py              # Main Streamlit dashboard
├── data/                   # Living Ledger storage & documentation sources
└── utils/                  # Core utilities & LLM wrappers
    └── groq_client.py      # Groq Llama 3.3 70B client with Zero-Hallucination system prompt
```

---

## 🏛️ Core Grounding Pillars (Zero-Hallucination)

1. **Sovereign Deployment**: Customer Data Plane deployed 100% in customer VPC/infrastructure. Customer data never leaves their perimeter.
2. **Apache Spark Compute**: Managed autoscaling Spark clusters with AQE, vectorized readers, and Thrift JDBC/ODBC endpoints.
3. **Apache Iceberg Storage**: Standard open table format with ACID transactions and zero vendor lock-in.
4. **Kubernetes Orchestration**: Cloud-native operators on AWS EKS, GCP GKE, Azure AKS, and on-prem K8s.
5. **Fallback Rule**: Unsupported technical claims strictly return:  
   `"Unknown / Requires Engineering Verification"`.

---

## 🔄 Roadmap & Completed Phases
- **Phase 1 [COMPLETE]**: Project architecture, dependencies, Groq client wrapper (`llama-3.3-70b-versatile`), and Zero-Hallucination prompt.
- **Phase 2 [COMPLETE]**: Knowledge Ingestion Pipeline, structured markdown knowledge base (`/data/iomte_knowledge_base.md`), and semantic chunker.
- **Phase 3 [COMPLETE]**: Core Retrieval module (`/backend/retrieval.py`) and Objection Inversion Engine (`/backend/engine.py`).
- **Phase 4 [COMPLETE]**: Streamlit Sales Copilot UI (`/frontend/app.py`) with telemetry, quick-select pills, and verification cards.
- **Phase 5 & 6 [COMPLETE]**: Automated C-Level Executive Proposal Generator & Deal Risk Assessor (`/backend/engine.py`).
- **Phase 11 [COMPLETE]**: Hallucination & Trap Testing & Hardening (`/tests/test_hallucination_audit.py`).

---

## 🚢 Deployment Options

### Option 1: Docker (Recommended for Container Platforms)
```bash
# Build the Docker image
docker build -t iomete-sales-engine .

# Run container locally or on Cloud VM
docker run -p 8501:8501 -e GROQ_API_KEY=your_key_here iomete-sales-engine
```

### Option 2: Docker Compose
```bash
docker compose up -d
```

### Option 3: Streamlit Community Cloud (1-Click Deployment)
1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Connect repository with main file path: `frontend/app.py`.
4. Add `GROQ_API_KEY` under **App Settings → Secrets**.

### Option 4: Production Linux / VM with `run.sh`
```bash
./run.sh
```
