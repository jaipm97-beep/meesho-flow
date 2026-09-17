"""
Predictive Attention Engine & Attention Debt Tracker.
Forecasts future drop-offs, triggers Pre-Drop Warnings with proactive fixes,
and tracks Attention Debt for intentionally slow scenic moments.
"""
from typing import Dict, Any, List, Optional
from ..models.blueprint import StoryBlueprint, StoryBeat
from ..models.attention import TimelineSegment, AttentionDebt

class PredictiveAttentionEngine:
    def __init__(self, ai_service=None):
        self.ai = ai_service

    def build_timeline_and_predict(self, blueprint: StoryBlueprint) -> Dict[str, Any]:
        """Generates visual timeline segments with predictive drop analysis and debt tracking."""
        timeline: List[TimelineSegment] = []
        debt = AttentionDebt(is_in_debt=False, debt_settled=True)
        
        total_beats = len(blueprint.beats)
        for i, b in enumerate(blueprint.beats):
            idx = b.beat_index
            phase = b.phase.lower()
            
            # Predictive level and retention percentage
            if "beginning" in phase or idx == 1:
                level = "HOOK 🔥"
                retention = 96
                warning = None
                fix = None
            elif "development" in phase or idx == 2:
                # Check for pre-drop risk: if text is short or action is passive
                has_action = any(w in b.narrative_action.lower() for w in ["walk", "discover", "enter", "glance", "twist", "turn", "react"])
                if not has_action or len(b.narrative_action) < 20:
                    level = "DROP RISK 🟡"
                    retention = 78
                    warning = "Viewer attention may dip in the next 2-3s due to low narrative velocity."
                    fix = "Inject an abrupt camera perspective shift, macro texture zoom, or candid micro-reaction."
                    debt = AttentionDebt(
                        is_in_debt=True,
                        slow_scene_index=idx,
                        reason="Pacing dips during transition into the venue.",
                        compensating_beat_index=idx + 1,
                        debt_settled=False
                    )
                else:
                    level = "BUILD 🟢"
                    retention = 88
                    warning = None
                    fix = None
            elif "surprise" in phase or idx == 3:
                level = "REVEAL 🔥"
                retention = 94
                warning = None
                fix = None
                if debt.is_in_debt:
                    debt.debt_settled = True # Settled by high-energy surprise!
            elif "payoff" in phase or idx >= 4:
                level = "PAYOFF 🔥"
                retention = 95
                warning = None
                fix = None
            else:
                level = "ENGAGED 🟢"
                retention = 90
                warning = None
                fix = None

            timeline.append(TimelineSegment(
                timestamp_range=b.timestamp_range,
                phase_name=b.phase,
                attention_level=level,
                predicted_retention_pct=retention,
                pre_drop_warning=warning,
                proactive_fix=fix
            ))

        return {
            "timeline": timeline,
            "debt": debt,
            "has_drop_risk": any(t.pre_drop_warning is not None for t in timeline)
        }
