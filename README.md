# Enhancement of Network Security in MANET using Guided Whale Optimization Algorithm

This project implements a major-project simulation of a Mobile Ad Hoc Network (MANET) where secure route selection is optimized using a Guided Whale Optimization Algorithm (GWO-inspired heuristic). The system aims to improve network security by selecting paths with high trust, sufficient energy, lower delay, and fewer malicious nodes.

## Project Objective
To improve the reliability and security of MANET communication by:
- identifying risky or malicious nodes,
- selecting secure communication routes,
- maximizing packet delivery ratio (PDR),
- minimizing delay and packet loss,
- optimizing energy-aware route selection.

## Problem Statement
MANETs are vulnerable to attacks because they lack centralized infrastructure and have dynamic topology. Routing protocols can be compromised by malicious nodes, causing packet loss, route hijacking, and network degradation. This project proposes a Guided Whale Optimization Algorithm for secure path selection under dynamic and hostile network conditions.

## Key Features
- MANET topology generation
- dynamic trust evaluation for nodes
- malicious node detection
- secure route optimization using whale-inspired search
- performance metrics output and graph generation
- academic-style report and implementation structure

## Repository Structure

```text
MANET-Security-GWO/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   └── manet_security_gwo.py
├── docs/
│   └── PROJECT_REPORT.md
├── results/
│   └── sample_output.txt
└── plots/
    └── .gitkeep
```

## Requirements
- Python 3.9+
- numpy
- matplotlib

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Execution
The project generates a secure route selection simulation and prints the key results including:
- selected secure route,
- security score,
- packet delivery ratio,
- throughput,
- delay,
- network lifetime,
- malicious nodes avoided.

## Sample Output
The sample execution output is available in:
- `results/sample_output.txt`

## Academic Relevance
This work is suitable for a B.Tech / M.Tech major project in:
- Computer Science
- Information Technology
- Wireless Networks
- Network Security

## Status
This repository contains the implementation, execution-ready script, and supporting project documentation.
