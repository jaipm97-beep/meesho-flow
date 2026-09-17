"""
Streamlit UI for AI Lifestyle Reel Story Director (Phase 2).
Features 3-Column Studio Layout:
- TOP: Action Bar (Save, Approve, Auto-Optimize, Revert, Export JSON)
- TIMELINE: Visual Attention Timeline (Hook, Curiosity, Build, Drop Risk, Reveal, Payoff)
- LEFT: Smart Input & Workflow Modes (Quick, Guided, Pro) + Reality/Fiction Mode
- CENTER: Story Intelligence Blueprint Editor (Goal, Curiosity Question, Open Loop stages, Natural Conflict, Beats, Micro-Events, Payoff)
- RIGHT: Total Attention Scorecard (11 Dimensions), Viewer Mind Simulator, Anti-Boring Diagnostics, 5 Story Angles Explorer, Creator Profile
"""
import streamlit as st
import datetime
from typing import Optional
from dataclasses import asdict
from ..models.project import UserInput, ExecutionMode, StoryMode, ProjectState, ApprovalStatus, StoryApproach
from ..models.blueprint import StoryBlueprint, StoryBeat
from ..models.attention import AttentionAnalysis, AttentionScore
from ..models.creator import CreatorProfile
from ..core.director import CreativeDirector
from ..storage.project_store import ProjectStore
from visual_attention_engine import render_studio_visual_attention_banner, render_section_why_watch_next_summary

