# NCC Risk Detector
## Version 1.0
## Last Updated: 2025-07-18


# 1. Introduction and Goals

## 1.1. Purpose
- This project, the NCC Risk Detector, is a command-line application designed to automatically analyze new engineering contracts to identify potential risks. It achieves this by comparing the contract text against a database of historical project failures, known as Non-Conformance Costs (NCCs).
- The primary goal is to provide project managers and engineers with an early warning system, highlighting clauses in a new contract that may correspond to problems encountered in the past, thereby enabling proactive risk mitigation.

## 1.2. Quality Goals
- Accuracy: The system must provide reliable and logical judgments on whether a risk is mitigated by the contract.
- Efficiency: The analysis of large contract documents (10+ pages) should be completed in a reasonable timeframe (under 5 minutes).
- Usability: The final output must be clear and actionable for non-technical stakeholders, providing not just a judgment but also the reasoning behind it.
- Maintainability: The codebase is structured in a modular, clean, and well-documented manner to allow for future enhancements.

# 2. Solution Strategy
To meet the quality goals of both speed and accuracy, the solution implements a two-stage NLP 

### pipeline:
- Fast Candidate Retrieval (Semantic Search): The system first uses a lightweight sentence-transformer model (all-MiniLM-L6-v2) to quickly scan the entire contract. It converts the NCC descriptions and all contract segments into numerical vectors (embeddings). By comparing these vectors, it identifies a small list of "candidate" contract clauses that are topically similar to past failures. This avoids the need to run a slow, powerful model on the entire document.
- Deep Reasoning (LLM Analysis): Each candidate pair is then sent to a much more powerful Large Language Model (Llama 3, accessed via Ollama). A carefully engineered prompt instructs the LLM to act as a risk analysis expert. It analyzes the contract clause and the historical failure description to provide a final, reasoned judgment: "Risk Mitigated", "Risk Identified", or "Uncertain".
- This hybrid approach provides the "best of both worlds": the efficiency of a small model for broad searching and the analytical power of an LLM for detailed, high-quality judgments.

# 3. Building Block View

The application is built with a modular architecture, separating distinct functionalities into 
different Python modules within the ncc_risk_detector source directory.

```
+---------------------------+
|         main.py           |
| (Orchestrator)            |
+-------------+-------------+
              |
+-------------v-------------+      +---------------------------+
|   ncc_processor.py        +<---->|       data/nccs.xlsx      |
| (Loads NCC Data)          |      +---------------------------+
+---------------------------+
              |
+-------------v-------------+      +---------------------------+
|   contract_parser.py      +<---->|    data/contract.pdf      |
| (Parses Contract PDF)     |      +---------------------------+
+---------------------------+
              |
+-------------v-------------+
|      matcher.py           |
| (Finds Similarities)      |
+---------------------------+
              |
+-------------v-------------+      +---------------------------+
|   matcher_llama.py        +<---->|      Ollama (Llama 3)     |
| (Reasons with LLM)        |      +---------------------------+
+---------------------------+
              |
+-------------v-------------+      +---------------------------+
| report_generator.py       +----->|   output/summary.txt      |
| (Creates Summary)         |      +---------------------------+
+---------------------------+
```


- main.py: The entry point and orchestrator of the application. It calls other modules in sequence to execute the analysis pipeline.
- ncc_processor.py: Handles reading and processing the nccs.xlsx file using pandas.
- contract_parser.py: Responsible for extracting text from the input PDF using PyMuPDF and splitting it into analyzable segments.
- matcher.py: Implements the first stage of the NLP pipeline—finding candidate risks using sentence-transformer models.
- matcher_llama.py: Implements the second stage—communicating with the Ollama Llama 3 model to get the final risk judgment and reasoning.
- report_generator.py: Creates the final human-readable summary_llama.txt file from the JSON results.

# 4. Runtime View

The script executes in a sequential pipeline orchestrated by main.py:
- Initialization: The script starts, and the configuration parameters (file paths, thresholds) are loaded.
- Load Data: ncc_processor loads the NCCs from Excel, and contract_parser loads the segments from the PDF.
- Find Similarities: The list of NCCs and contract segments are passed to the find_similarities function in matcher.py. This function returns a list of potential matches that exceed the similarity threshold.
- Reason with Llama: The script iterates through the list of potential matches. For each match, it calls the reason_with_llama function, sending the relevant contract text and NCC description to the Llama 3 model.
- Aggregate Results: The judgment and reasoning from Llama are collected into a final list of results.
- Save Output: The final list is written to output/results_llama.json.
- Generate Summary: The generate_llama_summary_report function is called to create the human-readable output/summary_llama.txt file.

# 5. Deployment View
This section provides instructions on how to set up and run the application.

## 5.1. Prerequisites
You must have the following software installed on your machine:

- Git: For cloning the repository.
- Python: Version 3.9 or newer.
- Poetry: For managing Python dependencies.
- Ollama: The application for running local LLMs. You must have it running and have pulled the Llama 3 model.
  ollama pull llama3


## 5.2. Installation & Setup
Clone the repository:
- git clone <https://github.com/pragat44/Ncc-Risk-Evacuation.git>

Install dependencies:
This command creates a virtual environment and installs all required libraries specified in pyproject.toml.
poetry install

## 5.3. Execution
To run the full analysis pipeline, execute the following command from the project's root directory:
poetry run python ncc_risk_detector/main.py

Alternatively, you can use the Makefile shortcut:
make run

## 5.4. How to Read the Output
After a successful run, two files will be generated in the output/ directory:
results_llama.json: This file contains the complete, detailed output in a machine-readable format. It includes the contract segment, the matched NCC, the initial similarity score, and the final judgment and reasoning from Llama.

summary_llama.txt: This is a human-readable report designed for quick assessment. It categorizes the findings (e.g., "Mitigated Risks", "Uncertain Items") and presents the key information, including the excellent reasoning provided by the Llama model, in a clean and simple format.
