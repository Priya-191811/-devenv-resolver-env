---
title: DevEnv-Resolver
emoji: 🛠️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# DevEnv-Resolver: A Cyber-Resilient AI Benchmark

## 🎯 Project Motivation
In modern DevOps, "Dependency Hell" is a multi-dimensional problem involving **version conflicts**, **file-system permissions**, and **supply-chain security**. Most AI agents struggle with "silent" environmental failures. 

**DevEnv-Resolver** is a specialized OpenEnv implementation designed to evaluate an agent's capability in **fault-tolerant system administration** and **secure software provisioning**. It moves beyond basic installation to test if an AI can navigate real-world engineering friction.

---

## 🚀 Key "Pro" Features
* **Permission Deadlocks:** Simulates `EACCES` blocks, requiring the agent to identify and resolve file-system permission issues using the `fix_permissions` protocol.
* **Security-First Logic (CVE-Aware):** Specifically evaluates whether an agent can distinguish between vulnerable (CVE-impacted) and patched package versions.
* **Transient Fault Tolerance:** Introduces a stochastic (10%) network jitter. The agent must demonstrate **Persistence** and **Retry Logic** to succeed.
* **Resource Economy:** Enforces a strict disk-space quota, forcing the agent to prioritize the `uninstall` of legacy data to maintain system health.

---

## 📊 Environment Specifications

### Action Space (`DevEnvAction`)
The agent interacts with the system using a high-precision command set:
* `install`: Provisions a package (Consumes 50MB).
* `uninstall`: Recovers storage space (Frees 50MB).
* `fix_permissions`: Resolves directory locks.
* `check_status`: Queries registry health and storage.

### Observation Space (`DevEnvObservation`)
* **Terminal Logs:** Raw ANSI console output with monotonic timestamps.
* **State Metadata:** Dictionaries mapping installed versions and resource availability.

---

## 🏆 Task Matrix & Difficulty
| Task ID | Level | Real-World Scenario | Evaluates |
| :--- | :--- | :--- | :--- |
| `task-easy` | **Easy** | Routine Provisioning | Syntax & Tool-calling accuracy. |
| `task-medium` | **Medium** | Dependency Upgrades | Reasoning about version compatibility. |
| `task-hard` | **Extreme** | **Secure Conflict Resolution** | Security awareness & Permission handling. |



---

## ⚖️ Grader & Reward Logic
The environment utilizes a **Deterministic Gradient Reward** system to provide clear training signals:
* **Partial Progress (+0.5):** Awarded for correctly resolving a prerequisite (e.g., fixing permissions or upgrading a base dependency).
* **Full Success (+1.0):** Awarded upon reaching the final desired system state.
* **Security Violation (0.0):** If an agent installs a known vulnerable version, the episode terminates with a zero score to simulate a production breach.

---

## 🛠️ Local Setup
To run the baseline evaluation script:
1. `pip install openenv-core pydantic openai`
2. `python inference.py`