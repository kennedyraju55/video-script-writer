<div align="center">
<img src="https://img.shields.io/badge/✍️_🎬_Video_Script_Writer-Local_LLM_Powered-blue?style=for-the-badge&labelColor=1a1a2e&color=16213e" alt="Project Banner" width="600"/>
<br/>
<img src="https://img.shields.io/badge/Gemma_4-Ollama-orange?style=flat-square&logo=google&logoColor=white" alt="Gemma 4"/>
<img src="https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Streamlit-Web_UI-red?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/>
<img src="https://img.shields.io/badge/Click-CLI-green?style=flat-square&logo=gnu-bash&logoColor=white" alt="Click CLI"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"/>
<br/><br/>
<strong>Part of <a href="https://github.com/kennedyraju55/90-local-llm-projects">90 Local LLM Projects</a> collection</strong>
</div>
<br/>

> Create professional YouTube/video scripts with timestamps, B-roll suggestions, hook options, and thumbnail ideas — powered by a local LLM via Ollama.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 **Complete Script Structure** | Hook → Intro → Main Content (with timestamps) → Outro |
| ⏱️ **Timestamps** | Precise timing for each section based on target duration |
| 🎥 **B-Roll Suggestions** | Visual overlay recommendations for every segment |
| 📺 **On-Screen Text** | Suggested text overlays and graphics |
| 🎣 **Hook Generator** | Multiple hook options to grab viewer attention |
| 🖼️ **Thumbnail Ideas** | Thumbnail concepts with text overlays and visual descriptions |
| 📋 **Scene Breakdown** | Detailed scene-by-scene structure in table format |
| 📖 **Teleprompter Mode** | Clean script text without production notes |
| 📊 **Duration Estimation** | Word count and estimated speaking time (~150 WPM) |
| 🎨 **6 Video Styles** | Educational, entertainment, tutorial, review, vlog, documentary |
| 🖥️ **CLI + Web UI** | Rich terminal interface and Streamlit web dashboard |
| 📥 **Export** | Download scripts as Markdown files |

## 🏗️ Architecture

```
35-video-script-writer/
├── src/
│   └── video_script/
│       ├── __init__.py        # Package metadata
│       ├── core.py            # Business logic, dataclasses, LLM calls
│       ├── cli.py             # Click CLI interface
│       └── web_ui.py          # Streamlit web dashboard
├── tests/
│   ├── conftest.py            # Shared test fixtures
│   ├── test_core.py           # Core logic tests
│   └── test_cli.py            # CLI integration tests
├── config.yaml                # App configuration
├── setup.py                   # Package installer
├── requirements.txt           # Dependencies
├── Makefile                   # Dev workflow commands
├── .env.example               # Environment template
└── README.md
```

## 📋 Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** running locally with a model (e.g., `llama3`)

## 🚀 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package (editable mode)
pip install -e ".[dev]"
```

## 💻 CLI Usage

```bash
# Basic educational video script
python src/video_script/cli.py --topic "Python Tips" --duration 10 --style educational

# Tutorial with target audience
python src/video_script/cli.py --topic "React Hooks" --duration 15 --style tutorial --audience "beginners"

# Generate hook options
python src/video_script/cli.py --topic "AI in 2024" --hooks

# Scene breakdown table
python src/video_script/cli.py --topic "Cooking Basics" --scene-breakdown

# Thumbnail ideas
python src/video_script/cli.py --topic "Travel Vlog" --style vlog --thumbnails

# Teleprompter mode (clean text)
python src/video_script/cli.py --topic "Tech Review" --style review --teleprompter

# Save to file
python src/video_script/cli.py --topic "Product Review" --duration 8 -o script.md

# If installed as package
video-script --topic "Python Tips" --hooks --thumbnails
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--topic` | Video topic (required) | — |
| `--duration` | Target duration in minutes | 10 |
| `--style` | Video style | educational |
| `--audience` | Target audience | None |
| `-o, --output` | Save to file | None |
| `--hooks` | Generate hook options | off |
| `--thumbnails` | Generate thumbnail ideas | off |
| `--scene-breakdown` | Scene-by-scene breakdown | off |
| `--teleprompter` | Clean teleprompter output | off |

## 🌐 Web UI

```bash
streamlit run src/video_script/web_ui.py
```

The web dashboard provides:
- 📝 Topic input, duration slider (1–60 min), style selector
- 🎣 Hook generator with multiple options displayed in columns
- 📋 Timeline view and expandable scene breakdown
- 🖼️ Thumbnail ideas gallery (card layout)
- 📖 Teleprompter mode with large, clean text
- 📊 Word count and estimated duration metrics
- 📥 Download script as Markdown

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=video_script --cov-report=term-missing
```

## ⚙️ Configuration

Edit `config.yaml` to customize defaults:

```yaml
app:
  name: "Video Script Writer"
  version: "2.0.0"
llm:
  model: "llama3"
  temperature: 0.7
  max_tokens: 4096
video:
  default_style: "educational"
  default_duration: 10
  max_duration: 60
  words_per_minute: 150
  styles: ["educational", "entertainment", "tutorial", "review", "vlog", "documentary"]
logging:
  level: "INFO"
```

## 📄 Example Output

```
╭─ 🎬 Video Script ──────────────────────────────╮
│ ## HOOK [0:00-0:15]                             │
│ **Script:** "Did you know that 90% of Python    │
│ developers don't use these 5 tips?"             │
│ [B-ROLL] Fast montage of code snippets          │
│                                                 │
│ ## INTRO [0:15-1:00]                            │
│ **Script:** "Hey everyone, welcome back..."     │
│ [ON-SCREEN TEXT] "5 Python Tips You Need"       │
│ ...                                             │
╰─────────────────────────────────────────────────╯

Word count: ~1200 | Estimated speaking time: ~8.0 min | Sections: 6
```


## 📸 Screenshots
<div align="center">
<table>
<tr>
<td><img src="https://via.placeholder.com/400x250/1a1a2e/e94560?text=CLI+Interface" alt="CLI"/></td>
<td><img src="https://via.placeholder.com/400x250/16213e/e94560?text=Web+UI" alt="Web UI"/></td>
</tr>
<tr><td align="center"><em>CLI Interface</em></td><td align="center"><em>Streamlit Web UI</em></td></tr>
</table>
</div>
