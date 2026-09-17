"""
Story Intelligence Engine (Phase 2).
Transforms user ideas into high-retention cinematic narrative structures:
Hook ➔ Goal ➔ Curiosity Question ➔ Open Loop ➔ Micro-Events ➔ Escalation ➔ Natural Conflict ➔ Surprise ➔ Payoff ➔ Rewatch Loop.
Supports Story Compression (15s), Expansion (60s), Multiple Story Approaches, and live Gemini AI generation.
"""
import random
import re
from typing import Optional, Dict, Any, List
from ..models.project import UserInput, StoryMode, AISuggestions, StoryApproach
from ..models.creator import CreatorProfile
from ..models.blueprint import StoryBlueprint, StoryBeat
from ..services.ai_service import AIService

class StoryEngine:
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai = ai_service

    def generate_blueprint(
        self,
        user_input: UserInput,
        suggestions: AISuggestions,
        creator: CreatorProfile,
        regeneration_directive: str = ""
    ) -> StoryBlueprint:
        """Generates a structured Story Blueprint following the 4-phase progression."""
        idea = user_input.idea.strip() if user_input.idea else "Aspirational lifestyle moment in high-fashion Indian setting."
        mode = user_input.story_mode

        if mode == StoryMode.FICTIONAL:
            disclosure = '⚠️ "Fictional / AI-generated lifestyle story for creative entertainment."'
        elif mode == StoryMode.REAL_LIFE:
            disclosure = 'ℹ️ "Real-Life Lifestyle Vlog (preserving actual user events with cinematic storytelling)."'
        else:
            disclosure = 'ℹ️ "Hybrid Lifestyle Story: Inspired by real experiences with creative visual storytelling."'

        # Parse duration for adaptive timing
        dur_str = user_input.duration.lower()
        if "15" in dur_str or "10" in dur_str:
            target_seconds = 15
        elif "60" in dur_str or "45" in dur_str or "1 min" in dur_str:
            target_seconds = 60
        else:
            target_seconds = 30

        # 1. Try Live Gemini AI Generation
        if self.ai and self.ai.has_valid_key():
            ai_bp = self._generate_ai_blueprint(
                user_input=user_input,
                suggestions=suggestions,
                creator=creator,
                disclosure=disclosure,
                target_seconds=target_seconds,
                directive=regeneration_directive
            )
            if ai_bp:
                return ai_bp

        # 2. Dynamic Heuristic Fallback
        return self._generate_enhanced_blueprint(user_input, suggestions, creator, disclosure, target_seconds, regeneration_directive)

    def _generate_ai_blueprint(
        self,
        user_input: UserInput,
        suggestions: AISuggestions,
        creator: CreatorProfile,
        disclosure: str,
        target_seconds: int,
        directive: str = ""
    ) -> Optional[StoryBlueprint]:
        """Uses Gemini AI to generate a rich, unique StoryBlueprint tailored directly to the user's idea."""
        if not self.ai or not self.ai.has_valid_key():
            return None

        idea = user_input.idea.strip()
        loc = user_input.location or (suggestions.location if suggestions else "Upscale Indian City Setting")
        veh = user_input.vehicle or (suggestions.vehicle_or_prop if suggestions else "Luxury Vehicle")
        style = user_input.style or (suggestions.story_style if suggestions else "Luxury Lifestyle")
        lang = user_input.language or "Hinglish"
        creator_name = creator.name or "Creator"

        beat_count = 3 if target_seconds <= 15 else (5 if target_seconds >= 60 else 4)
        directive_line = f"\nCREATIVE DIRECTIVE: {directive}\n" if directive else ""

        prompt = f"""You are the world's leading AI Lifestyle Reel Story Director for Instagram Reels & YouTube Shorts.
Transform this specific lifestyle reel idea into an ultra-high-retention cinematic Story Blueprint.

USER INPUT:
- Premise / Idea: "{idea}"
- Target Duration: {target_seconds} seconds ({beat_count} choreographed scenes)
- Spoken Language: {lang}
- Visual Aesthetic Style: {style}
- Location / Setting: {loc}
- Main Vehicle / Prop: {veh}
- Creator Name: {creator_name}
- Content Mode: {user_input.story_mode.value}
{directive_line}

CRITICAL RULES:
1. STRICTLY TAILORED TO USER IDEA: The story MUST revolve around "{idea}". Do NOT invent unrelated boutique or dress shopping storylines unless the idea is specifically about boutique shopping.
2. SPOKEN DIALOGUE IN {lang.upper()}: Every beat MUST include a natural, conversational, punchy spoken line ("spoken_hint") in {lang} matching the actual scene action.
3. CREATOR REFERENCE PHOTO LOCK: All video prompts and visual actions must lock the character to CREATOR_REFERENCE (Image 1) for 100% facial and physical identity consistency with the uploaded creator photo. Strictly discard the photo's domestic background and place her exclusively inside the scene's dynamic luxury location.
4. BEATS COUNT: Provide exactly {beat_count} beats timed across {target_seconds} seconds.
5. 8K UHD & DUCHENNE REALISM: Visual prompts must standardise on 8K UHD (Arri Alexa Mini LF 35mm f/1.8, visible skin pores, authentic fabric gravity drape). Facial expressions must enforce an authentic Duchenne smile with smiling eye crinkles and synchronized speech articulation (zero frozen/plastic mouth).
6. SPEED RAMPING CHOREOGRAPHY: Direct explicit speed ramping curves (1.0x entry ➔ 0.4x slow-mo 120fps glide ➔ 1.5x snap cut).
7. SYNCHRONIZED SFX & DUCKING: Provide exact Foley sound cues (car thud, heel click, fabric swish) with -8dB background music ducking during dialogue.

RESPOND ONLY WITH A VALID JSON OBJECT:
{{
  "title": "Punchy viral Instagram reel title with emojis",
  "concept": "2-sentence compelling logline capturing the premise, conflict, and payoff",
  "story_goal": "What the creator sets out to experience or accomplish",
  "main_curiosity_question": "The burning curiosity question keeping viewers watching",
  "open_loop": "What crucial information or outcome is withheld until the climax",
  "natural_conflict": "The organic obstacle, twist, or complication",
  "beginning": "Opening hook and premise establishment",
  "development": "Progression and encountering the complication",
  "surprise": "Unexpected discovery, twist, or realization",
  "payoff": "Satisfying resolution and aesthetic climax",
  "ending": "Seamless loop transition back to opening frame",
  "rewatch_potential": "Why viewers will immediately replay or share",
  "open_loop_stages": {{
    "Hint": "Subtle clue in Scene 1",
    "Partial Reveal": "Tease in Scene 2",
    "New Question": "Complication in Scene 3",
    "Final Payoff": "Full revelation at climax"
  }},
  "curiosity_chain": [
    {{"beat": "Beat 1", "viewer_learned": "...", "open_question": "..."}},
    {{"beat": "Beat 2", "viewer_learned": "...", "open_question": "..."}},
    {{"beat": "Beat 3", "viewer_learned": "...", "open_question": "..."}},
    {{"beat": "Beat 4", "viewer_learned": "...", "open_question": "..."}}
  ],
  "attention_peaks": [
    {{"timestamp": "00:00 - 00:02", "type": "Hook Peak", "intensity": 96, "description": "High status opening interrupt"}},
    {{"timestamp": "00:08 - 00:12", "type": "Surprise Peak", "intensity": 98, "description": "Unexpected reveal"}},
    {{"timestamp": "00:18 - 00:22", "type": "Payoff Peak", "intensity": 95, "description": "Satisfying resolution"}}
  ],
  "beats": [
    {{
      "beat_index": 1,
      "timestamp_range": "00:00 - 00:06",
      "phase": "Hook & Goal",
      "narrative_action": "Specific concrete character action in setting (e.g. stepping out of car, inspecting menu). Do not put camera motion here.",
      "visual_moment": "Cinematic camera movement, lens angle, and lighting palette (e.g. Low-angle tracking shot, golden hour sunlight reflecting). Do not put character narrative action here.",
      "why_keep_watching": "Viewer psychology: why keep watching",
      "spoken_hint": "Spoken dialogue line in {lang}",
      "suggested_duration_sec": 6.0,
      "attention_beat_type": "Visual",
      "micro_event": "Quick 1-second micro-event",
      "emotion_tone": "Curiosity & Anticipation",
      "sound_cues": {{"music_mood": "Punchy Electro Chill", "sfx": "Ambient SFX"}},
      "text_overlay": {{"purpose": "Hook curiosity", "timing": "00:00-00:03", "text": "Hook text"}},
      "keep_watching_rating": "Strong"
    }}
  ],
  "rewatch_analysis": {{
    "loop_mechanism": "Seamless visual or dialogue link back to scene 1",
    "replay_trigger": "Subtle detail in opening that makes sense only on rewatch",
    "predicted_rewatch_boost": "+35% rewatch rate"
  }}
}}
"""
        try:
            res = self.ai.generate_json(prompt, system_instruction="You are an expert AI Lifestyle Reel Story Director.")
            if res and isinstance(res, dict) and "beats" in res:
                bp = StoryBlueprint(
                    title=res.get("title", f"{idea[:35]} ✨"),
                    story_concept=res.get("concept", idea),
                    story_goal=res.get("story_goal", f"Experience {loc}"),
                    main_curiosity_question=res.get("main_curiosity_question", f"What happens during {idea[:25]}?"),
                    open_loop=res.get("open_loop", "The surprise payoff is revealed at the climax."),
                    beginning=res.get("beginning", ""),
                    development=res.get("development", ""),
                    surprise=res.get("surprise", ""),
                    payoff=res.get("payoff", ""),
                    ending=res.get("ending", ""),
                    rewatch_potential=res.get("rewatch_potential", "Seamless visual loop"),
                    mode_disclosure=disclosure,
                    natural_conflict=res.get("natural_conflict", "An unexpected complication"),
                    curiosity_chain=res.get("curiosity_chain", []),
                    open_loop_stages=res.get("open_loop_stages", {}),
                    attention_peaks=res.get("attention_peaks", []),
                    rewatch_loop_analysis=res.get("rewatch_analysis", {})
                )
                parsed_beats = []
                for b_data in res.get("beats", []):
                    if isinstance(b_data, dict):
                        parsed_beats.append(StoryBeat.from_dict(b_data))
                if parsed_beats:
                    bp.beats = parsed_beats
                    return bp
        except Exception:
            pass
        return None

    def _generate_enhanced_blueprint(
        self,
        user_input: UserInput,
        suggestions: AISuggestions,
        creator: CreatorProfile,
        disclosure: str,
        target_seconds: int,
        directive: str = ""
    ) -> StoryBlueprint:
        """Constructs rich Phase 2 narrative intelligence blueprint dynamically tailored to user idea."""
        idea = user_input.idea.strip() if user_input.idea else "Aspirational lifestyle outing"
        loc = user_input.location or (suggestions.location if suggestions else "Upscale Indian Promenade & Skyline")
        veh = user_input.vehicle or (suggestions.vehicle_or_prop if suggestions else "Matte Black Luxury Sports Coupe")
        lang = user_input.language or "Hinglish"
        lower_idea = idea.lower()

        # Dynamic category determination based on user idea
        if any(w in lower_idea for w in ["yacht", "boat", "sail", "sea", "cruise", "ocean"]):
            cat = "yacht"
            goal = f"Private sunset yacht voyage across coastal waters departing {loc}"
            natural_conflict = "Choppy open-sea currents forced captain to steer into a secluded tranquil cove"
            surprise = "Unlocking a private sun-deck twilight lounge with glowing neon aesthetics"
            payoff = "Golden-hour champagne toast against dramatic coastal waves in slow motion"
            curiosity = "Where is this private luxury yacht heading as the sun dips below the horizon?"
            open_loop = "The exclusive hidden destination at the end of the yacht cruise is held until climax."
            spoken_1 = "Private yacht ride book ki thi sunset dekhne ke liye... par captain ne rasta badal diya!" if lang == "Hinglish" else "Booked a sunset yacht cruise, but captain changed our route!"
            spoken_2 = "Open sea me sudden waves aane lage, aur hum ek secret hidden cove me enter hue..." if lang == "Hinglish" else "Sudden waves redirected us straight into a secluded private cove..."
            spoken_3 = "And look what was waiting on the private upper deck—pure luxury!" if lang == "English" else "Aur upper deck par dekho kya surprise tha—unreal views!"
            spoken_4 = "Best sunset decision ever! Comment 'VOYAGE' for the secret booking details." if lang == "English" else "Trip officially unforgettable ho gayi! Comment karo 'VOYAGE' direct link ke liye."
        elif any(w in lower_idea for w in ["trek", "mountain", "manali", "himalaya", "hike", "nature"]):
            cat = "trek"
            goal = f"Chasing a magical sunrise mountain peak near {loc}"
            natural_conflict = "Dense morning mountain fog obscured the main trail, forcing a scenic detour"
            surprise = "Stumbling upon a hidden wooden cliffside tea shack with 360° panoramic Himalayan view"
            payoff = "Sipping hot cardamom chai as golden morning light breaks through the alpine clouds"
            curiosity = "Will the creator reach the summit before the golden sunrise disappears?"
            open_loop = "The breathtaking view waiting beyond the fog wall is withheld until climax."
            spoken_1 = "Subah 5 baje mountain trail par nikle the sunrise pakadne..." if lang == "Hinglish" else "Hit the mountain trail at 5 AM chasing the golden sunrise..."
            spoken_2 = "Heavy mountain fog aa gayi aur main trail dikhna band ho gaya!" if lang == "Hinglish" else "Heavy mist rolled in, wiping out the trail markers completely!"
            spoken_3 = "Tabhi fog ke peeche se yeh hidden wooden cafe dikha!" if lang == "Hinglish" else "Just then, this hidden cliffside wooden tea shack appeared!"
            spoken_4 = "Garama-garam pahadi chai aur yeh view... comment 'PEAK' for location pin!" if lang == "Hinglish" else "Steaming chai and this 360° view... comment 'PEAK' for location!"
        elif any(w in lower_idea for w in ["hotel", "resort", "villa", "vacation", "stay"]):
            cat = "hotel"
            goal = f"Checking into an ultra-exclusive presidential suite retreat at {loc}"
            natural_conflict = "The booked suite faced an emergency maintenance upgrade upon arrival"
            surprise = "Manager personally upgraded creator to the private cliffside presidential villa with infinity pool"
            payoff = "Private twilight dip in the infinity pool overlooking starry skyline in total peace"
            curiosity = "What exclusive upgrade did the resort prepare behind the locked double doors?"
            open_loop = "The presidential suite's jaw-dropping private terrace view is withheld until the climax."
            spoken_1 = "Weekend getaway ke liye villa check-in kiya... but reception par ek shock mila." if lang == "Hinglish" else "Checked into the villa for weekend getaway... but reception had a shock waiting."
            spoken_2 = "Room under maintenance tha, par manager ne bola: 'Walk with me.'" if lang == "Hinglish" else "Our room was in maintenance, but manager said: 'Follow me to private wing.'"
            spoken_3 = "Direct cliffside presidential villa upgrade with private pool! Look at this!" if lang == "English" else "Sidha private infinity pool villa me upgrade mil gaya!"
            spoken_4 = "Weekend officially saved in pure 5-star luxury. Comment 'STAY' for room details!" if lang == "English" else "Weekend pure luxury me convert ho gaya! Comment karo 'STAY' details ke liye."
        elif any(w in lower_idea for w in ["cafe", "coffee", "breakfast", "brunch", "matcha"]):
            cat = "cafe"
            goal = f"Testing an artisanal aesthetic morning breakfast spot at {loc}"
            natural_conflict = "Popular outdoor tables were completely waitlisted for 2 hours"
            surprise = "Head barista invited creator to the secret sunlit garden greenhouse table"
            payoff = "Artisanal espresso pour and golden pastry aesthetic that looks like a Parisian magazine cover"
            curiosity = "Will she find a table or discover an even more aesthetic hidden corner?"
            open_loop = "The custom unreleased pastry creation served at her table is withheld until climax."
            spoken_1 = "City ke sabse aesthetic cafe me breakfast lene aayi thi in my sports car..." if lang == "Hinglish" else "Drove down to the most aesthetic rooftop cafe for morning coffee..."
            spoken_2 = "Poora cafe booked tha, but head barista offered a secret garden table!" if lang == "Hinglish" else "Two-hour waitlist outside, but barista opened the private greenhouse table!"
            spoken_3 = "Custom golden pistachio latte aur yeh morning light... aesthetic perfection!" if lang == "Hinglish" else "Custom pistachio latte and morning glow... pure aesthetic gold!"
            spoken_4 = "Aisi peaceful mornings रोज honi chahiye. Comment 'CAFE' for this hidden gem!" if lang == "Hinglish" else "Mornings should always feel this serene. Comment 'CAFE' for location!"
        elif any(w in lower_idea for w in ["thrift", "market", "bazaar", "budget", "dupe"]):
            cat = "thrift"
            goal = f"Hunting for viral high-fashion treasures in the historic lanes of {loc}"
            natural_conflict = "The famous vintage boutique corner was locked for inventory restock"
            surprise = "Stumbling upon a hidden back-alley artisan stall with luxury runway samples for ₹499"
            payoff = "Styling the ₹499 hidden find so flawlessly that people asked if it was high couture"
            curiosity = "Can an unscripted ₹499 street find truly look indistinguishable from designer fashion?"
            open_loop = "The actual price tag and styling reveal of the hidden find is withheld until climax."
            spoken_1 = "Hidden thrift hunt par nikli thi in my luxury outfit... looking for gold!" if lang == "Hinglish" else "Went on a hidden street hunt looking for runway-level fashion..."
            spoken_2 = "Main shop band thi, but back alley me ek hidden stall dikha!" if lang == "Hinglish" else "Main store was closed, but stumbled on an artisan stall in the back alley!"
            spoken_3 = "Yeh pure silk mirror-work piece sirf ₹499 me mila! Believe it or not!" if lang == "Hinglish" else "Found this incredible runway piece for just ₹499! Unbelievable drape!"
            spoken_4 = "Style doesn't need 50k, just good eyes! Comment 'THRIFT' for the exact shop lane." if lang == "English" else "50 hazaar ki zaroorat nahi, style chahiye! Comment karo 'THRIFT' shop ke liye."
        elif any(w in lower_idea for w in ["shop", "boutique", "mall", "dress", "gown", "outfit"]):
            cat = "shopping"
            goal = f"Hunting down a viral fashion statement look across {loc}"
            natural_conflict = "The high-end boutique reservation was mixed up at the counter"
            surprise = "Trying on an exquisite designer silhouette in the VIP trial suite that looks 10x richer"
            payoff = "Emerging in the breathtaking tried-on fit, executing a 360° twirl in front of the gilded mirror"
            curiosity = "How will she turn an outfit emergency into the most viral look of the evening?"
            open_loop = "The jaw-dropping fit and effortless drape of the tried-on dress is held until climax."
            spoken_1 = "Boutique outfit lene aayi thi... but counter par aate hi twist ho gaya!" if lang == "Hinglish" else "Came to pick up my reserved look, but counter had a surprise waiting!"
            spoken_2 = "Main outfit nahi tha! But manager ne bola: 'Yeh naya designer piece pehan kar dekho.'" if lang == "Hinglish" else "Reserved gown was missing! But manager said: 'Try on this secret new piece.'"
            spoken_3 = "Maine trial suite me pehna... and just look at this fit! Looks richer than a 50k gown!" if lang == "Hinglish" else "Tried it on in the mirror suite... and look at this drape! Pure couture energy!"
            spoken_4 = "Night saved and look 10/10! Comment 'STYLE' for direct link in your DM." if lang == "English" else "Outfit pehankar look 10/10 lag raha hai! Comment 'STYLE' karo link ke liye."
        else:
            cat = "general"
            goal = f"Experiencing a glamorous aesthetic outing at {loc} with {veh}"
            natural_conflict = "An unexpected twist redirected the original afternoon plan"
            surprise = "Unlocking an unscripted high-aesthetic moment that captivated everyone nearby"
            payoff = "Breathtaking visual confidence and satisfying emotional payoff in slow motion"
            curiosity = f"What unexpected lifestyle surprise awaits {creator.name or 'the creator'} at {loc}?"
            open_loop = "The key visual reveal and final outcome is withheld until the climax."
            spoken_1 = f"Aj {loc} me ek special day out plan kiya tha... but wait for the twist!" if lang == "Hinglish" else f"Planned a special day out at {loc}... but watch the twist!"
            spoken_2 = "Plan me sudden change aaya, and we took an unexpected detour!" if lang == "Hinglish" else "Sudden change in plans, so we took an unexpected aesthetic detour!"
            spoken_3 = "And this view turned out to be 10x better than what we planned!" if lang == "English" else "Aur yeh jagah hamare original plan se 10 guna zyada khoobsurat nikli!"
            spoken_4 = "Such spontaneous days are the best. Comment 'VIBE' for location & outfit info!" if lang == "English" else "Spontaneous moments are always best! Comment karo 'VIBE' details ke liye."

        open_loop_stages = {
            "Hint": f"Scene 1: Arriving at {loc} with anticipation while teasing the main goal.",
            "Partial Reveal": f"Scene 2: Encountering the twist ({natural_conflict}).",
            "New Question": f"Scene 3: Testing the unexpected discovery: {surprise}.",
            "Final Payoff": f"Scene 4: Full aesthetic payoff & celebratory resolution."
        }

        curiosity_chain = [
            {"beat": "Beat 1", "viewer_learned": f"Arrived at {loc} for {goal}.", "open_question": curiosity},
            {"beat": "Beat 2", "viewer_learned": f"Plan disrupted: {natural_conflict}.", "open_question": "How will she recover the situation?"},
            {"beat": "Beat 3", "viewer_learned": f"Discovered: {surprise}.", "open_question": "Does it deliver in motion under natural light?"},
            {"beat": "Beat 4", "viewer_learned": "Full aesthetic triumph achieved.", "open_question": "Where can viewers experience this?"}
        ]

        attention_peaks = [
            {"timestamp": "00:00 - 00:02", "type": "Hook Peak", "intensity": 96, "description": f"High-contrast arrival via {veh}."},
            {"timestamp": "00:08 - 00:12", "type": "Surprise Peak", "intensity": 98, "description": f"Encountering {surprise}."},
            {"timestamp": "00:18 - 00:22", "type": "Payoff Peak", "intensity": 95, "description": "Full slow-motion cinematic resolution."}
        ]

        # Adaptive Beats based on duration
        if target_seconds <= 15:
            beats = [
                StoryBeat(
                    beat_index=1,
                    timestamp_range="00:00 - 00:04",
                    phase="Hook & Goal",
                    narrative_action=f"Creator steps out of {veh} arriving at {loc}.",
                    visual_moment="Low-angle dynamic tracking shot stepping out with commanding confidence.",
                    why_keep_watching="Immediate status interrupt + curiosity about what she is rushing to pick up.",
                    spoken_hint=spoken_1,
                    suggested_duration_sec=4.0,
                    attention_beat_type="Action",
                    micro_event="Vehicle exit & sudden message glance",
                    emotion_tone="Curiosity & Urgency",
                    sound_cues={"music_mood": "Punchy Electro Chill", "sfx": "Car door thud + phone chime"},
                    text_overlay={"purpose": "Hook curiosity", "timing": "00:00-00:02", "text": "Wait for the twist... 😳"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=2,
                    timestamp_range="00:04 - 00:10",
                    phase="Surprise Discovery",
                    narrative_action=f"Discovering the unexpected twist: {surprise}.",
                    visual_moment="Fluid camera rotation capturing candid reaction and stunning environment.",
                    why_keep_watching="Sudden turning point: will this unexpected discovery actually work?",
                    spoken_hint=spoken_2,
                    suggested_duration_sec=6.0,
                    attention_beat_type="Reveal",
                    micro_event="Exploring the secret alternative",
                    emotion_tone="Excitement",
                    sound_cues={"music_mood": "Chorus Drop", "sfx": "Swoosh transition"},
                    text_overlay={"purpose": "Highlight twist", "timing": "00:05-00:08", "text": "Look what happened next..."},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=3,
                    timestamp_range="00:10 - 00:15",
                    phase="Payoff & Loop Ending",
                    narrative_action=f"{payoff} with direct interactive call-to-action.",
                    visual_moment="Full 360° fluid pivot under natural golden daylight, ending in a confident wink.",
                    why_keep_watching="Closure of open loop and seamless visual cut back to Scene 1 door frame.",
                    spoken_hint=spoken_4,
                    suggested_duration_sec=5.0,
                    attention_beat_type="Payoff",
                    micro_event="Public validation & seamless replay cut",
                    emotion_tone="Triumph & Joy",
                    sound_cues={"music_mood": "Uplifting High-End Outro", "sfx": "Camera shutter snap"},
                    text_overlay={"purpose": "CTA & Loop", "timing": "00:12-00:15", "text": "Comment for link 👇"},
                    keep_watching_rating="Strong"
                )
            ]
        elif target_seconds >= 60:
            beats = [
                StoryBeat(
                    beat_index=1,
                    timestamp_range="00:00 - 00:10",
                    phase="Establishing Hook",
                    narrative_action=f"Gliding through upscale boulevard in {veh}, parking at {loc}.",
                    visual_moment="Cinematic 4K anamorphic lens flares glinting off vehicle hood, stepping out in tailored elegance.",
                    why_keep_watching="Atmospheric luxury aesthetic, teasing the exclusive journey ahead.",
                    spoken_hint=spoken_1,
                    suggested_duration_sec=10.0,
                    attention_beat_type="Visual",
                    micro_event="Gliding past luxury streetfronts and parking with valet",
                    emotion_tone="Anticipation",
                    sound_cues={"music_mood": "Deep Sub-Bass Ambient", "sfx": "Engine growl + boulevard murmur"},
                    text_overlay={"purpose": "Location stamp", "timing": "00:02-00:06", "text": f"Day Out at {loc[:20]} ✨"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=2,
                    timestamp_range="00:10 - 00:22",
                    phase="Journey & Natural Conflict",
                    narrative_action=f"Striding through grand atrium; {natural_conflict}.",
                    visual_moment="Steadicam tracking through marble columns, discovering the unexpected complication.",
                    why_keep_watching="Tension builds as the anticipated plan takes a jarring turn.",
                    spoken_hint=spoken_2,
                    suggested_duration_sec=12.0,
                    attention_beat_type="Action",
                    micro_event="Encountering the unexpected obstacle",
                    emotion_tone="Surprise & Tension",
                    sound_cues={"music_mood": "Suspense Beat", "sfx": "Dramatic chime"},
                    text_overlay={"purpose": "Highlight conflict", "timing": "00:12-00:16", "text": "Plan completely changed?!"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=3,
                    timestamp_range="00:22 - 00:36",
                    phase="Micro-Discovery & Trial",
                    narrative_action="Inspecting the unexpected alternative and testing the experience.",
                    visual_moment="Macro close-up on authentic details, ASMR ambient rustle, candid reaction.",
                    why_keep_watching="Visual novelty and suspense over whether this spontaneous choice pays off.",
                    spoken_hint=spoken_3,
                    suggested_duration_sec=14.0,
                    attention_beat_type="Information",
                    micro_event="Tactile inspection and genuine surprise",
                    emotion_tone="Delight & Discovery",
                    sound_cues={"music_mood": "Melodic Chord Progression", "sfx": "Swoosh flourish"},
                    text_overlay={"purpose": "Detail appreciation", "timing": "00:24-00:30", "text": "Wait till you see this..."},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=4,
                    timestamp_range="00:36 - 00:48",
                    phase="Surprise Transformation",
                    narrative_action=f"{surprise} revealed under golden hour sunlight.",
                    visual_moment="Full-length mirror pivot, styling accessories, golden hour sunlight highlighting the scene.",
                    why_keep_watching="The aesthetic payoff of seeing the complete experience assembled.",
                    spoken_hint=spoken_3,
                    suggested_duration_sec=12.0,
                    attention_beat_type="Reveal",
                    micro_event="Aesthetic transformation reveal",
                    emotion_tone="Euphoria",
                    sound_cues={"music_mood": "Harmonic Beat Drop", "sfx": "Finger-snap transition"},
                    text_overlay={"purpose": "Surprise reveal", "timing": "00:40-00:45", "text": "Look at this view! 🤯"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=5,
                    timestamp_range="00:48 - 00:60",
                    phase="Payoff & Seamless Loop",
                    narrative_action=f"{payoff} at sunlit outdoor setting, laughing with confidence.",
                    visual_moment="Slow-motion 360° twirl, iced beverage toast, confident backward step looping to opening frame.",
                    why_keep_watching="Complete emotional resolution, lifestyle satisfaction, and seamless replay cut.",
                    spoken_hint=spoken_4,
                    suggested_duration_sec=12.0,
                    attention_beat_type="Payoff",
                    micro_event="Celebration toast & seamless cut",
                    emotion_tone="Confidence & Connection",
                    sound_cues={"music_mood": "Warm Euphoric Sunset Beat", "sfx": "Cup clink + bell chime"},
                    text_overlay={"purpose": "Interactive Call to Action", "timing": "00:52-00:60", "text": "Comment for link & info 👇"},
                    keep_watching_rating="Strong"
                )
            ]
        else:
            # 30s Standard 4-Phase Balanced Structure
            beats = [
                StoryBeat(
                    beat_index=1,
                    timestamp_range="00:00 - 00:06",
                    phase="Beginning & Hook",
                    narrative_action=f"Creator arrives at {loc} in {veh}.",
                    visual_moment="Low-angle tracking shot stepping out with commanding confidence, adjusting sunglasses under natural sunlight.",
                    why_keep_watching="High-status pattern interrupt + mystery of what she is rushing to experience.",
                    spoken_hint=spoken_1,
                    suggested_duration_sec=6.0,
                    attention_beat_type="Visual",
                    micro_event="Vehicle exit with sunglasses adjustment",
                    emotion_tone="Curiosity",
                    sound_cues={"music_mood": "Punchy Electro Chill", "sfx": "Car door thud + high-heel click"},
                    text_overlay={"purpose": "Hook viewer", "timing": "00:00-00:03", "text": "Wait till the end... 🏎️✨"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=2,
                    timestamp_range="00:06 - 00:14",
                    phase="Development & Conflict",
                    narrative_action=f"Striding through atmosphere; {natural_conflict}.",
                    visual_moment="Fluid Steadicam forward tracking through arches; encountering the unexpected twist.",
                    why_keep_watching="Tension builds as the anticipated plan takes an intriguing detour.",
                    spoken_hint=spoken_2,
                    suggested_duration_sec=8.0,
                    attention_beat_type="Action",
                    micro_event="Encountering the detour and pivoting",
                    emotion_tone="Tension & Curiosity",
                    sound_cues={"music_mood": "Bassline Build", "sfx": "Whoosh swell"},
                    text_overlay={"purpose": "Escalate tension", "timing": "00:07-00:11", "text": "Plan completely changed?!"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=3,
                    timestamp_range="00:14 - 00:22",
                    phase="Surprise Transformation",
                    narrative_action=f"{surprise} and instant validation.",
                    visual_moment="360° fluid camera pivot capturing ambient reflection and tailored silhouette under soft golden lighting.",
                    why_keep_watching="The satisfaction of an unexpected high-value discovery and aesthetic glow-up.",
                    spoken_hint=spoken_3,
                    suggested_duration_sec=8.0,
                    attention_beat_type="Reveal",
                    micro_event="Surprise reveal and joyful gasp",
                    emotion_tone="Excitement & Shock",
                    sound_cues={"music_mood": "Chorus Beat Drop", "sfx": "Sparkle chime"},
                    text_overlay={"purpose": "Highlight value", "timing": "00:15-00:20", "text": "Pure magic moment 🤯"},
                    keep_watching_rating="Strong"
                ),
                StoryBeat(
                    beat_index=4,
                    timestamp_range="00:22 - 00:30",
                    phase="Payoff & Loop Ending",
                    narrative_action=f"{payoff} with clear CTA.",
                    visual_moment="Close-up portrait table pose with iced beverage, playful wink and downward finger point looping to opening vehicle frame.",
                    why_keep_watching="Closure of open loop and immediate loop connection back to Scene 1 door frame.",
                    spoken_hint=spoken_4,
                    suggested_duration_sec=8.0,
                    attention_beat_type="Payoff",
                    micro_event="Celebration pose & seamless loop cut",
                    emotion_tone="Satisfaction & Joy",
                    sound_cues={"music_mood": "Smooth Sunset Outro", "sfx": "Shutter click + chime"},
                    text_overlay={"purpose": "Comment CTA", "timing": "00:24-00:30", "text": "Comment below for details 👇"},
                    keep_watching_rating="Strong"
                )
            ]

        rewatch_analysis = {
            "loop_mechanism": f"Final confident smile and backward step synchronizes with the opening frame at {loc}.",
            "replay_trigger": "Subtle detail in opening scene that only makes sense after watching the final payoff.",
            "predicted_rewatch_boost": "+38% replay probability based on curiosity closure."
        }

        title = f"{idea[:30].strip().title()} ✨" if len(idea) > 5 else "Unscripted Lifestyle Twist ✨"

        return StoryBlueprint(
            title=title,
            story_concept=f"Experiencing {goal}, but when {natural_conflict.lower()}, discovering {surprise.lower()}, leading to {payoff.lower()}.",
            story_goal=goal,
            main_curiosity_question=curiosity,
            open_loop=open_loop,
            beginning=f"Arriving at {loc} in {veh}.",
            development=f"Navigating the unexpected complication: {natural_conflict}.",
            surprise=surprise,
            payoff=payoff,
            ending=f"Triumphant celebration and seamless visual loop at {loc}.",
            rewatch_potential="High visual contrast and curiosity loop that reconnects seamlessly to opening frame.",
            beats=beats,
            mode_disclosure=disclosure,
            natural_conflict=natural_conflict,
            curiosity_chain=curiosity_chain,
            open_loop_stages=open_loop_stages,
            attention_peaks=attention_peaks,
            rewatch_loop_analysis=rewatch_analysis
        )

    def generate_multiple_approaches(self, user_input: UserInput) -> List[StoryApproach]:
        """Generates 5 distinct creative story approaches tailored to the user's idea."""
        idea = user_input.idea.strip() if user_input.idea else "Aspirational lifestyle outing"

        if self.ai and self.ai.has_valid_key():
            prompt = f"""Generate 5 distinct creative Instagram Reel story approaches for this lifestyle idea:
"{idea}"

Approaches needed:
1. Curiosity Story (Mystery & Open Loop)
2. Experience Story (Atmospheric Lifestyle)
3. Surprise Story (Expectation Subversion)
4. Emotional Story (Relatable Vulnerability & Connection)
5. Luxury Story (Aspirational High-Glam)

RESPOND ONLY WITH A VALID JSON ARRAY OF 5 OBJECTS:
[
  {{
    "name": "Curiosity Story",
    "story_angle": "Angle description tailored to the idea",
    "main_curiosity": "Curiosity question keeping viewers hooked",
    "payoff": "Climax and payoff resolution",
    "attention_potential": 96,
    "is_recommended": true
  }},
  ...
]
"""
            try:
                res = self.ai.generate_json(prompt, system_instruction="You are an expert creative story director.")
                if res and isinstance(res, list) and len(res) >= 3:
                    approaches = []
                    for i, item in enumerate(res):
                        approaches.append(StoryApproach(
                            name=item.get("name", f"Angle {i+1}"),
                            story_angle=item.get("story_angle", idea),
                            main_curiosity=item.get("main_curiosity", "What happens next?"),
                            payoff=item.get("payoff", "Satisfying payoff"),
                            attention_potential=int(item.get("attention_potential", 92)),
                            is_recommended=bool(item.get("is_recommended", (i == 0)))
                        ))
                    if approaches:
                        return approaches
            except Exception:
                pass

        # Contextual Fallback
        return [
            StoryApproach(
                name="Curiosity Story",
                story_angle=f"Mystery & Open Loop: A sudden unexpected discovery during {idea[:35]}.",
                main_curiosity=f"What secret revelation changes the entire outcome of {idea[:30]}?",
                payoff=f"An unscripted breakthrough that turns the situation into a complete viral win.",
                attention_potential=96,
                is_recommended=True
            ),
            StoryApproach(
                name="Experience Story",
                story_angle=f"Atmospheric Sensory Vlog: An aesthetic immersion into {idea[:40]}.",
                main_curiosity=f"Can this spontaneous experience live up to the breathtaking aesthetic hype?",
                payoff=f"Golden hour cinematic slow-mo capture that feels like an international luxury editorial.",
                attention_potential=91,
                is_recommended=False
            ),
            StoryApproach(
                name="Surprise Story",
                story_angle=f"Expectation Subversion: Starting with a high-stakes plan that completely turns on its head.",
                main_curiosity=f"How will she recover when the original itinerary falls apart completely?",
                payoff=f"The backup plan turns out 10x more spectacular and memorable than the planned option.",
                attention_potential=95,
                is_recommended=False
            ),
            StoryApproach(
                name="Emotional Story",
                story_angle=f"Relatable Bestie Connection: Overcoming insecurity and embracing the joy of {idea[:35]}.",
                main_curiosity=f"Will she feel out of place, or will confidence completely steal the spotlight?",
                payoff=f"Authentic candid laughter proving that true luxury is joyful confidence.",
                attention_potential=89,
                is_recommended=False
            ),
            StoryApproach(
                name="Luxury Story",
                story_angle=f"High-Glamour Flex: High-status arrival, private access, and bespoke aesthetic presentation.",
                main_curiosity=f"Which visual frame captures the ultra-luxury ambience best?",
                payoff=f"Slow-motion high-fashion twirl under warm ambient spotlights looking like a magazine cover.",
                attention_potential=94,
                is_recommended=False
            )
        ]
