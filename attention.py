"""
Attention Engine Models.
Full Total Attention Architecture (Phase 2):
11 Dimensions: Hook, Curiosity, Visual, Story, Emotion, Audio, Text, Pacing, Surprise, Payoff, Rewatch.
Timeline, Pre-Drop Detection, Attention Debt, and Diagnostic Reports.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class AttentionScore:
    hook: int = 88
    curiosity: int = 90
    visual_potential: int = 92
    story_progression: int = 89
    emotion: int = 86
    audio_potential: int = 85
    text_potential: int = 87
    pacing: int = 91
    surprise: int = 93
    payoff: int = 92
    rewatch_potential: int = 88
    overall_attention_potential: int = 89
    label: str = "High Attention Potential"

    def calculate_overall(self) -> int:
        vals = [
            self.hook, self.curiosity, self.visual_potential, self.story_progression,
            self.emotion, self.audio_potential, self.text_potential, self.pacing,
            self.surprise, self.payoff, self.rewatch_potential
        ]
        self.overall_attention_potential = round(sum(vals) / len(vals))
        if self.overall_attention_potential >= 90:
            self.label = "Viral Tier (90-100)"
        elif self.overall_attention_potential >= 80:
            self.label = "Strong Retentive (80-89)"
        else:
            self.label = "Needs Optimization (Below 80)"
        return self.overall_attention_potential

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionScore":
        return cls(
            hook=data.get("hook", 88),
            curiosity=data.get("curiosity", 90),
            visual_potential=data.get("visual_potential", 92),
            story_progression=data.get("story_progression", 89),
            emotion=data.get("emotion", 86),
            audio_potential=data.get("audio_potential", 85),
            text_potential=data.get("text_potential", 87),
            pacing=data.get("pacing", 91),
            surprise=data.get("surprise", 93),
            payoff=data.get("payoff", 92),
            rewatch_potential=data.get("rewatch_potential", 88),
            overall_attention_potential=data.get("overall_attention_potential", 89),
            label=data.get("label", "High Attention Potential")
        )

@dataclass
class KeepWatchingCheck:
    beat_index: int
    beat_name: str
    why_keep_watching: str
    is_sufficient: bool = True
    warning: str = ""
    improvement_tip: str = ""

@dataclass
class TimelineSegment:
    timestamp_range: str
    phase_name: str
    attention_level: str # e.g. "HOOK 🔥", "CURIOSITY 🔥", "BUILD 🟢", "DROP RISK 🟡", "REVEAL 🔥", "PAYOFF 🔥"
    predicted_retention_pct: int = 85
    pre_drop_warning: Optional[str] = None
    proactive_fix: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimelineSegment":
        return cls(
            timestamp_range=data.get("timestamp_range", "00:00 - 00:03"),
            phase_name=data.get("phase_name", "Hook"),
            attention_level=data.get("attention_level", "HOOK 🔥"),
            predicted_retention_pct=data.get("predicted_retention_pct", 85),
            pre_drop_warning=data.get("pre_drop_warning"),
            proactive_fix=data.get("proactive_fix")
        )

@dataclass
class AttentionDebt:
    is_in_debt: bool = False
    slow_scene_index: int = 0
    reason: str = ""
    compensating_beat_index: int = 0
    debt_settled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionDebt":
        return cls(
            is_in_debt=data.get("is_in_debt", False),
            slow_scene_index=data.get("slow_scene_index", 0),
            reason=data.get("reason", ""),
            compensating_beat_index=data.get("compensating_beat_index", 0),
            debt_settled=data.get("debt_settled", True)
        )

@dataclass
class AttentionReport:
    overall_attention_potential: int = 89
    strongest_moment: str = ""
    weakest_moment: str = ""
    attention_drop_risk: str = "Low" # Low, Medium, High
    curiosity_strength: str = "Strong"
    story_progression: str = "Smooth"
    payoff_strength: str = "High"
    rewatch_potential: str = "High"
    top_3_improvements: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionReport":
        return cls(
            overall_attention_potential=data.get("overall_attention_potential", 89),
            strongest_moment=data.get("strongest_moment", ""),
            weakest_moment=data.get("weakest_moment", ""),
            attention_drop_risk=data.get("attention_drop_risk", "Low"),
            curiosity_strength=data.get("curiosity_strength", "Strong"),
            story_progression=data.get("story_progression", "Smooth"),
            payoff_strength=data.get("payoff_strength", "High"),
            rewatch_potential=data.get("rewatch_potential", "High"),
            top_3_improvements=data.get("top_3_improvements", [])
        )

@dataclass
class AttentionAnalysis:
    score: AttentionScore = field(default_factory=AttentionScore)
    attention_questions: Dict[str, str] = field(default_factory=dict)
    keep_watching_checks: List[KeepWatchingCheck] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    # Phase 2 Extensions
    timeline: List[TimelineSegment] = field(default_factory=list)
    debt: Optional[AttentionDebt] = None
    report: Optional[AttentionReport] = None

    @property
    def overall_score(self) -> int:
        return self.score.overall_attention_potential

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["overall_score"] = self.score.overall_attention_potential
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttentionAnalysis":
        score_data = data.get("score", {})
        score = AttentionScore.from_dict(score_data) if isinstance(score_data, dict) else AttentionScore()
        raw_checks = data.get("keep_watching_checks", [])
        checks = [KeepWatchingCheck(**c) if isinstance(c, dict) else c for c in raw_checks]
        raw_timeline = data.get("timeline", [])
        timeline = [TimelineSegment.from_dict(t) if isinstance(t, dict) else t for t in raw_timeline]
        raw_debt = data.get("debt")
        debt = AttentionDebt.from_dict(raw_debt) if isinstance(raw_debt, dict) else None
        raw_report = data.get("report")
        report = AttentionReport.from_dict(raw_report) if isinstance(raw_report, dict) else None

        return cls(
            score=score,
            attention_questions=data.get("attention_questions", {}),
            keep_watching_checks=checks,
            warnings=data.get("warnings", []),
            improvement_suggestions=data.get("improvement_suggestions", []),
            timeline=timeline,
            debt=debt,
            report=report
        )
