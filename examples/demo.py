"""
Demo script for Video Script Writer
Shows how to use the core module programmatically.

Usage:
    python examples/demo.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.video_script.core import load_config, build_prompt, generate_script, generate_scene_breakdown, suggest_broll, generate_hook, generate_thumbnail_ideas, estimate_duration, export_teleprompter, parse_script_sections


def main():
    """Run a quick demo of Video Script Writer."""
    print("=" * 60)
    print("🚀 Video Script Writer - Demo")
    print("=" * 60)
    print()
    # Load configuration from config.yaml, falling back to defaults.
    print("📝 Example: load_config()")
    result = load_config()
    print(f"   Result: {result}")
    print()
    # Build the video script generation prompt.
    print("📝 Example: build_prompt()")
    result = build_prompt(
        topic="artificial intelligence and machine learning",
        duration=5,
        style="professional",
        audience=None
    )
    print(f"   Result: {result}")
    print()
    # Generate a full video script using the LLM.
    print("📝 Example: generate_script()")
    result = generate_script(
        topic="artificial intelligence and machine learning",
        duration=5,
        style="professional",
        audience=None
    )
    print(f"   Result: {result}")
    print()
    # Return a list of ScriptSection objects with a scene-by-scene breakdown.
    print("📝 Example: generate_scene_breakdown()")
    result = generate_scene_breakdown(
        topic="artificial intelligence and machine learning",
        duration=5,
        style="professional"
    )
    print(f"   Result: {result}")
    print()
    print("✅ Demo complete! See README.md for more examples.")


if __name__ == "__main__":
    main()
