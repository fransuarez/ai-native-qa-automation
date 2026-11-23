# AI‑Powered E2E Test Generation & Self‑Healing Prototype  

[![CI](https://github.com/fransuarez/ai-qa-prototype/actions/workflows/qa-ai-pipeline.yml/badge.svg)](https://github.com/fransuarez/ai-qa-prototype/actions/workflows/qa-ai-pipeline.yml)

*AI‑powered E2E test generation and self‑healing prototype using Python, Playwright, and LLMs.*

---

## 📦 Quickstart – The Two‑Command Rule  

```bash
# Install dependencies and browsers
pip install -r requirements.txt && playwright install chromium

# Generate a test from natural language
python scripts/generate_test.py "test that example.org loads and the Learn more link works"

# Run the generated test (with self‑healing enabled)
pytest tests/test_generated.py -v --llm-provider=ollama --ollama-model=qwen2.5-coder:3b
```

> **Tip:** The `healing_page` fixture (provided by `pytest-self-healer`) is used automatically; no extra setup is needed.

---

## 🏗️ Architecture & “Why”

| Component | Why we chose it |
|-----------|-----------------|
| **Groq (`gpt‑oss‑120b`)** | Fast, free‑tier model that produces high‑quality code from natural language. |
| **Ollama (`qwen2.5‑coder:3b`)** | Runs locally, eliminating API latency and cost during test execution; ideal for rapid selector repair loops. |
| **Playwright** | Modern, reliable browser automation with built‑in async support. |
| **pytest‑self‑healer** | Detects `selector‑not‑found` failures and rewrites selectors based on a human‑readable `purpose` string. |

**The Loop**  

```
Natural‑language description → Groq generates test → Playwright runs test → 
selector failure? → pytest‑self‑healer asks Ollama to locate element using the purpose string → test passes
```

---

## ⚖️ Trade‑offs (Engineering Judgment)

- **What it does well**  
  - Automatic healing of flaky selectors.  
  - One‑line generation of end‑to‑end tests from plain English.  

- **Known limitations**  
  - Healing only covers *selector‑not‑found* errors; logic changes, timing issues, or API contract shifts are still manual.  
  - Local model (`qwen2.5‑coder:3b`) is small; complex page structures may require a larger model for accurate repairs.  
  - Generated tests are **not** production‑ready out‑of‑the‑box – a human review step is essential before committing them.  

- **Future improvements**  
  - Add visual‑diff based healing for layout changes.  
  - Integrate contract testing (e.g., Pact) to catch backend API changes.  
  - Plug in a larger local model or a hosted LLM for richer reasoning.

---

## 🛠️ Requirements & Environment

| Requirement | Details |
|-------------|---------|
| **Python** | 3.11+ |
| **Ollama** | Installed and running; pull the model with `ollama pull qwen2.5-coder:3b`. |
| **Groq API Key** | Set as environment variable `GROQ_API_KEY` (never commit). |
| **Playwright browsers** | `playwright install chromium` (run after `pip install`). |

```bash
# Example of setting the Groq key on Unix/macOS
export GROQ_API_KEY=your_groq_key_here
```

---

## 🚀 CI/CD Evidence

The repository includes a GitHub Actions workflow (`.github/workflows/qa-ai-pipeline.yml`) that:

1. Installs Python & dependencies.  
2. Installs Ollama, pulls `qwen2.5-coder:3b`, and starts the Ollama daemon.  
3. Runs the full test suite with self‑healing enabled.  

A passing badge is displayed at the top of this README.

---

## 📂 Project Layout

```
.
├── .github/
│   └── workflows/qa-ai-pipeline.yml   # CI pipeline
├── scripts/
│   └── generate_test.py                # Groq test generation script
├── tests/
│   ├── test_example.py                 # Demo test with intentional broken selector
│   ├── test_generated.py               # Populated by generate_test.py
│   └── test_regression.py              # Optional regression check
├── requirements.txt                    # All Python dependencies
├── .env                                # (git‑ignored) GROQ_API_KEY
└── README.md                           # ← you are here