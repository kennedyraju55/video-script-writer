#!/usr/bin/env python3
"""CLI interface for Video Script Writer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from video_script.core import (
    STYLES,
    DEFAULT_STYLE,
    DEFAULT_DURATION,
    build_prompt,
    check_ollama_running,
    estimate_duration,
    export_teleprompter,
    generate_hook,
    generate_scene_breakdown,
    generate_script,
    generate_thumbnail_ideas,
    parse_script_sections,
    setup_logging,
    VideoScript,
)

console = Console()


def _spinner(description: str):
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


@click.command()
@click.option("--topic", required=True, help="Video topic.")
@click.option(
    "--duration",
    default=DEFAULT_DURATION,
    type=int,
    help=f"Target video duration in minutes (default: {DEFAULT_DURATION}).",
)
@click.option(
    "--style",
    type=click.Choice(STYLES, case_sensitive=False),
    default=DEFAULT_STYLE,
    help=f"Video style (default: {DEFAULT_STYLE}).",
)
@click.option("--audience", default=None, help="Target audience description.")
@click.option("--output", "-o", default=None, help="Save output to file.")
@click.option("--hooks", is_flag=True, default=False, help="Generate hook options.")
@click.option("--thumbnails", is_flag=True, default=False, help="Generate thumbnail ideas.")
@click.option("--scene-breakdown", is_flag=True, default=False, help="Generate detailed scene breakdown.")
@click.option("--teleprompter", is_flag=True, default=False, help="Output clean teleprompter text.")
def main(
    topic: str,
    duration: int,
    style: str,
    audience: str | None,
    output: str | None,
    hooks: bool,
    thumbnails: bool,
    scene_breakdown: bool,
    teleprompter: bool,
):
    """🎬 Create YouTube/video scripts with timestamps and B-roll suggestions."""
    setup_logging()

    console.print(Panel.fit("[bold red]🎬 Video Script Writer[/bold red]", border_style="red"))

    if not check_ollama_running():
        console.print("[red]Error: Ollama is not running. Start it with: ollama serve[/red]")
        sys.exit(1)

    console.print(f"[cyan]Topic:[/cyan] {topic}")
    console.print(f"[cyan]Duration:[/cyan] {duration} minutes")
    console.print(f"[cyan]Style:[/cyan] {style}")
    if audience:
        console.print(f"[cyan]Audience:[/cyan] {audience}")
    console.print()

    # ── Hook options ──────────────────────────────────────────────
    if hooks:
        with _spinner("Generating hook options...") as progress:
            progress.add_task("Generating hook options...", total=None)
            hook_list = generate_hook(topic, style, num_hooks=3)
        console.print(Panel("[bold]🎣 Hook Options[/bold]", border_style="yellow"))
        for idx, hook in enumerate(hook_list, 1):
            console.print(Panel(hook, title=f"Hook {idx}", border_style="cyan"))
        console.print()

    # ── Scene breakdown ───────────────────────────────────────────
    if scene_breakdown:
        with _spinner("Building scene breakdown...") as progress:
            progress.add_task("Building scene breakdown...", total=None)
            scenes = generate_scene_breakdown(topic, duration, style)
        table = Table(title="🎬 Scene Breakdown", border_style="red", show_lines=True)
        table.add_column("#", style="bold", width=4)
        table.add_column("Scene", style="cyan", min_width=20)
        table.add_column("Timestamp", style="green", width=14)
        table.add_column("B-Roll", style="yellow", min_width=25)
        for idx, scene in enumerate(scenes, 1):
            broll_str = "\n".join(scene.broll_suggestions) if scene.broll_suggestions else "-"
            table.add_row(str(idx), scene.title, scene.timestamp, broll_str)
        console.print(table)
        console.print()

    # ── Thumbnail ideas ───────────────────────────────────────────
    if thumbnails:
        with _spinner("Creating thumbnail ideas...") as progress:
            progress.add_task("Creating thumbnail ideas...", total=None)
            thumb_list = generate_thumbnail_ideas(topic, style, num_ideas=3)
        console.print(Panel("[bold]🖼️  Thumbnail Ideas[/bold]", border_style="magenta"))
        for idx, idea in enumerate(thumb_list, 1):
            console.print(Panel(idea, title=f"Thumbnail {idx}", border_style="magenta"))
        console.print()

    # ── Full script generation ────────────────────────────────────
    with _spinner("Writing video script...") as progress:
        progress.add_task("Writing video script...", total=None)
        result = generate_script(topic, duration, style, audience)

    # Build VideoScript object
    sections = parse_script_sections(result)
    script_obj = VideoScript(
        topic=topic,
        style=style,
        duration_minutes=duration,
        sections=sections,
        raw_text=result,
    )

    # ── Output ────────────────────────────────────────────────────
    if teleprompter:
        teleprompter_text = export_teleprompter(script_obj)
        console.print(Panel(teleprompter_text, title="📖 Teleprompter Mode", border_style="green"))
    else:
        console.print(Panel(Markdown(result), title="🎬 Video Script", border_style="red"))

    word_count = script_obj.word_count
    est_minutes = script_obj.estimated_duration
    console.print(
        f"\n[dim]Word count: ~{word_count} | "
        f"Estimated speaking time: ~{est_minutes:.1f} min | "
        f"Sections: {len(script_obj.sections)}[/dim]"
    )

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        console.print(f"[green]✅ Saved to {output}[/green]")


if __name__ == "__main__":
    main()
