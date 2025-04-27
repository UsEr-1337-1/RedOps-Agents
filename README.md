## RedOps Agents
An intelligent pentesting agents framework built with Python and SPADE multi-agent technology.  
SMA automates cybersecurity tasks by coordinating distributed pentesting agents for reconnaissance, vulnerability scanning, exploitation, and reporting.

---
## DASHBOARD 

![Screenshot 2025-04-25 185935](https://github.com/user-attachments/assets/94978045-7156-46f0-bfba-df2f7eb0438d)


## 📋 Description

RedOps Agents is a modular framework designed to simplify and automate penetration testing processes.  
Using SPADE (Smart Python Agent Development Environment), each agent specializes in different tasks such as scanning, exploitation, and reporting.

Agents communicate and cooperate to:
- Perform advanced network reconnaissance
- Discover and exploit vulnerabilities
- Generate structured penetration test reports
- Visualize operations in a dashboard

Built for cybersecurity researchers, ethical hackers, and pentest teams who want scalable, distributed, and intelligent operations.

---

## 🚀 Features
- 📡 Multi-agent architecture for distributed pentest tasks
- 🤖 Automated Recon, Exploitation, and Reporting
- 🌐 HTML Dashboard and Reports
- ⚡ Fast task execution using concurrent agents
- 🛠️ Highly extensible: Add your own custom agents easily
---

## ✨ Key Features

| Capability | Description |
|------------|-------------|
| **Distributed agents** | Each task (recon, scan, fuzz, auth) runs in its own **SPADE** agent process, communicating over XMPP. |
| **Modern HTML dashboard** | ReporterAgent compiles findings into a **Tailwind + Chart.js** single‑page report with dark‑mode, live search and exports (CSV/JSON). |
| **Pluggable payloads** | Easily extend `FuzzingAgent.payloads` for SQLi, XXE or custom word‑lists. |
| **Heuristic auth‑tester** | AuthAgent enumerates forms & attempts default creds to identify weak login flows. |
| **Single‑command run** | Spin up all agents with `python main.py` (or Docker). |
| **Exportable results** | Findings persist in `pentest_dashboard.html` – perfect for sharing or CI artifacts. |

---

## 🏗️ Architecture

```text
┌──────────┐      findings      ┌──────────────┐
│ Recon    │ ───────────────▶ │              │
│ Agent    │                  │              │
└──────────┘                  │              │
      │  discovered URLs      │              │
      ▼                       │              │
┌──────────┐      findings     │ Reporter     │
│ VulnScan │ ───────────────▶ │ Agent        │───►  pentest_dashboard.html
└──────────┘                  │ (HTML report)│
      ▲                       │              │
      │                       │              │
┌──────────┐ findings          │              │
│ Fuzzing  │ ─────────────────▶│              │
└──────────┘                  └──────────────┘
      |
┌──────────┐ findings
│ Auth     │ ──▶
└──────────┘
```

> Agents exchange **XMPP messages**; credentials and JIDs are defined in `main.py` (adjust to match your server).

---

## 📦 Repository Layout

```
.
├── Agents/
│   ├── recon_agent.py      # Crawl & enumerate URLs
│   ├── vulnscan_agent.py   # XSS injection tests
│   ├── fuzzing_agent.py    # Parameter & directory fuzzing
│   ├── auth_agent.py       # Login form brute heuristics
│   └── reporter_agent.py   # Generates dashboard
├── main.py                 # Boots all agents
├── requirements.txt        # Python deps
└── README.md               # You are here 🖖
```

---

## 🚀 Quick Start

```bash
# 1. Clone & install deps
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Ensure an XMPP server (e.g. Prosody) is running
#    and create the agent accounts used in main.py

# 3. Fire it up 🚀
python main.py

# 4. Open the report
xdg-open pentest_dashboard.html  # or double‑click in your file explorer
```

### Docker (optional)

```bash
docker compose up --build
```

> The Compose file starts Prosody and the agents in isolated containers.

---

## 🖥️ Reporter Dashboard

* **Summary cards** – live counts per vulnerability type.
* **Doughnut chart** – visual ratio of findings.
* **Search bar** – instant filtering.
* **Dark‑mode** – 🌞 / 🌙 toggle.
* **Export buttons** – download full JSON or CSV.

![Findings GIF](docs/screens/demo.gif)

---

## 🔌 Extending the Framework

| Where | What to tweak |
|-------|---------------|
| `FuzzingAgent.payloads` | Add new payload strings for injections. |
| `AuthAgent.looks_like_login` | Improve heuristics for detecting login pages. |
| `ReporterAgent.parse_finding()` | Support extra finding categories. |
| Add a new agent | Sub‑class `Agent`, implement behaviour, and wire messages to ReporterAgent. |

---


## 📜 License

Licensed under the **MIT License** – see `LICENSE` for details.

---
