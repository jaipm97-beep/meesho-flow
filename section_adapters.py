"""
Section Adapters for Visual Attention Engine.
Provides tailored visual rules for all 9 application studios with:
- 8K UHD photorealistic cinematography standards
- Duchenne smile & real facial micro-expressions
- Speed ramping camera choreography (1.0x -> 0.4x slow-mo -> 1.5x snap cut)
- Synchronized Foley SFX timeline with -8dB dialogue audio ducking
"""
from typing import Dict, Any, List
from .models import VisualBeatCue, VisualMode
from .motion_rules import (
    get_speed_curve_for_phase,
    get_speed_ramp_notation_for_phase,
    get_sfx_timeline_for_phase,
    get_micro_expression_for_phase,
    get_camera_for_phase,
    CINEMATOGRAPHY_8K_STANDARD
)
from .curiosity_gap import generate_why_watch_next

class BaseSectionAdapter:
    section_name: str = "Generic Studio"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        return get_sfx_timeline_for_phase(phase)

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        return get_micro_expression_for_phase(phase, has_dialogue=True)

    def adapt_scene(self, scene_idx: int, total_scenes: int, raw_data: Dict[str, Any], mode: VisualMode) -> VisualBeatCue:
        action = raw_data.get("action", raw_data.get("visual", "Action in scene"))
        phase = raw_data.get("phase", f"Scene {scene_idx}")
        ts = raw_data.get("timestamp_range", f"00:0{scene_idx*3 - 3} - 00:0{scene_idx*3}")
        
        c_gap = generate_why_watch_next(scene_idx, total_scenes, action, self.section_name)
        speed = get_speed_curve_for_phase(phase, mode.value)
        speed_ramp = get_speed_ramp_notation_for_phase(phase, mode.value)
        camera = get_camera_for_phase(phase, mode.value)
        sfx = self.get_custom_sfx(scene_idx, phase)
        expr = self.get_custom_expression(scene_idx, phase, mode)

        if mode == VisualMode.PRECISION_LOCK:
            pat_int = "Abrupt 0.5s visual cut, high-contrast entrance or camera speed shift"
        else:
            pat_int = "Organic motion flow"

        return VisualBeatCue(
            beat_index=scene_idx,
            timestamp_range=ts,
            phase_name=phase,
            visual_action=action,
            camera_motion=camera,
            speed_curve=speed,
            speed_ramp_timeline=speed_ramp,
            sfx_foley_timeline=sfx,
            micro_expressions=expr,
            cinematography_8k=CINEMATOGRAPHY_8K_STANDARD,
            facial_expression=expr,
            fabric_motion="Fluid wave ripples and authentic fabric gravity drape",
            pattern_interrupt=pat_int,
            why_watch_next=c_gap["why_watch_next"],
            tension_level=c_gap["tension_level"],
            subconscious_question=c_gap.get("subconscious_question", ""),
            micro_cliffhanger=c_gap.get("micro_cliffhanger", ""),
            drop_risk_status="SAFE"
        )

class LifestyleAdapter(BaseSectionAdapter):
    section_name = "Lifestyle Vlog"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        cues = [
            "00:00.2s: Matte luxury sports car door thud | 00:01.3s: Stiletto clicks on high-gloss marble | -8dB BGM ducking during dialogue",
            "00:00.5s: Ambient grand mall atrium acoustics & faint chatter | 00:02.1s: Designer handbag chain clink | -8dB BGM ducking",
            "00:00.8s: Velvet curtain pull & luxury boutique register chime | 00:02.2s: Fabric glide across satin hanger",
            "00:00.4s: Terrace café espresso cup clinking porcelain saucer | 00:01.8s: Gentle afternoon breeze whisper",
            "00:01.5s: Sunset rooftop ambient lounge music swell | 00:02.8s: Bass beat impact for seamless rewatch loop"
        ]
        return cues[(scene_idx - 1) % len(cues)]

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        exprs = [
            "Confident high-status entry, authentic Duchenne smiling eyes crinkling, candid lips greeting lens naturally.",
            "Intrigued storytelling gaze, micro-eyebrow raise discovering unexpected boutique display, animated speech.",
            "Stunned delight, genuine laughter parting lips, playful shoulder shrug admiring mirror fit reflection.",
            "Serene luxury aesthetic smile, warm direct eye contact over espresso cup, conversational warmth.",
            "Radiant triumphant Duchenne smile, subtle playful wink, effortlessly transitioning into loop bookmark pose."
        ]
        return exprs[(scene_idx - 1) % len(exprs)]

