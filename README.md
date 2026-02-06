# 🔷 ShivAI - Autonomous General Intelligence (AGI)

> **India's First Offline Expert Assistant** - Your Personal Jarvis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🌟 **Unique Selling Proposition**

**"Your Personal Jarvis - Offline, Bilingual, Unstoppable"**

ShivAI is a completely **offline AI assistant** that automates your phone, PC, and daily life — and can even **build new apps for you**. No cloud dependency. No LLM required. 100% yours.

### Why ShivAI?

- ✅ **100% Offline** - No internet, no API costs, no data privacy risks
- 🇮🇳 **Bilingual** - Native Hindi + English + Hinglish support
- 📱 **Cross-Device** - Control PC and Android phone seamlessly
- 🤖 **500+ Tasks** - From simple commands to expert-level automation
- 🗏️ **App Builder** - Generates complete applications automatically
- 🧠 **Learning** - Remembers patterns and learns your workflows
- 🔒 **Privacy First** - All data stays on your device

---

## 🚀 **Quick Start**

### Prerequisites

- Python 3.10 or higher
- Windows 10/11, Linux, or macOS
- Microphone (for voice input)
- [Optional] Android phone with USB debugging for phone control

### Installation

```bash
# Clone repository
git clone https://github.com/shivai/shivai.git
cd shivai

# Install dependencies
pip install -e .

# Download speech models (for offline recognition)
./scripts/setup-vosk-models.sh

# Run ShivAI
python -m shivai
```

### First Command

```
You: "help"
ShivAI: Shows complete command list

You: "build todo app"
ShivAI: Creates a complete todo application!

You: "open notepad"
ShivAI: Opens Notepad
```

---

## 🎯 **Core Features**

### 1️⃣ **Offline Intelligence**
- Vosk-based speech recognition (no internet required)
- Local TTS with pyttsx3
- SQLite knowledge base
- No cloud dependency

### 2️⃣ **Bilingual Support**
```
"Phone unlock karo" ✓
"open calculator" ✓
"notepad kholo" ✓
```

### 3️⃣ **Android Control** (via ADB)
- Unlock phone
- Open apps (WhatsApp, Instagram, etc.)
- Take screenshots
- Transfer files
- Control volume, brightness
- Check battery status

### 4️⃣ **App Builder**
Automatically generates complete applications:
- Todo List App
- Calculator
- Notes App
- Custom templates

```
You: "build calculator app"
ShivAI: *Creates complete Python + Tkinter calculator*
```

### 5️⃣ **Multi-Step Workflows**
Pre-built workflows for common tasks:
- **Morning Routine**: Open email, calendar, create task list
- **Backup Workflow**: Organize files, compress, backup
- **Productivity Setup**: Split screen, open tools

### 6️⃣ **Pattern Learning**
```
You: "learn pattern as morning_routine"
ShivAI: "Commands recorded"
You: "execute pattern morning_routine"
ShivAI: *Executes saved sequence*
```

---

## 📚 **Complete Feature List**

| Category | Count | Examples |
|----------|-------|----------|
| 📁 File Operations | 50+ | Create, delete, organize, search files |
| 🖥️ System Control | 80+ | CPU/RAM monitor, shutdown, volume |
| 🪟 Window Management | 60+ | Minimize, split-screen, snap windows |
| 🌐 Web Automation | 70+ | Search, social media, email |
| ⌨️ Text Operations | 40+ | Type, format, clipboard |
| 🖱️ Mouse Control | 50+ | Click, drag, automate patterns |
| 📸 Screenshots | 30+ | Full screen, region, screen recording |
| 🔄 Automation | 60+ | Organize, backup, cleanup |
| 📋 Productivity | 40+ | Timer, todo, notes |
| 🧠 AI Features | 50+ | Memory, learning, predictions |
| 📱 Android Control | 20+ | Phone automation via ADB |
| 🗏️ App Builder | 10+ | Generate complete apps |

**Total: 560+ Tasks**

---

## 🛠️ **Architecture**

```
┌─────────────────────────────────────────┐
│         INPUT LAYER                     │
│  Voice Recognition (Vosk) + Text Input  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      UNDERSTANDING LAYER                │
│  Intent Parser + Context Memory         │
│  • Keyword Extraction                   │
│  • SQLite Knowledge Base                │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       EXECUTION LAYER                   │
│  Task Router + Plugin System            │
│  • PC: pyautogui, subprocess            │
│  • Phone: ADB integration               │
│  • Workflows: Multi-step automation     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       CREATION LAYER                    │
│  App Builder + Code Generator           │
│  • Template Engine (Jinja2)             │
│  • Pre-built App Templates              │
└─────────────────────────────────────────┘
```

