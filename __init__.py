"""
Visual Attention Engine Package.
Universal retention intelligence for all Meesho AI Director studios.
"""
from .models import VisualMode, VisualBeatCue, VisualAttentionBlueprint
from .core_engine import VisualAttentionEngine
from .section_adapters import get_adapter_for_section
from .ui_components import (
    render_visual_mode_selector,
    render_why_watch_next_card,
    render_studio_visual_attention_banner,
    render_section_why_watch_next_summary
)

__all__ = [
    "VisualMode",
    "VisualBeatCue",
    "VisualAttentionBlueprint",
    "VisualAttentionEngine",
    "get_adapter_for_section",
    "render_visual_mode_selector",
    "render_why_watch_next_card",
    "render_studio_visual_attention_banner",
    "render_section_why_watch_next_summary"
]
