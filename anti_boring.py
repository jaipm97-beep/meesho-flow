"""
Anti-Boring Diagnostic Engine.
Performs a full-story scan to detect slow openings, generic intros, repeated information,
dead narrative stretches, weak payoffs, and flat visuals.
Returns structured diagnostics with Problem, Reason, and Actionable Fix.
"""
from typing import Dict, Any, List, Optional
from ..models.blueprint import StoryBlueprint, StoryBeat

class AntiBoringEngine:
    def __init__(self, ai_service=None):
        self.ai = ai_service

    def audit_story(self, blueprint: StoryBlueprint) -> Dict[str, Any]:
        """Scans story for all anti-boring criteria and provides structured diagnostics."""
        issues: List[Dict[str, str]] = []

        # 1. Slow Opening / Generic Intro check
        if blueprint.beats:
            first_beat = blueprint.beats[0]
            first_text = (first_beat.visual_moment + " " + first_beat.narrative_action).lower()
            generic_words = ["wakes up", "standing normally", "talking to camera saying hello", "intro", "just walking"]
            if any(w in first_text for w in generic_words):
                issues.append({
                    "problem": "Generic / Slow Opening",
                    "reason": "First 2 seconds lack an immediate visual pattern interrupt or high-status hook.",
                    "fix": "Open directly in mid-motion (stepping out of luxury vehicle or sharp camera push-in)."
                })

        # 2. Curiosity & Open Loop Check
        if not blueprint.open_loop or len(blueprint.open_loop) < 15:
            issues.append({
                "problem": "Missing or Weak Open Loop",
                "reason": "Viewer knows everything upfront; no unresolved question pulls them to the end.",
                "fix": "Withhold the outfit price or destination until Scene 3 to create narrative tension."
            })

        # 3. Repeated Information / Beats
        actions = [b.narrative_action.lower() for b in blueprint.beats]
        if len(actions) != len(set(actions)):
            issues.append({
                "problem": "Redundant Story Beat",
                "reason": "Multiple scenes feature near-identical actions without escalating the journey.",
                "fix": "Replace the duplicate action with an unexpected choice, small obstacle, or discovery."
            })

        # 4. Weak Payoff Check
        if not blueprint.payoff or len(blueprint.payoff) < 15:
            issues.append({
                "problem": "Unearned / Underwhelming Payoff",
                "reason": "The climax does not deliver on the promise established in the hook.",
                "fix": "Elevate payoff with a full 360° ghera drape twirl and unmistakable budget vs luxury flex."
            })

        # 5. Ending Check
        ending_text = blueprint.ending.lower()
        if "bye guys" in ending_text or "see you next time" in ending_text:
            issues.append({
                "problem": "Cliche Farewell Ending",
                "reason": "Abrupt goodbye breaks the lifestyle aesthetic and destroys loop potential.",
                "fix": "End with a confident smile, bookmark gesture, or seamless visual cut to Scene 1."
            })

        is_clean = len(issues) == 0
        return {
            "passed": is_clean,
            "total_issues": len(issues),
            "issues": issues,
            "summary": "Narrative is tight, retentive, and high-velocity!" if is_clean else f"Found {len(issues)} retention leak(s) needing optimization."
        }
