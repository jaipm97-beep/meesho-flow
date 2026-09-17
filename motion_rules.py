"""
Motion Rules, Speed Ramping & SFX Choreography Library.
Provides precise speed ramping curves (1.0x -> 0.4x slow-mo 120fps -> 1.5x snap cut),
synchronized Foley SFX timelines, 8K cinematography directives, and Duchenne micro-expressions.
"""
from typing import Dict, Any

SPEED_CURVES = {
    "unbox_hold": "1.0x Engaging Conversational Unbox (Creator in casuals holding & unfolding garment towards lens)",
    "throw_snap": "1.5x Speed Ramp ➔ 0.4x Slow-Mo Match-Cut (Garment toss/snap into full try-on)",
    "fast_entry": "1.3x Fast Stride (Instant high-status visual entry)",
    "conversational": "1.0x Normal Conversational Speed (Clear dialogue articulation)",
    "ultra_slowmo": "0.4x Ultra Slow-Motion 120fps (Mesmerizing fabric twirl & flare wave)",
    "detail_zoom": "0.6x Smooth Push-In (Macro embroidery & tactile texture focus)",
    "snap_cut": "1.5x Snap Cut / Loop Pivot (Crisp bookmark pose & instant loop transition)"
}

SPEED_RAMP_NOTATIONS = {
    "unbox_hold": "00:00 - 00:01s: 1.0x Normal greeting ➔ 00:01 - 00:03.5s: 1.0x Hand unfolding cloth towards lens with crisp Steadicam lock",
    "throw_snap": "00:00 - 00:01s: 1.0x Holding cloth ➔ 00:01 - 00:02.2s: 1.5x Rapid garment throw/snap toward camera lens ➔ 00:02.2 - 00:03.5s: 0.4x Slow-mo 120fps match-cut worn reveal",
    "fast_entry": "00:00 - 00:01s: 1.0x Normal entry ➔ 00:01 - 00:02.5s: 0.4x Slow-mo 120fps glide ➔ 00:02.5 - 00:03s: 1.3x Snap transition",
    "conversational": "00:00 - 00:04s: 1.0x Continuous conversational pace with subtle micro-stabilized Steadicam drift",
    "ultra_slowmo": "00:00 - 00:00.8s: 1.0x Pre-twirl ➔ 00:00.8 - 00:03.2s: 0.35x Ultra slow-motion optical flow showing 360° fabric flare ➔ 00:03.2 - 00:04s: 1.2x Catch",
    "detail_zoom": "00:00 - 00:00.8s: 1.2x Rapid push-in ➔ 00:00.8 - 00:02.8s: 0.5x Macro inspection glide ➔ 00:02.8 - 00:03.5s: 1.0x Reset",
    "snap_cut": "00:00 - 00:02.5s: 1.0x Confident posture ➔ 00:02.5 - 00:03s: 2.0x High-speed whip/snap loop transition back to Scene 1"
}

SFX_TIMELINE_CUES = {
    "unbox_hold": "00:00.2s: Delivery parcel tear / polybag rustle | 00:01.2s: Tactile fabric unfolding whisper | 00:02.8s: Natural candid breath | -8dB BGM ducking during dialogue",
    "throw_snap": "00:00.8s: Cloth rustle & whoosh fluttering toward camera lens | 00:01.6s: Crisp finger snap / shutter click | 00:02.0s: Heavy sub-bass 808 drop on match-cut outfit reveal | -8dB BGM ducking during dialogue",
    "fast_entry": "00:00.2s: Sub-bass car door / heavy entrance thud | 00:01.2s: Crisp marble heel clicks echoing | 00:02.4s: High-status synth riser | -8dB BGM ducking during dialogue",
    "conversational": "00:00.4s: Intimate room acoustic warmth | 00:01.8s: Subtle jewelry clink | 00:02.9s: Natural conversational breath | -8dB BGM ducking during dialogue",
    "ultra_slowmo": "00:00.8s: Cinematic sub-drop | 00:01.5s: Silky fabric whoosh & aerodynamic air flutter | 00:03.2s: Shimmer chime resonance",
    "detail_zoom": "00:00.5s: Camera lens rack-focus click | 00:01.6s: Tactile fabric weave friction / zipper glide sound | 00:02.8s: Soft atmospheric swell",
    "snap_cut": "00:01.8s: Crisp finger snap / camera shutter click | 00:02.8s: Bass drop impact with seamless loop reverberation"
}