def convert_blueprint_to_9tab_package(proj: ProjectState) -> str:
    """Converts Phase 2 Blueprint into complete 9-Tab Production Suite format with strict CREATOR_REFERENCE photo locks."""
    bp = StoryBlueprint.from_dict(proj.story_blueprint) if proj.story_blueprint else None
    att = AttentionAnalysis.from_dict(proj.attention_analysis) if proj.attention_analysis else None
    cr = CreatorProfile.from_dict(proj.creator_profile) if proj.creator_profile else None
    if not bp:
        return ""

    base_loc = proj.user_input.location or (proj.ai_suggestions.location if proj.ai_suggestions and proj.ai_suggestions.location else "Luxury Indian Mall & Promenade")
    base_veh = proj.user_input.vehicle or (proj.ai_suggestions.vehicle_or_prop if proj.ai_suggestions and proj.ai_suggestions.vehicle_or_prop else "Matte Black Luxury Sports Coupe")
    cr_name = cr.name if cr and cr.name else "Aria"
    cr_outfit = cr.outfit if cr and cr.outfit else "Western chic luxury tailored outfit"

    is_shopping_story = any(k in (str(proj.user_input.idea) + " " + str(bp.concept) + " " + str(base_loc)).lower() for k in ["boutique", "shop", "mall", "store", "dress", "outfit", "gown", "bkc", "fairytale"])
    
    beats_md = ""
    prompts_md = ""
    dialogues_md = ""
    sfx_full_timeline = ""
    for b in bp.beats:
        spoken = f'"{b.spoken_hint}"' if b.spoken_hint else '(Ambient sound / BGM)'
        curr_action = b.narrative_action
        curr_visual = b.visual_moment
        curr_garment = f"{cr_outfit}. Tailored luxury drape, authentic fabric texture and rich color matching scene lighting."
        curr_why = f"{b.why_keep_watching} (Rating: {b.keep_watching_rating})"
        
        # Calculate distinct, photorealistic venue for each scene
        if b.beat_index == 1:
            scene_venue = f"{base_loc} (Driveway & Valet Arrival exterior next to {base_veh})"
            speed_ramp = "00:00 - 00:01s: 1.0x Normal entry ➔ 00:01 - 00:02.5s: 0.4x Slow-mo 120fps glide ➔ 00:02.5 - 00:03s: 1.3x Snap transition"
            sfx_cue = "00:00.2s: Sub-bass car door thud | 00:01.3s: Stiletto clicks on high-gloss marble | -8dB BGM ducking during dialogue"
            duchenne_expr = "Confident high-status entry, authentic Duchenne smiling eyes crinkling, candid lips greeting lens naturally, no frozen mouth."
        elif b.beat_index == 2:
            scene_venue = f"{base_loc} (Grand High-Street Atrium & Marble Columns)"
            speed_ramp = "00:00 - 00:04s: 1.0x Steadicam backward glide with continuous conversational pacing"
            sfx_cue = "00:00.5s: Grand mall atrium acoustics & faint chatter | 00:02.1s: Designer handbag chain clink | -8dB BGM ducking during dialogue"
            duchenne_expr = "Intrigued storytelling gaze, micro-eyebrow raise discovering unexpected boutique display, animated speech articulation matching words."
        elif b.beat_index == 3:
            if is_shopping_story:
                scene_venue = f"{base_loc} (Exclusive Flagship Boutique VIP Fitting Suite & Arched Mirror Gallery)"
                speed_ramp = "00:00 - 00:01s: 1.2x Entrance push-in ➔ 00:01 - 00:03.5s: 0.4x Ultra Slow-Motion 120fps 360° twirl ➔ 00:03.5 - 00:05s: 1.0x Mirror fit admire"
                sfx_cue = "00:00.3s: Velvet trial curtain glide | 00:01.2s: Heavy sub-bass 808 drop on dress reveal | 00:02.5s: Liquid silk fabric swish flutter | -8dB BGM ducking"
                duchenne_expr = "Stunned delight, genuine laughter parting lips, admiring reflection in mirror with natural head tilt and authentic eye crinkles, lively conversational speech."
                curr_action = f"Match-cut reveal inside the luxury VIP fitting salon! {cr_name} pulls back the emerald velvet curtain, now WEARING an exquisite Emerald Green cowl-neck backless silk slip gown with delicate criss-cross straps and a fluid floor-length drape. She executes a breathtaking 360° slow-motion twirl in front of the grand arched gilded floor mirror, admiring the snatched silhouette with radiant Duchenne smiling eyes!"
                curr_visual = "Arched full-length mirror orbital pan, rich warm accent lighting, 0.4x slow-mo 120fps silk twirl capturing fluid drape and back silhouette."
                spoken = '"Maine bas dekhne ke liye try kiya tha... but look at this fit! I am NEVER taking this off! 😭💚✨"'
                curr_garment = "NEW TRIED-ON OUTFIT: Liquid-silk cowl-neck slip gown in deep jewel-toned Emerald Green, delicate criss-cross back straps, bias-cut snatched waistline with flowing floor-length hemline drape."
                curr_why = "Jaw-dropping live try-on transformation payoff in the mirror (Rating: Viral Peak 🔥)"
            else:
                scene_venue = f"{base_loc} (Exclusive Flagship Boutique & Private Showcase)"
                speed_ramp = "00:00 - 00:01s: 1.2x Push-in ➔ 00:01 - 00:03s: 0.5x Slow-motion 120fps fabric inspection ➔ 00:03 - 00:04s: 1.0x Reset"
                sfx_cue = "00:00.8s: Velvet curtain pull & luxury boutique register chime | 00:02.2s: Fabric glide across satin hanger | -8dB BGM ducking"
                duchenne_expr = "Stunned delight, genuine laughter parting lips, playful shoulder shrug admiring mirror fit reflection, authentic eye crinkles."
        elif b.beat_index == 4:
            scene_venue = f"{base_loc} (Sunlit Outdoor Terrace Café & Lounge)"
            speed_ramp = "00:00 - 00:00.8s: 1.0x ➔ 00:00.8 - 00:03.2s: 0.35x Ultra slow-motion optical flow showing 360° fabric flare ➔ 00:03.2 - 00:04s: 1.2x Catch"
            sfx_cue = "00:00.4s: Terrace café espresso cup clinking porcelain saucer | 00:01.8s: Gentle afternoon breeze whisper | -8dB BGM ducking"
            duchenne_expr = "Serene luxury aesthetic smile, warm direct eye contact over espresso cup, conversational warmth, glowing smiling eyes."
        else:
            scene_venue = f"{base_loc} (Panoramic Sunset Promenade & Golden Hour Skyline)"
            speed_ramp = "00:00 - 00:02.5s: 1.0x Confident flex pose ➔ 00:02.5 - 00:03s: 2.0x High-speed snap whip loop cut back to Scene 1"
            sfx_cue = "00:01.5s: Sunset rooftop ambient lounge music swell | 00:02.8s: Bass beat impact for seamless rewatch loop"
            duchenne_expr = "Radiant triumphant Duchenne smile, subtle playful wink, effortlessly transitioning into loop bookmark pose."

        beats_md += f"""#### SCENE {b.beat_index}: {b.phase.upper()} [{b.timestamp_range}]
* **Visual Action**: {curr_action}
* **Cinematography & Camera**: {curr_visual}
* **Speed Ramping**: {speed_ramp}
* **Facial Micro-Expressions**: {duchenne_expr}
* **Foley Sound Timeline**: {sfx_cue}
* **Dialogue / Spoken Line**: {spoken}
* **Viewer Retention Factor**: {curr_why}

"""
        sfx_full_timeline += f"* **Scene {b.beat_index} [{b.timestamp_range}]**: {sfx_cue}\n"

        # Build production-ready Google Flow / Kling AI prompt with 100% CREATOR_REFERENCE photo lock & 14-Point Master Lock
        prompts_md += f"""```text
SCENE {b.beat_index} — {b.phase.upper()} [{b.timestamp_range}]
Voice-over:
{spoken}

Visual Action:
Vertical 9:16 {curr_visual}. A stylish 24-year-old Indian woman (CREATOR_REFERENCE / Image 1: exact facial features, dark hair, natural warm Indian skin tone, and authentic body proportions from the uploaded creator reference photo) {curr_action}. High aesthetic quality, sharp focus, 8K 60fps photorealistic cinematic commercial ad.

8K UHD Cinematography Standard:
Master shot on Arri Alexa Mini LF, 35mm prime f/1.8 lens, shallow depth of field with organic bokeh. 8K UHD clarity, authentic skin micro-pores and subtle peach fuzz, authentic fabric drape/gravity physics, natural volumetric daylight flares, zero AI plastic smoothing, zero waxy skin.

Facial Micro-Expressions & Duchenne Smile:
{duchenne_expr} Natural mouth and jaw articulation naturally synchronized with spoken syllables when talking. Subtle candid head movement, eliminating any frozen, waxy, or fake plastic mouth expressions.

Camera Motion & Speed Ramping:
[Speed Ramp: {speed_ramp}]. Lens: 24mm-35mm dynamic tracking push-in with fluid Steadicam stabilization, capturing natural venue lighting.

Synchronized SFX Timeline:
[Foley Cues: {sfx_cue}].

Subject & Character Lock:
CREATOR_REFERENCE (Image 1). 100% facial and physical identity consistency with the attached creator reference photo (Image 1). Use exact eyes, smile, cheekbones, dark hair, natural Indian skin undertone, and body silhouette from the reference photo. Do NOT generate a generic face; preserve the exact woman from Image 1 across all scenes.

Background Isolation Lock:
STRICTLY DISCARD and IGNORE the original background, room, bedroom, or home interior from CREATOR_REFERENCE photo. Extract ONLY the human creator subject. Place creator exclusively inside: {scene_venue}.

Garment Lock:
{curr_garment}

Lip Delivery:
Natural speech articulation. Lips actively move in sync with spoken dialogue: {spoken}.

Duration:
{b.suggested_duration_sec} seconds.

Avoid / Negative Prompt:
original photo background, background bleed from CREATOR_REFERENCE photo, bedroom backdrop, domestic home interior, repeating static room, altered facial identity, generic model face, face swap distortion, waxy skin, plastic skin smoothing, frozen mouth smile, sliding feet, floating heels, third leg, extra limbs, blurry, low resolution, glitch.
```

"""
        if b.spoken_hint:
            dialogues_md += f"""* **Scene {b.beat_index} [{b.timestamp_range}]**: "{b.spoken_hint}"\n"""

    pkg = f"""# 🎬 COMPLETE LIFESTYLE VLOG PRODUCTION PACKAGE & GOOGLE FLOW PROMPTS

## 📖 TAB 1 — STORY & CURIOSITY BLUEPRINT
* **Story Title**: {bp.title}
* **Logline & Story Summary**: {bp.concept}
* **Fictional Disclosure**: ℹ️ **Mode**: {proj.user_input.story_mode.value}
* **Story Goal**: {bp.story_goal}
* **Main Curiosity Question**: {bp.main_curiosity_question}
* **Open Loop**: {bp.open_loop}
* **Natural Conflict**: {bp.natural_conflict}

### Narrative Arc
* **Beginning**: {bp.beginning}
* **Development**: {bp.development}
* **Surprise**: {bp.surprise}
* **Payoff**: {bp.payoff}
* **Ending**: {bp.ending}
* **Rewatch / Loop Potential**: {bp.rewatch_potential}

---

## 📝 TAB 2 — FINAL SCRIPT & SCENE-BY-SCENE BREAKDOWN
{beats_md}

---

## 🎥 TAB 3 — VISUAL SHOT LIST & CAMERA SPEED RAMPING DIRECTIVES
* **Total Scenes**: {len(bp.beats)}
* **Cinematography Standard**: 8K UHD, Arri Alexa Mini LF, 35mm Prime f/1.8, Shallow Depth of Field
* **Speed Ramping Matrix**: 1.0x Normal Entrance ➔ 0.4x Slow-Mo 120fps Glide ➔ 1.5x/2.0x Snap Cut Loop
* **Framing**: Vertical 9:16 Ultra-Photorealistic Cinematic

---

## 🤖 TAB 4 — GOOGLE FLOW & KLING AI VIDEO PROMPTS (8K & 14-POINT MASTER LOCK)
{prompts_md}

---

## 🎙️ TAB 5 — VOICE-OVER & AUDIO NARRATION
### 🎙️ MASTER CONTINUOUS VOICE-OVER SCRIPT (1-TAKE RECORDING)
> "{' '.join([b.spoken_hint for b in bp.beats if b.spoken_hint]) if any(b.spoken_hint for b in bp.beats) else bp.concept}"

### 💬 Scene-by-Scene Spoken Dialogue Lines:
{dialogues_md if dialogues_md else '* Pure visual storytelling with ambient audio and soundtrack.'}

---

## ✍️ TAB 6 — ON-SCREEN TEXT & CAPTION OVERLAYS
* **00:00 - 00:03**: ⚡ "{bp.main_curiosity_question}"
* **Payoff Scene**: 🔥 "{bp.surprise}"

---

## 🎵 TAB 7 — SOUND DESIGN & FOLEY TIMELINE
* **Music Genre**: Modern Luxury Chill Hop / Ambient Electro (110-120 BPM)
* **Audio Ducking**: -8dB Background Music Ducking during all spoken dialogue lines
* **Second-by-Second Foley Timeline**:
{sfx_full_timeline}

---

## 🏷️ TAB 8 — INSTAGRAM SEO & VIRAL HASHTAGS
* **Caption**: {bp.title} ✨ Comment "STYLE" for direct links! 👇
* **Hashtags**: #LifestyleVlog #LuxuryReels #ReelsIndia #OOTD #ViralReel #8KCinematic

---

## 📊 TAB 9 — RETENTION SCORECARD & REWATCH POTENTIAL
* **Overall Retention Potential**: {att.overall_score if att else 95.0} / 100
* **Curiosity Strength**: {att.score.curiosity if att else 96} / 100
* **Pacing & Speed Ramping**: {att.score.pacing if att else 95} / 100
* **Surprise Factor**: {att.score.surprise if att else 96} / 100
* **Payoff Satisfaction**: {att.score.payoff if att else 95} / 100
* **Rewatch / Loop Potential**: {att.score.rewatch_potential if att else 95} / 100
"""
    return pkg


