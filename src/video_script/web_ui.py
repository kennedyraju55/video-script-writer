#!/usr/bin/env python3
"""Streamlit Web UI for Video Script Writer."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import streamlit as st

from video_script.core import (
    STYLES,
    DEFAULT_STYLE,
    DEFAULT_DURATION,
    MAX_DURATION,
    check_ollama_running,
    estimate_duration,
    export_teleprompter,
    generate_hook,
    generate_scene_breakdown,
    generate_script,
    generate_thumbnail_ideas,
    parse_script_sections,
    VideoScript,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

# Custom CSS for professional dark theme
st.set_page_config(page_title="Video Script Writer", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%); }
    h1 { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem !important; }
    h2 { color: #667eea !important; }
    h3 { color: #a78bfa !important; }
    .stButton>button { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.5rem 2rem; font-weight: 600; transition: transform 0.2s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1a1a2e; border: 1px solid #333; color: #e0e0e0; border-radius: 8px; }
    .stSelectbox>div>div { background-color: #1a1a2e; border: 1px solid #333; }
    .stMetric { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 1rem; border-radius: 10px; border: 1px solid #333; }
    .css-1d391kg { background-color: #1a1a2e; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); }
    .stSuccess { background-color: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("🎬 Video Script Writer")
    st.caption("Create professional YouTube/video scripts with timestamps and B-roll suggestions")

    # ── Ollama check ──────────────────────────────────────────────
    if not check_ollama_running():
        st.error("⚠️ Ollama is not running. Start it with: `ollama serve`")
        st.stop()

    # ── Sidebar inputs ────────────────────────────────────────────
    with st.sidebar:
        st.header("📝 Script Settings")
        topic = st.text_input("Video Topic", placeholder="e.g. Python Tips for Beginners")
        duration = st.slider("Duration (minutes)", min_value=1, max_value=MAX_DURATION, value=DEFAULT_DURATION)
        style = st.selectbox("Video Style", STYLES, index=STYLES.index(DEFAULT_STYLE))
        audience = st.text_input("Target Audience (optional)", placeholder="e.g. beginner developers")

        st.divider()
        st.header("⚙️ Options")
        gen_hooks = st.checkbox("🎣 Generate Hook Options", value=False)
        gen_thumbnails = st.checkbox("🖼️ Generate Thumbnail Ideas", value=False)
        gen_breakdown = st.checkbox("📋 Scene Breakdown", value=False)
        teleprompter_mode = st.checkbox("📖 Teleprompter Mode", value=False)

        st.divider()
        generate_btn = st.button("🚀 Generate Script", type="primary", use_container_width=True)

    if not generate_btn:
        st.info("👈 Configure your video settings in the sidebar and click **Generate Script**.")
        return

    if not topic:
        st.warning("Please enter a video topic.")
        return

    audience_val = audience if audience else None

    # ── Hook options ──────────────────────────────────────────────
    if gen_hooks:
        with st.spinner("Generating hook options..."):
            hooks = generate_hook(topic, style, num_hooks=3)
        st.subheader("🎣 Hook Options")
        cols = st.columns(len(hooks))
        for idx, (col, hook) in enumerate(zip(cols, hooks), 1):
            with col:
                st.markdown(f"**Hook {idx}**")
                st.info(hook)

    # ── Scene breakdown ───────────────────────────────────────────
    if gen_breakdown:
        with st.spinner("Building scene breakdown..."):
            scenes = generate_scene_breakdown(topic, duration, style)
        st.subheader("📋 Scene Breakdown")

        # Timeline view
        if scenes:
            timeline_cols = st.columns(len(scenes))
            for idx, (col, scene) in enumerate(zip(timeline_cols, scenes)):
                with col:
                    st.markdown(f"**{scene.title}**")
                    st.caption(scene.timestamp or "—")

        # Detailed breakdown in expanders
        for idx, scene in enumerate(scenes, 1):
            with st.expander(f"Scene {idx}: {scene.title} {scene.timestamp}", expanded=False):
                if scene.script_text:
                    st.markdown("**Script:**")
                    st.write(scene.script_text)
                if scene.broll_suggestions:
                    st.markdown("**B-Roll Suggestions:**")
                    for broll in scene.broll_suggestions:
                        st.markdown(f"- 🎥 {broll}")
                if scene.onscreen_text:
                    st.markdown(f"**On-Screen Text:** {scene.onscreen_text}")

    # ── Thumbnail ideas ───────────────────────────────────────────
    if gen_thumbnails:
        with st.spinner("Creating thumbnail ideas..."):
            thumb_ideas = generate_thumbnail_ideas(topic, style, num_ideas=3)
        st.subheader("🖼️ Thumbnail Ideas")
        cols = st.columns(len(thumb_ideas))
        for idx, (col, idea) in enumerate(zip(cols, thumb_ideas), 1):
            with col:
                st.markdown(f"**Thumbnail {idx}**")
                st.success(idea)

    # ── Full script ───────────────────────────────────────────────
    st.divider()
    with st.spinner("✍️ Writing your video script..."):
        raw_script = generate_script(topic, duration, style, audience_val)

    sections = parse_script_sections(raw_script)
    script_obj = VideoScript(
        topic=topic,
        style=style,
        duration_minutes=duration,
        sections=sections,
        raw_text=raw_script,
    )

    # Metrics bar
    col1, col2, col3 = st.columns(3)
    col1.metric("📝 Word Count", f"~{script_obj.word_count}")
    col2.metric("⏱️ Est. Duration", f"~{script_obj.estimated_duration:.1f} min")
    col3.metric("📋 Sections", str(len(script_obj.sections)))

    # ── Teleprompter mode ─────────────────────────────────────────
    if teleprompter_mode:
        st.subheader("📖 Teleprompter Mode")
        teleprompter_text = export_teleprompter(script_obj)
        st.markdown(
            f'<div style="font-size:1.4em;line-height:1.8;padding:1em;">{teleprompter_text}</div>',
            unsafe_allow_html=True,
        )
    else:
        # Script in expandable sections
        st.subheader("🎬 Video Script")
        if sections and len(sections) > 1:
            for idx, section in enumerate(sections, 1):
                with st.expander(f"{section.title} {section.timestamp}", expanded=(idx == 1)):
                    st.markdown(section.script_text)
                    if section.broll_suggestions:
                        st.markdown("**B-Roll:**")
                        for broll in section.broll_suggestions:
                            st.markdown(f"- 🎥 {broll}")
                    if section.onscreen_text:
                        st.caption(f"📺 On-Screen: {section.onscreen_text}")
        else:
            st.markdown(raw_script)

    # ── B-Roll panel ──────────────────────────────────────────────
    if sections:
        all_broll = []
        for s in sections:
            for broll in s.broll_suggestions:
                all_broll.append((s.title, s.timestamp, broll))
        if all_broll:
            with st.expander("🎥 All B-Roll Suggestions", expanded=False):
                for scene_title, ts, broll in all_broll:
                    st.markdown(f"- **{scene_title}** {ts}: {broll}")

    # ── Download ──────────────────────────────────────────────────
    st.divider()
    st.download_button(
        label="📥 Download Script as Markdown",
        data=raw_script,
        file_name=f"script_{topic.replace(' ', '_').lower()}.md",
        mime="text/markdown",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
