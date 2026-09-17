"""
Viewer Mind Simulator Engine.
Simulates subconscious viewer psychology, knowledge state, curiosity tension,
boredom risk, and why the viewer will or will not keep watching at each beat.
"""
from typing import Dict, Any, List, Optional
from ..models.blueprint import StoryBlueprint, StoryBeat

class ViewerMindSimulator:
    def __init__(self, ai_service=None):
        self.ai = ai_service

    def simulate_beat(self, beat: StoryBeat, previous_beats: List[StoryBeat], blueprint: StoryBlueprint) -> Dict[str, Any]:
        """Simulates viewer cognitive state at a specific beat."""
        idx = beat.beat_index
        total_beats = len(blueprint.beats)
        
        # Determine knowledge state
        if idx == 1:
            knows = f"Arrived at venue/setting ({beat.visual_moment[:45]}...). Notices high-status entry."
            does_not_know = "What the creator's true objective or hidden secret is."
            subconscious_question = blueprint.main_curiosity_question or "Why is she here and what happens next?"
            expects_next = "Movement into the main scene or an encounter."
            curiosity_alive = True
            boredom_risk = False
            reward_next = "Discovery of unexpected environment or obstacle."
            rating = "Strong"
            fix = ""
        elif idx == 2:
            knows = "The plan is in motion, but a twist or complication begins to surface."
            does_not_know = "How the conflict or mix-up will be resolved."
            subconscious_question = "Will she find what she came for, or is the plan ruined?"
            expects_next = "The turning point or dramatic reaction."
            curiosity_alive = True
            boredom_risk = len(beat.narrative_action) < 15
            reward_next = "Uncovering the secret backup solution."
            rating = "Medium" if boredom_risk else "Strong"
            fix = "Add an expressive gasp or close-up reveal to elevate tension." if boredom_risk else ""
        elif idx == 3:
            knows = "The surprise alternative or luxury dupe has been unveiled."
            does_not_know = "The full payoff, how it looks in full motion, and the true price."
            subconscious_question = "How good does this look and what's the actual catch/price?"
            expects_next = "Full aesthetic transformation and validation."
            curiosity_alive = True
            boredom_risk = False
            reward_next = "Stunning 360° visual movement and price reveal."
            rating = "Strong"
            fix = ""
        else: # Climax / Ending
            knows = "The surprise succeeded, full outfit/moment validated in public/terrace."
            does_not_know = "Where to get it or how the story loops back."
            subconscious_question = "Where can I get this exact look / link?"
            expects_next = "Clear call to action or replay loop."
            curiosity_alive = False # Resolved!
            boredom_risk = False
            reward_next = "Actionable comment trigger and satisfying loop closure."
            rating = "Strong"
            fix = ""

        return {
            "beat_index": idx,
            "phase": beat.phase,
            "viewer_knows": knows,
            "viewer_does_not_know": does_not_know,
            "subconscious_question": subconscious_question,
            "expects_next": expects_next,
            "curiosity_alive": curiosity_alive,
            "boredom_risk": boredom_risk,
            "meaningful_reward_next": reward_next,
            "keep_watching_rating": rating,
            "keep_watching_fix": fix
        }

    def simulate_full_story(self, blueprint: StoryBlueprint) -> Dict[str, Any]:
        """Full simulation of viewer's psychological journey through the reel."""
        beat_simulations = []
        prev = []
        overall_curiosity_alive = True
        boredom_hotspots = []

        for b in blueprint.beats:
            sim = self.simulate_beat(b, prev, blueprint)
            beat_simulations.append(sim)
            prev.append(b)
            if sim["boredom_risk"]:
                boredom_hotspots.append(f"Beat {b.beat_index} ({b.phase})")

        return {
            "beat_simulations": beat_simulations,
            "overall_curiosity_maintained": len(boredom_hotspots) == 0,
            "boredom_hotspots": boredom_hotspots,
            "viewer_takeaway": f"Engaged by '{blueprint.main_curiosity_question}', satisfied by '{blueprint.payoff}'."
        }
