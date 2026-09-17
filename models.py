"""
Visual Attention Engine Data Models.
Defines VisualMode, VisualBeatCue, and VisualAttentionBlueprint.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional

class VisualMode(str, Enum):
    PRECISION_LOCK = "precision_lock" # 🔒 Locked camera angles, speed ramping (0.5x slow-mo), and facial micro-expressions
    FLUID_FLOW = "fluid_flow"         # 🌿 Natural, organic visual storytelling with relaxed camera freedom

@dataclass
class VisualBeatCue:
    beat_index: int
    timestamp_range: str
    phase_name: str
    visual_action: str
    camera_motion: str
    speed_curve: str # e.g. "1.3x Fast Stride", "0.5x Ultra Slow-Mo", "1.0x Normal", "1.2x Snap Cut"
    facial_expression: str
    fabric_motion: str
    pattern_interrupt: str
    why_watch_next: str
    tension_level: str # Hook 🔥, Curiosity 🔥, Build 🟢, Reveal 🔥, Payoff 🔥
    drop_risk_status: str = "SAFE" # SAFE, DROP_RISK_WARNING
    lens_recommendation: str = "24mm f/1.8"
    lighting_tone: str = "Warm Cinematic 4K Sunlight"
    speed_ramp_timeline: str = ""
    sfx_foley_timeline: str = ""
    micro_expressions: str = ""
    cinematography_8k: str = "8K UHD Master, Arri Alexa Mini LF, 35mm prime f/1.8, photorealistic skin micro-pores"
    subconscious_question: str = ""
    micro_cliffhanger: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualBeatCue":
        return cls(
            beat_index=data.get("beat_index", 1),
            timestamp_range=data.get("timestamp_range", "00:00 - 00:03"),
            phase_name=data.get("phase_name", "Hook"),
            visual_action=data.get("visual_action", ""),
            camera_motion=data.get("camera_motion", "Low-angle fluid push-in"),
            speed_curve=data.get("speed_curve", "1.0x Normal Speed"),
            facial_expression=data.get("facial_expression", "Confident smile"),
            fabric_motion=data.get("fabric_motion", "Natural fabric wave"),
            pattern_interrupt=data.get("pattern_interrupt", "Sharp entry"),
            why_watch_next=data.get("why_watch_next", "Visual novelty and narrative progression."),
            tension_level=data.get("tension_level", "Hook 🔥"),
            drop_risk_status=data.get("drop_risk_status", "SAFE"),
            lens_recommendation=data.get("lens_recommendation", "24mm f/1.8"),
            lighting_tone=data.get("lighting_tone", "Warm Cinematic 4K Sunlight"),
            speed_ramp_timeline=data.get("speed_ramp_timeline", ""),
            sfx_foley_timeline=data.get("sfx_foley_timeline", ""),
            micro_expressions=data.get("micro_expressions", ""),
            cinematography_8k=data.get("cinematography_8k", "8K UHD Master, Arri Alexa Mini LF, 35mm prime f/1.8, photorealistic skin micro-pores"),
            subconscious_question=data.get("subconscious_question", ""),
            micro_cliffhanger=data.get("micro_cliffhanger", "")
        )

@dataclass
class VisualAttentionBlueprint:
    section_name: str
    visual_mode: VisualMode
    cues: List[VisualBeatCue] = field(default_factory=list)
    overall_retention_score: int = 95
    strongest_visual_moment: str = ""
    repetition_risk: str = "LOW"
    seamless_loop_cue: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["visual_mode"] = self.visual_mode.value
        return d
