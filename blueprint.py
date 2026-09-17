"""
Story Blueprint Models.
Defines 4-Phase narrative progression: Goal -> Curiosity -> Journey -> Discovery -> Surprise -> Payoff -> Ending.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class StoryBeat:
    beat_index: int
    timestamp_range: str
    phase: str # Beginning, Development, Surprise, Payoff, Ending
    narrative_action: str
    visual_moment: str
    why_keep_watching: str
    attention_warning: Optional[str] = None
    spoken_hint: str = ""

    # Phase 2 Extensions
    suggested_duration_sec: float = 3.0
    attention_beat_type: str = "Visual" # Visual, Information, Action, Emotion, Question, Reveal
    micro_event: str = ""
    visual_attention: Dict[str, Any] = field(default_factory=dict)
    emotion_tone: str = "Curiosity"
    sound_cues: Dict[str, str] = field(default_factory=dict)
    text_overlay: Dict[str, str] = field(default_factory=dict)
    keep_watching_rating: str = "Strong" # Strong, Medium, Weak
    keep_watching_fix: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryBeat":
        return cls(
            beat_index=data.get("beat_index", 1),
            timestamp_range=data.get("timestamp_range", "00:00 - 00:03"),
            phase=data.get("phase", "Beginning"),
            narrative_action=data.get("narrative_action", ""),
            visual_moment=data.get("visual_moment", ""),
            why_keep_watching=data.get("why_keep_watching", "High visual interest and curiosity."),
            attention_warning=data.get("attention_warning"),
            spoken_hint=data.get("spoken_hint", ""),
            suggested_duration_sec=float(data.get("suggested_duration_sec", 3.0)),
            attention_beat_type=data.get("attention_beat_type", "Visual"),
            micro_event=data.get("micro_event", ""),
            visual_attention=data.get("visual_attention", {}),
            emotion_tone=data.get("emotion_tone", "Curiosity"),
            sound_cues=data.get("sound_cues", {}),
            text_overlay=data.get("text_overlay", {}),
            keep_watching_rating=data.get("keep_watching_rating", "Strong"),
            keep_watching_fix=data.get("keep_watching_fix", "")
        )

@dataclass
class StoryBlueprint:
    title: str = "Untitled Lifestyle Reel"
    story_concept: str = ""
    story_goal: str = ""
    main_curiosity_question: str = ""
    open_loop: str = ""
    beginning: str = ""
    development: str = ""
    surprise: str = ""
    payoff: str = ""
    ending: str = ""
    rewatch_potential: str = ""
    beats: List[StoryBeat] = field(default_factory=list)
    mode_disclosure: str = '⚠️ "Fictional / AI-generated lifestyle story for creative entertainment."'

    # Phase 2 Extensions
    natural_conflict: str = ""
    curiosity_chain: List[Dict[str, str]] = field(default_factory=list)
    open_loop_stages: Dict[str, str] = field(default_factory=dict)
    attention_peaks: List[Dict[str, Any]] = field(default_factory=list)
    rewatch_loop_analysis: Dict[str, str] = field(default_factory=dict)

    @property
    def concept(self) -> str:
        return self.story_concept

    @concept.setter
    def concept(self, val: str):
        self.story_concept = val

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["concept"] = self.story_concept
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoryBlueprint":
        raw_beats = data.get("beats", [])
        beats = [StoryBeat.from_dict(b) if isinstance(b, dict) else b for b in raw_beats]
        return cls(
            title=data.get("title", "Untitled Lifestyle Reel"),
            story_concept=data.get("story_concept") or data.get("concept", ""),
            story_goal=data.get("story_goal", ""),
            main_curiosity_question=data.get("main_curiosity_question", ""),
            open_loop=data.get("open_loop", ""),
            beginning=data.get("beginning", ""),
            development=data.get("development", ""),
            surprise=data.get("surprise", ""),
            payoff=data.get("payoff", ""),
            ending=data.get("ending", ""),
            rewatch_potential=data.get("rewatch_potential", ""),
            beats=beats,
            mode_disclosure=data.get("mode_disclosure", '⚠️ "Fictional / AI-generated lifestyle story for creative entertainment."'),
            natural_conflict=data.get("natural_conflict", ""),
            curiosity_chain=data.get("curiosity_chain", []),
            open_loop_stages=data.get("open_loop_stages", {}),
            attention_peaks=data.get("attention_peaks", []),
            rewatch_loop_analysis=data.get("rewatch_loop_analysis", {})
        )
