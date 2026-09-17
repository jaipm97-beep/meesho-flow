"""
Curiosity Gap & Micro-Tension Generator.
Implements the psychological 'Aage kya hone wala hai?' tension mechanics across ALL 9 studios.
"""
from typing import Dict, Any, Optional

def generate_why_watch_next(scene_idx: int, total_scenes: int, action: str, section_type: str) -> Dict[str, str]:
    """
    Generates the exact 'Why Watch Next' reason, tension rating, subconscious question ('Aage kya hoga?'),
    and micro-cliffhanger for any scene across all application studios.
    """
    sec = section_type.lower()
    act = action.lower()
    is_unbox = ("unbox" in sec or "unbox" in act or "hath" in act or "hold" in act or "throw" in act) and "runway" not in sec

    # -------------------------------------------------------------
    # SCENE 1: HOOK & SUSPENSE PEAK
    # -------------------------------------------------------------
    if scene_idx == 1:
        tension = "Hook & Suspense Peak 🔥"
        if is_unbox:
            reason = "Creator in casual clothes unfolds garment: 'Maine Meesho se mangaya hai, dekho kaisa aaya!' Immediate curiosity whether it is a gem or a disaster."
            question = "Hath me kapda kaisa lag raha hai, aur pehenne ke baad fit aayega ya blunder hoga?"
            cliffhanger = "Unopened promise: Will the try-on fail or blow minds?"
        elif "problem" in sec or "hack" in sec:
            reason = "Relatable wardrobe struggle shown instantly: 'Yeh blunder har ladki ke saath hota hai!' Viewer stops to see if their own struggle has an instant fix."
            question = "Kya sach me is embarrassing wardrobe problem ka koi 5-second solution hai?"
            cliffhanger = "High-stakes dilemma: How can she fix this without ruining the dress?"
        elif "runway" in sec:
            reason = "Commanding high-fashion catwalk entry with intense eye-contact: 'Wait for this walk!' Viewer stops to see the grand silhouette in motion."
            question = "Ye designer runway look kaun sa hai aur iska ghera motion me kaisa dikhega?"
            cliffhanger = "Approaching climax: What will the full stride reveal?"
        elif "dance" in sec:
            reason = "Snappy rhythm hookstep & freeze-frame tease: Viewer brain locks into musical beat and anticipates transition."
            question = "Bass drop aane par kaisa viral hookstep aur outfit twirl dekhne ko milega?"
            cliffhanger = "Pre-chorus tension: Will the beat drop transition land cleanly?"
        elif "product" in sec or "photo" in sec:
            reason = "Direct challenge to catalog photography: 'Photo me toh accha dikh raha tha, par reality me?' Viewer stops for brutal authenticity."
            question = "Catalog photo vs Real product: Kya Meesho ne photo jaisa hi bheja hai ya dhokha hua?"
            cliffhanger = "Skepticism anchor: Real fabric truth is about to be exposed."
        elif "trends" in sec:
            reason = "Breaking viral trend alert: 'This trend is blowing up everywhere!' Viewer stops to check if they are missing out."
            question = "Ye naya fashion trend kya hai aur kya ye normal budget me recreate ho sakta hai?"
            cliffhanger = "Trend challenge: Can this luxury look be pulled off for cheap?"
        elif "haul" in sec:
            reason = "Mystery haul showdown: 'Inme se ek ₹299 ka hai aur ek ₹1,499 ka!' Viewer plays along to guess the steal."
            question = "In parcels me se kaun sa piece superhit hai aur kaun sa complete flop?"
            cliffhanger = "Blind test curiosity: Which box holds the jackpot?"
        elif "stylist" in sec:
            reason = "Pattern interrupt styling mistake: 'Stop wearing your co-ord sets like this!' Viewer urgently checks their own styling."
            question = "Maine is outfit ko style karne me kaun si galti ki hai?"
            cliffhanger = "Mistake callout: What is the single styling hack that fixes everything?"
        elif "lifestyle" in sec:
            reason = "Cinematic high-status arrival + urgent narrative conflict: Viewer needs to know what unexpected twist is about to unfold."
            question = "Ye itni luxury entry ke baad achanak kaun sa twist aane wala hai?"
            cliffhanger = "Enigmatic setup: What is the creator secret agenda?"
        else: # Meesho Try-On / Studio / Remix Default
            reason = "Visual aesthetic anchor + controversial disbelief hook: 'Mujhe laga tha Meesho se bada dhokha ho gaya... 😳'. Viewer brain freezes to see why she felt scammed."
            question = "Kya Meesho se sach me scam hua ya ye ₹15,000 ka designer look nikla? Aage kya hua?"
            cliffhanger = "Paradoxical hook: Is this an embarrassing fail or a luxury miracle?"

    # -------------------------------------------------------------
    # SCENE 2: ESCALATION & CURIOSITY CALLOUT
    # -------------------------------------------------------------
    elif scene_idx == 2:
        tension = "Anticipation Spike 🔥"
        if is_unbox:
            reason = "Fast 1.5x speed ramp! Garment tossed toward lens or finger snap: viewer brain is primed for the instant match-cut worn reveal!"
            question = "Agla second kya hone wala hai? Will the transition reveal a stunning fit or an awkward mismatch?"
            cliffhanger = "Kinetic whoosh: The transformation is happening right now!"
        elif "problem" in sec or "hack" in sec:
            reason = "Creator rejects expensive tailors and reveals the secret everyday household tool/technique: Stakes rise!"
            question = "Bina tailor ke yeh aasan trick kaam karegi ya kapda kharab ho jayega?"
            cliffhanger = "Tool reveal: How exactly does this hack apply in 5 seconds?"
        elif "runway" in sec:
            reason = "Camera tilts and paces with runway stride; fabric begins catching studio breeze right before the spin."
            question = "Look at that posture! Full 360-degree flare aane par fabric kaisa lagega?"
            cliffhanger = "Stride buildup: The orbital twirl is about to ignite."
        elif "dance" in sec:
            reason = "Micro-speed ramp with fluid hip gesture right on beat riser: Upcoming beat drop is inevitable."
            question = "Beat drop hone par outfit ka kaun sa angle sabse striking dikhega?"
            cliffhanger = "Rhythm suspension: Wait for the beat drop impact!"
        elif "product" in sec or "photo" in sec:
            reason = "Creator does live touch-and-feel test: Rubbing fabric between fingers near mic for tactile proof."
            question = "Hath lagane par material kaisa feel ho raha hai? Soft hai ya rough synthetic?"
            cliffhanger = "Sensory test: How does the weight and fall compare to luxury brands?"
        elif "trends" in sec:
            reason = "Creator pits high-end designer reference against Meesho piece: Side-by-side gap is introduced."
            question = "Kya Meesho ka version sach me designer brand ke standard ko match kar payega?"
            cliffhanger = "Dupe tension: Will the details hold up under inspection?"
        elif "haul" in sec:
            reason = "Tearing open the first package with sensory sound: Creator face shows extreme candid micro-expression."
            question = "Pehla parcel kholte hi creator ka expression kyu badla? Acha nikla ya bura?"
            cliffhanger = "Unboxing shock: What did she see inside the package?"
        elif "stylist" in sec:
            reason = "Demonstrating Wrong Way vs Stylist Way: Stark contrast makes viewers realize their own mistake."
            question = "Sirf ek tuck ya belt change karne se look itna badal sakta hai kya?"
            cliffhanger = "Formula setup: What is the golden rule of this silhouette?"
        elif "lifestyle" in sec:
            reason = "The complication or plot twist hits: An unexpected invitation or venue change forces sudden wardrobe pivot."
            question = "Kya ye backup outfit is grand event me impress kar payega ya out of place lagega?"
            cliffhanger = "Dramatic pivot: How will she adapt to this sudden situation?"
        else: # Meesho Try-On / Studio / Remix Default
            reason = "Creator confesses parcel shock on-camera: '₹15,000 wala look itne saste me impossible laga, lekin...'. Viewer is compelled to see the truth."
            question = "Lekin kya? What did she discover when putting it on?"
            cliffhanger = "Unfinished confession: The live inspection barrier is coming up."

    # -------------------------------------------------------------
    # SCENE 3: SKEPTICISM BARRIER & LIVE TESTING
    # -------------------------------------------------------------
    elif scene_idx == 3 or (scene_idx == total_scenes - 2):
        tension = "Skepticism Barrier & Live Test 🔥"
        if is_unbox:
            reason = "Instant 0.4x slow-mo 120fps match cut worn reveal! Viewer sees full outfit on body for first time."
            question = "Sach me ₹499 me itna premium fit aur luxury flare possible hai?"
            cliffhanger = "Immediate validation: But how does the fabric look under macro sunlight?"
        elif "problem" in sec or "hack" in sec:
            reason = "Live execution of hack: Hands working on camera in 85mm macro zoom. Zero editing tricks."
            question = "Watch closely: Does the seam really hold invisible under tension?"
            cliffhanger = "Proof point: Will the before-and-after withstand the pull test?"
        elif "runway" in sec:
            reason = "85mm macro tracking zoom on high-end embellishments and embroidery while gliding forward."
            question = "Itne close-up me stitches aur finishing kaisi dikh rahi hai?"
            cliffhanger = "Craftsmanship check: Are the details cheap or couture level?"
        elif "dance" in sec:
            reason = "Explosive transition landing right on sub-bass impact: Complete outfit transformation with flare wave."
            question = "Woah, ye transition itna clean kaise hua? Let me check the flare flow!"
            cliffhanger = "Movement peak: Look at the full garment ripple in slow motion!"
        elif "product" in sec or "photo" in sec:
            reason = "Harsh sunlight / studio light transparency test: Creator holds fabric up to verify it is completely non-see-through."
            question = "Dhoop me fabric see-through hai ya solid opaque lining ke saath aaya hai?"
            cliffhanger = "Transparency trial: The biggest fear of online shoppers being tested."
        elif "trends" in sec:
            reason = "Testing fabric flow and elasticity: Stretching waistband and checking comfort for long wear."
            question = "Kya ye trend sirf photos ke liye hai ya sach me din bhar pehan sakte hain?"
            cliffhanger = "Wearability audit: Is it genuinely comfortable or stiff?"
        elif "haul" in sec:
            reason = "Head-to-head quality comparison: Placing both items side-by-side to inspect stitching and fabric density."
            question = "₹299 wale aur mehnge wale me aakhir real difference kahan par hai?"
            cliffhanger = "Comparison climax: The shocking quality verdict is moments away."
        elif "stylist" in sec:
            reason = "Applying magic tweak: Instant optical illusion that snatches waistline and balances proportions."
            question = "Dekho waistline achanak kitni snatched lagne lagi! Is it really this simple?"
            cliffhanger = "Transformation in real-time: Wait for the 360 orbital reveal!"
        elif "lifestyle" in sec:
            reason = "Arrival at luxury terrace or boutique venue: Turning heads and receiving instant social validation."
            question = "Look at that entrance: Will anyone believe this outfit was bought online on a budget?"
            cliffhanger = "Social triumph: The confidence payoff is undeniable."
        else: # Meesho Try-On / Studio / Remix Default
            reason = "Direct objection handling: 'Mirror-work to asli nikla, par sabse bada dar fabric ke see-through hone ka tha... dhoop me dekho!'. Viewer stays glued to verify."
            question = "Dhoop me kya nikla? Is the fabric genuinely high quality or cheap transparent material?"
            cliffhanger = "Fabric truth reveal: Live inspection proves non-see-through quality."

    # -------------------------------------------------------------
    # SCENE 4: DELAYED MOVEMENT PAYOFF & SILHOUETTE TWIRL
    # -------------------------------------------------------------
    elif scene_idx == 4 or (scene_idx == total_scenes - 1):
        tension = "Delayed Movement Payoff 🔥"
        if "problem" in sec or "hack" in sec:
            reason = "Shocking side-by-side Before vs After split screen: Embarrassing wardrobe blunder is 100% invisible."
            question = "Aisa lag raha hai jaise problem kabhi thi hi nahi! How is it so seamless?"
            cliffhanger = "Transformation mastery: The final confidence twirl."
        elif "runway" in sec or "dance" in sec:
            reason = "0.4x ultra slow-motion 120fps 360° circular orbital twirl: Hypnotic fabric flare expands across full screen."
            question = "Look at that massive ghera and breathtaking fabric drape wave!"
            cliffhanger = "Aesthetic climax: The most beautiful frame of the entire video."
        elif "product" in sec or "photo" in sec:
            reason = "Full 360-degree rotation showing how garment sits on natural Indian body proportions."
            question = "Peeche se fall kaisa aa raha hai? Does it flatter natural body curves?"
            cliffhanger = "360 fit check: Zero awkward bunching or pulling."
        elif "trends" in sec:
            reason = "Complete styled look reveal with accessories, heels, and clutch: A viral Pinterest-worthy aesthetic."
            question = "Ye complete look party ya wedding ke liye ready hai ya nahi?"
            cliffhanger = "Styling completion: Where can I get the full coordinated look?"
        elif "haul" in sec:
            reason = "Winning piece worn in motion: Outperforming the expensive alternative by a mile."
            question = "Saste wale piece ka fall itna better kaise nikal sakta hai?"
            cliffhanger = "Value shock: An unbelievable price-to-quality triumph."
        elif "stylist" in sec:
            reason = "Full-length editorial mirror glide showing transformed snatched silhouette from all angles."
            question = "Peeche aur side profile se silhouette kitni flattering lag rahi hai?"
            cliffhanger = "Full posture payoff: Snatched waist and elongated proportions."
        elif "lifestyle" in sec:
            reason = "Golden hour cinematic slow-motion glide: Wind catching fabric in true cinematic fashion."
            question = "Ye visuals itne mesmerizing hain, let me watch this movement again!"
            cliffhanger = "Visual peak: Pure aspirational lifestyle luxury."
        else: # Meesho Try-On / Studio / Remix Default
            reason = "Delayed gratification payoff: 'Fitting kaisi hai? Wait for this 360 twirl... peeche ka cape fall dekh kar main khud shock ho gayi!'"
            question = "Peeche se kaisa dikhta hai? Look at that snatched waist and dramatic cape flow!"
            cliffhanger = "Movement reward: 360 orbital twirl reveals full flare and drape."

    # -------------------------------------------------------------
    # SCENE 5 / FINAL: PRICE SHOCK & CONVERSION REWARD
    # -------------------------------------------------------------
    else:
        tension = "Price Shock & Conversion Action 🔥"
        if "problem" in sec or "hack" in sec:
            reason = "Honest verdict + saveable bookmark CTA: Viewer immediately saves the reel to avoid this blunder in future."
            question = "Mujhe ye hack yaad rakhna hai... let me save and share this with my bestie!"
            cliffhanger = "Action trigger: Direct DM/Comment for the exact hack tool link."
        elif "runway" in sec or "dance" in sec:
            reason = "Confident sassy bookmark pose with direct eye contact + seamless loop sync matching Scene 1 entrance."
            question = "Where can I buy this exact runway outfit code and recreate this look?"
            cliffhanger = "Replay trigger: The end frame loops seamlessly back to the start."
        elif "product" in sec or "photo" in sec:
            reason = "Final scorecard rating (9.8/10) with exact sizing advice (True to Size) and direct code trigger."
            question = "Kaun sa size order karna chahiye aur Meesho search code kya hai?"
            cliffhanger = "Purchasing clarity: Instant code drop in DMs."
        elif "haul" in sec:
            reason = "Scoreboard ranking with prices revealed: Highlighting the ₹299 steal deal and ManyChat DM prompt."
            question = "Dono items ka link lene ke liye kahan comment karna hai?"
            cliffhanger = "Affiliate trigger: Comment keyword to receive links automatically."
        elif "stylist" in sec:
            reason = "Closing style recap with 1-click DM automation keyword and bookmark prompt."
            question = "Ye styling tips save kar loon aur direct product link le loon!"
            cliffhanger = "Community engagement: Comment keyword for full outfit breakdown."
        elif "lifestyle" in sec:
            reason = "Satisfying narrative closure + subtle product link drop + infinite audio replay loop."
            question = "How did she pull this off so smoothly? Watching again from 00:00!"
            cliffhanger = "Seamless loop: First and last frames connect perfectly."
        else: # Meesho Try-On / Studio / Remix Default
            reason = "Shockingly low price reveal (Under ₹800!) + sizing verdict + ManyChat automated DM comment trigger."
            question = "Exact price kitna hai aur direct link kahan se milega? I need to comment right now!"
            cliffhanger = "Instant reward: Comment keyword for direct shopping link & seamless replay loop."

    return {
        "tension_level": tension,
        "why_watch_next": reason,
        "subconscious_question": question,
        "micro_cliffhanger": cliffhanger
    }
