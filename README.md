---
title: DevEnv Resolver
emoji: 🛠️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
license: mit
short_description: OpenEnv SRE Debugging Simulator
---


<div align="center">

# 🛠️ DevEnv Resolver
### SRE Incident Triage Environment

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-Compliant-success?style=for-the-badge&logo=framework)](https://github.com/meta-pytorch/OpenEnv)
[![Tasks](https://img.shields.io/badge/Tasks-3_Tiers-blue?style=for-the-badge)](https://github.com/meta-pytorch/OpenEnv)
[![Deployment](https://img.shields.io/badge/Deployment-HuggingFace_Spaces-orange?style=for-the-badge&logo=huggingface)](https://huggingface.co/)
[![Runtime](https://img.shields.io/badge/Runtime-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

*A deterministic, zero-LLM reinforcement learning environment evaluating the root-cause analysis and remediation capabilities of AI agents against real-world developer environment outages.*

<br>
</div>

---

## 💡 Motivation & Real-World Utility
Broken development environments, silent dependency conflicts, and obscured OS-level permission errors cost engineering teams millions of hours annually. Resolving them involves deductive reasoning, state manipulation, and strict execution ordering. 

**DevEnv Resolver** tests whether an LLM can simulate a Staff Site Reliability Engineer (SRE) by reading raw terminal outputs, recognizing system-level conflicts, and applying exact remediation commands to restore a healthy state. 

This is a deep, stateful simulation—not a shallow text-echo environment. Actions have actual consequences, and incorrect operations will leave the system in an unrecoverable state.

---

## 🧭 Action & Observation Spaces

The environment strictly adheres to the OpenEnv standard using Pydantic-typed models inheriting from `CallToolAction` and `CallToolObservation`.

### Action Space (`DevEnvAction`)
The agent interacts with the environment by passing structured JSON commands.
* **`command`** `(str)`: The shell action to execute (`install`, `uninstall`, `fix_permissions`, `check_status`).
* **`package_name`** `(str, optional)`: Target package (e.g., `requests`, `numpy`).
* **`version`** `(str, optional)`: Target version for strict pinning (e.g., `1.20.0`).

### Observation Space (`DevEnvObservation`)
The environment returns the exact system state after command execution.
* **`terminal_output`** `(str)`: Standard output or error logs from the simulated terminal.
* **`goal_prompt`** `(str)`: The explicit objective the agent must achieve.
* **`feedback`** `(str)`: Heuristic feedback from the system evaluator.

---

## 📈 Tasks & Difficulty Gradient

The environment evaluates agents across 3 distinct difficulty tiers. Tasks are stateful; agents must execute actions in the correct logical sequence.

| Tier | Challenge | Description | Core Competency |
| :--- | :--- | :--- | :--- |
| 🟢 **Easy** | Missing Package | Diagnose a `ModuleNotFoundError` and install the missing dependency. | Log parsing and basic package management. |
| 🟡 **Medium** | Version Conflict | Resolve a strict version clash requiring an explicit `uninstall` of a newer package before installing an older, pinned version. | Multi-step remediation and state awareness. |
| 🔴 **Hard** | Permission Denied | Diagnose a silent crash caused by `/var/run/` socket permission errors and remediate using system commands. | Deep system architecture and OS-level debugging. |

---

## ⚖️ Deterministic Evaluation (Graders)
To ensure absolute zero-LLM reproducibility, speed, and fairness across millions of inference runs, all grading is performed via deterministic deductive heuristics (`server/graders.py`).

* **Strict Bounds:** Rewards are strictly clamped to `[0.01, 0.99]` to maintain OpenEnv boundary validation compliance.
* **Partial Credit Allocation:** Agents receive partial scores for identifying the correct package/version, even if they fail to execute the correct sequence (e.g., scoring `0.50` for failing to uninstall before downgrading, instead of a binary `0.0`).

---

## 🏗️ Repository Architecture

```text
devenv-resolver/
├── openenv.yaml           # Core OpenEnv metadata and task routing
├── models.py              # Pydantic schemas (Action/Observation)
├── inference.py           # Hackathon-compliant baseline agent evaluation
├── Dockerfile             # 2vCPU / 8GB RAM strict container spec
├── requirements.txt       # Environment dependencies
└── server/
    ├── app.py             # FastAPI server & hackathon validation endpoints
    ├── environment.py     # Stateful RL environment simulator
    └── graders.py         # Deterministic scoring logic


### 🚀 Quick Start & Setup

### Local Execution
Ensure you have Python 3.10+ installed.

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/devenv-resolver.git](https://github.com/your-username/devenv-resolver.git)
cd devenv-resolver

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the OpenEnv FastAPI server
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Docker Deployment
The environment is rigorously containerized for standard OpenEnv Phase 1 validation (operating comfortably under the 2 vCPU / 8GB RAM hardware limits).

```bash
docker build -t devenv_resolver:latest .
docker run -p 7860:7860 devenv_resolver:latest
```

---

## 🤖 Baseline Inference Testing

The repository includes a battle-tested `inference.py` script that natively integrates with the OpenEnv HTTP API. It safely handles LLM markdown formatting and strictly adheres to the hackathon's regex output logging protocols (`[START]`, `[STEP]`, `[END]`).

```bash
# Export your Hugging Face Token for the API Router
export HF_TOKEN="your_hf_token_here"

# Run the evaluation loop against all 3 tiers
python inference.py
```

### Verified Baseline Scores
Tested locally against `Qwen/Qwen2.5-72B-Instruct` (via Hugging Face API) at `temperature=0.1`.

| Task | Mean Score | Result |
| :--- | :--- | :--- |
| **Easy** | 0.95 | ✅ Pass |
| **Medium** | 0.85 | ✅ Pass |
| **Hard** | 0.75 | ✅ Pass |

---

<div align="center">
  <i>Submitted for the Meta × HuggingFace × Scaler OpenEnv Hackathon 2026.</i>
</div>