MICRO_EXPRESSIONS = {
    "duchenne_smile": "Authentic Duchenne smile with orbicularis oculi crinkling at eye corners, genuine warmth, lifelike conversational mouth articulation without exaggerated jaw drop, subtle candid head tilt.",
    "shocked_curiosity": "Intrigued micro-eyebrow raise, naturally parted lips with sudden realization, playful smirk, engaged conversational eye contact.",
    "confident_flex": "Radiant candid laughter, effortless head tilt, relaxed genuine smile, sharp communicative eye gaze.",
    "conversational_talk": "Dynamic lip and jaw articulation naturally synchronized with spoken syllables, candid eye contact, no frozen mouth or plastic grin."
}

CINEMATOGRAPHY_8K_STANDARD = (
    "8K UHD Master, Arri Alexa Mini LF, 35mm prime f/1.8, shallow depth of field with organic bokeh, "
    "visible skin micro-pores and peach fuzz, authentic fabric drape/gravity physics, natural volumetric daylight flares, "
    "zero plastic AI smoothing, zero waxy skin."
)

CAMERA_CHOREOGRAPHY = {
    "unbox_hold": "35mm eye-level Steadicam shot, creator in casual clothes holding and unfolding the garment toward the camera lens, medium close-up",
    "throw_snap": "24mm dynamic whip push-in as cloth is tossed directly toward lens, cutting immediately into full-body vertical 9:16 tracking shot of styled outfit",
    "low_angle_entry": "24mm low-angle fluid tracking push-in, keeping subject centered with shallow depth of field",
    "atrium_stride": "Eye-level smooth Steadicam backward tracking shot, capturing ambient venue light reflections",
    "orbital_twirl": "360-degree dynamic circular orbit tracking shot with low-to-high boom sweep",
    "macro_detail": "85mm macro tilt-up, sharp focus on intricate lace, mirror embroidery, or fabric weave",
    "side_split": "Static side-by-side split screen with crisp match-cut framing (Before vs After)",
    "candid_table": "Eye-level static portrait framing with gentle 2% punch-in zoom during the wink"
}

def get_speed_curve_for_phase(phase: str, visual_mode: str) -> str:
    """Returns appropriate speed curve description for the scene phase."""
    if visual_mode == "fluid_flow":
        return "1.0x Natural Fluid Speed"
    
    p = phase.lower()
    if "unbox" in p or "hath" in p or "hold" in p:
        return SPEED_CURVES["unbox_hold"]
    elif "throw" in p or "snap" in p or "toss" in p:
        return SPEED_CURVES["throw_snap"]
    elif "hook" in p or "beginning" in p or "entry" in p:
        return SPEED_CURVES["fast_entry"]
    elif "twirl" in p or "dance" in p or "slow" in p or "flare" in p:
        return SPEED_CURVES["ultra_slowmo"]
    elif "detail" in p or "hack" in p or "reveal" in p:
        return SPEED_CURVES["detail_zoom"]
    elif "loop" in p or "cta" in p or "ending" in p:
        return SPEED_CURVES["snap_cut"]
    else:
        return SPEED_CURVES["conversational"]

def get_speed_ramp_notation_for_phase(phase: str, visual_mode: str) -> str:
    """Returns exact second-by-second speed ramp notations."""
    if visual_mode == "fluid_flow":
        return "00:00 - 00:04s: 1.0x Natural handheld fluid motion with organic camera glide"
        
    p = phase.lower()
    if "unbox" in p or "hath" in p or "hold" in p:
        return SPEED_RAMP_NOTATIONS["unbox_hold"]
    elif "throw" in p or "snap" in p or "toss" in p:
        return SPEED_RAMP_NOTATIONS["throw_snap"]
    elif "hook" in p or "beginning" in p or "entry" in p:
        return SPEED_RAMP_NOTATIONS["fast_entry"]
    elif "twirl" in p or "dance" in p or "slow" in p or "flare" in p:
        return SPEED_RAMP_NOTATIONS["ultra_slowmo"]
    elif "detail" in p or "hack" in p or "reveal" in p:
        return SPEED_RAMP_NOTATIONS["detail_zoom"]
    elif "loop" in p or "cta" in p or "ending" in p:
        return SPEED_RAMP_NOTATIONS["snap_cut"]
    else:
        return SPEED_RAMP_NOTATIONS["conversational"]

