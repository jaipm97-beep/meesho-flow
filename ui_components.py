"""
Streamlit UI Components for Visual Attention Engine.
Provides Visual Mode selector and 'Why Watch Next' visual cards.
"""
import streamlit as st
from typing import Dict, Any
from .models import VisualMode, VisualBeatCue

def render_visual_mode_selector(key_prefix: str = "global") -> VisualMode:
    """Renders the dual visual mode selector widget."""
    choice = st.radio(
        "🎛️ Visual Attention & Camera Mode",
        [
            "🔒 Cinematic Precision Director Lock (Maximum Viral Retention)",
            "🌿 Fluid & Flexible Creator Flow (Natural Organic Mode)"
        ],
        index=0,
        key=f"{key_prefix}_visual_mode_radio",
        help="Precision Lock locks exact camera angles, 0.5x slow-mo speed curves, and facial expressions. Fluid Flow allows relaxed organic AI camera freedom."
    )
    if "Precision" in choice:
        return VisualMode.PRECISION_LOCK
    else:
        return VisualMode.FLUID_FLOW

def render_studio_visual_attention_banner(section_name: str, key_prefix: str = "studio") -> VisualMode:
    """Renders a prominent Visual Attention Engine banner and mode switch at the top of any studio."""
    default_is_precision = st.session_state.get("global_visual_mode", "precision") == "precision"
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.95) 100%); padding: 0.7rem 1rem; border-radius: 10px; border: 1px solid rgba(236, 72, 153, 0.25); margin-bottom: 0.8rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.6rem;">
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="font-size:1.1rem;">👁️</span>
            <div>
                <span style="font-weight:700; color:#f8fafc; font-size:0.85rem;">
                    Visual Attention Engine Active: <span style="color:#f472b6;">{section_name}</span>
                </span>
                <div style="color:#94a3b8; font-size:0.75rem;">
                    Zero Scroll-Away Standard • Micro-Tension Hook • Anticipation: "Aage kya hone wala hai?"
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_vm1, col_vm2 = st.columns([1.5, 1])
    with col_vm1:
        choice = st.radio(
            f"🎛️ {section_name} Visual Mode:",
            [
                "🔒 Precision Director Lock (Camera & Speed Curves Locked)",
                "🌿 Fluid Natural Flow (Natural Organic AI Freedom)"
            ],
            index=0 if default_is_precision else 1,
            horizontal=True,
            key=f"{key_prefix}_local_vmode_radio"
        )
    with col_vm2:
        if "Precision" in choice:
            st.caption("🔒 **Locked**: 24mm low-angle, 0.5x slow-mo twirl, micro-gaze, and pattern interrupts locked.")
            return VisualMode.PRECISION_LOCK
        else:
            st.caption("🌿 **Fluid**: Preserves curiosity gap while giving AI natural camera & expression freedom.")
            return VisualMode.FLUID_FLOW

def render_why_watch_next_card(cue: VisualBeatCue):
    """Renders a single scene Why Watch Next card with speed ramp timeline, Foley SFX, and attention metric."""
    tension_color = "#ec4899" if "Hook" in cue.tension_level or "Reveal" in cue.tension_level or "Payoff" in cue.tension_level else "#8b5cf6"
    sfx_html = f'<div style="font-size:0.72rem; color:#facc15; margin-bottom:0.3rem;">🔊 <strong>SFX Foley:</strong> {cue.sfx_foley_timeline}</div>' if cue.sfx_foley_timeline else ''
    ramp_html = f'<div style="font-size:0.72rem; color:#38bdf8; margin-bottom:0.3rem;">⏱️ <strong>Speed Ramp:</strong> {cue.speed_ramp_timeline}</div>' if cue.speed_ramp_timeline else f'<div style="font-size:0.72rem; color:#38bdf8; margin-bottom:0.3rem;">⚡ <strong>Speed:</strong> {cue.speed_curve}</div>'
    expr_html = f'<div style="font-size:0.72rem; color:#34d399; margin-bottom:0.3rem;">😊 <strong>Micro-Expression:</strong> {cue.micro_expressions or cue.facial_expression}</div>'
    q_html = f'<div style="font-size:0.73rem; color:#f43f5e; margin-bottom:0.3rem; background:rgba(244,63,94,0.1); padding:3px 6px; border-radius:4px;">❓ <strong>"आगे क्या होगा?" Tension:</strong> {cue.subconscious_question}</div>' if getattr(cue, 'subconscious_question', '') else ''
    cliff_html = f'<div style="font-size:0.71rem; color:#f59e0b; margin-bottom:0.3rem;">🪝 <strong>Micro-Cliffhanger:</strong> {cue.micro_cliffhanger}</div>' if getattr(cue, 'micro_cliffhanger', '') else ''
    
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
            <span style="font-weight:700; color:#f8fafc; font-size:0.85rem;">Scene {cue.beat_index} ({cue.timestamp_range})</span>
            <span style="background:{tension_color}; color:#fff; font-size:0.65rem; padding: 2px 6px; border-radius:4px; font-weight:600;">{cue.tension_level}</span>
        </div>
        {ramp_html}
        <div style="font-size:0.72rem; color:#cbd5e1; margin-bottom:0.3rem;">
            🎥 <strong>Camera:</strong> <span style="color:#a78bfa;">{cue.camera_motion}</span>
        </div>
        {sfx_html}
        {expr_html}
        {q_html}
        {cliff_html}
        <div style="font-size:0.70rem; color:#94a3b8; margin-bottom:0.3rem;">
            ✨ <strong>Standard:</strong> 8K UHD • Arri Alexa LF • Skin Pores • Fabric Drape
        </div>
        <div style="background: rgba(30, 41, 59, 0.8); border-left: 3px solid #ec4899; padding: 0.4rem 0.6rem; border-radius: 4px; font-size:0.73rem; color:#e2e8f0; margin-top:0.4rem;">
            👁️ <strong>Why Watch Next:</strong> {cue.why_watch_next}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_section_why_watch_next_summary(section_name: str, scenes: list, visual_mode: VisualMode = VisualMode.PRECISION_LOCK):
    """Generates and displays Why Watch Next cards for all scenes in a studio."""
    from .core_engine import VisualAttentionEngine
    engine = VisualAttentionEngine()
    bp = engine.generate_visual_blueprint(section_name, scenes, visual_mode)
    
    st.markdown("##### 👁️ Visual Retention Breakdown (Why Viewer Will Keep Watching):")
    if bp.cues:
        cols = st.columns(min(len(bp.cues), 4))
        for idx, cue in enumerate(bp.cues):
            with cols[idx % len(cols)]:
                render_why_watch_next_card(cue)

