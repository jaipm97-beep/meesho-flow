"""
Creator Engine & Smart Suggestion Generator.
Derives intelligent metadata from small user ideas and maintains creator profile consistency.
"""
from typing import Dict, Any, Optional
from ..models.project import UserInput, AISuggestions
from ..models.creator import CreatorProfile
from ..services.ai_service import AIService

class CreatorEngine:
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai = ai_service

    def generate_smart_suggestions(self, idea: str) -> AISuggestions:
        """Analyzes a minimal user idea and derives smart suggestions."""
        clean_idea = idea.strip()
        if not clean_idea:
            return AISuggestions()

        # Deterministic smart fallback if no AI service / offline
        lower = clean_idea.lower()
        if any(w in lower for w in ["car", "drive", "porsche", "sports coupe", "sedan"]):
            sug = AISuggestions(
                story_style="Luxury Lifestyle",
                location="South Mumbai Seaface Promenade & High-Street Boulevard",
                mood="High-Status & Confident",
                visual_style="Cinematic High-Contrast (4K Golden Hour)",
                story_goal="Arriving in style for a high-profile boutique reservation",
                curiosity_question="What unexpected surprise happens right outside the car?",
                vehicle_or_prop="Matte Black Luxury Sports Coupe",
                suggested_outfit="Vibrant Embroidered Sharara Set with Flowing Cape"
            )
        elif any(w in lower for w in ["hotel", "resort", "suite", "vacation", "villa"]):
            sug = AISuggestions(
                story_style="Hotel & 5-Star Resort",
                location="Private Oceanfront Presidential Villa & Rooftop",
                mood="Relaxed Luxury & Indulgence",
                visual_style="Sunlit Warm Coastal (4K Soft Sunlight)",
                story_goal="Unveiling an exclusive vacation stay and secret itinerary",
                curiosity_question="What hidden luxury experience was left inside the room?",
                vehicle_or_prop="White Range Rover SUV",
                suggested_outfit="Breezy Pastel Co-ord Set & Designer Sunglasses"
            )
        elif any(w in lower for w in ["mall", "shopping", "boutique", "dress", "buy"]):
            sug = AISuggestions(
                story_style="Shopping Spree & Fashion",
                location="Luxury Indian Mall Atrium & Artisan Boutique",
                mood="Excited + Curious",
                visual_style="Natural Luxury Commercial (Warm Daylight)",
                story_goal="Finding an elusive viral designer piece",
                curiosity_question="Why did the boutique staff give her a mystery envelope?",
                vehicle_or_prop="Matte Black Coupe / Luxury Handbag",
                suggested_outfit="Western Chic Blazer Dress & Gold Accessories"
            )
        elif any(w in lower for w in ["cafe", "coffee", "latte", "breakfast"]):
            sug = AISuggestions(
                story_style="Café & Fine Dining",
                location="Aesthetic Sunlit Rooftop Café (Bandra / Khan Market)",
                mood="Aesthetic & Candid",
                visual_style="Editorial Soft Sunlight (35mm Film Tone)",
                story_goal="Enjoying a peaceful morning fashion ritual",
                curiosity_question="What unexpected compliment or encounter changes her morning?",
                vehicle_or_prop="Italian Espresso Glass & Designer Clutch",
                suggested_outfit="Casual Luxury Ribbed Knit Top & Tailored Denim"
            )
        else:
            sug = AISuggestions(
                story_style="Daily Lifestyle Vlog",
                location="Upscale City Center & Aesthetic Promenade",
                mood="Relatable & Upbeat",
                visual_style="Natural UGC Influencer (4K Crisp)",
                story_goal="Documenting a special daily milestone",
                curiosity_question="What unexpected twist happens before the day ends?",
                vehicle_or_prop="Premium City Sunroof Sedan",
                suggested_outfit="Contemporary Fusion Kurti & Palazzo Set"
            )

        # Enhance with AI if key is present
        if self.ai and self.ai.has_valid_key():
            prompt = f"""Analyze this short lifestyle reel idea:
"{clean_idea}"

Suggest optimal creative parameters in JSON:
{{
  "story_style": "...",
  "location": "...",
  "mood": "...",
  "visual_style": "...",
  "story_goal": "...",
  "curiosity_question": "...",
  "vehicle_or_prop": "...",
  "suggested_outfit": "..."
}}
Keep locations upscale Indian luxury settings (South Mumbai, Bandra, Khan Market Delhi, luxury Indian malls).
"""
            try:
                res = self.ai.generate_json(prompt, "You are an expert AI Lifestyle Reel Director.")
                if res and isinstance(res, dict):
                    return AISuggestions(
                        story_style=res.get("story_style", sug.story_style),
                        location=res.get("location", sug.location),
                        mood=res.get("mood", sug.mood),
                        visual_style=res.get("visual_style", sug.visual_style),
                        story_goal=res.get("story_goal", sug.story_goal),
                        curiosity_question=res.get("curiosity_question", sug.curiosity_question),
                        vehicle_or_prop=res.get("vehicle_or_prop", sug.vehicle_or_prop),
                        suggested_outfit=res.get("suggested_outfit", sug.suggested_outfit),
                        raw_suggestions=res
                    )
            except Exception:
                pass

        return sug

    def build_creator_profile(self, user_input: UserInput, suggestions: AISuggestions) -> CreatorProfile:
        """Constructs a consistent, non-sexualized creator profile."""
        outfit = user_input.outfit if user_input.outfit else suggestions.suggested_outfit
        if not outfit:
            outfit = "Western Chic Dress & Tailored Blazer"

        vis_style = user_input.visual_style if user_input.visual_style else suggestions.visual_style
        if not vis_style:
            vis_style = "Luxury Cinematic (4K Soft Sunlight)"

        return CreatorProfile(
            creator_id="creator_master",
            name="Aria",
            age_range="23-26",
            general_appearance="Poised Indian woman, warm glowing skin undertone, natural elegance, smiling eyes",
            hair_type="Dark brown natural voluminous hair",
            hairstyle="Soft shoulder-length blow-dried waves",
            outfit=outfit,
            footwear="Comfortable nude pointed heels, stable footing",
            accessories="Structured luxury shoulder bag, delicate gold bracelet, minimal earrings",
            personality="Charming, relatable bestie with confident modern poise",
            mood_style="High-energy, curious, candid",
            body_language="Natural graceful walk, direct eye contact with lens, candid smile",
            visual_style=vis_style
        )
