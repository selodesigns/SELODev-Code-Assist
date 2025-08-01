# SELODev Code Assist 🚀

**Free, Open-Source AI-Powered Code Assistant**

A completely free alternative to paid services like GitHub Copilot, Codeium, and Tabnine. Get professional-grade AI code assistance without monthly subscriptions or sending your code to the cloud.

## ✨ Features

- 🤖 **AI Code Completion** - Intelligent code suggestions powered by local LLMs
- 📖 **Code Explanation** - Understand complex code with natural language explanations
- ✨ **Smart Improvements** - Get actionable suggestions to improve your code
- 🎨 **Auto Formatting** - Keep your code clean with Black, isort, and Ruff
- 🔒 **100% Private** - Your code never leaves your machine
- 💰 **Completely Free** - No API costs, no subscriptions, no limits
- 🌐 **Multi-Language** - Python, JavaScript, TypeScript, Go, Rust, Java, C++, and more

## 🆚 Why Choose SELODev Code Assist?

| Feature | SELODev Code Assist | GitHub Copilot | Codeium | Tabnine |
|---------|-------------------|----------------|---------|----------|
| **Cost** | 🟢 Free Forever | 🔴 $10-19/month | 🟡 Free tier limited | 🔴 $12-39/month |
| **Privacy** | 🟢 100% Local | 🔴 Cloud-based | 🔴 Cloud-based | 🟡 Hybrid |
| **Offline** | 🟢 Works offline | 🔴 Requires internet | 🔴 Requires internet | 🔴 Requires internet |
| **Open Source** | 🟢 Fully open | 🔴 Proprietary | 🔴 Proprietary | 🔴 Proprietary |
| **Customizable** | 🟢 Use any model | 🔴 Fixed models | 🔴 Fixed models | 🟡 Limited options |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 4GB+ RAM (for local AI models)
- 10GB+ free disk space

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/SELODevCodeAssist.git
cd SELODevCodeAssist
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama (Free Local AI)
```bash
# On Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows (PowerShell)
iwr -useb https://ollama.ai/install.ps1 | iex
```

### 4. Download AI Models
```bash
# Recommended: Fast and efficient
ollama pull codellama:7b-instruct

# Alternative options:
# ollama pull deepseek-coder:6.7b    # Great for code
# ollama pull starcoder2:7b          # GitHub's model
# ollama pull codellama:13b-instruct # More powerful but slower
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env if needed (defaults work for most users)
```

### 6. Start the Service
```bash
python backend/app.py
```

### 7. Open Web Interface
Open your browser to: http://localhost:5000

## 🎯 Usage

### Web Interface
The web interface provides an easy way to test all features:
- **Code Completion**: Paste code and get AI suggestions
- **Code Explanation**: Understand what any code does
- **Code Improvement**: Get suggestions to make your code better
- **Code Formatting**: Clean up your code automatically

### API Endpoints

#### Code Completion
```bash
curl -X POST http://localhost:5000/api/complete \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.py",
    "language": "python",
    "prefix": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return ",
    "suffix": "",
    "cursor_position": 65
  }'
```

#### Code Explanation
```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr[1:] if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x >= arr[0]])",
    "language": "python"
  }'
```

#### Code Improvements
```bash
curl -X POST http://localhost:5000/api/improve \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in range(len(items)):\n    print(items[i])",
    "language": "python"
  }'
```

#### Code Formatting
```bash
curl -X POST http://localhost:5000/api/format \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello( name ):\nprint(f\"Hello {name}!\")",
    "language": "python"
  }'
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Local LLM Configuration (PRIMARY - FREE)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b-instruct

# Alternative Local LLM
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model

# Local Model Settings
LOCAL_MODEL_TIMEOUT=30
LOCAL_MODEL_MAX_TOKENS=512
LOCAL_MODEL_TEMPERATURE=0.1

# Application Settings
API_PORT=5000
SUPPORTED_LANGUAGES=python,javascript,typescript,html,css,json,yaml,go,rust,java,cpp
DEFAULT_AI_PROVIDER=ollama
```

### Recommended Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `codellama:7b-instruct` | 3.8GB | Fast | Good | General coding |
| `deepseek-coder:6.7b` | 3.8GB | Fast | Great | Code completion |
| `starcoder2:7b` | 4.0GB | Medium | Great | Multi-language |
| `codellama:13b-instruct` | 7.3GB | Slow | Excellent | Complex tasks |

## 🔧 Advanced Setup

### Using LM Studio (Alternative to Ollama)
1. Download [LM Studio](https://lmstudio.ai)
2. Load a code model (CodeLlama, DeepSeek Coder, etc.)
3. Start the local server
4. Update `.env`: `DEFAULT_AI_PROVIDER=lm_studio`

### File Watcher (Auto-validation)
The system includes automatic file watching and validation:
```bash
python validator_watcher.py
```
This monitors your code files and automatically formats them when changed.

### Cloud Fallback (Optional - Costs Money)
If you want cloud AI as a fallback (not recommended due to costs):
```bash
# Uncomment in .env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │────│   Flask Backend  │────│  Local LLM      │
│   (HTML/JS)     │    │   (Python API)   │    │  (Ollama/LM)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────┴────────┐
                       │  File Watcher   │
                       │  (Auto-format)  │
                       └─────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest`
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama  # Linux
brew services restart ollama   # macOS

# Check available models
ollama list
```

### Performance Issues
- Use smaller models (7b instead of 13b)
- Increase timeout: `LOCAL_MODEL_TIMEOUT=60`
- Reduce max tokens: `LOCAL_MODEL_MAX_TOKENS=256`

### Memory Issues
- Close other applications
- Use quantized models (Q4_K_M variants)
- Increase system swap space

## 🌟 Star History

If this project helps you, please consider giving it a star! ⭐

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/SELODevCodeAssist/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/yourusername/SELODevCodeAssist/discussions)
- 📧 **Email**: your-email@example.com

---

**Made with ❤️ for the open-source community**

*Stop paying for AI code assistance. Take control of your development workflow with SELODev Code Assist.*