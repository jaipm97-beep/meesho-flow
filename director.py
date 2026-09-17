"""
AI Creative Director Orchestrator (Phase 2).
Coordinates StoryEngine, AttentionEngine, ViewerMindSimulator, PredictiveAttentionEngine,
AntiBoringEngine, and StoryOptimizer.
"""
from typing import Optional, Dict, Any, List
import copy
from dataclasses import asdict
from ..models.project import ProjectState, UserInput, ApprovalStatus, StoryApproach
from ..models.blueprint import StoryBlueprint
from ..models.attention import AttentionAnalysis
from ..services.ai_service import AIService
from ..engines.creator_engine import CreatorEngine
from ..engines.story_engine import StoryEngine
from ..engines.attention_engine import AttentionEngine
from ..engines.viewer_mind import ViewerMindSimulator
from ..engines.predictive_attention import PredictiveAttentionEngine
from ..engines.anti_boring import AntiBoringEngine
from ..engines.optimizer import StoryOptimizer

class CreativeDirector:
    def __init__(self, api_key: Optional[str] = None):
        self.ai = AIService(api_key=api_key)
        self.creator_engine = CreatorEngine(self.ai)
        self.story_engine = StoryEngine(self.ai)
        self.attention_engine = AttentionEngine(self.ai)
        self.viewer_mind = ViewerMindSimulator(self.ai)
        self.predictive_engine = PredictiveAttentionEngine(self.ai)
        self.anti_boring = AntiBoringEngine(self.ai)
        self.optimizer = StoryOptimizer(self.story_engine, self.attention_engine, self.viewer_mind, self.anti_boring)

    def set_api_key(self, api_key: str):
        self.ai.set_key(api_key)

    def process_idea(self, user_input: UserInput, project_id: Optional[str] = None) -> ProjectState:
        """Main Phase 1 & 2 pipeline: Input -> Suggestions -> Creator Profile -> Blueprint -> Attention Analysis -> Phase 2 Intel."""
        if not user_input.idea or not user_input.idea.strip():
            user_input.idea = "Aesthetic lifestyle day out discovering an unexpected hidden gem boutique."

        # 1. Smart Suggestions
        suggestions = self.creator_engine.generate_smart_suggestions(user_input.idea)

        # 2. Reusable Creator Profile
        creator = self.creator_engine.build_creator_profile(user_input, suggestions)

        # 3. Story Blueprint Generation
        blueprint = self.story_engine.generate_blueprint(user_input, suggestions, creator)

        # 4. Total Attention Analysis & Score (11 Dimensions)
        attention = self.attention_engine.evaluate_attention(blueprint, user_input.idea)

        # 5. Phase 2 Story Intelligence Extensions
        approaches = [asdict(a) for a in self.story_engine.generate_multiple_approaches(user_input)]
        mind_analysis = self.viewer_mind.simulate_full_story(blueprint)
        boring_audit = self.anti_boring.audit_story(blueprint)
        timeline_dicts = [asdict(t) for t in attention.timeline]

        proj = ProjectState(
            project_id=project_id if project_id else ProjectState().project_id,
            project_name=blueprint.title,
            user_input=user_input,
            ai_suggestions=suggestions,
            creator_profile=creator.to_dict(),
            story_blueprint=blueprint.to_dict(),
            attention_analysis=attention.to_dict(),
            approval_status=ApprovalStatus.DRAFT,
            story_approaches=approaches,
            original_story_blueprint=copy.deepcopy(blueprint.to_dict()),
            viewer_mind_analysis=mind_analysis,
            anti_boring_audit=boring_audit,
            attention_timeline=timeline_dicts
        )
        return proj

    def auto_optimize_story(self, project: ProjectState, max_rounds: int = 3) -> ProjectState:
        """Runs iterative optimization loop (up to 3 rounds) with change tracking and rescoring."""
        return self.optimizer.auto_optimize(project, max_rounds=max_rounds)

    def generate_multiple_approaches(self, user_input: UserInput) -> List[StoryApproach]:
        """Generates 5 distinct creative angles for the given idea."""
        return self.story_engine.generate_multiple_approaches(user_input)

    def apply_story_approach(self, project: ProjectState, approach: StoryApproach) -> ProjectState:
        """Applies a selected story approach to the active blueprint."""
        if not project.original_story_blueprint and project.story_blueprint:
            project.original_story_blueprint = copy.deepcopy(project.story_blueprint)

        bp = StoryBlueprint.from_dict(project.story_blueprint) if project.story_blueprint else None
        if bp:
            bp.title = f"{approach.name}: {approach.story_angle[:35]} ✨"
            bp.story_concept = approach.story_angle
            bp.main_curiosity_question = approach.main_curiosity
            bp.payoff = approach.payoff
            if bp.beats and len(bp.beats) >= 2:
                bp.beats[1].narrative_action = f"Encountering the {approach.name.lower()} twist: {approach.main_curiosity}"
                bp.beats[-1].narrative_action = f"Executing the satisfying {approach.name.lower()} payoff: {approach.payoff}"

            new_attention = self.attention_engine.evaluate_attention(bp, project.user_input.idea)
            project.story_blueprint = bp.to_dict()
            project.attention_analysis = new_attention.to_dict()
            project.viewer_mind_analysis = self.viewer_mind.simulate_full_story(bp)
            project.anti_boring_audit = self.anti_boring.audit_story(bp)
            project.attention_timeline = [asdict(t) for t in new_attention.timeline]
            project.project_name = bp.title
            project.approval_status = ApprovalStatus.REVISED
            project.touch()

        return project

    def revert_to_original(self, project: ProjectState) -> ProjectState:
        """Reverts the story blueprint to the original version before auto-optimization."""
        if project.original_story_blueprint:
            project.story_blueprint = copy.deepcopy(project.original_story_blueprint)
            bp = StoryBlueprint.from_dict(project.story_blueprint)
            new_attention = self.attention_engine.evaluate_attention(bp, project.user_input.idea)
            project.attention_analysis = new_attention.to_dict()
            project.viewer_mind_analysis = self.viewer_mind.simulate_full_story(bp)
            project.anti_boring_audit = self.anti_boring.audit_story(bp)
            project.attention_timeline = [asdict(t) for t in new_attention.timeline]
            project.project_name = bp.title
            project.touch()
        return project

    def run_anti_boring_scan(self, project: ProjectState) -> Dict[str, Any]:
        """Runs the Anti-Boring diagnostic scan across the current blueprint."""
        bp = StoryBlueprint.from_dict(project.story_blueprint) if project.story_blueprint else None
        if not bp:
            return {"passed": True, "issues": []}
        audit = self.anti_boring.audit_story(bp)
        project.anti_boring_audit = audit
        return audit

    def regenerate_blueprint(self, project: ProjectState, flavor: str) -> ProjectState:
        """Applies targeted creative directives without wiping existing user settings."""
        directive_map = {
            "improve": "General polish: enhance rhythm, visual clarity, and emotional resonance.",
            "curiosity": "Amplify curiosity: increase mystery around the open loop and delay the reveal.",
            "cinematic": "Maximum cinematic grandeur: upscale camera motion, dramatic lighting contrast, and depth of field.",
            "natural": "Hyper-natural lifestyle vlog: candid reactions, bestie conversational intimacy, unpretentious charm.",
            "luxury": "Ultra-luxury flex: opulent South Mumbai / Delhi setting, high-end vehicle ingress, refined accessories.",
            "emotional": "Deeper emotional connection: vulnerability, relatable fear of being out of place, joyful relief.",
            "pacing": "Fast-paced punchy tempo: quick 2-3 second visual beats, high-energy cuts.",
            "hook": "Unignorable viral hook: intense 0.5s visual pattern interrupt and shock opening.",
            "refresh": "Creative alternative: explore a fresh narrative angle with the same core ingredients."
        }
        directive = directive_map.get(flavor.lower(), "Refine and elevate the story blueprint.")

        suggestions = project.ai_suggestions or self.creator_engine.generate_smart_suggestions(project.user_input.idea)
        from ..models.creator import CreatorProfile
        creator = CreatorProfile.from_dict(project.creator_profile) if project.creator_profile else self.creator_engine.build_creator_profile(project.user_input, suggestions)

        new_blueprint = self.story_engine.generate_blueprint(
            project.user_input,
            suggestions,
            creator,
            regeneration_directive=directive
        )
        new_attention = self.attention_engine.evaluate_attention(new_blueprint, project.user_input.idea)

        project.story_blueprint = new_blueprint.to_dict()
        project.attention_analysis = new_attention.to_dict()
        project.viewer_mind_analysis = self.viewer_mind.simulate_full_story(new_blueprint)
        project.anti_boring_audit = self.anti_boring.audit_story(new_blueprint)
        project.attention_timeline = [asdict(t) for t in new_attention.timeline]
        project.project_name = new_blueprint.title
        project.approval_status = ApprovalStatus.REVISED
        project.touch()
        return project

    def approve_blueprint(self, project: ProjectState) -> ProjectState:
        """Locks and marks the blueprint as approved for future Phase 2/3 engines."""
        project.approval_status = ApprovalStatus.APPROVED
        project.touch()
        return project
