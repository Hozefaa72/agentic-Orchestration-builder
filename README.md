#  Agentic Orchestration Builder (v2)

An **agentic orchestration platform** designed to create, execute, and manage AI-driven workflows dynamically.  
The system supports **multi-role access**, **modular orchestration design**, and **rollback-capable DAG execution** — enabling advanced automation and flexible agent collaboration.

---

##  Overview

This project implements an **Agentic Orchestration Builder** — a backend system where **Admins** can design and manage AI-driven orchestration flows, and **Users** can interact with them in real-time.

###  Core Objectives
- Build **orchestrations** using modular **steps** connected as a **DAG (Directed Acyclic Graph)**.
- Allow **rollback** of any orchestration flow when a step fails.
- Support **multi-user orchestration instances** for concurrent execution.
- Maintain **separate models** for key components like:
  - `LLM`
  - `KnowledgeBase`
  - `Agent`
  - `Orchestration`
  - `OrchestrationInstance`
  - `Steps`
- Introduce **real-time communication** via **WebSockets** and **threaded execution** (v2).

---

##  System Architecture

### **Roles**
| Role | Description |
|------|--------------|
| **SuperAdmin** | Manages platform-level configurations and permissions. |
| **Admin** | Creates and manages orchestrations and their steps (DAG builder). |
| **User** | Executes orchestrations, interacts with agents, and views results. |

---

### **Data Models**

| Model | Responsibility |
|--------|----------------|
| **User** | Authentication, role management, and user-specific orchestration access. |
| **LLMModel** | Defines the base LLMs used (e.g., OpenAI, Gemini, Anthropic). |
| **KnowledgeBase** | Stores knowledge chunks and embeddings for context-aware retrieval. |
| **Agent** | Represents an AI agent with capabilities tied to orchestration steps. |
| **Orchestration** | Defines the workflow (DAG) with metadata and step relationships. |
| **OrchestrationInstance** | Handles execution context per user; supports rollback and multiple concurrent runs. |
| **Steps** | Represents a single atomic unit in an orchestration, can include prompts, API calls, or approvals. |

---

### **Execution Flow**

1. **Admin creates orchestration**
   - Defines steps (nodes) and their dependency structure (edges).
   - Each step may contain:
     - LLM interaction
     - Tool/API execution
     - Human approval via email/websocket
     - Validation logic

2. **User executes orchestration**
   - A new `OrchestrationInstance` is created.
   - Steps are executed as per DAG sequence.
   - Each step status is tracked (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`).

3. **Rollback mechanism**
   - If a step fails or validation fails:
     - The orchestration can rollback to a previous checkpoint or re-execute.
     - Steps maintain state and logs for recovery.

4. **WebSocket / Threading (v2)**
   - Real-time updates to frontend via WebSockets.
   - Thread-based handling for non-blocking orchestration execution.
   - Users can view live orchestration status, logs, and step progress.

---

##  Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend Framework** | FastAPI |
| **Database** | MongoDB (via Beanie ODM) |
| **Auth** | JWT-based authentication |
| **Real-time Communication** | WebSocket |
| **LLM Integrations** | OpenAI / Gemini  |
| **Embedding / KB** | Vector Databases (chroma_db) |
| **Deployment** | Docker-ready, modular microservice structure |

---

## 🔄 Example Flow

```mermaid
graph TD
A[Admin Creates Orchestration] --> B[Define Steps as DAG]
B --> C[User Executes Instance]
C --> D[Step 1 - Agent/LLM Execution]
D --> E[Step 2 - Human Approval]
E --> F{Validation Successful?}
F -->|Yes| G[Proceed to Next Step]
F -->|No| H[Rollback to Previous State]
G --> I[Complete Orchestration]