def get_sfx_timeline_for_phase(phase: str) -> str:
    """Returns Foley sound design timeline cues for the phase."""
    p = phase.lower()
    if "unbox" in p or "hath" in p or "hold" in p:
        return SFX_TIMELINE_CUES["unbox_hold"]
    elif "throw" in p or "snap" in p or "toss" in p:
        return SFX_TIMELINE_CUES["throw_snap"]
    elif "hook" in p or "beginning" in p or "entry" in p:
        return SFX_TIMELINE_CUES["fast_entry"]
    elif "twirl" in p or "dance" in p or "slow" in p or "flare" in p:
        return SFX_TIMELINE_CUES["ultra_slowmo"]
    elif "detail" in p or "hack" in p or "reveal" in p:
        return SFX_TIMELINE_CUES["detail_zoom"]
    elif "loop" in p or "cta" in p or "ending" in p:
        return SFX_TIMELINE_CUES["snap_cut"]
    else:
        return SFX_TIMELINE_CUES["conversational"]

def get_micro_expression_for_phase(phase: str, has_dialogue: bool = True) -> str:
    """Returns facial micro-expression directive with Duchenne smile standard."""
    p = phase.lower()
    if has_dialogue:
        if "unbox" in p or "hold" in p or "hath" in p:
            return f"Curious, candid expression in casual wear holding unfolded garment in hands, smiling eyes, natural conversational mouth: {MICRO_EXPRESSIONS['conversational_talk']}"
        elif "throw" in p or "snap" in p:
            return f"Playful, energetic smirk anticipating transformation, crisp eye lock right before match cut."
        elif "hook" in p or "beginning" in p:
            return f"{MICRO_EXPRESSIONS['shocked_curiosity']} {MICRO_EXPRESSIONS['conversational_talk']}"
        elif "reveal" in p or "flex" in p or "payoff" in p:
            return f"{MICRO_EXPRESSIONS['confident_flex']} {MICRO_EXPRESSIONS['duchenne_smile']}"
        else:
            return f"{MICRO_EXPRESSIONS['duchenne_smile']} {MICRO_EXPRESSIONS['conversational_talk']}"
    else:
        if "twirl" in p or "flare" in p:
            return f"{MICRO_EXPRESSIONS['confident_flex']} Radiant closed-mouth Duchenne smile with smiling eyes, zero speech movement."
        else:
            return f"{MICRO_EXPRESSIONS['duchenne_smile']} Warm natural smile with closed lips, zero talking head."

def get_camera_for_phase(phase: str, visual_mode: str) -> str:
    """Returns camera motion instructions based on mode and phase."""
    if visual_mode == "fluid_flow":
        return "Natural steady tracking camera shot with organic handheld fluidity"
        
    p = phase.lower()
    if "unbox" in p or "hath" in p or "hold" in p:
        return CAMERA_CHOREOGRAPHY["unbox_hold"]
    elif "throw" in p or "snap" in p or "toss" in p:
        return CAMERA_CHOREOGRAPHY["throw_snap"]
    elif "hook" in p or "beginning" in p or "entry" in p:
        return CAMERA_CHOREOGRAPHY["low_angle_entry"]
    elif "twirl" in p or "dance" in p:
        return CAMERA_CHOREOGRAPHY["orbital_twirl"]
    elif "detail" in p or "reveal" in p or "hack" in p:
        return CAMERA_CHOREOGRAPHY["macro_detail"]
    elif "loop" in p or "cta" in p or "ending" in p:
        return CAMERA_CHOREOGRAPHY["candid_table"]
    else:
        return CAMERA_CHOREOGRAPHY["atrium_stride"]

