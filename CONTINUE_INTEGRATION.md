# Continue Extension Integration Guide 🔌

This guide shows how to integrate SELODev Code Assist with the Continue extension in VS Code for seamless AI-powered coding directly in your editor.

## 🎯 What is Continue?

[Continue](https://continue.dev) is an open-source AI coding assistant extension for VS Code that:
- Provides inline code completion as you type
- Offers chat-based code assistance
- Supports custom AI providers (perfect for local LLMs)
- Works with Ollama and other local models

## 🚀 Integration Options

### Option 1: Direct Ollama Integration (Recommended)

Since SELODev Code Assist uses Ollama, Continue can connect directly to your local models:

#### 1. Install Continue Extension
```bash
# In VS Code, install the Continue extension
# Or via command line:
code --install-extension Continue.continue
```

#### 2. Configure Continue
Create or edit `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "CodeLlama 7B (Local)",
      "provider": "ollama",
      "model": "codellama:7b-instruct",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "DeepSeek Coder (Local)",
      "provider": "ollama", 
      "model": "deepseek-coder:6.7b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "CodeLlama 7B",
    "provider": "ollama",
    "model": "codellama:7b-instruct",
    "apiBase": "http://localhost:11434"
  },
  "systemMessage": "You are an expert software engineer. Provide helpful, accurate code suggestions and explanations."
}
```

#### 3. Start Your Services
```bash
# Terminal 1: Ensure Ollama is running
ollama serve

# Terminal 2: Start SELODev Code Assist (optional, for web interface)
python backend/app.py
```

#### 4. Use in VS Code
- **Tab Completion**: Type code and press Tab for AI suggestions
- **Chat**: Cmd/Ctrl+Shift+P → "Continue: Open Chat"
- **Explain Code**: Select code → right-click → "Continue: Explain"

### Option 2: SELODev API Integration (Advanced)

Use SELODev Code Assist as a custom OpenAI-compatible provider:

#### Configure Continue for SELODev API
```json
{
  "models": [
    {
      "title": "SELODev Code Assist",
      "provider": "openai",
      "model": "selodev-local",
      "apiBase": "http://localhost:5000/api/v1",
      "apiKey": "not-needed"
    }
  ],
  "tabAutocompleteModel": {
    "title": "SELODev Code Assist",
    "provider": "openai",
    "model": "selodev-local", 
    "apiBase": "http://localhost:5000/api/v1",
    "apiKey": "not-needed"
  }
}
```

## 🎨 Features Available

### 1. Inline Code Completion
- Type code and get AI suggestions as you type
- Press Tab to accept suggestions
- Works with all supported languages

### 2. Chat-Based Assistance
- Ask questions about your code
- Get explanations of complex functions
- Request code improvements
- Generate new code from descriptions

### 3. Code Actions
- Right-click on selected code for context menu
- "Explain this code"
- "Improve this code"
- "Generate tests for this"

### 4. Multi-Language Support
Works with all languages supported by your models:
- Python, JavaScript, TypeScript
- Go, Rust, Java, C++
- HTML, CSS, JSON, YAML

## ⚙️ Configuration Examples

### Basic Configuration
```json
{
  "models": [
    {
      "title": "Local CodeLlama",
      "provider": "ollama",
      "model": "codellama:7b-instruct"
    }
  ]
}
```

### Advanced Configuration
```json
{
  "models": [
    {
      "title": "CodeLlama 7B",
      "provider": "ollama",
      "model": "codellama:7b-instruct",
      "apiBase": "http://localhost:11434",
      "contextLength": 4096,
      "completionOptions": {
        "temperature": 0.1,
        "topP": 0.9,
        "maxTokens": 512
      }
    },
    {
      "title": "DeepSeek Coder",
      "provider": "ollama",
      "model": "deepseek-coder:6.7b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Fast Completion",
    "provider": "ollama",
    "model": "codellama:7b-instruct",
    "apiBase": "http://localhost:11434"
  },
  "systemMessage": "You are an expert software engineer. Provide concise, accurate code suggestions.",
  "allowAnonymousTelemetry": false,
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  }
}
```

## 🔧 Troubleshooting

### Continue Not Working
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if models are available
ollama list

# Restart Ollama if needed
ollama serve
```

### Slow Completions
1. Use smaller models: `codellama:7b-instruct` instead of `13b`
2. Reduce context length in config
3. Lower `maxTokens` in completion options

### No Suggestions Appearing
1. Check Continue extension is enabled
2. Verify config.json syntax is valid
3. Check VS Code Developer Console for errors
4. Ensure model is downloaded: `ollama pull codellama:7b-instruct`

### API Integration Issues
```bash
# Test SELODev API endpoints
curl http://localhost:5000/api/v1/models

# Check if backend is running
curl http://localhost:5000/api/status
```

## 🎯 Usage Tips

### 1. Optimize for Speed
- Use `codellama:7b-instruct` for fastest completions
- Set `temperature: 0.1` for consistent results
- Limit `maxTokens: 256` for quick responses

### 2. Improve Accuracy
- Use `deepseek-coder:6.7b` for better code understanding
- Increase context length for larger files
- Use specific system messages for your use case

### 3. Multi-Model Setup
```json
{
  "models": [
    {
      "title": "Fast Completion",
      "provider": "ollama",
      "model": "codellama:7b-instruct"
    },
    {
      "title": "Smart Analysis", 
      "provider": "ollama",
      "model": "deepseek-coder:6.7b"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Fast Completion",
    "provider": "ollama",
    "model": "codellama:7b-instruct"
  }
}
```

## 🚀 Workflow Integration

### 1. Development Workflow
1. **Code**: Write code with AI completions
2. **Explain**: Select complex code → right-click → explain
3. **Improve**: Ask Continue for optimization suggestions
4. **Test**: Generate tests using chat interface

### 2. Learning Workflow
1. **Explore**: Ask Continue to explain unfamiliar code
2. **Practice**: Request coding exercises
3. **Review**: Get feedback on your implementations

### 3. Debugging Workflow
1. **Analyze**: Select buggy code → ask for analysis
2. **Fix**: Request specific bug fixes
3. **Verify**: Ask for code review of fixes

## 🔒 Privacy & Security

### Benefits of Local Integration
- ✅ **100% Private**: Code never leaves your machine
- ✅ **No Internet Required**: Works completely offline
- ✅ **No API Costs**: Free forever
- ✅ **Full Control**: You own the models and data

### Security Considerations
- All processing happens locally
- No telemetry sent to external services
- Models run in isolated containers
- Full audit trail of all operations

## 📊 Performance Comparison

| Model | Size | Speed | Quality | Memory | Best For |
|-------|------|-------|---------|--------|----------|
| `codellama:7b-instruct` | 3.8GB | Fast | Good | 8GB RAM | General completion |
| `deepseek-coder:6.7b` | 3.8GB | Fast | Great | 8GB RAM | Code understanding |
| `starcoder2:7b` | 4.0GB | Medium | Great | 10GB RAM | Multi-language |
| `codellama:13b-instruct` | 7.3GB | Slow | Excellent | 16GB RAM | Complex tasks |

## 🎉 Next Steps

1. **Install Continue**: Get it from VS Code marketplace
2. **Configure**: Use the examples above
3. **Test**: Try completions and chat features
4. **Customize**: Adjust settings for your workflow
5. **Enjoy**: Free, private AI coding assistance!

---

**🎯 Result**: Professional-grade AI coding assistant in VS Code, completely free and private, powered by your local SELODev Code Assist system.