def render_lifestyle_story_director(env_api_key: Optional[str] = None):
    """Renders the comprehensive Phase 2 Story Intelligence UI of AI Lifestyle Reel Story Director."""
    
    # 1. State Initialization
    if "life_director" not in st.session_state:
        st.session_state["life_director"] = CreativeDirector(api_key=env_api_key)
    director: CreativeDirector = st.session_state["life_director"]
    if env_api_key:
        director.set_api_key(env_api_key)

    if "current_life_project" not in st.session_state:
        default_input = UserInput(
            idea="आज मैं luxury sports car से exclusive mall में shopping करने गई और boutique में एक unexpected surprise mila.",
            duration="30s",
            language="Hinglish",
            story_mode=StoryMode.FICTIONAL,
            style="Luxury Lifestyle",
            voiceover_enabled=True,
            execution_mode=ExecutionMode.QUICK
        )
        st.session_state["current_life_project"] = director.process_idea(default_input)

    proj: ProjectState = st.session_state["current_life_project"]
    blueprint = StoryBlueprint.from_dict(proj.story_blueprint) if proj.story_blueprint else None
    attention = AttentionAnalysis.from_dict(proj.attention_analysis) if proj.attention_analysis else None
    creator = CreatorProfile.from_dict(proj.creator_profile) if proj.creator_profile else None
    sug = proj.ai_suggestions

    # ---------------------------------------------------------
    # TOP HEADER & ACTION BAR
    # ---------------------------------------------------------
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%); padding: 1.4rem 1.8rem; border-radius: 14px; border: 1px solid rgba(244, 114, 182, 0.25); margin-bottom: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem;">
            <div>
                <div style="display:flex; align-items:center; gap:0.6rem;">
                    <span style="font-size:1.4rem;">🎬</span>
                    <h2 style="margin:0; color:#f8fafc; font-weight:800; font-size:1.4rem; letter-spacing:-0.02em;">
                        AI Lifestyle Reel Story Director
                    </h2>
                    <span style="background:linear-gradient(90deg, #ec4899, #8b5cf6); color:white; font-size:0.7rem; font-weight:700; padding:0.18rem 0.6rem; border-radius:999px; text-transform:uppercase; letter-spacing:0.05em;">
                        Phase 2 Story Intelligence
                    </span>
                </div>
                <p style="margin:0.35rem 0 0 0; color:#cbd5e1; font-size:0.88rem;">
                    Story Intelligence Engine • Viewer Mind Simulator • Predictive Pre-Drop Detection • Total Attention Architecture
                </p>
            </div>
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span style="color:#94a3b8; font-size:0.82rem;">Status:</span>
                <span style="background:""" + ('#10b981' if proj.approval_status == ApprovalStatus.APPROVED else '#f59e0b') + """; color:white; font-weight:700; font-size:0.75rem; padding:0.2rem 0.6rem; border-radius:6px;">
                    """ + proj.approval_status.value.upper() + """
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    life_va_mode = render_studio_visual_attention_banner("AI Lifestyle Reel Story Director", key_prefix="life_director_ui_va")

    # Top Action Row
    col_act1, col_act2, col_act3, col_act4, col_act5, col_act6 = st.columns([2.0, 0.9, 1.1, 1.1, 1.1, 1.0])
    with col_act1:
        new_proj_name = st.text_input("Project Name", value=proj.project_name, key="life_top_proj_name", label_visibility="collapsed")
        if new_proj_name != proj.project_name:
            proj.project_name = new_proj_name
            proj.touch()

    with col_act2:
        if st.button("💾 Save", use_container_width=True, key="life_btn_save_top"):
            path = ProjectStore.save_project(proj)
            st.toast("Project saved successfully!", icon="💾")

    with col_act3:
        if st.button("✅ Approve", type="primary" if proj.approval_status != ApprovalStatus.APPROVED else "secondary", use_container_width=True, key="life_btn_approve_top"):
            director.approve_blueprint(proj)
            ProjectStore.save_project(proj)
            st.toast("🎉 Story Blueprint Approved!", icon="✅")
            st.rerun()

    with col_act4:
        if st.button("⚡ Auto-Optimize", use_container_width=True, key="life_btn_opt_top", help="Executes up to 3 automatic optimization rounds to eliminate weak retention spots."):
            with st.spinner("Simulating viewer psychology and auto-optimizing story beats..."):
                director.auto_optimize_story(proj, max_rounds=3)
                ProjectStore.save_project(proj)
                st.toast(f"Auto-Optimization complete! Current score: {proj.attention_analysis.get('overall_score', 95)}/100", icon="⚡")
                st.rerun()

    with col_act5:
        if proj.original_story_blueprint and st.button("🔄 Use Original", use_container_width=True, key="life_btn_revert_top", help="Revert to original blueprint before auto-optimization"):
            director.revert_to_original(proj)
            st.toast("Reverted to original blueprint!", icon="🔄")
            st.rerun()
        else:
            if st.button("✨ Improve Story", use_container_width=True, key="life_btn_improve_top"):
                with st.spinner("Elevating narrative rhythm..."):
                    director.regenerate_blueprint(proj, "improve")
                    st.toast("Story Blueprint elevated!", icon="✨")
                    st.rerun()

    with col_act6:
        json_export_str = ProjectStore.export_as_json_string(proj)
        st.download_button(
            "📥 Export JSON",
            data=json_export_str,
            file_name=f"{proj.project_id}_blueprint.json",
            mime="application/json",
            use_container_width=True,
            key="life_btn_export_json_top"
        )

    # ---------------------------------------------------------
    # VISUAL ATTENTION TIMELINE (Interactive Strip)
    # ---------------------------------------------------------
    if attention and attention.timeline:
        st.markdown("##### ⏱️ Visual Attention Timeline & Drop-Risk Predictor:")
        t_cols = st.columns(len(attention.timeline))
        for i, t in enumerate(attention.timeline):
            with t_cols[i]:
                is_drop = "DROP" in t.attention_level
                bg_color = "rgba(239, 68, 68, 0.15)" if is_drop else "rgba(16, 185, 129, 0.12)"
                border_color = "#ef4444" if is_drop else "#10b981"
                st.markdown(f"""
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:8px; padding:0.45rem; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#94a3b8;">{t.timestamp_range}</div>
                    <div style="font-size:0.85rem; font-weight:800; margin:0.2rem 0;">{t.attention_level}</div>
                    <div style="font-size:0.72rem; color:#cbd5e1;">Retention: <b>{t.predicted_retention_pct}%</b></div>
                </div>
                """, unsafe_allow_html=True)
                if t.pre_drop_warning:
                    st.caption(f"⚠️ {t.pre_drop_warning}")
                    st.caption(f"💡 Fix: {t.proactive_fix}")

    st.markdown("---")

    # ---------------------------------------------------------
    # 3-COLUMN WORKSPACE: LEFT (INPUT) | CENTER (BLUEPRINT) | RIGHT (ATTENTION)
    # ---------------------------------------------------------
    col_left, col_center, col_right = st.columns([1.1, 1.3, 1.1], gap="medium")

    # =========================================================
    # LEFT COLUMN: SMART INPUT & CONTROLS
    # =========================================================
    with col_left:
        st.markdown("### 1️⃣ Smart Input & Controls")

        # Mode Selector: Quick / Guided / Pro
        exec_mode = st.radio(
            "Workflow Mode",
            ["⚡ Quick Mode", "🧭 Guided Mode", "🛠️ Pro Mode"],
            index=0 if proj.user_input.execution_mode == ExecutionMode.QUICK else (1 if proj.user_input.execution_mode == ExecutionMode.GUIDED else 2),
            horizontal=True,
            key="life_exec_mode_radio"
        )
        current_em = ExecutionMode.QUICK if "Quick" in exec_mode else (ExecutionMode.GUIDED if "Guided" in exec_mode else ExecutionMode.PRO)
        if current_em != proj.user_input.execution_mode:
            proj.user_input.execution_mode = current_em
            proj.touch()

        # Reality / Fictional / Hybrid Mode
        story_mode_choice = st.radio(
            "🎯 Content Reality Mode",
            [
                "✨ Fictional / AI-Generated Mode (Default)",
                "📸 Real-Life Mode (Strict Authenticity)",
                "🔀 Hybrid Mode (Real Base + Cinematic Flair)"
            ],
            index=0 if proj.user_input.story_mode == StoryMode.FICTIONAL else (1 if proj.user_input.story_mode == StoryMode.REAL_LIFE else 2),
            key="life_story_mode_radio",
            help="Fictional mode mandates entertainment disclosure. Real-Life preserves user facts truthfully."
        )
        selected_sm = StoryMode.FICTIONAL if "Fictional" in story_mode_choice else (StoryMode.REAL_LIFE if "Real-Life" in story_mode_choice else StoryMode.HYBRID)
        if selected_sm != proj.user_input.story_mode:
            proj.user_input.story_mode = selected_sm
            proj.touch()

        # Smart Input Text Area
        new_idea = st.text_area(
            "✍️ Reel Story Idea / Premise",
            value=proj.user_input.idea,
            height=110,
            key="life_user_idea_input",
            help="Enter your core premise (e.g., 'Going to mall in sports car and finding an unreleased ₹499 dupe')."
        )
        if new_idea != proj.user_input.idea:
            proj.user_input.idea = new_idea
            proj.user_input.mark_user_provided("idea")
            proj.touch()

        # Basic Settings (Quick Mode)
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            new_dur = st.selectbox(
                "⏱️ Duration",
                ["15 sec", "30 sec", "60 sec"],
                index=0 if "15" in proj.user_input.duration or "10" in proj.user_input.duration else (2 if "60" in proj.user_input.duration else 1),
                key="life_dur_select"
            )
            if new_dur != proj.user_input.duration:
                proj.user_input.duration = new_dur
                proj.user_input.mark_user_provided("duration")
                proj.touch()

        with col_q2:
            new_lang = st.selectbox(
                "🗣️ Language",
                ["Hinglish", "Hindi", "English"],
                index=0 if proj.user_input.language == "Hinglish" else (1 if proj.user_input.language == "Hindi" else 2),
                key="life_lang_select"
            )
            if new_lang != proj.user_input.language:
                proj.user_input.language = new_lang
                proj.user_input.mark_user_provided("language")
                proj.touch()

        new_vo = st.toggle("🎙️ Voice-Over Narration Enabled", value=proj.user_input.voiceover_enabled, key="life_vo_toggle")
        if new_vo != proj.user_input.voiceover_enabled:
            proj.user_input.voiceover_enabled = new_vo
            proj.touch()

        # Guided / Pro Mode Controls
        if current_em in (ExecutionMode.GUIDED, ExecutionMode.PRO):
            st.markdown("---")
            st.markdown("##### 🧭 Guided Context Attributes")
            g_loc = st.text_input("📍 Setting / Location", value=proj.user_input.location or (sug.location if sug else ""), key="life_guid_loc")
            if g_loc != proj.user_input.location:
                proj.user_input.location = g_loc
                proj.user_input.mark_user_provided("location")

            g_veh = st.text_input("🚗 Vehicle / Luxury Prop", value=proj.user_input.vehicle or (sug.vehicle_or_prop if sug else ""), key="life_guid_veh")
            if g_veh != proj.user_input.vehicle:
                proj.user_input.vehicle = g_veh
                proj.user_input.mark_user_provided("vehicle")

            g_style = st.selectbox(
                "🎨 Story Style",
                ["Luxury Lifestyle", "Daily Lifestyle", "Shopping Spree", "Travel & Airports", "Café Aesthetic", "Fashion & Styling"],
                index=0,
                key="life_guid_style"
            )
            if g_style != proj.user_input.style:
                proj.user_input.style = g_style
                proj.user_input.mark_user_provided("style")

        if current_em == ExecutionMode.PRO:
            st.markdown("---")
            st.markdown("##### 🛠️ Pro Precision Controls")
            p_goal = st.text_input("🎯 Specific Story Goal", value=proj.user_input.story_goal, key="life_pro_goal", placeholder="e.g. Hunting down an unreleased gala gown")
            if p_goal != proj.user_input.story_goal:
                proj.user_input.story_goal = p_goal
                proj.user_input.mark_user_provided("story_goal")

            col_p_c1, col_p_c2 = st.columns(2)
            with col_p_c1:
                p_cur = st.selectbox("Curiosity Tension", ["High (Maximum Mystery)", "Medium (Balanced)", "Subtle"], index=0, key="life_pro_cur")
                proj.user_input.curiosity_level = p_cur
            with col_p_c2:
                p_pac = st.selectbox("Pacing Engine", ["Fast & Punchy", "Adaptive Dynamic", "Cinematic Atmospheric"], index=1, key="life_pro_pac")
                proj.user_input.pacing = p_pac

        # Generate / Re-generate Button
        if st.button("🚀 Generate Story Blueprint", type="primary", use_container_width=True, key="btn_gen_blueprint_main"):
            with st.spinner("AI Creative Director synthesizing narrative intelligence..."):
                updated_proj = director.process_idea(proj.user_input, project_id=proj.project_id)
                st.session_state["current_life_project"] = updated_proj
                ProjectStore.save_project(updated_proj)
                st.toast("✨ Story Blueprint synthesized!", icon="🚀")
                st.rerun()

    # =========================================================
    # CENTER COLUMN: STORY INTELLIGENCE BLUEPRINT LIVE EDITOR
    # =========================================================
    with col_center:
        st.markdown("### 2️⃣ Story Blueprint Live Editor")

        if blueprint:
            st.caption(f"Disclosure: {blueprint.mode_disclosure}")

            # Editable Title & Concept
            blueprint.title = st.text_input("Story Title", value=blueprint.title, key="bp_title_input")
            blueprint.concept = st.text_area("Logline & Concept", value=blueprint.concept, height=65, key="bp_concept_input")

            # Story Goal & Natural Conflict
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                blueprint.story_goal = st.text_input("🎯 Story Goal", value=blueprint.story_goal, key="bp_goal_input")
            with col_g2:
                blueprint.natural_conflict = st.text_input("⚡ Natural Conflict / Obstacle", value=blueprint.natural_conflict, key="bp_conflict_input")

            # Main Curiosity Question & Open Loop
            blueprint.main_curiosity_question = st.text_input("❓ Main Curiosity Question", value=blueprint.main_curiosity_question, key="bp_curiosity_input")
            blueprint.open_loop = st.text_input("🔓 Open Loop Suspense", value=blueprint.open_loop, key="bp_openloop_input")

            # Open Loop Stages Expander
            if blueprint.open_loop_stages:
                with st.expander("🔍 Open Loop 4-Stage Breakdown", expanded=False):
                    for stage, desc in blueprint.open_loop_stages.items():
                        st.markdown(f"**{stage}**: {desc}")

            # 4-Phase Narrative Arc
            arc_tabs = st.tabs(["Beginning", "Development", "Surprise", "Payoff & Loop"])
            with arc_tabs[0]:
                blueprint.beginning = st.text_area("Beginning Hook", value=blueprint.beginning, height=65, key="bp_beg_input")
            with arc_tabs[1]:
                blueprint.development = st.text_area("Development & Conflict", value=blueprint.development, height=65, key="bp_dev_input")
            with arc_tabs[2]:
                blueprint.surprise = st.text_area("Surprise Discovery", value=blueprint.surprise, height=65, key="bp_sur_input")
            with arc_tabs[3]:
                blueprint.payoff = st.text_area("Payoff Resolution", value=blueprint.payoff, height=65, key="bp_pay_input")
                blueprint.ending = st.text_input("Ending & Loop", value=blueprint.ending, key="bp_end_input")

            # Scene Beats List
            st.markdown("##### 🎬 Story Beats Breakdown")
            for i, beat in enumerate(blueprint.beats):
                icon = "🔥" if beat.keep_watching_rating == "Strong" else ("⚠️" if beat.keep_watching_rating == "Weak" else "🟢")
                with st.expander(f"{icon} Beat #{beat.beat_index} [{beat.timestamp_range}] — {beat.phase}", expanded=(i == 0)):
                    st.markdown(f"**Visual Moment**: {beat.visual_moment}")
                    st.markdown(f"**Action**: {beat.narrative_action}")
                    if beat.micro_event:
                        st.markdown(f"⚡ **Micro-Event**: `{beat.micro_event}`")
                    if beat.spoken_hint:
                        st.markdown(f"🎙️ *Spoken Line*: \"{beat.spoken_hint}\"")
                    st.markdown(f"👁️ **Why keep watching?**: `{beat.why_keep_watching}` *(Rating: {beat.keep_watching_rating})*")

            # Save Edits and Bridge to 9-Tab Suite
            col_bp_btn1, col_bp_btn2 = st.columns([1, 1])
            with col_bp_btn1:
                if st.button("💾 Apply & Save Blueprint", use_container_width=True, key="btn_apply_bp_edits"):
                    proj.story_blueprint = blueprint.to_dict()
                    proj.touch()
                    ProjectStore.save_project(proj)
                    st.toast("Blueprint edits saved!", icon="✅")
            with col_bp_btn2:
                if st.button("🚀 Push to 9-Tab Suite", use_container_width=True, key="btn_push_to_9tab"):
                    proj.story_blueprint = blueprint.to_dict()
                    proj.touch()
                    ProjectStore.save_project(proj)
                    st.session_state["latest_lifestyle_package"] = convert_blueprint_to_9tab_package(proj)
                    st.session_state["lifestyle_active_subtab_selector"] = "🎬 Full 9-Tab Production Suite & Google Flow Prompts"
                    st.session_state["life_idea_input"] = blueprint.concept
                    st.toast("Transferred to 9-Tab Production Suite!", icon="🚀")
                    st.rerun()

            # 9 Regeneration Flavor Buttons
            st.markdown("---")
            st.markdown("##### 🔄 Targeted Regeneration Flavors:")
            r_c1, r_c2, r_c3 = st.columns(3)
            with r_c1:
                if st.button("🔥 More Curiosity", use_container_width=True, key="rf_curiosity"):
                    director.regenerate_blueprint(proj, "curiosity")
                    st.rerun()
                if st.button("🌿 More Natural", use_container_width=True, key="rf_natural"):
                    director.regenerate_blueprint(proj, "natural")
                    st.rerun()
                if st.button("⚡ Faster Pacing", use_container_width=True, key="rf_pacing"):
                    director.regenerate_blueprint(proj, "pacing")
                    st.rerun()
            with r_c2:
                if st.button("🎬 More Cinematic", use_container_width=True, key="rf_cinematic"):
                    director.regenerate_blueprint(proj, "cinematic")
                    st.rerun()
                if st.button("💎 Ultra Luxury", use_container_width=True, key="rf_luxury"):
                    director.regenerate_blueprint(proj, "luxury")
                    st.rerun()
                if st.button("💖 More Emotional", use_container_width=True, key="rf_emotional"):
                    director.regenerate_blueprint(proj, "emotional")
                    st.rerun()
            with r_c3:
                if st.button("🪝 Stronger Hook", use_container_width=True, key="rf_hook"):
                    director.regenerate_blueprint(proj, "hook")
                    st.rerun()
                if st.button("✨ General Polish", use_container_width=True, key="rf_improve"):
                    director.regenerate_blueprint(proj, "improve")
                    st.rerun()
                if st.button("🔄 Fresh Angle", use_container_width=True, key="rf_refresh"):
                    director.regenerate_blueprint(proj, "refresh")
                    st.rerun()

    # =========================================================
    # RIGHT COLUMN: TOTAL ATTENTION & RETENTION INTELLIGENCE
    # =========================================================
    with col_right:
        st.markdown("### 3️⃣ Total Attention & Intelligence")

        right_tabs = st.tabs([
            "📊 Attention",
            "🧠 Viewer Mind",
            "⚡ Optimization",
            "🎭 5 Angles",
            "👤 Creator"
        ])

        with right_tabs[0]:
            if attention:
                score = attention.score
                st.metric(
                    label="🎯 Overall Attention Potential Score",
                    value=f"{score.overall_attention_potential} / 100",
                    delta=score.label
                )
                st.caption("ℹ️ AI quality estimate based on narrative velocity and tension (not viral guarantee).")

                # 11 Attention Dimensions
                st.markdown("##### 📈 11 Retention Dimensions:")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"🪝 Hook: **{score.hook}/100**")
                    st.write(f"❓ Curiosity: **{score.curiosity}/100**")
                    st.write(f"👁️ Visual: **{score.visual_potential}/100**")
                    st.write(f"📜 Story: **{score.story_progression}/100**")
                    st.write(f"💖 Emotion: **{score.emotion}/100**")
                    st.write(f"🎙️ Audio: **{score.audio_potential}/100**")
                with col_d2:
                    st.write(f"✍️ Text: **{score.text_potential}/100**")
                    st.write(f"⚡ Pacing: **{score.pacing}/100**")
                    st.write(f"🎁 Surprise: **{score.surprise}/100**")
                    st.write(f"🏆 Payoff: **{score.payoff}/100**")
                    st.write(f"🔁 Rewatch: **{score.rewatch_potential}/100**")

                if attention.report:
                    st.markdown("---")
                    st.markdown("##### 📑 Diagnostic Report:")
                    rep = attention.report
                    st.write(f"🌟 **Strongest Moment**: {rep.strongest_moment}")
                    st.write(f"⚠️ **Weakest Moment**: {rep.weakest_moment}")
                    st.write(f"📉 **Attention Drop Risk**: `{rep.attention_drop_risk}`")
                    st.markdown("**Top 3 Improvements:**")
                    for tip in rep.top_3_improvements:
                        st.markdown(f"- {tip}")

        with right_tabs[1]:
            mind = proj.viewer_mind_analysis or (director.viewer_mind.simulate_full_story(blueprint) if blueprint else None)
            if mind:
                st.markdown("##### 🧠 Subconscious Viewer Psychology:")
                st.caption(mind.get("viewer_takeaway", "Simulation complete."))
                for b_sim in mind.get("beat_simulations", []):
                    icon = "🔥" if b_sim["keep_watching_rating"] == "Strong" else "⚠️"
                    with st.expander(f"{icon} Beat #{b_sim['beat_index']} ({b_sim['phase']})", expanded=False):
                        st.markdown(f"**Viewer Knows**: {b_sim['viewer_knows']}")
                        st.markdown(f"**Viewer Wonders**: *\"{b_sim['subconscious_question']}\"*")
                        st.markdown(f"**Expects Next**: {b_sim['expects_next']}")
                        st.markdown(f"**Boredom Risk**: `{'YES (Attention Leak)' if b_sim['boredom_risk'] else 'None'}`")
                        if b_sim["keep_watching_fix"]:
                            st.warning(f"Fix: {b_sim['keep_watching_fix']}")

        with right_tabs[2]:
            st.markdown("##### ⚡ Automatic Optimization Engine")
            st.caption("Runs up to 3 automatic optimization rounds to eliminate weak retention spots:")
            if st.button("🚀 Run 3-Round Auto-Optimization", type="primary", use_container_width=True, key="btn_run_3_rounds"):
                with st.spinner("Optimizing story blueprint across 3 iterative rounds..."):
                    director.auto_optimize_story(proj, max_rounds=3)
                    ProjectStore.save_project(proj)
                    st.toast("Optimization completed!", icon="⚡")
                    st.rerun()

            if proj.optimization_history:
                st.markdown("###### 📜 Optimization Rounds History:")
                for r in proj.optimization_history:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.04); border-left:3px solid #10b981; padding:0.4rem 0.6rem; margin-bottom:0.4rem; font-size:0.8rem;">
                        <b>Round #{r['round_number']}</b>: {r['changed_section']}<br>
                        <span style="color:#94a3b8;">Score: {r['old_score']} ➔ <b>{r['new_score']}</b></span><br>
                        <i>{r['change_summary']}</i>
                    </div>
                    """, unsafe_allow_html=True)

            audit = proj.anti_boring_audit or (director.run_anti_boring_scan(proj))
            if audit:
                st.markdown("###### 🔍 Anti-Boring Diagnostics:")
                if audit.get("passed"):
                    st.success("✅ Zero boredom leaks detected! High narrative velocity.")
                else:
                    for iss in audit.get("issues", []):
                        st.warning(f"**{iss['problem']}**: {iss['reason']}")
                        st.caption(f"💡 Recommended Fix: {iss['fix']}")

        with right_tabs[3]:
            st.markdown("##### 🎭 5 Creative Story Approaches")
            st.caption("Generate alternative storytelling angles from your idea:")
            approaches = proj.story_approaches or [asdict(a) for a in director.generate_multiple_approaches(proj.user_input)]
            for app_dict in approaches:
                app = StoryApproach(**app_dict) if isinstance(app_dict, dict) else app_dict
                badge = " (Recommended)" if app.is_recommended else ""
                with st.expander(f"✨ {app.name}{badge} — Potential: {app.attention_potential}/100"):
                    st.markdown(f"**Angle**: {app.story_angle}")
                    st.markdown(f"**Curiosity**: {app.main_curiosity}")
                    st.markdown(f"**Payoff**: {app.payoff}")
                    if st.button(f"🎯 Apply '{app.name}'", key=f"btn_apply_app_{app.name}", use_container_width=True):
                        director.apply_story_approach(proj, app)
                        st.toast(f"Applied {app.name}!", icon="🎯")
                        st.rerun()

        with right_tabs[4]:
            if creator:
                st.markdown("##### 👤 Master Reusable Creator Profile")
                st.caption("Locked for character identity and non-sexualized natural presentation:")
                st.info("🛡️ **Subject Isolation Active**: Video prompts lock creator facial identity and body proportions while discarding photo background so each scene unfolds in its own luxury location.")

                st.markdown("###### 📸 Creator Face & Identity Reference Photo (Image 1)")
                cr_photo_file = st.file_uploader(
                    "Upload Creator Reference Photo",
                    type=["jpg", "jpeg", "png", "webp"],
                    key="life_dir_cr_photo_uploader",
                    help="Upload creator photo. 100% facial identity, hairstyle, skin tone, and body silhouette will be locked across all video prompts."
                )
                if cr_photo_file:
                    st.session_state["life_creator_bytes"] = cr_photo_file.read()

                if st.session_state.get("life_creator_bytes"):
                    st.image(st.session_state["life_creator_bytes"], caption="🔒 Active Creator Reference Photo (Image 1)", width=140)
                    st.success("✅ Creator Reference Photo Active (Image 1): All video prompts lock to this exact face and appearance.")
                else:
                    import os
                    sample_path = os.path.join(r"d:\meesho", "static", "sample_products", "sample_creator.jpg")
                    if os.path.exists(sample_path) and st.button("✨ Load Sample Creator Model", key="btn_life_dir_load_sample_cr"):
                        with open(sample_path, "rb") as scf:
                            st.session_state["life_creator_bytes"] = scf.read()
                        st.toast("Loaded sample creator model!", icon="🌸")
                        st.rerun()

                c_name = st.text_input("Creator Name", value=creator.name, key="cp_name")
                c_age = st.text_input("Age Range", value=creator.age_range, key="cp_age")
                c_app = st.text_area("General Appearance", value=creator.general_appearance, height=60, key="cp_app")
                c_outfit = st.text_area("Active Outfit", value=creator.outfit, height=60, key="cp_outfit")
                c_acc = st.text_input("Accessories", value=creator.accessories, key="cp_acc")
                c_pers = st.text_input("Personality Tone", value=creator.personality, key="cp_pers")

                if st.button("💾 Update Creator Profile", use_container_width=True, key="btn_save_creator_profile"):
                    creator.name = c_name
                    creator.age_range = c_age
                    creator.general_appearance = c_app
                    creator.outfit = c_outfit
                    creator.accessories = c_acc
                    creator.personality = c_pers
                    proj.creator_profile = creator.to_dict()
                    proj.touch()
                    ProjectStore.save_project(proj)
                    st.toast("Creator profile updated!", icon="👤")
