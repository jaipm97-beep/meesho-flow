"""
Project State & Input Models for AI Lifestyle Reel Story Director.
Phase 1 Foundation.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Optional, List
import uuid
import datetime

class ExecutionMode(str, Enum):
    QUICK = "quick"
    GUIDED = "guided"
    PRO = "pro"

class StoryMode(str, Enum):
    FICTIONAL = "fictional"
    REAL_LIFE = "real_life"
    HYBRID = "hybrid"

    def is_fictional(self) -> bool:
        return self in (StoryMode.FICTIONAL, StoryMode.HYBRID)

class ApprovalStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REVISED = "revised"

@dataclass
class UserInput:
    idea: str = ""
    duration: str = "30s"
    language: str = "Hinglish"
    story_mode: StoryMode = StoryMode.FICTIONAL
    style: str = "Natural Vlog"
    voiceover_enabled: bool = False
    execution_mode: ExecutionMode = ExecutionMode.QUICK
    
    # Guided / Pro extra inputs
    story_type: str = "Daily Lifestyle"
    location: str = ""
    mood: str = ""
    outfit: str = ""
    vehicle: str = ""
    visual_style: str = ""
    ending_style: str = ""
    
    # Pro Mode controls
    story_goal: str = ""
    curiosity_level: str = "Medium"
    pacing: str = "Medium"
    camera_preference: str = "Dynamic Steadicam"
    emotion: str = "Excited & Curious"
    structure_type: str = "Standard 4-Phase"
    
    # Metadata tagging (User Provided vs AI Suggested)
    user_provided_fields: List[str] = field(default_factory=list)

    def mark_user_provided(self, field_name: str):
        if field_name not in self.user_provided_fields:
            self.user_provided_fields.append(field_name)

    def is_user_provided(self, field_name: str) -> bool:
        return field_name in self.user_provided_fields

@dataclass
class AISuggestions:
    story_style: str = ""
    location: str = ""
    mood: str = ""
    visual_style: str = ""
    story_goal: str = ""
    curiosity_question: str = ""
    vehicle_or_prop: str = ""
    suggested_outfit: str = ""
    raw_suggestions: Dict[str, str] = field(default_factory=dict)
    tag: str = "AI Suggested"

@dataclass
class StoryApproach:
    name: str = "" # e.g. "Curiosity Story", "Experience Story", "Surprise Story", "Emotional Story", "Luxury Story"
    story_angle: str = ""
    main_curiosity: str = ""
    payoff: str = ""
    attention_potential: int = 90
    is_recommended: bool = False

@dataclass
class OptimizationRound:
    round_number: int = 1
    changed_section: str = ""
    reason: str = ""
    old_score: int = 85
    new_score: int = 92
    change_summary: str = ""

@dataclass
class ProjectState:
    project_id: str = field(default_factory=lambda: f"life_proj_{uuid.uuid4().hex[:8]}")
    project_name: str = "Untitled Lifestyle Vlog Reel"
    user_input: UserInput = field(default_factory=UserInput)
    ai_suggestions: Optional[AISuggestions] = None
    creator_profile: Optional[Dict[str, Any]] = None
    story_blueprint: Optional[Dict[str, Any]] = None
    attention_analysis: Optional[Dict[str, Any]] = None
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    version: str = "2.0.0"

    # Phase 2 Extensions
    story_approaches: List[Dict[str, Any]] = field(default_factory=list)
    optimization_history: List[Dict[str, Any]] = field(default_factory=list)
    original_story_blueprint: Optional[Dict[str, Any]] = None
    viewer_mind_analysis: Optional[Dict[str, Any]] = None
    anti_boring_audit: Optional[Dict[str, Any]] = None
    attention_timeline: Optional[List[Dict[str, Any]]] = None

    def touch(self):
        self.updated_at = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["user_input"]["story_mode"] = self.user_input.story_mode.value
        d["user_input"]["execution_mode"] = self.user_input.execution_mode.value
        d["approval_status"] = self.approval_status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectState":
        u_data = data.get("user_input", {})
        if "story_mode" in u_data and isinstance(u_data["story_mode"], str):
            u_data["story_mode"] = StoryMode(u_data["story_mode"])
        if "execution_mode" in u_data and isinstance(u_data["execution_mode"], str):
            u_data["execution_mode"] = ExecutionMode(u_data["execution_mode"])
        user_input = UserInput(**u_data) if u_data else UserInput()

        ai_sug = data.get("ai_suggestions")
        ai_suggestions = AISuggestions(**ai_sug) if ai_sug and isinstance(ai_sug, dict) else None

        app_status = data.get("approval_status", ApprovalStatus.DRAFT.value)
        if isinstance(app_status, str):
            try:
                app_status = ApprovalStatus(app_status)
            except ValueError:
                app_status = ApprovalStatus.DRAFT

        return cls(
            project_id=data.get("project_id", f"life_proj_{uuid.uuid4().hex[:8]}"),
            project_name=data.get("project_name", "Untitled Lifestyle Vlog Reel"),
            user_input=user_input,
            ai_suggestions=ai_suggestions,
            creator_profile=data.get("creator_profile"),
            story_blueprint=data.get("story_blueprint"),
            attention_analysis=data.get("attention_analysis"),
            approval_status=app_status,
            created_at=data.get("created_at", datetime.datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.datetime.now().isoformat()),
            version=data.get("version", "2.0.0"),
            story_approaches=data.get("story_approaches", []),
            optimization_history=data.get("optimization_history", []),
            original_story_blueprint=data.get("original_story_blueprint"),
            viewer_mind_analysis=data.get("viewer_mind_analysis"),
            anti_boring_audit=data.get("anti_boring_audit"),
            attention_timeline=data.get("attention_timeline")
        )
