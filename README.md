# SELODev Code Assist 🧠✨
A dual-LLM local development workflow using Continue, Ollama, and a built-in Python validator to ensure industry-standard code generation.

## 💡 Overview
SELODev Code Assist uses:
- Mistral for critical thinking and planning
- Qwen for code generation
- A custom validator to clean, format, and lint all AI-generated code

## ⚙️ Requirements
- VS Code with the Continue extension
- Ollama with mistral and qwen2-coder-7b
- Python 3.12+
- `black`, `flake8`, `isort` installed

## 🚀 Setup
```bash
git clone https://github.com/selodesigns/SELODev-Code-Assist.git
cd SELODev-Code-Assist
pip install black flake8 isort
cp .continue/config.json ~/.continue/config.json
chmod +x code_validator/code_validator.py