---

## 💻 **Usage Examples**

### Basic Commands
```python
# Voice commands (Hindi/English/Hinglish)
"open notepad"
"screenshot lo"
"volume up karo"
"time batao"
```

### Android Control
```python
"phone unlock karo"
"WhatsApp kholo phone mein"
"phone screenshot lo"
"phone battery check karo"
```

### App Builder
```python
"build todo app"
"create calculator"
"generate notes app"
"list app templates"
```

### Workflows
```python
"run morning workflow"
"execute backup workflow"
"start productivity setup"
```

### Expert Tasks
```python
"create project structure named MyProject"
"bulk rename files with pattern document"
"analyze system performance"
"create database users.db"
```

---

## 🔌 **Plugin System**

ShivAI uses a modular plugin architecture. Every feature is a plugin:

```python
# Example: Creating a custom plugin

from shivai.core_engine.plugin_loader import BasePlugin

class MyPlugin(BasePlugin):
    def initialize(self):
        return True
    
    def get_capabilities(self):
        return ["my_feature"]
    
    def handle_command(self, command, context):
        # Your logic here
        return "Command executed"
```

Place in `shivai/plugins/my_plugin/` with `manifest.json`.

---

## 📱 **Android Setup (Optional)**

1. **Install ADB**:
   - Download [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools)
   - Add to PATH

2. **Enable USB Debugging**:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → USB Debugging ON

3. **Connect Phone**:
   ```bash
   adb devices  # Verify connection
   ```

4. **Enable in config**:
   ```yaml
   adb:
     enabled: true
   ```

---

## 🧪 **Development**

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=shivai

# Format code
black shivai/
ruff check shivai/

# Type check
mypy shivai/
```

### Project Structure

```
shivai/
├── core_engine/       # Agent orchestration, plugin loader
├── speech/            # Voice recognition (Vosk)
├── tts/               # Text-to-speech
├── adb/               # Android control
├── workflows/         # Multi-step automation
├── app_builder/       # App generation
├── automation/        # PC automation
├── knowledge/         # Knowledge base
├── plugins/           # Plugin system
├── web_api/           # FastAPI backend
├── security/          # Auth, encryption
└── utils/             # Shared utilities
```

---

## 🏗️ **Building**

### Desktop App (Windows EXE)

```bash
# Build Electron desktop app
cd desktop
npm install
npm run build

# Output: desktop/dist/ShivAI-Setup-1.0.0.exe
```

### Mobile App (Android APK)

```bash
# Build Flutter app
cd mobile
flutter build apk --release

# Output: mobile/build/app/outputs/flutter-apk/app-release.apk
```

### Web App

```bash
# Build static web app
cd web
npm install
npm run build

# Output: web/dist/
```

---

## 📖 **Documentation**

Full documentation available at: [docs.shivai.in](https://docs.shivai.in)

- [Installation Guide](docs/installation.md)
- [User Manual](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Plugin Development](docs/plugin-development.md)
- [API Reference](docs/api-reference.md)

---

## 🤝 **Contributing**

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where you can help:
- 🆕 New app templates
- 🌍 Additional language support
- 🔄 Custom workflow templates
- 🐛 Bug fixes
- 📚 Documentation

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) for details.

Free for personal use. Commercial license required for business use.

---

## 💬 **Community & Support**

- **Discord**: [Join our community](https://discord.gg/shivai)
- **GitHub Issues**: [Report bugs](https://github.com/shivai/shivai/issues)
- **Email**: support@shivai.in
- **Twitter**: [@ShivAI_India](https://twitter.com/ShivAI_India)

---

## 🎯 **Roadmap**

### Version 2.0 (Q2 2025)
- [ ] Web interface
- [ ] iOS support
- [ ] Cloud sync (optional)
- [ ] Team collaboration

### Version 3.0 (Q4 2025)
- [ ] IoT device integration
- [ ] Smart home control
- [ ] Voice cloning
- [ ] Advanced reasoning

---

## 🌟 **Star History**

[![Star History Chart](https://api.star-history.com/svg?repos=shivai/shivai&type=Date)](https://star-history.com/#shivai/shivai&Date)

---

## 🙏 **Acknowledgments**

Built with ❤️ in India

Special thanks to:
- Vosk for offline speech recognition
- pyttsx3 for text-to-speech
- The open-source community

---

**ShivAI - Apka Apna AI Assistant 🔷**

*Made with ❤️ in India | 🇮🇳 Proudly Indian*
