# IMDC (Heng) Metastatic Renal Cell Carcinoma Risk Score

> **Domain:** Medical Oncology & Cancer Staging Systems
> **Reference Guidelines & Standards:** AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

IMDC (Heng) Metastatic Renal Cell Carcinoma Risk Score calculator for mRCC systemic therapy. Computes IMDC risk group (Favorable, Intermediate, Poor) based on clinical parameters.

Zero-dependency Python implementation with single and batch evaluation modes, FastAPI REST API, and enterprise-grade security features.

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm computing weighted risk scores
- **`process_single()`**: Evaluate a single case with provided parameters
- **`process_batch()`**: Process multiple cases from CSV input
- **`main()`**: CLI entry point with subcommands

### 🏗️ Architecture

- **`imdc_risk.py`**: Core risk calculation engine
- **`cli.py`**: Command-line interface with audit, chat, batch, and serve commands
- **`agents/`**: Enterprise multi-agent orchestration framework
  - `supervisor.py`: Master orchestrator coordinating specialized workers
  - `workers.py`: Domain-specific evaluation workers (QC, Safety, Protocol)
  - `base.py`: Security guards, PHI protection, HMAC-SHA256 audit trail
  - `models.py`: Pydantic data models with validation
  - `api.py`: FastAPI REST endpoints
  - `metrics.py`: Prometheus operational metrics
  - `learning.py`: Bayesian calibration engine
  - `streamer.py`: WebSocket telemetry broadcaster
- **`enrichment.py`**: Extended feature engines (longitudinal tracking, FHIR, dashboards)
- **`simulator.py`**: High-throughput stress testing

---

## 📐 Mathematical Formulation

```text
score = primary_val + Σ(numeric_vals[i] * (1.0 / (i+1)) for i in range(1, n))
rounded_score = round(score, 2)

Classification:
  score < 10.0  → "Low / Standard"       → Standard monitoring
  score < 25.0  → "Moderate / Intermediate" → Close observation
  score >= 25.0 → "High / Severe"          → Urgent clinical intervention
```

---

## 💻 Installation

### Prerequisites
- Python 3.10, 3.11, or 3.12
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/imdc-metastatic-renal-risk.git
cd imdc-metastatic-renal-risk

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your AUDIT_SECRET_KEY
```

---

## 🚀 Usage

### 1. Single Case Evaluation
```bash
python imdc_risk.py single --v1 14.5 --v2 4.2 --v3 1.8
```

### 2. Batch CSV Processing
```bash
python imdc_risk.py batch -i sample.csv -o results.csv
```

### 3. Enterprise CLI with Audit Trail
```bash
# Run single task evaluation with HMAC audit
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2

# Batch process with full audit trail
python cli.py batch -i sample.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Query supervisory chat
python cli.py chat "Explain risk stratification"
```

### 4. FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Or with Docker:
```bash
docker-compose up --build
```

### 5. API Endpoints

| Endpoint | Method | Description |
|:---------|:-------|:------------|
| `/health` | GET | Health check and system metadata |
| `/metrics` | GET | Prometheus operational metrics |
| `/api/audit` | POST | Submit task for evaluation |
| `/api/chat` | POST | Supervisory conversational query |
| `/api/audit/logs` | GET | Retrieve and verify audit trail |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Patient identifier | Required |
| `v1` | Primary measurement | Required |
| `v2` | Secondary measurement | Required |
| `v3` | Tertiary measurement | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with integrity verification
* **Path Traversal Protection:** Input validation preventing directory traversal attacks
* **Secure Secret Management:** Environment-based configuration with no hardcoded production secrets
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama, Claude, GPT-4o, and deterministic mocks
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights
* **FastAPI & Prometheus Telemetry:** OpenAPI 3.1 REST endpoints and operational metrics

### Environment Configuration

| Variable | Description | Required |
|:---------|:------------|:---------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 signing key | Yes (production) |
| `MODEL_PROVIDER` | LLM provider (mock/ollama/claude/openai) | No (default: mock) |
| `HOST` | API server host | No (default: 127.0.0.1) |
| `PORT` | API server port | No (default: 8000) |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

### Test Coverage

- **Core algorithm tests**: Single and batch evaluation
- **Security tests**: PHI detection, path traversal prevention, audit integrity
- **Worker tests**: Specialized agent evaluation logic
- **Integration tests**: Supervisor consensus and CLI commands
- **Enrichment tests**: Feature engine execution

---

## 🐳 Container Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or manually
docker build -t imdc-metastatic-renal-risk .
docker run -p 8000:8000 --env-file .env imdc-metastatic-renal-risk
```

---

## 📁 Project Structure

```
imdc-metastatic-renal-risk/
├── agents/                 # Enterprise multi-agent framework
│   ├── __init__.py
│   ├── api.py             # FastAPI REST endpoints
│   ├── base.py            # Security, PHI guard, audit trail
│   ├── learning.py        # Bayesian calibration engine
│   ├── llm_factory.py     # LLM provider factory
│   ├── metrics.py         # Prometheus metrics
│   ├── models.py          # Pydantic data models
│   ├── streamer.py        # WebSocket telemetry
│   ├── supervisor.py      # Master orchestrator
│   └── workers.py         # Specialized evaluation workers
├── tests/                  # Test suite
│   ├── test_enrichment.py
│   ├── test_imdc_metastatic_renal_risk.py
│   └── test_security.py
├── web/                    # Operations console UI
│   └── index.html
├── conftest.py            # Pytest configuration
├── cli.py                 # Enterprise CLI
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container definition
├── enrichment.py          # Extended feature engines
├── imdc_risk.py           # Core risk calculation
├── openapi_spec.json      # OpenAPI specification
├── requirements.txt       # Python dependencies
├── sample.csv             # Sample input data
└── simulator.py           # Stress testing simulator
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
