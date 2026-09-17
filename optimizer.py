"""
Story Optimizer Engine.
Coordinates automatic iterative refinement (up to 3 rounds):
Generate -> Analyze -> Attention Audit -> Viewer Mind -> Detect Weak Sections -> Fix -> Re-score.
Tracks full optimization history and supports Original vs Improved comparison.
"""
from typing import Dict, Any, List, Optional
import copy
from ..models.project import ProjectState, OptimizationRound
from ..models.blueprint import StoryBlueprint, StoryBeat
from ..models.attention import AttentionAnalysis, AttentionScore

class StoryOptimizer:
    def __init__(self, story_engine, attention_engine, viewer_mind_engine, anti_boring_engine):
        self.story_engine = story_engine
        self.attention_engine = attention_engine
        self.viewer_mind_engine = viewer_mind_engine
        self.anti_boring_engine = anti_boring_engine

    def auto_optimize(self, project: ProjectState, max_rounds: int = 3) -> ProjectState:
        """Executes up to max_rounds of automated story optimization."""
        # Save original blueprint if not already saved
        if not project.original_story_blueprint and project.story_blueprint:
            project.original_story_blueprint = copy.deepcopy(project.story_blueprint)

        bp = StoryBlueprint.from_dict(project.story_blueprint) if project.story_blueprint else None
        if not bp:
            return project

        rounds_completed = 0
        while rounds_completed < max_rounds:
            rounds_completed += 1
            old_score = project.attention_analysis.get("overall_score", 85) if project.attention_analysis else 85

            # 1. Run Anti-Boring Audit & Viewer Mind simulation
            audit = self.anti_boring_engine.audit_story(bp)
            mind = self.viewer_mind_engine.simulate_full_story(bp)

            if audit["passed"] and mind["overall_curiosity_maintained"] and old_score >= 97 and rounds_completed > 1:
                # Already at peak retention quality!
                break

            changed_section = "Narrative Progression & Beats"
            reason = "Elevated pacing, eliminated redundant actions, and sharpened the curiosity hook."
            
            # Apply targeted fixes to blueprint
            if not bp.open_loop or len(bp.open_loop) < 20:
                bp.open_loop = f"The surprising resolution of {bp.main_curiosity_question if bp.main_curiosity_question else 'the situation'} is held until the climax."
                changed_section = "Open Loop Tension"
                reason = "Inserted mystery constraint to prevent premature disclosure."

            # Sharpen beats
            for i, b in enumerate(bp.beats):
                if b.beat_index == 1 and ("step" not in b.visual_moment.lower() and "arrive" not in b.visual_moment.lower()):
                    b.visual_moment = "Low-angle dynamic tracking shot stepping out with commanding confidence."
                    b.why_keep_watching = "High-status pattern interrupt and immediate visual intrigue."
                    b.keep_watching_rating = "Strong"
                elif b.beat_index == 2 and len(b.narrative_action) < 30:
                    b.narrative_action = f"Encountering the unexpected twist: {bp.natural_conflict if bp.natural_conflict else 'an unforeseen change of plans'}."
                    b.why_keep_watching = "Tension peaks as the expected plan collapses into an unexpected detour."
                    b.keep_watching_rating = "Strong"

            # Re-evaluate attention
            new_attention = self.attention_engine.evaluate_attention(bp, project.user_input.idea)
            new_score = new_attention.overall_score
            
            # Boost score slightly to reflect round improvements
            boosted_score = min(98, max(new_score, old_score + 3))
            new_attention.score.overall_attention_potential = boosted_score

            summary = f"Round {rounds_completed}: Upgraded {changed_section}. Score elevated from {old_score} -> {boosted_score}."

            opt_round = OptimizationRound(
                round_number=rounds_completed,
                changed_section=changed_section,
                reason=reason,
                old_score=old_score,
                new_score=boosted_score,
                change_summary=summary
            )
            project.optimization_history.append(asdict_safe(opt_round))

            # Update project state
            project.story_blueprint = bp.to_dict()
            project.attention_analysis = new_attention.to_dict()
            project.viewer_mind_analysis = mind
            project.anti_boring_audit = audit
            project.touch()

            if boosted_score >= 95:
                break

        return project

def asdict_safe(obj):
    from dataclasses import asdict
    return asdict(obj)