class ProblemHacksAdapter(BaseSectionAdapter):
    section_name = "Problem Stories"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        cues = [
            "00:00.3s: Sharp gasp / record scratch halt | 00:01.2s: Restless fabric tugging rustle | -8dB BGM ducking",
            "00:00.6s: Dramatic tension drone | 00:01.8s: Uncomfortable seam friction | -8dB BGM ducking",
            "00:00.4s: Lightbulb ding / upbeat synth riser | 00:01.5s: Smooth zipper / safety hack snap",
            "00:00.7s: Triumphant bass drop | 00:01.8s: Crisp outfit brush sound showing flawless silhouette",
            "00:01.2s: Cheerful affirmation chime | 00:02.5s: Loop snap transition"
        ]
        return cues[(scene_idx - 1) % len(cues)]

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        exprs = [
            "Relatable dismay, genuine furrowed brow and exasperated gasp looking down at ill-fitting outfit, authentic human micro-expression with zero frozen mouth.",
            "Direct conversational venting, expressive eyebrow movements, honest relatable eye contact with natural speech articulation.",
            "Sudden eureka micro-expression: widening eyes, parting lips with excited realization, joyful smile forming.",
            "Triumphant Duchenne smile with glowing crinkles around eyes, showing off the effortless hack with proud confidence.",
            "Relieved, celebratory warm Duchenne smile, nodding reassuringly to the viewer, no fake grin."
        ]
        return exprs[(scene_idx - 1) % len(exprs)]

class RunwayDanceAdapter(BaseSectionAdapter):
    section_name = "Runway & Dance"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        cues = [
            "00:00.0s: Heavy trending bass 808 kick drop | 00:01.2s: Resonant runway heel strike",
            "00:00.8s: Mesmerizing sub-bass glide | 00:02.0s: Lyrical vocal hook accent",
            "00:00.5s: 120fps slow-motion fabric air whoosh | 00:02.5s: Shimmer sparkle chime on peak twirl",
            "00:00.4s: Snare clap sync with hip pivot | 00:02.1s: Layered vocal harmony peak",
            "00:01.5s: Punchy sync kick on freeze bookmark | 00:02.8s: Sub-drop reverberation looping to start"
        ]
        return cues[(scene_idx - 1) % len(cues)]

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        exprs = [
            "Fierce high-fashion gaze, confident runway composure, gentle lip part transitioning into captivating smile.",
            "Playful rhythmic lip mouthing perfectly in sync with trending lyrical syllables, sparkling expressive eyes.",
            "Mesmerizing Duchenne smile caught in 120fps slow-motion, hair blowing naturally, closed lips with radiant warmth.",
            "Dynamic rhythm-locked facial energy, cheek dimples visible, engaging joyful direct camera gaze.",
            "Poised editorial bookmark smile, subtle head tilt, high-energy eye lock for seamless loop."
        ]
        return exprs[(scene_idx - 1) % len(exprs)]

class ProductPhotoAdapter(BaseSectionAdapter):
    section_name = "Product Photo"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        cues = [
            "00:00.2s: Professional camera shutter click | 00:01.1s: Soft atmospheric studio swell",
            "00:00.5s: Tactile fabric rub & texture glide | 00:01.8s: Subtle metallic zipper / button touch",
            "00:00.4s: Slow-motion air swish of hem flare | 00:02.2s: Golden warm acoustic chime",
            "00:00.6s: Modern synth pulse | 00:02.0s: Crisp outfit fit-check brush",
            "00:01.2s: Shutter burst sound | 00:02.5s: Smooth audio fade into loop"
        ]
        return cues[(scene_idx - 1) % len(cues)]

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        exprs = [
            "Pristine commercial model poise, genuine micro-smile, authentic eye engagement with camera lens.",
            "Appreciative micro-gaze inspecting garment texture, gentle head tilt of admiration, candid smile.",
            "Dynamic Duchenne smile with laughing eyes during garment movement, 100% natural facial warmth.",
            "Clear speech articulation explaining neckline and fabric fall, expressive brows, zero frozen grin.",
            "Polished final fit confirmation, warm inviting smile, subtle nod of high recommendation."
        ]
        return exprs[(scene_idx - 1) % len(exprs)]

