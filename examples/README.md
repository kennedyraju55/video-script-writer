# Examples for Video Script Writer

This directory contains example scripts demonstrating how to use this project.

## Quick Demo

```bash
python examples/demo.py
```

## What the Demo Shows

- **`load_config()`** — Load configuration from config.yaml, falling back to defaults.
- **`build_prompt()`** — Build the video script generation prompt.
- **`generate_script()`** — Generate a full video script using the LLM.
- **`generate_scene_breakdown()`** — Return a list of ScriptSection objects with a scene-by-scene breakdown.
- **`suggest_broll()`** — Generate B-roll ideas for a given script section.
- **`ScriptSection`** — A single section of a video script.
- **`VideoScript`** — Complete video script with metadata.

## Prerequisites

- Python 3.10+
- Ollama running with Gemma 4 model
- Project dependencies installed (`pip install -e .`)

## Running

From the project root directory:

```bash
# Install the project in development mode
pip install -e .

# Run the demo
python examples/demo.py
```