class TrendsRadarAdapter(BaseSectionAdapter):
    section_name = "Trends Radar"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        return "00:00.2s: Viral notification ping | 00:01.1s: Upbeat hyper-pop bass drop | -8dB BGM ducking during trend breakdown"

class BatchHaulAdapter(BaseSectionAdapter):
    section_name = "Batch Haul"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        return f"00:00.3s: Unboxing parcel tear / hanger slide | 00:01.5s: Price tag rustle | -8dB BGM ducking for Item {scene_idx}"

class FashionStylistAdapter(BaseSectionAdapter):
    section_name = "Fashion Stylist"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        return "00:00.4s: Wardrobe door slide | 00:01.6s: Accessory clink / belt buckle snap | -8dB BGM ducking during styling rule"

class GenericStudioAdapter(BaseSectionAdapter):
    section_name = "Studio Workspace"

class MeeshoUnboxAdapter(BaseSectionAdapter):
    section_name = "Meesho Unbox & Try-On"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        cues = [
            "00:00.2s: Meesho delivery parcel tear / polybag rustle | 00:01.3s: Tactile fabric unfolding whisper | -8dB BGM ducking during spoken unbox hook",
            "00:00.6s: Garment air whoosh fluttering toward camera lens | 00:01.4s: Crisp finger snap / shutter click | 00:01.8s: Heavy sub-bass 808 drop on match-cut outfit reveal",
            "00:00.8s: 120fps slow-motion fabric wave flutter | 00:02.2s: Shimmer chime on 360° twirl flare | -8dB BGM ducking during fit narration",
            "00:00.5s: Lens rack-focus click on stitching | 00:01.8s: Honest verdict affirmation chime | -8dB BGM ducking",
            "00:01.2s: Comment CTA notification ping | 00:02.6s: Smooth audio fade looping seamlessly to Scene 1 unboxing"
        ]
        return cues[(scene_idx - 1) % len(cues)]

    def get_custom_expression(self, scene_idx: int, phase: str, mode: VisualMode) -> str:
        exprs = [
            "Curious, candid expression in casual wear, holding unfolded Meesho garment in both hands with playful intrigue: 'Dekho kaisa aaya hai!', genuine eye contact, dynamic speech articulation.",
            "Playful, mischievous smirk right as she tosses the garment toward the camera lens / snaps fingers, anticipating viewer surprise.",
            "Radiant Duchenne smile with orbicularis oculi eye crinkles, stunning worn fit reveal, genuine laughter and head tilt during twirl.",
            "Honest, confident reviewer expression inspecting fabric and seam up close, warm conversational smile, zero plastic mouth.",
            "Triumphant friendly smile, inviting direct DM comment, seamless bookmark posture for replay loop."
        ]
        return exprs[(scene_idx - 1) % len(exprs)]

class RemixerAdapter(BaseSectionAdapter):
    section_name = "Remixer"

    def get_custom_sfx(self, scene_idx: int, phase: str) -> str:
        return "00:00.2s: Vinyl DJ scratch / visual match-cut whoosh | 00:01.4s: Remixed bass drop impact"

ADAPTER_REGISTRY = {
    "lifestyle": LifestyleAdapter(),
    "problem": ProblemHacksAdapter(),
    "runway": RunwayDanceAdapter(),
    "dance": RunwayDanceAdapter(),
    "product": ProductPhotoAdapter(),
    "trends": TrendsRadarAdapter(),
    "haul": BatchHaulAdapter(),
    "stylist": FashionStylistAdapter(),
    "studio": GenericStudioAdapter(),
    "remix": RemixerAdapter(),
    "unbox": MeeshoUnboxAdapter(),
    "meesho": MeeshoUnboxAdapter()
}

def get_adapter_for_section(section_name: str) -> BaseSectionAdapter:
    sec = section_name.lower()
    for key, adapter in ADAPTER_REGISTRY.items():
        if key in sec:
            return adapter
    return GenericStudioAdapter()
