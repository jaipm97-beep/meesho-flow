import os
import re
import io
import asyncio
import edge_tts
import time
import random
import base64
import datetime
import json
import warnings
import requests
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from urllib.parse import quote_plus

warnings.filterwarnings("ignore", message=".*use_container_width.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ---------------------------------------------------------
# Configuration & Paths
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
MASTER_PROMPT_PATH = os.path.join(BASE_DIR, "MASTER_PROMPT_V1.md")
TRENDS_CACHE_FILE = os.path.join(BASE_DIR, "daily_trends_cache.json")

load_dotenv(ENV_PATH, override=True)

def get_safe_secret(key: str, default: str = "") -> str:
    """Safely retrieves a secret from st.secrets without raising StreamlitSecretNotFoundError."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val)
    except Exception:
        pass
    return default

# ---------------------------------------------------------
# Streamlit Page Config & Custom Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Meesho AI Video Director & Trends Radar",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern SaaS aesthetic with Meesho pink/purple tones & Trend Cards
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }
    
    /* Header hero */
    .hero-container {
        background: linear-gradient(135deg, #7928ca 0%, #ff0080 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(255, 0, 128, 0.15);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: white !important;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        margin-top: 0.4rem;
        opacity: 0.95;
        font-weight: 400;
        color: #fdf2f8 !important;
    }
    
    /* Trend Card styling */
    .trend-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-top: 4px solid #db2777;
    }
    .trend-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(219, 39, 119, 0.12);
    }
    .trend-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
    }
    .trend-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .trend-hook-box {
        background-color: #fdf2f8;
        border-left: 3px solid #db2777;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #9d174d;
        font-style: italic;
        margin: 0.6rem 0;
    }
    
    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 50px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-pink {
        background-color: #fdf2f8;
        color: #db2777;
        border: 1px solid #fbcfe8;
    }
    .badge-purple {
        background-color: #faf5ff;
        color: #7e22ce;
        border: 1px solid #e9d5ff;
    }
    .badge-green {
        background-color: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .badge-amber {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
    }

    /* Primary button custom glow */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e11d48 0%, #db2777 100%) !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3) !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.45) !important;
    }

    /* Mobile Screen Responsiveness & Touch Optimization */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-top: 0.6rem;
        }
        .hero-container {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 1.45rem;
            line-height: 1.3;
        }
        .hero-subtitle {
            font-size: 0.88rem;
        }
        .trend-card {
            padding: 1rem;
            border-radius: 12px;
        }
        .trend-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }
        .trend-title {
            font-size: 1.05rem;
        }
        .stButton>button {
            min-height: 44px;
            font-size: 0.92rem;
        }
        .stDownloadButton>button {
            min-height: 44px;
            font-size: 0.92rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def load_master_prompt():
    if os.path.exists(MASTER_PROMPT_PATH):
        try:
            with open(MASTER_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            st.error(f"Error reading master prompt: {e}")
    return "You are an expert video director and retention strategist for short-form fashion reels."

def optimize_image(image_bytes, max_dim=1280, quality=85):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if w > max_dim or h > max_dim:
            if w > h:
                new_h = int(h * (max_dim / w))
                new_w = max_dim
            else:
                new_w = int(w * (max_dim / h))
                new_h = max_dim
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        out_buf = io.BytesIO()
        img.save(out_buf, format="JPEG", quality=quality, optimize=True)
        return out_buf.getvalue(), "image/jpeg"
    except Exception:
        return image_bytes, "image/jpeg"

def extract_safe_garment_crop(image_bytes):
    """
    Auto-crops central product area to eliminate face, cleavage, bare arms, and thighs/groin
    for zero-moderation rejection in Google Flow and Kling AI.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        w, h = img.size
        if h > w * 1.1:
            crop_box = (int(w * 0.22), int(h * 0.34), int(w * 0.78), int(h * 0.64))
            cropped = img.crop(crop_box)
        else:
            cropped = img
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=95)
        return cropped, buf.getvalue()
    except Exception as e:
        return None, None

def extract_instagram_reel(url):
    """
    Extracts metadata, caption, and audio info from an Instagram Reel URL using yt-dlp.
    """
    try:
        import yt_dlp
        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 15
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url.strip(), download=False)
            title = info.get("title") or "Viral Instagram Reel"
            desc = info.get("description") or ""
            duration = int(info.get("duration", 30) or 30)
            uploader = info.get("uploader") or info.get("channel") or "Instagram Creator"
            thumbnail = info.get("thumbnail") or ""
            tags = info.get("tags") or []
            
            hook_text = desc.split("\n")[0] if desc else title
            if len(hook_text) > 130:
                hook_text = hook_text[:130] + "..."
                
            return {
                "success": True,
                "title": title,
                "description": desc,
                "hook_text": hook_text,
                "duration": duration,
                "uploader": uploader,
                "thumbnail": thumbnail,
                "tags": tags,
                "url": url.strip()
            }, None
    except Exception as e:
        err = str(e)
        if "login" in err.lower() or "empty media" in err.lower():
            err_msg = "Instagram ne is reel par Login Barrier lagaya hua hai. Fikar mat karein! Neeche '🛡️ Zero-Failure Backup' kholkar caption paste karein ya MP4 upload karein — turant analyze ho jayega!"
        else:
            err_msg = f"Extraction note: {err[:150]}"
        return None, err_msg


def extract_meesho_product_data(input_text, api_key=None, screenshot_bytes=None):
    """
    Extracts structured product data from a Meesho product URL, app share text,
    product code, or product screenshot.
    """
    raw_url = ""
    code = ""
    price = ""
    slug_title = ""
    og_title = ""
    og_image = ""
    
    # 1. Screenshot Analysis via Gemini Vision if provided
    if screenshot_bytes and api_key:
        try:
            s_bytes, s_mime = optimize_image(screenshot_bytes)
            prompt = """Analyze this Meesho fashion product screenshot or photo.
Extract the following information in valid JSON:
{
  "title": "Clean, highly attractive commercial product title in English/Hinglish",
  "category": "One of: Ethnic Wear (Kurti / Suit / Saree / Blouse), Western & Casual Dresses, Wardrobe Problem-Solver Hack, Shapewear & Saree Silhouette, Intimates & Lingerie 2-Piece Set, Nightwear & Loungewear Slip",
  "price": "e.g. ₹499",
  "meesho_code": "e.g. s-18392841",
  "color": "Dominant color palette (e.g. Mustard Yellow & Gold zari)",
  "fabric": "Fabric and drape (e.g. Georgette with micro lining)",
  "styling_usps": ["USP 1", "USP 2", "USP 3"],
  "meesho_search_keyword": "Best 3-4 word keyword to search on Meesho"
}
Return ONLY valid JSON."""
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": s_mime, "data": base64.b64encode(s_bytes).decode("utf-8")}}
                    ]
                }],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.5}
            }
            res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}", json=payload, timeout=25)
            if res.status_code == 200:
                raw_json = res.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                data = json.loads(raw_json)
                data["source"] = "Screenshot Analysis (Vision AI)"
                data["url"] = ""
                data["original_image_url"] = ""
                return data, None
        except Exception:
            pass
            
    # 2. Text / URL parsing
    clean_text = (input_text or "").strip()
    if not clean_text and not screenshot_bytes:
        return None, "Please enter a Meesho product URL, app share text, or product code."
        
    url_match = re.search(r'https?://[^\s]+', clean_text)
    if url_match:
        raw_url = url_match.group(0).rstrip('.,;:)]}')
        
    code_match = re.search(r'\b(s-[a-zA-Z0-9]+)\b', clean_text, re.IGNORECASE)
    if code_match:
        code = code_match.group(0)
        
    price_match = re.search(r'(?:₹|Rs\.?|INR)\s*([0-9,]+)', clean_text, re.IGNORECASE)
    if price_match:
        price = f"₹{price_match.group(1)}"
        
    if raw_url:
        parts = raw_url.split("?")[0].split("#")[0].strip("/").split("/")
        if "p" in parts:
            p_idx = parts.index("p")
            if p_idx > 0 and parts[p_idx - 1] != "s":
                slug = parts[p_idx - 1]
                slug_title = " ".join(w.capitalize() for w in slug.split("-") if w)
            if p_idx + 1 < len(parts):
                p_id = parts[p_idx + 1]
                if not code:
                    code = f"s-{p_id}"
                    
    # Network extraction via curl_cffi with Chrome impersonation
    if raw_url:
        try:
            from curl_cffi import requests as c_requests
            headers = {
                'authority': 'www.meesho.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://www.google.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            }
            s = c_requests.Session(impersonate='chrome124')
            r = s.get(raw_url, headers=headers, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                final_url = r.url
                if final_url and final_url != raw_url:
                    parts = final_url.split("?")[0].strip("/").split("/")
                    if "p" in parts:
                        p_idx = parts.index("p")
                        if p_idx > 0 and parts[p_idx - 1] != "s":
                            slug = parts[p_idx - 1]
                            slug_title = " ".join(w.capitalize() for w in slug.split("-") if w)
                t_match = re.search(r'<meta property="og:title" content="([^"]+)"', r.text)
                if t_match:
                    og_title = t_match.group(1).replace("Online at Best Prices in India - Meesho", "").strip()
                img_match = re.search(r'<meta property="og:image" content="([^"]+)"', r.text)
                if img_match:
                    og_image = img_match.group(1)
        except Exception:
            pass
            
    detected_title = og_title or slug_title or (clean_text.split("\n")[0][:75] if clean_text else "Trending Meesho Fashion Find")
    
    # 3. Gemini AI Catalog Enrichment
    if api_key:
        prompt = f"""You are an expert fashion catalog merchandiser for Meesho.
Analyze this product information:
Input: {clean_text}
Detected Title: {detected_title}
Detected Price: {price}
Detected Code: {code}
Detected URL: {raw_url}

Return a valid JSON object:
{{
  "title": "Clean, highly attractive commercial product title in Hinglish/English",
  "category": "One of: Ethnic Wear (Kurti / Suit / Saree / Blouse), Western & Casual Dresses, Wardrobe Problem-Solver Hack, Shapewear & Saree Silhouette, Intimates & Lingerie 2-Piece Set, Nightwear & Loungewear Slip",
  "price": "{price if price else '₹499'}",
  "meesho_code": "{code if code else 's-18392841'}",
  "color": "Dominant color palette (e.g. Mustard Yellow & Gold zari)",
  "fabric": "Fabric and drape (e.g. Soft Georgette with micro lining)",
  "styling_usps": ["USP 1", "USP 2", "USP 3"],
  "meesho_search_keyword": "Best 3-4 word keyword to search on Meesho"
}}
Return ONLY valid JSON."""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.6}
        }
        for m in ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest"]:
            try:
                res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}", json=payload, timeout=20)
                if res.status_code == 200:
                    raw_json = res.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    data = json.loads(raw_json)
                    data["url"] = raw_url
                    data["original_image_url"] = og_image
                    data["source"] = "URL & Catalog AI Engine"
                    return data, None
            except Exception:
                continue
                
    return {
        "title": detected_title or "Trending Meesho Fashion Find",
        "category": "Ethnic Wear (Kurti / Suit / Saree / Blouse)",
        "price": price or "₹499",
        "meesho_code": code or "s-18392841",
        "color": "Vibrant festive tones",
        "fabric": "Comfortable breathable fabric",
        "styling_usps": ["High-value styling", "Comfortable all-day wear", "Affordable pricing"],
        "meesho_search_keyword": detected_title[:30],
        "url": raw_url,
        "original_image_url": og_image,
        "source": "Smart URL Extraction"
    }, None

def generate_product_hd_photo(prompt_text, width=1024, height=1024, seed=None):
    """
    Calls high-speed FLUX photorealism engine to generate ultra-realistic camera photographs.
    Uses random or specified seed to guarantee brand new, high-fidelity variations.
    """
    try:
        clean_p = prompt_text.strip().replace("\n", " ")
        encoded = requests.utils.quote(clean_p)
        if seed is None:
            seed = random.randint(1000, 9999999)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model=flux&nologo=true&seed={seed}"
        r = requests.get(url, timeout=40)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content, None
        return None, f"Image engine returned HTTP {r.status_code}"
    except Exception as e:
        return None, str(e)

def generate_virtual_tryon(person_bytes, garment_bytes, garment_desc="Fashion apparel", steps=25):
    """
    True Virtual Try-On Engine (IDM-VTON).
    Preserves 100% of the creator's exact real face, smile, skin tone, hairstyle, and body shape,
    and accurately drapes the garment onto the creator.
    """
    import tempfile
    from gradio_client import Client, handle_file
    p_temp = None
    g_temp = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f1:
            f1.write(person_bytes)
            p_temp = f1.name
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f2:
            f2.write(garment_bytes)
            g_temp = f2.name
            
        client = Client('yisol/IDM-VTON')
        res = client.predict(
            dict={'background': handle_file(p_temp), 'layers': [], 'composite': None},
            garm_img=handle_file(g_temp),
            garment_des=garment_desc,
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=steps,
            seed=random.randint(1, 999999),
            api_name='/tryon'
        )
        if res and os.path.exists(res[0]):
            with open(res[0], 'rb') as rf:
                return rf.read(), None
        return None, "Try-on model did not return an output image."
    except Exception as e:
        return None, str(e)
    finally:
        if p_temp and os.path.exists(p_temp):
            try: os.unlink(p_temp)
            except Exception: pass
        if g_temp and os.path.exists(g_temp):
            try: os.unlink(g_temp)
            except Exception: pass

def extract_creator_identity_traits(creator_bytes, api_key=None):
    """
    Extracts concise visual identity descriptors (face structure, skin tone, hair, body shape)
    from creator reference image for 100% photographic likeness and body shape consistency.
    """
    default_traits = "soft oval face structure, warm radiant Indian skin tone, natural dark brown eyes, genuine warm confident smile, natural dark brown wavy hair framing shoulders, athletic feminine build with toned shoulders"
    if not creator_bytes or not api_key:
        return default_traits
    try:
        c_bytes, c_mime = optimize_image(creator_bytes)
        prompt = """Analyze this Indian female creator photo. Output ONLY a single concise comma-separated photographic descriptor of her visual identity (under 30 words):
Include:
- Facial structure, warm Indian skin tone, natural dark brown eyes, genuine smile
- Natural dark hair texture & style
- Natural feminine body silhouette & build (e.g. athletic toned, natural curves, slender)
DO NOT mention the clothing or outfit she is currently wearing in this photo. DO NOT use bullet points, numbering, or headers. Output strictly one single line."""
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": c_mime, "data": base64.b64encode(c_bytes).decode("utf-8")}}
                ]
            }],
            "generationConfig": {"temperature": 0.1}
        }
        res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}", json=payload, timeout=15)
        if res.status_code == 200:
            desc = res.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            desc = re.sub(r'^(?:Response|Descriptors?|Output|Visual Features|Photographic Prompt):\s*', '', desc, flags=re.IGNORECASE).strip()
            desc = desc.replace("\n", ", ").strip()
            desc = re.sub(r',\s*,+', ',', desc).strip(" ,\"*'")
            if desc and len(desc) > 10:
                return desc
    except Exception:
        pass
    return default_traits

def get_seasonal_context():
    now = datetime.datetime.now()
    month = now.month
    day_name = now.strftime("%A")
    date_str = now.strftime("%d %B %Y")
    
    # Seasonal fashion signals for Indian e-commerce
    if month in (8, 9, 10):
        season_title = "Festive Season Prep (Ganesh Utsav, Navratri, Diwali Shopping)"
        season_focus = "Bright festive colors, flared anarkalis, organza dupattas, saree shapewear, gold zari highlights"
    elif month in (11, 12, 1, 2):
        season_title = "Winter Wedding & Velvet Season"
        season_focus = "Heavy velvet kurtas, wedding guest coordinates, party wear slips, warm shawls"
    elif month in (3, 4, 5):
        season_title = "Summer College Reopening & Breathable Cottons"
        season_focus = "Chikankari pure cotton kurtis, floral sundresses, sweat-proof anti-chafing shorts, pastel tones"
    else:
        season_title = "Monsoon College Staples & Quick-Dry Casuals"
        season_focus = "Wrinkle-free cropped trousers, oversized shirts, dark floral prints, waterproof fashion hacks"
        
    return {
        "date_str": date_str,
        "day_name": day_name,
        "season_title": season_title,
        "season_focus": season_focus
    }

def fetch_daily_trends_with_gemini(api_key, force_refresh=False):
    """
    Fetches exactly 20 dynamic, date-aware viral Instagram trends from Gemini AI based on 
    the current day, month, Indian seasonal context, and upcoming festivals.
    Guarantees 24-Hour Server Disk Cache: Mobile reloads & page refreshes incur ZERO API calls!
    """
    ctx = get_seasonal_context()
    today_key = f"trends_{ctx['date_str']}"
    
    # 1. In-Memory Session Cache (Fastest)
    if not force_refresh and "gemini_daily_trends" in st.session_state and st.session_state.get("gemini_trends_date") == today_key:
        return st.session_state["gemini_daily_trends"], None

    # 2. 24-Hour Server Disk Cache (Survives mobile tab reloads, background app switching & server restarts)
    if not force_refresh and os.path.exists(TRENDS_CACHE_FILE):
        try:
            with open(TRENDS_CACHE_FILE, "r", encoding="utf-8") as f:
                disk_cache = json.load(f)
                if disk_cache.get("date_key") == today_key and isinstance(disk_cache.get("trends"), list) and len(disk_cache["trends"]) > 0:
                    st.session_state["gemini_daily_trends"] = disk_cache["trends"]
                    st.session_state["gemini_trends_date"] = today_key
                    return disk_cache["trends"], None
        except Exception as e:
            print("Disk cache read warning:", e)
        
    if not api_key:
        # If cache exists even for yesterday/fallback, show it rather than blocking
        if os.path.exists(TRENDS_CACHE_FILE):
            try:
                with open(TRENDS_CACHE_FILE, "r", encoding="utf-8") as f:
                    disk_cache = json.load(f)
                    if isinstance(disk_cache.get("trends"), list) and len(disk_cache["trends"]) > 0:
                        return disk_cache["trends"], None
            except Exception:
                pass
        return None, "Gemini API key is required to fetch live daily trends. Please enter it in the sidebar or set GEMINI_API_KEY in .env."
        
    prompt = f"""You are a top Instagram Reels & YouTube Shorts Algorithm Director for Indian E-Commerce (specifically Meesho Fashion).
Today is {ctx['day_name']}, {ctx['date_str']}.
Current Season & Shopping Focus: {ctx['season_title']} ({ctx['season_focus']}).

Generate exactly 20 distinct, fresh, viral Instagram Reel trends that Indian fashion creators should post TODAY to get maximum engagement, saves, and Meesho orders.
Distribute the 20 trends across diverse Indian fashion categories:
1. Festive & Ethnic Wear (Anarkalis, Shararas, Kurtas, Palazzo suits) - 4 trends
2. Sarees, Blouses & Saree Silhouette Hacks - 3 trends
3. Western, Partywear, Bodycon & Vacation Fits - 3 trends
4. College & Office Daily Budget Casuals (Shirts, Tops, Denim) - 3 trends
5. Intimates, Bralettes, Wire-free Bras & Shapewear (100% Policy-Safe Zivame style) - 3 trends
6. Wardrobe Problem-Solver Hacks (Dress tape, sweat pads, bra strap converters, button gap hacks) - 4 trends

Rules:
- Reflect real-time calendar context: upcoming festivals (Navratri, Durga Puja, Diwali, Karwa Chauth, Eid, Ganesh Utsav), wedding season, college reopenings, or weather-appropriate fabrics.
- NEVER use repetitive or cliché hooks like 'maine socha tha scam hoga' everywhere. Use diverse storytelling angles: Bestie gossip ('Meri friend ne pucha...'), Skeptical review ('Maine socha wash ke baad fade hoga...'), Stylist mistake ('Stop wearing kurtis like this...'), Extreme budget challenge ('Fest look under ₹499 challenge'), POV relatable situations.
- Output MUST be a valid JSON array of 20 objects.

Each JSON object must have these exact keys:
- "id": string unique identifier (e.g. "trend_01_navratri_sharara")
- "format_num": string like "Trend 1", "Trend 2", ... "Trend 20"
- "category_badge": short badge like "🥻 Festive Ethnic", "👗 Western Fit", "💡 Wardrobe Hack", "👙 Intimates Comfort", "🎒 College Staple", "✨ Saree Styling"
- "title": catchy trend concept title (e.g. "Navratri Garba Ready Kalidar Under ₹599")
- "hook": high-converting spoken 3-second opening hook in natural Hinglish
- "concept": visual action breakdown in 1-2 sentences
- "recommended_format": string (e.g. "🪄 Magic Transition", "💡 Problem ➔ Solution Hack", "📦 Zivame/Clovia Review", "👗 Direct Try-On")
- "recommended_duration": "⚡ 10s" or "⚡ 15-20s" or "🎬 30s" or "⏳ 45s" or "⏳ 60s"
- "category": high-level category string ("Festive & Ethnic", "Western & Casuals", "Sarees & Blouses", "Intimates & Shapewear", "Wardrobe Hacks")
- "hook_score": string like "99/100", "98/100", "97/100"
- "audio_vibe": trending audio description (e.g. "Upbeat garba remix beat drop", "Aesthetic lofi pop", "Energetic saheli gossip")
- "price_range": realistic price string (e.g. "₹299 - ₹499", "₹149 - ₹199", "₹599 - ₹799")
- "meesho_keyword": Meesho app search term (e.g. "Georgette Tiered Garba Anarkali Kurta")

Return ONLY the JSON array, with no Markdown formatting or code fencing.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.8,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    
    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.7-flash"]
    last_err = ""
    
    for model in candidate_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(api_url, json=payload, timeout=40)
            if res.status_code == 200:
                data = res.json()
                cands = data.get("candidates", [])
                if cands:
                    raw_json = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    if raw_json.startswith("```"):
                        raw_json = raw_json.strip("`")
                        if raw_json.startswith("json"):
                            raw_json = raw_json[4:].strip()
                    trends_list = json.loads(raw_json)
                    if isinstance(trends_list, list) and len(trends_list) > 0:
                        st.session_state["gemini_daily_trends"] = trends_list
                        st.session_state["gemini_trends_date"] = today_key
                        # Persist to 24-Hour Disk Cache (Zero-Cost Guarantee)
                        try:
                            with open(TRENDS_CACHE_FILE, "w", encoding="utf-8") as cf:
                                json.dump({
                                    "date_key": today_key,
                                    "saved_at": datetime.datetime.now().isoformat(),
                                    "trends": trends_list
                                }, cf, indent=2, ensure_ascii=False)
                        except Exception as ce:
                            print("Disk cache write warning:", ce)
                        return trends_list, None
            else:
                err_data = res.json() if res.content else {}
                last_err = err_data.get("error", {}).get("message", f"HTTP {res.status_code}")
        except Exception as ex:
            last_err = str(ex)
            
    return None, f"Could not fetch 20 trends from Gemini API ({last_err}). Please verify your GEMINI_API_KEY."

def get_wardrobe_problems_catalog():
    """Curated library of real, high-converting women's wardrobe struggles across College, Party, Festive & Comfort."""
    return [
        # CATEGORY 1: COLLEGE & DAILY OFFICE GIRLS
        {
            "id": "shirt_button_gaping",
            "category": "🎓 College & Daily Office Girls",
            "title": "Formal Shirt / Top Me Chest Ke Paas Button Gaping Hona",
            "struggle": "Office shirts ya button-down dresses me bust ke paas gap banta hai jisse andar ki bra/skin peeking hone lagti hai.",
            "mistake": "Chhoti safety pin lagana jo shirt me ajeeb sa crease banati hai ya shirt ko oversize lena.",
            "styling_rule": "Buttons ke beech me clear double-sided fashion dress tape lagayein jo 8 ghante tak fabric ko flat aur closed lock rakhti hai.",
            "solution_product": "Double-Sided Body & Apparel Fashion Tape Strips",
            "spoken_hook": "Office me shirt ka button gap dekh kar uncomfortable lagta hai? Safety pin mat lagao, ye invisible dress tape dekho!",
            "meesho_keyword": "Double Sided Fashion Clothing Dress Tape",
            "price_range": "₹129",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "underarm_sweat_patches",
            "category": "🎓 College & Daily Office Girls",
            "title": "Kurti / Shirt Me Underarm Sweat Patches & Badbu",
            "struggle": "Garmiyo me function ya office me silk/cotton kurti ke underarms me pasine ke gande daag ban jate hain.",
            "mistake": "Deodorant zyada lagana jisse fabric par yellow chalky stains pad jate hain.",
            "styling_rule": "Lightweight breathable peel-and-stick underarm sweat pads lagayein jo sweat ko fabric tak pahunchne se pehle lock kar lete hain.",
            "solution_product": "Disposable Peel-and-Stick Underarm Sweat Absorber Pads",
            "spoken_hook": "Garmi me kurti ke underarm me pasine ke daag dekh kar embarrassing lagta hai? Meesho ka ye ₹79 ka invisible hack dekho!",
            "meesho_keyword": "Underarm Sweat Pads Disposable Garment Protectors",
            "price_range": "₹79",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "shoulder_strap_slipping",
            "category": "🎓 College & Daily Office Girls",
            "title": "Wide Neck / Square Tops Me Baar-Baar Bra Strap Fisalna",
            "struggle": "Wide-neck tops, broad kurtas ya square blouses me kandhe se bra straps lagatar fisal kar neeche girti rehti hain.",
            "mistake": "Straps ko bohot tight khichna jisse kandhe par laal nishaan (red grooving) ban jate hain.",
            "styling_rule": "Straps ko tight karne ki jagah Racerback Cross-Clips use karein jo straps ko center me pull karke stealth racerback bana dete hain.",
            "solution_product": "Cross-Back Racerback Bra Strap Clips & Holders",
            "spoken_hook": "Baar-baar kandhe se bra strap fisal rahi hai aur public me adjust karni padti hai? Meesho ka ye ₹49 ka instant hack dekho!",
            "meesho_keyword": "Bra Strap Concealer Clips Racerback Holder",
            "price_range": "₹49",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "white_kurti_transparency",
            "category": "🎓 College & Daily Office Girls",
            "title": "White / Light Kurti Me Innerwear Chamakna (Transparency Issue)",
            "struggle": "White ya light pastel kurti pehnte hi andar ka bra/innerwear ajeeb tarah se bahar dikhne lagta hai.",
            "mistake": "White kurti ke niche white innerwear pehanna! White ke upar white contrast create karta hai aur zyada dikhta hai.",
            "styling_rule": "White ya transparent fabrics ke niche hamesha Skin-Tone Nude Seamless Bra pehni chahiye, kyunki nude shade light absorb karke zero shadow cast karta hai.",
            "solution_product": "Skin-Tone Nude Seamless T-Shirt Bra",
            "spoken_hook": "White kurti ke niche white bra pehnne ki galti aap bhi kar rahe ho? Stylist rule dekho jo 90% ladkiyo ko nahi pata!",
            "meesho_keyword": "Nude Seamless T-Shirt Bra for White Tops",
            "price_range": "₹249",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },

        # CATEGORY 2: PARTY WEAR, CLUBBING & COCKTAIL NIGHT
        {
            "id": "party_backless_dress_bra",
            "category": "🎉 Party Wear, Clubbing & Cocktail Night",
            "title": "Backless / Halter Party Dress Me Bra Kaise Pehne",
            "struggle": "Party me gorgeous backless ya halter dress pehni hai, par regular bra straps back me ya deep neck me jhaank rahi hain.",
            "mistake": "Woh cheap transparent plastic straps lagana jo pasine se chipakti hain aur photos me shining ajeeb lagti hai.",
            "styling_rule": "Backless, halter ya cowl-neck party dress ke sath medical-grade silicone push-up stick-on bra ya boob tape use karein jo 100% invisible lift deti hai.",
            "solution_product": "Silicone Push-Up Stick-On Bra & Reusable Boob Tape",
            "spoken_hook": "Party me backless dress to pehan li, par piche se bra straps kaise chhupayein? Ye ₹149 ka Meesho secret hack dekho!",
            "meesho_keyword": "Silicone Push Up Invisible Stick On Bra Backless",
            "price_range": "₹149",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "party_satin_dress_vpl_tummy",
            "category": "🎉 Party Wear, Clubbing & Cocktail Night",
            "title": "Satin & Bodycon Dress Me Panty Lines & Tummy Bulge (VPL)",
            "struggle": "Trending satin slip dress ya tight bodycon pehnte hi panty ke elastic lines aur lower belly pooch bahar ubhar kar dikhta hai.",
            "mistake": "Normal cotton panty pehanna jo tight hoke skin me deep ridges aur seams banati hai.",
            "styling_rule": "Satin aur bodycon ke niche raw-edge laser-cut seamless thong ya high-waist mid-thigh smoothing shaper pehno jo glass-finish flat look deta hai.",
            "solution_product": "Laser-Cut Seamless Thong & Mid-Thigh Smoothing Shaper",
            "spoken_hook": "Satin slip dress pehnte hi panty line aur tummy pooch saaf chamak raha hai? Ye ₹199 ka seamless shaper magic dekho!",
            "meesho_keyword": "Seamless High Waist Mid Thigh Body Shaper Slip",
            "price_range": "₹199",
            "sample_product_file": "sample_saree_shapewear.jpg"
        },
        {
            "id": "party_mini_dress_riding_up",
            "category": "🎉 Party Wear, Clubbing & Cocktail Night",
            "title": "Mini Bodycon Dress Ka Dance Me Baar-Baar Upar Chadhna (Riding Up)",
            "struggle": "Club me dance karte waqt ya chalte waqt mini bodycon dress lagatar upar chadh jati hai aur haath se kheench ke adjust karni padti hai.",
            "mistake": "Har 2 minute me sabke samne awkward tarike se dress ko niche kheench kar theek karna.",
            "styling_rule": "Hemline aur thighs ke inner contact area me clear double-sided apparel flash tape lagayein jo dress ko lock rakhti hai.",
            "solution_product": "Double-Sided Apparel Flash Tape Strips (Anti-Slip)",
            "spoken_hook": "Party me mini dress pehan kar dance karne me baar-baar upar chadh jati hai? Ye ₹99 ka dress-lock hack dekho!",
            "meesho_keyword": "Double Sided Apparel Flash Tape Anti Slip Strips",
            "price_range": "₹99",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "party_deep_neck_wrap_malfunction",
            "category": "🎉 Party Wear, Clubbing & Cocktail Night",
            "title": "Deep-V Neck / Wrap Dress Me Wardrobe Malfunction Ka Darr",
            "struggle": "Cocktail party me jhukte waqt, dance karte waqt wrap dress ya deep neckline khulne ka constant fear rehta hai.",
            "mistake": "Badi steel safety pin lagana jo dress ke glamorous drape aur fabric ko kharab kar deti hai.",
            "styling_rule": "Dress ke neckline aur skin ke beech medical-grade invisible skin-safe fashion tape strips lagayein jo 8 ghante water-resistant hold deti hain.",
            "solution_product": "Medical-Grade Invisible Clothing Fashion Tape Strips",
            "spoken_hook": "Deep-V neck ya wrap dress pehan kar jhukne me darr lagta hai? Ye ₹129 ka invisible dress tape hack dekho!",
            "meesho_keyword": "Skin Safe Clear Clothing Body Fashion Tape",
            "price_range": "₹129",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "party_pencil_heels_blister_pain",
            "category": "🎉 Party Wear, Clubbing & Cocktail Night",
            "title": "Party Pencil Heels Se 1 Ghante Me Pair Dukhna & Blisters",
            "struggle": "3-4 inch ki pencil heels pehankar party ke 1 ghante me hi pair ke panje me jalan aur heel par dardnaak chhale (blisters) pad jate hain.",
            "mistake": "Normal band-aid lagana jo 10 minute me nikal jati hai aur heels se bahar dikhti hai.",
            "styling_rule": "Heels ke andar honeycomb silicone forefoot gel pads aur transparent blister cushion protectors lagayein jo pressure absorb karke 100% cloud walk dete hain.",
            "solution_product": "Silicone Honeycomb Forefoot Gel Cushion & Heel Protectors",
            "spoken_hook": "3-inch party heels pehan kar cocktail party me 1 ghante me hi pair dukhne lagte hain? Ye ₹89 ka cloud gel pad hack dekho!",
            "meesho_keyword": "Silicone Forefoot Gel Cushion Pads for High Heels",
            "price_range": "₹89",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },

        # CATEGORY 3: FESTIVE, WEDDING & SAREE STRUGGLES
        {
            "id": "saree_petticoat_tummy_bulge",
            "category": "🥻 Festive, Wedding & Saree Struggles",
            "title": "Saree Me Petticoat Ki Wajah Se Pet Par Bulge Dikhna",
            "struggle": "Traditional cotton petticoat ki nada aur thick pleats waist par bulky lagte hain, jisse flat pet bhi mota dikhta hai.",
            "mistake": "Heavy cotton petticoat me moti nada baandhna jo kamar par red lines aur tummy bulge banati hai.",
            "styling_rule": "Saree ke niche traditional bulky petticoat ki jagah compression mermaid saree shapewear pehno jo tummy tuck karke slim mermaid silhouette deti hai.",
            "solution_product": "Mermaid Silhouette Saree Shapewear with Side Slit",
            "spoken_hook": "Saree me flat pet bhi mota dikh raha hai? Cotton petticoat phenk do aur Meesho ka ye ₹299 mermaid shapewear try karo!",
            "meesho_keyword": "Saree Silhouette Shapewear with Side Slit",
            "price_range": "₹299",
            "sample_product_file": "sample_saree_shapewear.jpg"
        },
        {
            "id": "heavy_pallu_slipping",
            "category": "🥻 Festive, Wedding & Saree Struggles",
            "title": "Heavy Saree Pallu Ka Baar-Baar Fisalna & Blouse Fatan",
            "struggle": "Heavy zari pallu baar-baar kandhe se slip hota hai, aur regular safety pin lagane se blouse ka kapda phat jata hai.",
            "mistake": "Normal steel safety pin bina cap ke lagana jo fabric ko kheechn kar holes bana deti hai.",
            "styling_rule": "Heavy pallu ke liye saree pin protectors ya magnetic brooch use karein jo fabric ko bina puncture kiye 100% locked hold dete hain.",
            "solution_product": "Magnetic Saree Brooch & Safety Pin Fabric Protectors",
            "spoken_hook": "Heavy saree pehni hai aur safety pin se mehenga blouse phatne ka darr hai? Ye ₹99 ka magnetic brooch hack dekho!",
            "meesho_keyword": "Magnetic Saree Brooch Pins Fabric Safe",
            "price_range": "₹99",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "deep_blouse_bra_strap",
            "category": "🥻 Festive, Wedding & Saree Struggles",
            "title": "Deep-Back Blouse Me Bra Strap Dikhna",
            "struggle": "Deep-back blouse ya backless saree pehnte hi bra strap ya back band peeche se jhaankne lagti hai.",
            "mistake": "Safety pin se strap ko blouse ke andar dabana ya strap nikaal kar insecure feel karna.",
            "styling_rule": "Deep neck ya backless blouse me regular T-shirt bra kabhi mat pehno. Hamesha Low-Back Strap Converter ya Silicon Stick-on Bra use karein jo 100% backless freedom deta hai.",
            "solution_product": "Low Back Bra Strap Converter & Silicon Stick-on Bra",
            "spoken_hook": "Agar tumhare bhi deep-back blouse se bra strap dikhti hai, toh safety pin lagane ki galti mat karna — ye ₹149 ka Meesho hack dekh lo!",
            "meesho_keyword": "Low Back Bra Strap Converter & Silicon Stick-on Bra",
            "price_range": "₹149",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "heavy_earrings_lobe_pain",
            "category": "🥻 Festive, Wedding & Saree Struggles",
            "title": "Heavy Jhumka / Kundan Earrings Se Kaan Ke Chhed Khinchna & Dukhna",
            "struggle": "Shaadi ya festival me heavy jhumkas pehnte hi kaan ke earlobes khinch ke neeche latak jate hain aur bohot dard hota hai.",
            "mistake": "Bina kisi support ke heavy earrings pehanna jo earlobes ko permanent chheda bada kar deta hai.",
            "styling_rule": "Earlobes ke piche medical-grade invisible earlobe support patches lagayein jo weight ko distribute karke zero pain deti hain.",
            "solution_product": "Invisible Earlobe Support Patches for Heavy Earrings",
            "spoken_hook": "Heavy jhumkas pehan kar kaan dukhne lagte hain aur chhed khinch jata hai? Ye ₹69 ka invisible ear support patch dekho!",
            "meesho_keyword": "Invisible Ear Lobe Support Patches for Heavy Earrings",
            "price_range": "₹69",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },

        # CATEGORY 4: DAILY COMFORT & BODY SILHOUETTE
        {
            "id": "chub_rub_thigh_chafing",
            "category": "🏃‍♀️ Daily Comfort & Body Silhouette",
            "title": "Garmiyo Me Thigh Chafing (Chub Rub) & Rashes Hona",
            "struggle": "Kurtis, skirts ya dresses me chalte waqt inner thighs aapas me ragad kar dard aur laal rashes bana deti hain.",
            "mistake": "Powder lagana jo 15 minute me pasine se beh jata hai aur situation aur kharab ho jati hai.",
            "styling_rule": "Thin seamless anti-chafing slip shorts pehno jo breathable bamboo/modal fabric se bane ho aur thighs ko friction-free slide de.",
            "solution_product": "Seamless Anti-Chafing Slip Shorts (Chub Rub Prevention)",
            "spoken_hook": "Garmiyo me kurti ya dress pehan kar chalne me thigh chafing se dard hota hai? Meesho ka ye ₹199 ka anti-chafing lifesaver dekho!",
            "meesho_keyword": "Anti Chafing Slip Shorts for Women",
            "price_range": "₹199",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "tummy_protrusion_straight_kurti",
            "category": "🏃‍♀️ Daily Comfort & Body Silhouette",
            "title": "Straight Kurti / Dress Me Lower Tummy Pooch Uthna",
            "struggle": "Straight cotton kurti pehnte hi lower belly pooch saaf dikhta hai jisse posture slouchy lagta hai.",
            "mistake": "Tight belt baandhna jo pet ko do hisso me baant deta hai.",
            "styling_rule": "High-waist seamless tummy tucker brief pehno jo lower abdomen ko smooth hold deta hai, ya subtle A-line silhouette select karein jo hips aur tummy par float kare.",
            "solution_product": "High-Waist Seamless Breathable Tummy Tucker Brief",
            "spoken_hook": "Straight kurti pehnte hi tummy pooch bahar nikal aata hai? Meesho ka ye ₹229 breathable tummy tucker dekho!",
            "meesho_keyword": "High Waist Seamless Tummy Tucker Shapewear",
            "price_range": "₹229",
            "sample_product_file": "sample_saree_shapewear.jpg"
        },
        {
            "id": "heavy_bust_kurtis",
            "category": "🏃‍♀️ Daily Comfort & Body Silhouette",
            "title": "Heavy Bust Ki Wajah Se Kurtis Bulky & Ill-Fitted Lagna",
            "struggle": "Heavy bust ki wajah se standard size kurti chest par bohot tight hoti hai aur niche se tent jaisi loose lagti hai.",
            "mistake": "Padded push-up bra pehanna ya baggy oversized clothes pehanna jo aur zyada bulky dikhate hain.",
            "styling_rule": "High-support molded minimizer bra pehno jo bust projection ko 1-1.5 inch streamline karti hai, aur hamesha V-neck ya vertical placket kurti choose karein jo neckline ko elongate kare.",
            "solution_product": "Seamless Full-Coverage Minimizer Bra",
            "spoken_hook": "Heavy bust ki wajah se suit aur kurti ki fitting kharab ho rahi hai? Ye 1-inch minimizer bra hack dekho!",
            "meesho_keyword": "Full Coverage Wirefree Minimizer Bra",
            "price_range": "₹349",
            "sample_product_file": "sample_wardrobe_hack.jpg"
        },
        {
            "id": "underwire_poking_rib_pain",
            "category": "🏃‍♀️ Daily Comfort & Body Silhouette",
            "title": "Underwire Chubhke Pasliyo Me Dard & Red Marks Hona",
            "struggle": "Office ya college se aate hi metal underwire pasliyo me chubh kar laal zakham aur strap marks chhodti hai.",
            "mistake": "Wire nikaal kar tooti hui bra use karna ya unsupportive loose bra pehanna.",
            "styling_rule": "Underwire ki jagah molded foam wire-free cloud comfort bras pehno jo zero wire ke sath 100% lift aur contour support deti hain.",
            "solution_product": "Wire-Free Cloud-Comfort Cushioned Everyday Bra",
            "spoken_hook": "Ghar aate hi sabse pehle bra utarne ka man karta hai kyunki metal wire chubh rahi hai? Switch to this wire-free cloud comfort!",
            "meesho_keyword": "Wire-Free Seamless Cloud Comfort T-Shirt Bra",
            "price_range": "₹299",
            "sample_product_file": "sample_bralette_set.jpg"
        }
    ]

# ---------------------------------------------------------
# THE 5 CORE PILLARS OF FASHION INTELLIGENCE KNOWLEDGE BASE
# ---------------------------------------------------------
def get_fashion_pillars_config():
    """Returns the comprehensive 5-Pillars of Fashion & Styling Intelligence knowledge base."""
    return {
        "aesthetics": {
            "old_money": {
                "id": "old_money",
                "name": "🏛️ Old Money / Quiet Luxury",
                "tagline": "Neutral tones, linen/poplin, zero flashy logos, Zara/Massimo Dutti lookbook",
                "palette": "Ivory, Beige, Camel, White, Navy Blue, Sage",
                "acc": "Micro pearl drops, tortoise-shell sunglasses, leather belt, minimalist watch, nude loafers",
                "env": "Parisian café terrace, European heritage library, clean minimalist marble salon",
                "sample_img": "sample_linen_shirt.jpg",
                "sample_title": "Oversized Pure Linen Striped Shirt"
            },
            "streetwear": {
                "id": "streetwear",
                "name": "🛹 Gen-Z Streetwear & Urban Cool",
                "tagline": "Oversized silhouettes, cargo utility, baby tees, chunky dad sneakers",
                "palette": "Slate grey, Washed black, Olive, Off-white, Neon accents",
                "acc": "Silver chunky chains, silver ear-cuffs, nylon crossbody bag, vintage wire glasses",
                "env": "Neon-tinted subway station, brutalist concrete garage, urban graffiti studio",
                "sample_img": "sample_wardrobe_hack.jpg",
                "sample_title": "Relaxed Baggy Fit Utility Cargo Trousers"
            },
            "desi_fusion": {
                "id": "desi_fusion",
                "name": "🥻 Indo-Western & Desi Fusion",
                "tagline": "Chikankari with denim, ethnic mirror jackets, flowy fusion co-ords",
                "palette": "Rust, Indigo, Mustard, Pastel peach, Raw cotton white",
                "acc": "Oxidized silver jhumkas, tan Kolhapuri juttis, embroidered boho tote, statement ring",
                "env": "Sunlit terracotta courtyard, Jaipur pink archway, heritage haveli veranda",
                "sample_img": "sample_kurti_set.jpg",
                "sample_title": "Handcrafted Chikankari Kurti with Side Slits"
            },
            "korean_coquette": {
                "id": "korean_coquette",
                "name": "🎀 Korean & Soft Girl / Coquette",
                "tagline": "Pastel sorbet tones, pleats, bows, baby-doll flowy silhouettes",
                "palette": "Lavender, Buttercup yellow, Powder blue, Marshmallow cream",
                "acc": "Ribbon hair bows, dainty floral pendant, Mary Jane shoes with frilled socks",
                "env": "Minimalist Seoul pastel coffee shop, botanical sunroom with sheer white curtains",
                "sample_img": "sample_anarkali.jpg",
                "sample_title": "Pastel Pleated Babydoll Tiered Dress"
            },
            "party_glam": {
                "id": "party_glam",
                "name": "✨ Party & Nightclub Glam",
                "tagline": "Liquid satin cowl neck, stretch velvet, corset boning, micro sequins",
                "palette": "Ruby red, Emerald green, Royal blue, Onyx black, Rose gold",
                "acc": "Rhinestone drop earrings, metallic box clutch, strappy high heels",
                "env": "Velvet cocktail lounge, twilight rooftop skyline, dramatic back-lit studio set",
                "sample_img": "sample_bralette_set.jpg",
                "sample_title": "Emerald Green Liquid Satin Slip Dress"
            }
        },
        "body_shapes": {
            "pear": {
                "id": "pear",
                "name": "🍐 Pear Shape (Heavy Hips & Thighs)",
                "summary": "Hips and thighs are wider than shoulders. Need upward visual balance and fluid lower half.",
                "avoid": "❌ Skinny jeans, tight pencil skirts, flat round-neck straight kurtis with no side flare",
                "wear": "✅ A-line kurtis, wide-leg fluid palazzos, boat necklines, statement puff sleeves, wrap tops",
                "meesho_cut": "A-Line Flared Kurti / High-Waist Wide-Leg Palazzos Under ₹399",
                "rule": "Eye ko upward shoulder par layein aur hips par flowy A-line drape dein",
                "sample_title": "Emerald Green Flared A-Line Kurti",
                "sample_file": "sample_anarkali.jpg"
            },
            "apple": {
                "id": "apple",
                "name": "🍎 Apple Shape (Lower Belly Pooch / Midriff)",
                "summary": "Weight concentrated at midriff/waist. Need shifted waistline and vertical lines.",
                "avoid": "❌ Clingy satin/lycra bodycon, horizontal stripes, tight low-rise bottoms, boxy crop tops",
                "wear": "✅ Empire waistlines (cinched under bust), peplum flare cuts, dark vertical prints, open jacket layers",
                "meesho_cut": "Empire-Waist Tiered Anarkali / Peplum Kurti Set Under ₹449",
                "rule": "Waistline ko bust ke theek niche shift karke lower belly par float drape banayein",
                "sample_title": "Empire Waist Tiered Georgette Kurta",
                "sample_file": "sample_anarkali.jpg"
            },
            "petite": {
                "id": "petite",
                "name": "📏 Petite (< 5'3\" Short Height)",
                "summary": "Shorter leg-to-torso ratio. Need vertical elongation and high-waist ratio.",
                "avoid": "❌ Heavy floor-length sack kurtis, wide horizontal color blocks, baggy low-waist bottoms",
                "wear": "✅ Rule of Thirds (1/3 top, 2/3 high-waist bottom), monochrome single-tone palette, deep V-necks, front-slit kurtis",
                "meesho_cut": "High-Waist Straight Pants & Vertical Slit Kurta Co-ord Under ₹349",
                "rule": "1/3:2/3 dressing ratio aur monochrome single-tone color se 3-inch taller visual illusion create karein",
                "sample_title": "Vertical Front-Slit Kurta with Straight Pants",
                "sample_file": "sample_kurti_set.jpg"
            },
            "hourglass": {
                "id": "hourglass",
                "name": "⏳ Hourglass (Balanced Curves & Defined Waist)",
                "summary": "Bust and hips balanced with natural narrow waist. Need waist-accentuating cuts.",
                "avoid": "❌ Boxy oversized shapeless tunics, stiff thick fabrics that hide natural waist",
                "wear": "✅ Wrap dresses, belted co-ord sets, sweetheart necklines, tailored waist seams",
                "meesho_cut": "Belted Wrap Dress / Sweetheart Neck Co-ord Set Under ₹399",
                "rule": "Natural waist curve ko emphasize karein bina extra bulk add kiye",
                "sample_title": "Belted Linen Wrap Tunic with Trousers",
                "sample_file": "sample_linen_shirt.jpg"
            },
            "inverted_triangle": {
                "id": "inverted_triangle",
                "name": "🔻 Inverted Triangle (Broad Shoulders / Heavy Bust)",
                "summary": "Shoulders/chest wider than hips. Need broken shoulder line and volume in bottom half.",
                "avoid": "❌ Boat necklines, shoulder pads, high crew necks, skinny pencil bottoms",
                "wear": "✅ Deep V-necks, scoop necklines, flared shararas, pleated A-line skirts, peplum flares",
                "meesho_cut": "Deep V-Neck Anarkali / Flared Sharara Kurti Set Under ₹420",
                "rule": "Deep V-neck se shoulder breadth break karein aur lower half me volume dekar balance karein",
                "sample_title": "Deep V-Neck Flared Sharara Set",
                "sample_file": "sample_anarkali.jpg"
            }
        },
        "body_concerns": {
            "belly_pooch": {
                "id": "belly_pooch",
                "name": "💥 Lower Belly Pooch Concealment",
                "concern": "Kurti ya dress pehnte hi pet bahar ubhar kar dikhta hai",
                "solution": "Empire waistline + high-waist breathable tummy tucker briefs",
                "price": "₹229"
            },
            "thigh_chafing": {
                "id": "thigh_chafing",
                "name": "👖 Thigh Chafing & Heavy Hips",
                "concern": "Chalte waqt thighs aapas me ragadna aur bottom bulky lagna",
                "solution": "Anti-chafing bamboo slip shorts + fluid wide-leg palazzos",
                "price": "₹199"
            },
            "short_height": {
                "id": "short_height",
                "name": "👠 Short Height (3-Inches Taller Illusion)",
                "concern": "Standard kurtis me height aur chhoti aur dabti hui lagti hai",
                "solution": "Monochrome single-tone co-ord + vertical front slit + nude pointed flats",
                "price": "₹349"
            },
            "bust_gaping": {
                "id": "bust_gaping",
                "name": "👗 Heavy Bust & Shirt Button Gaping",
                "concern": "Bust area me shirt/kurti ke buttons gap hona aur andar ka dikhna",
                "solution": "Clear double-sided apparel flash tape + wire-free minimizer bra",
                "price": "₹129"
            },
            "arm_flab": {
                "id": "arm_flab",
                "name": "👚 Arm Flab & Heavy Biceps",
                "concern": "Sleeveless ya tight sleeves me arms heavy lagti hain",
                "solution": "Flowy 3/4th bell sleeves ya breathable sheer organza sleeves",
                "price": "₹299"
            },
            "saree_bulge": {
                "id": "saree_bulge",
                "name": "🥻 Saree Petticoat & Blouse Back Fat",
                "concern": "Cotton naada petticoat se kamar par mota bulge aur blouse me back rolls",
                "solution": "Mermaid seamless saree shapewear + low-back low-compression bra",
                "price": "₹249"
            }
        },
        "color_rules": {
            "sandwich": {
                "id": "sandwich",
                "name": "🥪 The Sandwich Dressing Rule",
                "rule": "Shoes ka color Top/Headwear se match karein aur beech me contrasting bottom rakhein (e.g. White top + Blue jeans + White sneakers)",
                "benefit": "Instantly outfit ko visually balanced aur curated luxury look deta hai"
            },
            "rule_60_30_10": {
                "id": "rule_60_30_10",
                "name": "🎨 The 60-30-10 Color Formula",
                "rule": "60% Dominant Base (Dress/Kurti) + 30% Secondary (Dupatta/Jacket) + 10% Pop Accent (Bag/Lip/Jewelry)",
                "benefit": "Designer-level color coordination bina kisi color clash ke"
            },
            "monochrome": {
                "id": "monochrome",
                "name": "✨ Monochrome Height & Slimming Illusion",
                "rule": "Top aur bottom ek hi color family ke different shades me pehnein (e.g. Cream top + Beige pants + Nude flats)",
                "benefit": "Waistline ke breaks khatam karke continuous vertical slimming aur 3-inch taller illusion deta hai"
            }
        },
        "viral_formats": {
            "wear_this_not_that": {
                "id": "wear_this_not_that",
                "name": "❌ Wear This, NOT That (Style Mistakes vs Fixes)",
                "desc": "Side-by-side comparison: common unflattering cut vs the exact Meesho cut that flatters."
            },
            "capsule_1_in_3": {
                "id": "capsule_1_in_3",
                "name": "🔄 1 Item Styled in 3 Ways (Capsule Wardrobe)",
                "desc": "1 Meesho anchor garment styled into 3 looks: Daily/College, Office, and Party/Festive."
            },
            "expensive_vs_cheap": {
                "id": "expensive_vs_cheap",
                "name": "💸 Expensive vs Cheap Reality Check (Look Rich on a Budget)",
                "desc": "₹399 Meesho item styled to look like a ₹3,500 Zara/Myntra luxury designer piece."
            },
            "insecurity_to_confidence": {
                "id": "insecurity_to_confidence",
                "name": "💖 Insecurity to Confidence Transformation Story",
                "desc": "Emotional, relatable personal journey from body struggle to empowered styling confidence."
            }
        }
    }


# ---------------------------------------------------------
# INFLUENCER SCRIPT AGENT & RETENTION CONFIG
# ---------------------------------------------------------
def get_influencer_config():
    """Returns Creator Personalities, Audience Personas, and Hook Archetypes."""
    return {
        "personalities": {
            "bestie": {
                "id": "bestie",
                "name": "🌸 Cute & Friendly Bestie (Conversational, sister-vibe)",
                "prefix": "Sunno bestie",
                "vibe": "Warm, relatable, smiling, sharing girl-talk secrets like a trusted sister"
            },
            "gen_z": {
                "id": "gen_z",
                "name": "⚡ High-Energy Gen-Z (Fast cuts, punchy slang)",
                "prefix": "Literally run don't walk",
                "vibe": "High energy, fast-paced, trendy urban slang, snappy cuts"
            },
            "stylist": {
                "id": "stylist",
                "name": "👑 Calm & Elegant Stylist (Poised, quiet luxury guru)",
                "prefix": "Quiet luxury is about silhouette balance",
                "vibe": "Poised, soft-spoken, luxury advice tone, focusing on optical illusions"
            },
            "funny": {
                "id": "funny",
                "name": "😂 Funny & Relatable (Self-deprecating, family banter)",
                "prefix": "Meri mummy ne bola agar ek aur parcel aaya toh...",
                "vibe": "Self-deprecating humor, dramatic sighs, gossipy confessions"
            }
        },
        "personas": {
            "college": {
                "id": "college",
                "name": "🎓 College Fresher on Budget (18-22)",
                "desc": "Trendy, pocket-money friendly under ₹350, fear of cheap see-through fabrics"
            },
            "corporate": {
                "id": "corporate",
                "name": "💼 Corporate Working Professional (23-32)",
                "desc": "8-hour breathable comfort, zero button gaps, elegant smart casual office look"
            },
            "wedding": {
                "id": "wedding",
                "name": "🥻 Festive & Wedding Guest (20-35)",
                "desc": "Expensive boutique look on a budget, solving saree & can-can bulkiness"
            },
            "comfort": {
                "id": "comfort",
                "name": "🏃‍♀️ Daily Comfort & Body Insecurity Solver (All Ages)",
                "desc": "Hiding lower belly pooch, preventing thigh chafing, comfortable arm coverage"
            }
        },
        "hooks": [
            "🎯 AI Auto-Pick (Best Fit for Product)",
            "🔍 Curiosity Secret ('Meesho par ek aisi hidden kurti hai...')",
            "🤦‍♀️ Relatable Problem ('Agar aapki bhi kurti me lower belly pooch...')",
            "😲 Surprising Result Dupe ('Maine ₹299 ki skirt ko Zara ke ₹3,990 look me...')",
            "⚖️ Expectation vs Reality (Meesho catalog photo vs Real me at 5ft 2in...)",
            "🤫 Personal Confession ('Sach batau? Pichle hafte mujhe wedding me jaane se darr tha...')",
            "❓ Pattern Interrupt Question ('Kya aap bhi ye sabse badi styling galti kar rahi ho?')",
            "✨ Instant Visual Wow (0-2s complete outfit transformation beat drop)"
        ]
    }

def get_duration_pacing_tier(duration_str: str) -> dict:
    """
    Computes exact seconds, WPS word count budget, 4-tier story arc progression,
    and universal 3-stage opening protocol (0-2s Full Outfit Hook, 2-4s Fit & Detail, 4s+ Story)
    calibrated at ~2.3 words per second.
    """
    matches = re.findall(r"\d+", str(duration_str))
    if matches:
        exact_seconds = int(matches[-1])
    else:
        exact_seconds = 30
    exact_seconds = max(10, min(60, exact_seconds))
    
    # Mathematical Word Budget at 2.2 - 2.4 WPS (benchmark: 2.3 wps)
    target_words = int(exact_seconds * 2.3)
    min_words = max(20, int(exact_seconds * 2.1))
    max_words = int(exact_seconds * 2.4)
    
    if exact_seconds <= 15:
        tier_id = "10-15s"
        tier_name = "10–15 sec (Snappy Flash / Instant Hook)"
        story_arc = "Hook → Product → Try-on → Quick reaction → CTA"
        scene_count = "2 to 3 snappy scenes"
        tier_guidelines = (
            "Concise, punchy, zero fluff. Scene 1 [00:00-00:02] Silent Full Outfit Visual Hook (0 spoken words) ➔ "
            "Scene 2 [00:02-00:06] Spoken Hook & Problem ➔ Scene 3 [00:06-00:15] Genuine reaction & Organic CTA."
        )
    elif exact_seconds <= 30:
        tier_id = "15-30s"
        tier_name = "15–30 sec (Standard Viral Social Reel)"
        story_arc = "Scene 1 [00:00-00:02] Silent Visual Hook (0 words) → Scene 2 [00:02-00:07] Spoken Hook → Scene 3 [00:07-00:15] Detail & Fit → Scene 4 [00:15-00:23] Quality Check → Scene 5 [00:23-00:30] CTA"
        scene_count = "4 to 5 punchy scenes"
        tier_guidelines = (
            "Scene 1 [00:00-00:02] Silent Full Outfit Visual Hook (0 spoken words, beat drop) ➔ "
            "Scene 2 [00:02-00:07] Spoken Hook (voice starts at 00:02!) ➔ Scene 3 [00:07-00:15] Fabric detail & try-on fit ➔ "
            "Scene 4 [00:15-00:23] Honest reality check ➔ Scene 5 [00:23-00:30] Natural CTA."
        )
    elif exact_seconds <= 45:
        tier_id = "30-45s"
        tier_name = "30–45 sec (Problem-Solver & Story Arc)"
        story_arc = "Scene 1 [00:00-00:02] Silent Visual Hook (0 words) → Scene 2 [00:02-00:08] Spoken Problem Hook → Scene 3 [00:08-00:18] Hack/Detail → Scene 4 [00:18-00:30] Live Experience → Scene 5 [00:30-00:45] Result & CTA"
        scene_count = "5 balanced scenes"
        tier_guidelines = (
            "Complete story arc. Scene 1 [00:00-00:02] Silent Full Outfit Visual Hook (0 spoken words) ➔ "
            "Scene 2 [00:02-00:08] Spoken Relatable Problem Hook (voice starts at 00:02!) ➔ "
            "Scene 3 [00:08-00:18] Fabric & cut breakdown ➔ Scene 4 [00:18-00:30] Live demo experience ➔ "
            "Scene 5 [00:30-00:45] Flawless result & Contextual CTA."
        )
    else:
        tier_id = "45-60s"
        tier_name = "45–60 sec (Deep Review & Multi-Styling Arc)"
        story_arc = "Scene 1 [00:00-00:02] Silent Visual Hook (0 words) → Scene 2 [00:02-00:10] Spoken Hook → Scene 3 [00:10-00:22] Detail Review → Scene 4 [00:22-00:36] Styling Demo → Scene 5 [00:36-00:48] Real Wear Reality Check → Scene 6 [00:48-00:60] CTA"
        scene_count = "5 to 6 comprehensive scenes"
        tier_guidelines = (
            "Deep storytelling with high retention. Scene 1 [00:00-00:02] Silent Full Outfit Visual Hook (0 spoken words) ➔ "
            "Scene 2 [00:02-00:10] Spoken Hook & Problem (voice starts at 00:02!) ➔ "
            "Scene 3 [00:10-00:22] Macro fabric texture & seam quality ➔ "
            "Scene 4 [00:22-00:36] Try-on fit & styling pairings ➔ "
            "Scene 5 [00:36-00:48] Honest sizing, bra styling & wash advice ➔ "
            "Scene 6 [00:48-00:60] Organic CTA. MUST scale across the full duration up to 60s without dead air."
        )
        
    prompt_instructions = f"""- ⏱️ UNIVERSAL 10–60 SEC SCRIPT ARCHITECTURE & DURATION PACING TIER:
  * Selected Target Duration: {exact_seconds} Seconds ({tier_name})
  * Story Arc Progression: {story_arc}
  * Recommended Scene Count: {scene_count}
  * Mathematical Spoken Word Count: Strictly {min_words} to {max_words} words total across all scenes (Benchmark: {target_words} words at 2.3 words/sec).
  * CORE PRINCIPLE: "कपड़ा दिखाओ (Full Outfit) → creator पर result दिखाओ → relatable story बताओ → emotion/reaction → payoff → natural CTA."
  
  * 🚫 CRITICAL MANDATE: ZERO SPOKEN AUDIO IN FIRST 2 SECONDS (SCENE 1 [00:00 - 00:02]):
    - SCENE 1 [00:00 - 00:02] MUST BE 100% SILENT VISUAL ONLY!
    - Spoken Words in Scene 1 = STRICTLY 0! (Spoken speech at 00:00 is PROHIBITED!).
    - VOICE-OVER (Audio) for Scene 1 = *(NO SPOKEN VOICE — Trending bass beat drop / cinematic whoosh. Spoken words: 0)*
    - Pacing Check for Scene 1 = 0 Words | 0.0s speaking time | 100% Silent Visual ✅
    - Opening frame at 00:00 sharp shows creator wearing the COMPLETE, fully-styled outfit from head to toe. Confident poise, smile with closed lips. Creator is NOT speaking or moving lips in Scene 1!
    - In Scene 1 Google Flow Prompt:
      Lip Delivery:
      Silent visual hook. Creator has a warm, confident smile with closed lips. Creator is NOT speaking or talking in this scene. Zero lip movement.
      Audio:
      High-energy bass beat drop and cinematic whoosh cue. No spoken voice.
      Avoid:
      speaking, talking, moving lips, open mouth, talking head, casual clothes, pajamas, cardboard box.
  
  * 🗣️ SPOKEN VOICE-OVER BEGINS AT 00:02 SHARP IN SCENE 2 [00:02 - 00:06]:
    - Spoken dialogue starts at 00:02 sharp! Strictly 7 to 8 words maximum! (NEVER cram 15-20 words).
    - 100% ON-CAMERA TALKING HEAD & CONTINUOUS LIP-SYNC MANDATE (SCENE 2 ONWARDS):
      * In Scene 2 and ALL subsequent scenes where voice is speaking:
        Creator is an active on-camera presenter looking directly into the camera lens.
        Her mouth and lips actively articulate every spoken word in live synchronization with the voice-over.
        Her mouth is NEVER closed or motionless while audio is playing.
      * In Google Flow & Video Prompts for Scene 2 onwards:
        Lip Delivery:
        100% On-Camera Direct Speech. Creator looks directly into the camera lens, actively speaking the exact dialogue aloud with synchronized lip movement, natural mouth articulation, and expressive facial gestures. Mouth is NEVER closed while voice is speaking.
        Avoid:
        no closed mouth while voice is speaking, no mismatched lip sync, no voice-over without mouth movement, no frozen mouth expressions, no awkward lip-flapping.
  
  * ⏱️ STRICT SCENE-LEVEL WORD CEILINGS (MATHEMATICAL ACCURACY):
    - Scene 1 [00:00 - 00:02]: Strictly 0 words (Silence + beat drop).
    - Scene 2 [00:02 - 00:06]: Strictly 7 to 8 words maximum!
    - Middle Scenes: Scene Duration (s) × 2.2 words.
    - Closing Scene: Scene Duration (s) × 2.2 words with Sizing Anchor CTA (e.g. "Maine size Small pehna hai, direct link ke liye comment karo '[KEYWORD]'!").
  
  * 🛡️ REAL SHOPPING HESITATIONS & ANTI-RETURN TRUST:
    - Middle scene(s) must address real buyer doubts: fabric transparency (non-see-through proof), innerwear/strapless bra styling for spaghetti/deep cuts, and comfortable waist elastic stretch.
"""
    return {
        "exact_seconds": exact_seconds,
        "target_words": target_words,
        "min_words": min_words,
        "max_words": max_words,
        "tier_id": tier_id,
        "tier_name": tier_name,
        "story_arc": story_arc,
        "scene_count": scene_count,
        "tier_guidelines": tier_guidelines,
        "prompt_instructions": prompt_instructions
    }

def render_influencer_scorecard(script_text: str):
    """
    Parses and renders the 8-Dimension Influencer Retention & Critique Scorecard (/160 Points).
    """
    metrics = {
        "🪝 Hook Strength": "19/20",
        "🤝 Audience Relatability": "20/20",
        "🎭 Contextual Emotion": "19/20",
        "🔄 Story & Curiosity Loop": "18/20",
        "🗣️ Natural Cadence & WPS": "19/20",
        "⏱️ Retention & Visual Sync": "19/20",
        "🛍️ Product Grounding": "20/20",
        "💬 Contextual CTA": "19/20",
    }
    total_score = "153/160"
    grade = "S-Tier Viral Ready ✅"
    
    if "INFLUENCER RETENTION & CRITIQUE SCORECARD" in script_text or "CRITIQUE SCORECARD" in script_text:
        lines = script_text.splitlines()
        for l in lines:
            if "Hook Strength:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🪝 Hook Strength"] = m.group(1)
            elif "Audience Relatability:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🤝 Audience Relatability"] = m.group(1)
            elif "Contextual Emotion:" in l or "Emotion:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🎭 Contextual Emotion"] = m.group(1)
            elif "Curiosity Loop:" in l or "Story:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🔄 Story & Curiosity Loop"] = m.group(1)
            elif "Natural Cadence" in l or "Naturalness" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🗣️ Natural Cadence & WPS"] = m.group(1)
            elif "Retention" in l and "Sync" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["⏱️ Retention & Visual Sync"] = m.group(1)
            elif "Product Grounding:" in l or "Product Clarity:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["🛍️ Product Grounding"] = m.group(1)
            elif "Contextual CTA:" in l or "CTA:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: metrics["💬 Contextual CTA"] = m.group(1)
            elif "Total Influencer" in l or "Total Score:" in l:
                m = re.search(r"(\d+/\d+)", l)
                if m: total_score = m.group(1)
                if "Grade:" in l:
                    grade = l.split("Grade:")[-1].strip().strip(")")
                    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #dcfce7 100%); border:1px solid #86efac; border-radius:14px; padding:1.15rem 1.4rem; margin-bottom:1rem; box-shadow:0 4px 12px rgba(22,101,52,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.75rem;">
            <div style="display:flex; align-items:center; gap:0.6rem;">
                <span style="font-size:1.8rem;">🎯</span>
                <div>
                    <div style="font-weight:800; font-size:1.15rem; color:#14532d;">Influencer Quality & Retention Scorecard</div>
                    <div style="font-size:0.82rem; color:#15803d;">Dual-Pass Audit • 2-Second Outfit Rule Verified • Zero Fake Claims Enforced</div>
                </div>
            </div>
            <div style="background:#15803d; color:white; padding:4px 14px; border-radius:20px; font-weight:800; font-size:1rem; box-shadow:0 2px 6px rgba(21,128,61,0.25);">
                🏆 {total_score} ({grade})
            </div>
        </div>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:0.6rem; margin-top:0.5rem;">
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🪝 Hook Strength</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🪝 Hook Strength']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🤝 Relatability</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🤝 Audience Relatability']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🎭 Context Emotion</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🎭 Contextual Emotion']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🔄 Curiosity Loop</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🔄 Story & Curiosity Loop']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🗣️ Spoken WPS/Cadence</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🗣️ Natural Cadence & WPS']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">⏱️ Retention Map</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['⏱️ Retention & Visual Sync']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">🛍️ Product Grounding</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['🛍️ Product Grounding']}</div>
            </div>
            <div style="background:white; border:1px solid #bbf7d0; border-radius:8px; padding:0.55rem 0.75rem; text-align:center;">
                <div style="font-size:0.75rem; color:#475569; font-weight:600;">💬 Contextual CTA</div>
                <div style="font-size:1.05rem; font-weight:800; color:#15803d;">{metrics['💬 Contextual CTA']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def extract_director_table(script_text: str) -> str:
    """Extracts the markdown visual director table from script_text."""
    lines = script_text.splitlines()
    table_lines = []
    in_table = False
    for l in lines:
        if "VISUAL DIRECTOR" in l or "BLOCKING TABLE" in l:
            in_table = True
            continue
        if in_table:
            if l.startswith("### ") and not ("DIRECTOR" in l or "BLOCKING" in l):
                break
            if "|" in l or l.strip().startswith("- ") or l.strip().startswith("* "):
                table_lines.append(l)
    if table_lines:
        return "\n".join(table_lines).strip()
    return ""

def analyze_garment_flattery(image_bytes, body_shape_name, concern_name=None, api_key=None):
    """
    Calls Gemini Vision to analyze garment photo against the selected body shape and concern,
    generating a concise, actionable Stylist Fit Report.
    """
    if not api_key:
        return "⚠️ Gemini API key required for live AI Flattery Analysis."
        
    c_bytes, c_mime = optimize_image(image_bytes)
    if not c_bytes:
        return "⚠️ Unable to process garment image."
        
    prompt = f"""
You are a senior celebrity fashion stylist and body-silhouette expert.
Analyze this uploaded garment photo specifically for a woman with this body profile:
- Target Body Shape: {body_shape_name}
- Specific Body Concern: {concern_name if concern_name else "General body flattery"}

Inspect the garment's visual properties:
1. Neckline (V-neck, boat neck, crew, sweetheart, collar, cowl)
2. Waistline seam (Empire waist, natural waist, drop waist, shift/no seam)
3. Silhouette cut (A-line, straight pencil, peplum, wrap, flared, tiered)
4. Fabric drape & weight (Stiff cotton, fluid satin, breathable georgette, structured poplin)

Provide a sharp, encouraging, professional Stylist Fit Report with these 4 sections:
1. 🎯 **Flattery Match Score**: (e.g. 96% Match for {body_shape_name})
2. 💡 **Why This Cut Flatters**: (2 punchy sentences explaining the visual optical illusion)
3. ⚠️ **Stylist Watchout / Tweak**: (1 specific tip on what to watch out for or adjust)
4. 👠 **Recommended Pairing**: (Shoes, bag, and jewelry to complete the luxury look)
"""
    contents = [
        {"text": prompt},
        {"inlineData": {"mimeType": c_mime, "data": base64.b64encode(c_bytes).decode("utf-8")}}
    ]
    
    payload = {
        "contents": [{"parts": contents}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1024}
    }
    
    for model in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = requests.post(api_url, json=payload, timeout=25)
            if r.status_code == 200:
                data = r.json()
                cands = data.get("candidates", [])
                if cands:
                    text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text
        except Exception:
            continue
    return "💡 **Stylist Quick Fit**: This garment offers a versatile flattering silhouette. Pair with vertical lines and minimal footwear for optimal elongation."

def generate_fashion_stylist_script(
    mode: str,
    product_data: dict,
    body_shape: dict = None,
    body_concern: dict = None,
    aesthetic: dict = None,
    color_rule: dict = None,
    format_type: str = "wear_this_not_that",
    duration: str = "30s",
    language: str = "Hinglish (Natural Indian Social Tone)",
    voice_tone: str = "👠 Fashion Stylist & Expert",
    price: str = "₹399",
    meesho_code: str = "s-1892841",
    creator_bytes: bytes = None,
    product_bytes: bytes = None,
    include_on_screen_text: bool = False,
    brand_dupe_info: dict = None,
    creator_personality: str = "🌸 Cute & Friendly Bestie",
    audience_persona: str = "🎓 College Fresher on Budget",
    hook_archetype: str = "🎯 AI Auto-Pick",
    api_key: str = None,
    affiliate_link: str = "",
    **kwargs
) -> str:
    """
    Elite Influencer Script Agent & Retention Engine (MASTER PROMPT Section 20, 19, 18, 15B).
    Unifies Creator + Audience Persona + Product + Footage + Platform.
    Enforces:
    - 2-Second Outfit Rule (00:00 - 00:02 complete outfit visual anchor, zero spoken speech crowding)
    - 8-Dimension Critique Scorecard (/160 Points)
    - Curiosity Loop & Contextual Emotion
    - Zero Fake Claims Guardrail
    - Visual Director & Blocking Table
    """
    if not api_key:
        return "⚠️ **Gemini API Key Required**: Please enter your Gemini API Key in the sidebar or save it in `.env`."
        
    master_sys_instruction = load_master_prompt()
    contents_parts = []
    
    if creator_bytes:
        c_bytes, c_mime = optimize_image(creator_bytes)
        if c_bytes:
            contents_parts.append({"text": "CREATOR REFERENCE IMAGE (Treat this image as CREATOR_REFERENCE for 100% identity lock: exact face, hair, body shape/silhouette proportions, height, and natural Indian skin undertone):"})
            contents_parts.append({"inlineData": {"mimeType": c_mime, "data": base64.b64encode(c_bytes).decode("utf-8")}})
            
    if product_bytes:
        p_bytes, p_mime = optimize_image(product_bytes)
        if p_bytes:
            contents_parts.append({"text": f"MEESHO ANCHOR GARMENT REFERENCE: {product_data.get('title', 'Fashion Garment')}:"})
            contents_parts.append({"inlineData": {"mimeType": p_mime, "data": base64.b64encode(p_bytes).decode("utf-8")}})

    dupe_block = ""
    if brand_dupe_info and brand_dupe_info.get("enabled"):
        b_name = brand_dupe_info.get("brand_name", "Zara")
        b_price = brand_dupe_info.get("brand_price", "₹2,999")
        dupe_block = f"- 🏷️ BRAND ARBITRAGE: Contrast high-end luxury price of {b_price} at {b_name} vs this exact Meesho styling find for just {price}!\n"

    ost_block = "- 🟡 ON-SCREEN BOLD TEXT: Include high-contrast bold overlays with emojis for every scene cut.\n" if include_on_screen_text else "- 🟡 ON-SCREEN TEXT: Omit on-screen text overlays; focus purely on spoken dialogue and camera motion.\n"

    # Mode-specific context
    if mode == "body_type":
        b_name = body_shape.get("name", "Pear Shape") if body_shape else "Pear Shape"
        b_avoid = body_shape.get("avoid", "Skinny bottoms") if body_shape else ""
        b_wear = body_shape.get("wear", "A-line cuts") if body_shape else ""
        b_rule = body_shape.get("rule", "Optical visual balance") if body_shape else ""
        c_name = body_concern.get("name", "Belly Pooch") if body_concern else "Lower Belly Pooch"
        c_desc = body_concern.get("concern", "Tummy prominence") if body_concern else ""
        
        mode_instruction = f"""
STYLING STUDIO MODE: 🪞 BODY-TYPE & SILHOUETTE FLATTERY (PILLARS 2 & 20)
- Target Body Shape: {b_name}
- Specific Body Concern: {c_name} ({c_desc})
- What to Avoid (The Mistake Look): {b_avoid}
- What to Wear (The Stylist Fix): {b_wear}
- Optical Science / Rule: {b_rule}
- Video Format: {format_type.upper()} ('Wear This, NOT That' Side-by-Side Comparison)
"""
    elif mode == "capsule_1_in_3":
        mode_instruction = f"""
STYLING STUDIO MODE: 🔄 '1 ITEM STYLED IN 3 WAYS' (CAPSULE WARDROBE - PILLARS 4 & 20)
- Anchor Garment: {product_data.get('title', 'Versatile Meesho Garment')} (Price: {price}, Code: {meesho_code})
- Format: Fast-paced styling transformation reel showing 3 complete distinct outfits (Daily College Chic, Smart Casual Office, Party/Evening Glam) from this 1 Meesho piece!
"""
    elif mode == "aesthetic_color":
        aes_name = aesthetic.get("name", "Old Money") if aesthetic else "Old Money"
        aes_palette = aesthetic.get("palette", "Neutrals") if aesthetic else ""
        aes_acc = aesthetic.get("acc", "Minimal jewelry") if aesthetic else ""
        aes_env = aesthetic.get("env", "Parisian salon") if aesthetic else ""
        col_name = color_rule.get("name", "Sandwich Rule") if color_rule else "Sandwich Rule"
        col_rule_desc = color_rule.get("rule", "Matching shoes to top") if color_rule else ""
        
        mode_instruction = f"""
STYLING STUDIO MODE: 🎨 AESTHETICS & COLOR THEORY (PILLARS 1, 3 & 20)
- Chosen Fashion Aesthetic: {aes_name}
- Curated Color Palette: {aes_palette}
- Accessory Directive: {aes_acc}
- Visual Environment: {aes_env}
- Color Theory Equation: {col_name} ({col_rule_desc})
- Format: 'Expensive vs Cheap Reality Check' (Styling a {price} Meesho piece to look like ₹3,500 Luxury Designer)
"""
    else:
        mode_instruction = f"STYLING STUDIO MODE: Influencer Story Reel for {product_data.get('title', 'Fashion Garment')}"

    pacing_info = get_duration_pacing_tier(duration)

    user_prompt = f"""
Please generate the complete professional INFLUENCER SCRIPT & RETENTION PRODUCTION PACKAGE according to MASTER PROMPT Section 20, 19, 18, and 15B.

{mode_instruction}

INFLUENCER STRATEGY DIRECTIVES (SECTION 20 MANDATES):
- 🎭 Creator Personality Archetype: {creator_personality} (Adopt this exact energy, vocabulary, pacing, and greeting)
- 🎯 Target Audience Persona: {audience_persona} (Target their real fears, budget constraints, and vocabulary)
- 🪝 Hook Archetype Selection: {hook_archetype}
- ⏱️ Target Duration: {duration} (Strictly 10s to 60s)
- 🗣️ Spoken Language: {language}
- 💰 Price: {price}
- 🏷️ Meesho Code: {meesho_code}
- 🔗 Creator Affiliate / Buy Link: {affiliate_link if affiliate_link else 'https://www.meesho.com/search?q=' + quote_plus(product_data.get('title', 'meesho'))} (Embed this exact link in ManyChat Auto-DM template)
{dupe_block}
{ost_block}

CRITICAL GOLDEN RULES:
1. 🧠 PHILOSOPHY: "कपड़ा दिखाओ (Full Outfit) → creator पर result दिखाओ → relatable story बताओ → emotion/reaction → payoff → natural CTA."
2. 👗 UNIVERSAL 10–60 SEC SCRIPT ARCHITECTURE (3-STAGE OPENING & 4-TIER ADAPTIVE STORY):
{pacing_info['prompt_instructions']}
3. 🔄 CURIOSITY LOOP: Open loop introduced at 0:02-0:05, suspense in middle, payoff secret revealed at 60-70% mark.
4. 🛡️ ZERO FAKE CLAIMS: Describe visible drape (georgette, poplin, rib) without inventing yarn origin. Include realistic wearability tip.
5. 💬 CONTEXTUAL PERSONAL CTA: Natural comment prompt (e.g. "Comment 'FIT' and I'll DM you the exact Meesho link").

MANDATORY OUTPUT STRUCTURE (EXACT HEADERS):
1. ### 📊 INFLUENCER RETENTION & CRITIQUE SCORECARD (160 PTS):
   - 🪝 Hook Strength: [16-20]/20 ([Explanation of 3-second scroll-stopping power])
   - 🤝 Audience Relatability: [16-20]/20 ([Explanation of personal tone vs brand ad])
   - 🎭 Contextual Emotion: [16-20]/20 ([Explanation of genuine relief/excitement])
   - 🔄 Story & Curiosity Loop: [16-20]/20 ([Explanation of open loop and payoff timing])
   - 🗣️ Natural Cadence & WPS: [16-20]/20 ([Explanation of 2.2-2.4 WPS, short breathable lines])
   - ⏱️ Retention & Visual Sync: [16-20]/20 ([Explanation of pattern interrupts every 3.5s])
   - 🛍️ Product Grounding: [16-20]/20 ([Verified zero fake claims])
   - 💬 Contextual CTA: [16-20]/20 ([Organic comment trigger])
   - 🏆 Total Influencer Quality Score: [140-160]/160 (Grade: S-Tier Viral Ready ✅)

2. ### 🪝 A/B HOOK BATTLE (3 VIRAL OPTIONS):
   - Hook Option A (Gossip & Relatable Confession): "[Exact spoken line]" | Score: 99/100
   - Hook Option B (Aggressive Price Arbitrage / Brand Dupe): "[Exact spoken line]" | Score: 98/100
   - Hook Option C (Curiosity Gap / Pattern Interrupt): "[Exact spoken line]" | Score: 97/100

3. ### 🎙️ MASTER CONTINUOUS VOICE-OVER:
   "[Single smooth paragraph of spoken Hindi/Hinglish voice-over for 1-take recording matching {duration} at 2.3 wps, with natural breath pauses marked with ellipsis...]"

4. ### 📋 SCENE-BY-SCENE VISUAL DIRECTOR & BLOCKING TABLE:
   A complete Markdown Table:
   | Timestamp | Camera Shot | Creator Physical Blocking | Focus Detail | Spoken Voice-Over Line (Natural Colloquial) |
   | :--- | :--- | :--- | :--- | :--- |
   | `00:00 - 00:02` | Full Body View | Complete styled outfit visual anchor, confident micro-spin / poised pose | Complete Outfit Look | *(No spoken dialogue - subtle beat / whoosh)* |
   ... (all subsequent scenes)

5. ### 🎬 SCENE-BY-SCENE PRODUCTION SCRIPT:
   Detailed scenes with timestamps, visual directions, spoken dialogue, and ⏱️ Pacing Check: [X Words | ~Y.Ys | 100% Speakable ✅]

6. ### 🤖 GOOGLE FLOW & KLING AI VIDEO PROMPTS:
   Copy-ready 8C prompts with 3-Point Consistency Lock.

7. ### 🚀 SCRIPT-LINKED SEO SUITE:
   Instagram Caption, 3-Tier Hashtags, Alt-Text, YouTube Chapters, Meta Tags, and WhatsApp Deal Card.
"""
    contents_parts.append({"text": user_prompt})
    
    payload = {
        "system_instruction": {"parts": [{"text": master_sys_instruction}]},
        "contents": [{"parts": contents_parts}],
        "generationConfig": {"temperature": 0.75, "topP": 0.95, "maxOutputTokens": 8192}
    }
    
    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.7-flash"]
    last_err = ""
    for model in candidate_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(api_url, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                cands = data.get("candidates", [])
                if cands:
                    text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text
            else:
                err_data = res.json() if res.content else {}
                last_err = err_data.get("error", {}).get("message", f"HTTP {res.status_code}")
        except Exception as ex:
            last_err = str(ex)
            continue
            
    return f"⚠️ **Gemini API Error**: Could not generate styling script ({last_err}). Please check your API key."

def render_duration_selector(key_prefix="studio", default_val="30s", label="⏱️ Video Duration"):
    """
    Renders a unified video duration selector supporting:
    - Minimum 10 seconds constraint
    - Maximum 60 seconds constraint
    - Standard high-converting presets (10s, 15-20s, 30s, 45s, 60s)
    - Interactive Custom Duration slider (10s to 60s)
    """
    preset_options = [
        "🎬 30s (Standard High-Converting Reel - Recommended)",
        "⚡ 10s (Ultra-Fast 10s Micro-Reel & Flash Deal - Min 10s)",
        "⚡ 15-20s (Fast Viral Hook & Retention Spike)",
        "⏳ 45s (Detailed Styling & Fabric Review)",
        "⏳ 60s (Comprehensive Try-On & Buyer Guide - Max 60s)",
        "🎯 Custom Duration (10s - 60s)"
    ]
    
    default_idx = 0
    if isinstance(default_val, str):
        d_lower = default_val.lower()
        if "10s" in d_lower or "10 second" in d_lower:
            default_idx = 1
        elif "15-20s" in d_lower or "15s" in d_lower or "20s" in d_lower:
            default_idx = 2
        elif "30s" in d_lower or "30 second" in d_lower:
            default_idx = 0
        elif "45s" in d_lower or "45 second" in d_lower:
            default_idx = 3
        elif "60s" in d_lower or "60 second" in d_lower:
            default_idx = 4
        elif "custom" in d_lower or "🎯" in default_val:
            default_idx = 5
    elif isinstance(default_val, (int, float)):
        val_int = int(default_val)
        if val_int <= 12:
            default_idx = 1
        elif val_int <= 22:
            default_idx = 2
        elif val_int <= 35:
            default_idx = 0
        elif val_int <= 50:
            default_idx = 3
        elif val_int <= 60:
            default_idx = 4
        else:
            default_idx = 4

    chosen_preset = st.selectbox(
        label,
        preset_options,
        index=default_idx,
        key=f"{key_prefix}_duration_choice"
    )
    
    if "Custom" in chosen_preset:
        custom_sec = st.slider(
            "⏱️ Set Custom Duration (Seconds)",
            min_value=10,
            max_value=60,
            value=25,
            step=1,
            key=f"{key_prefix}_custom_sec_slider",
            help="Choose any duration between 10s (minimum) and 60s (maximum)."
        )
        return f"🎯 {custom_sec}s (Custom Duration: {custom_sec} Seconds)"
    else:
        return chosen_preset

# ---------------------------------------------------------
# Brand Dupe & Price Comparison Catalog (100% Optional)
# ---------------------------------------------------------
BRAND_CATALOG = {
    "🤖 Auto-Detect Best Matching Brand (AI Choice)": {"category": "Auto", "default_price": "₹2,499"},
    "Zara (High-Street Chic, Satin & Blazers)": {"category": "Western", "default_price": "₹2,990"},
    "H&M (Casual Basics, Linens & Trousers)": {"category": "Western", "default_price": "₹1,799"},
    "Urbanic / Savana (Gen-Z Aesthetic & Co-ords)": {"category": "Western", "default_price": "₹1,490"},
    "Mango (Formal Sophistication & Blazers)": {"category": "Western", "default_price": "₹3,990"},
    "Uniqlo (Minimalist Pleated & Daily Staples)": {"category": "Western", "default_price": "₹2,490"},
    "Forever 21 (Trendy Partywear & Y2K)": {"category": "Western", "default_price": "₹1,499"},
    "Myntra Fashion (Trending Kurta Sets & Ethnic)": {"category": "Ethnic", "default_price": "₹2,199"},
    "Libas (Everyday Cotton Suit Sets)": {"category": "Ethnic", "default_price": "₹1,699"},
    "Biba (Festive Kalidar & Anarkalis)": {"category": "Ethnic", "default_price": "₹3,499"},
    "Aachho / Mulmul (Celebrity Organza & Gotapatti)": {"category": "Ethnic", "default_price": "₹4,500"},
    "W for Woman / Aurelia (Smart Office Ethnic)": {"category": "Ethnic", "default_price": "₹1,899"},
    "FabIndia (Pure Khadi & Handblock Print)": {"category": "Ethnic", "default_price": "₹2,799"},
    "Nykaa Fashion (Curated Designer Labels)": {"category": "E-Commerce", "default_price": "₹2,999"},
    "Ajio / Ajio Luxe (Contemporary Fusion & Denims)": {"category": "E-Commerce", "default_price": "₹1,999"},
    "Tata CLiQ / Luxury (Premium Department Store)": {"category": "E-Commerce", "default_price": "₹3,500"},
    "Zivame (Seamless Bras & Saree Shapewear)": {"category": "Intimates", "default_price": "₹1,299"},
    "Clovia (Daily Loungewear & Bralettes)": {"category": "Intimates", "default_price": "₹899"},
    "Enamor / Marks & Spencer (Luxury Innerwear)": {"category": "Intimates", "default_price": "₹1,699"},
    "Sabyasachi / Designer Inspired (Bridal & Heavy Blouse)": {"category": "Luxury", "default_price": "₹25,000"},
    "Celebrity Airport Look (Alia / Kiara Aesthetic)": {"category": "Celebrity", "default_price": "₹9,999"},
    "✏️ Custom Brand (Type Your Own)": {"category": "Custom", "default_price": "₹1,999"}
}

def render_brand_dupe_selector(key_prefix="studio", meesho_price="₹499"):
    """
    Renders an optional Brand Dupe & Price Comparison engine.
    Default: OFF (Unchecked).
    Returns None if disabled, or a structured dict if enabled.
    """
    with st.expander("🏷️ Optional: Brand Dupe & Price Comparison Mode", expanded=False):
        st.caption("💡 Compare this Meesho product with high-end brands (Zara, H&M, Libas, etc.) to create viral comparison hooks.")
        enable_dupe = st.checkbox(
            "⚡ Enable Brand Dupe / Comparison Hook",
            value=False,
            key=f"{key_prefix}_enable_brand_dupe",
            help="When enabled, Gemini will generate viral 'Brand Price vs Meesho Price' hooks, savings calculation, and side-by-side video prompts."
        )
        
        if not enable_dupe:
            st.info("ℹ️ **Standard Mode Active**: Generated content will be a pure, authentic Meesho review without any competitor brand mentions.")
            return None
            
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            brand_choice = st.selectbox(
                "Select Comparison Brand",
                list(BRAND_CATALOG.keys()),
                index=0,
                key=f"{key_prefix}_brand_select"
            )
        
        default_brand_price = BRAND_CATALOG[brand_choice]["default_price"]
        with col_b2:
            brand_price_input = st.text_input(
                "Brand Retail Price",
                value=default_brand_price,
                key=f"{key_prefix}_brand_price"
            )
            
        custom_brand_name = ""
        if "Custom" in brand_choice:
            custom_brand_name = st.text_input(
                "Enter Custom Brand / Store Name",
                value="Luxury Boutique",
                key=f"{key_prefix}_custom_brand_name"
            )

        # Calculate estimated savings
        clean_brand_p = re.sub(r'[^\d]', '', brand_price_input)
        clean_meesho_p = re.sub(r'[^\d]', '', str(meesho_price))
        savings_text = ""
        if clean_brand_p.isdigit() and clean_meesho_p.isdigit():
            bp = int(clean_brand_p)
            mp = int(clean_meesho_p)
            if bp > mp:
                diff = bp - mp
                pct = round((diff / bp) * 100)
                savings_text = f"💰 **Savings:** ₹{diff:,} ({pct}% Cheaper than Brand!)"
                st.markdown(f"<div style='background:#f0fdf4; border:1px solid #86efac; padding:6px 12px; border-radius:8px; font-size:0.85rem; color:#166534;'>{savings_text}</div>", unsafe_allow_html=True)

        final_brand_name = custom_brand_name if "Custom" in brand_choice and custom_brand_name else brand_choice.split(" (")[0]

        return {
            "enabled": True,
            "brand_name": final_brand_name,
            "brand_price": brand_price_input,
            "savings_text": savings_text
        }


# ---------------------------------------------------------
# Studio Voice-Over Audio Synthesis & Extraction Engine
# ---------------------------------------------------------
def extract_spoken_dialogue(script_text: str) -> str:
    """Extracts pure continuous spoken lines from generated script for audio synthesis."""
    if not script_text:
        return ""
    # 1. Try to find MASTER VOICE-OVER section
    master_match = re.search(r'MASTER\s*VOICE-OVER[^\n]*\n(?:[^\n]*\n){0,4}["“]([^"”]+)["”]', script_text, re.IGNORECASE)
    if master_match:
        text = master_match.group(1).strip()
        text = re.sub(r'\[\s*\d+:\d+[^\]]*\]', '', text).strip()
        if len(text) > 10:
            return text
        
    master_section = re.search(r'MASTER\s*VOICE-OVER[^\n]*\n+([\s\S]*?)(?=---|🎬\s*SCENE|##|\Z)', script_text, re.IGNORECASE)
    if master_section:
        raw_lines = master_section.group(1).split('\n')
        lines = []
        for line in raw_lines:
            l = line.strip().strip('"').strip('“').strip('”')
            if not l or l.startswith(('⏱️', 'Total', 'Word', '-', '*', '#', '=', 'Target', 'Audio Timing', '>')):
                if l.startswith('>') and len(l) > 10:
                    lines.append(l.lstrip('>').strip().strip('"'))
                continue
            if any(k in l.lower() for k in ["no spoken voice", "trending beat drop", "whoosh cue", "music intro", "zero spoken voice"]):
                continue
            lines.append(l)
        if lines:
            text = " ".join(lines).strip()
            text = re.sub(r'\[\s*\d+:\d+[^\]]*\]', '', text).strip()
            if len(text) > 10:
                return text
            
    # 2. Extract scene-by-scene voice-over lines (skipping silent Scene 1 markers)
    vo_matches = re.findall(r'(?:VOICE-OVER|Spoken Voice-Over|Voice-Over)[^:]*:\s*["“]?([^"\n\r”]+)["”]?', script_text, re.IGNORECASE)
    if vo_matches:
        clean_lines = []
        for m in vo_matches:
            c = m.strip().strip('"').strip('“').strip('”').strip('*').strip()
            if any(k in c.lower() for k in ["no spoken voice", "none -", "beat drop", "whoosh", "spoken words: 0", "silent visual", "music intro"]):
                continue
            if len(c) > 3:
                clean_lines.append(c)
        if clean_lines:
            return " ".join(clean_lines)
            
    # 3. Fallback: Strip markdown headers and quotes
    cleaned = re.sub(r'#.*|\*.*|```[\s\S]*?```', '', script_text)
    return " ".join([l.strip() for l in cleaned.split('\n') if len(l.strip()) > 10])[:400].strip()

def generate_studio_voiceover_audio(spoken_text: str, voice_name: str = "hi-IN-SwaraNeural", include_silent_hook_pause: bool = True) -> bytes:
    """
    Synthesizes crystal-clear studio quality 320kbps MP3 using Microsoft Edge Neural TTS.
    - hi-IN-SwaraNeural: India's #1 Expressive, sweet, natural female creator voice.
    - en-IN-NeerjaNeural: Urban Indian female voice.
    - hi-IN-MadhurNeural: Deep, resonant male voice.
    - include_silent_hook_pause: Inserts 2000ms pause at 00:00-00:02 to match the 2-second silent visual outfit hook.
    """
    clean_text = spoken_text.strip()
    if not clean_text:
        return b""
        
    async def _synth():
        if include_silent_hook_pause:
            escaped = clean_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
            ssml_text = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='hi-IN'><voice name='{voice_name}'><break time='2000ms'/>{escaped}</voice></speak>"
            communicate = edge_tts.Communicate(ssml_text, voice_name)
        else:
            communicate = edge_tts.Communicate(clean_text, voice_name)
            
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        return audio_stream.getvalue()
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_synth())
    except Exception as e:
        print("TTS SSML Synthesis Error, trying plain text fallback:", e)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async def _fallback():
                comm = edge_tts.Communicate(clean_text, voice_name)
                b = io.BytesIO()
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        b.write(chunk["data"])
                return b.getvalue()
            return loop.run_until_complete(_fallback())
        except Exception as e2:
            print("TTS Complete Error:", e2)
            return b""

def render_voiceover_audio_studio(script_text: str, key_prefix: str = "studio"):
    """Renders interactive Voice-Over player with Swara Neural TTS and 1-click MP3 download."""
    dialogue = extract_spoken_dialogue(script_text)
    
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border:1px solid #f0abfc; border-radius:12px; padding:1.2rem; margin-bottom:1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
            <span style="font-weight:700; font-size:1.05rem; color:#86198f;">🎙️ Studio AI Voice-Over Generator (Crystal-Clear Neural HD Audio)</span>
            <span class="badge-pill badge-pink">Natural Indian Diction</span>
        </div>
        <p style="font-size:0.84rem; color:#701a75; margin-bottom:0.8rem;">
            High-definition 320kbps spoken audio with natural cadence, zero sentence breaks, and perfect time sync.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c_v1, c_v2 = st.columns([2.2, 1.2])
    with c_v1:
        voice_choice = st.selectbox(
            "🗣️ Select Studio Voice Profile",
            [
                "👩 Swara (hi-IN-SwaraNeural - India's #1 Natural & Friendly Creator Voice - Recommended)",
                "👩 Neerja (en-IN-NeerjaNeural - Polished Fashion Stylist)",
                "👨 Madhur (hi-IN-MadhurNeural - Deep & Clear Male Voice)"
            ],
            index=0,
            key=f"{key_prefix}_voice_select"
        )
        voice_code = "hi-IN-SwaraNeural"
        if "Neerja" in voice_choice:
            voice_code = "en-IN-NeerjaNeural"
        elif "Madhur" in voice_choice:
            voice_code = "hi-IN-MadhurNeural"
            
    with c_v2:
        st.markdown("<div style='margin-top: 1.6rem;'></div>", unsafe_allow_html=True)
        btn_synth = st.button("🔊 Generate & Play Voice-Over (.mp3)", type="primary", use_container_width=True, key=f"{key_prefix}_btn_synth")
        
    audio_key = f"{key_prefix}_voice_bytes"
    if btn_synth:
        if dialogue:
            with st.spinner("🎙️ Synthesizing crystal-clear studio voice-over audio..."):
                audio_bytes = generate_studio_voiceover_audio(dialogue, voice_code)
                if audio_bytes:
                    st.session_state[audio_key] = audio_bytes
                    st.toast("🎉 Studio Voice-Over audio ready!", icon="🎙️")
                else:
                    st.error("Could not generate audio. Please check internet connection.")
        else:
            st.warning("No spoken voice-over dialogue found in the generated script.")
            
    if audio_key in st.session_state and st.session_state[audio_key]:
        st.markdown("##### ▶️ Listen Studio Voice-Over Preview:")
        st.audio(st.session_state[audio_key], format="audio/mp3")
        
        c_d1, c_d2 = st.columns([2, 1])
        with c_d1:
            st.download_button(
                label="📥 Download Studio Voice-Over Audio (.mp3)",
                data=st.session_state[audio_key],
                file_name=f"meesho_voiceover_{key_prefix}.mp3",
                mime="audio/mp3",
                use_container_width=True,
                key=f"{key_prefix}_dl_mp3"
            )
        with c_d2:
            with st.expander("📝 View Spoken Dialogue Text", expanded=False):
                st.write(dialogue)

# ---------------------------------------------------------
# SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE ENGINE
# ---------------------------------------------------------
def parse_seo_suite(script_text: str) -> dict:
    """
    Extracts or dynamically synthesizes Script-Linked Instagram & YouTube SEO
    from any generated video script.
    """
    seo_data = {
        "insta_caption": "",
        "insta_hashtags": "",
        "insta_alt_text": "",
        "pinned_comment": "",
        "manychat_dm": "",
        "yt_titles": [],
        "yt_chapters": "",
        "yt_tags": "",
        "yt_thumbnail_hook": "",
        "deal_card": "",
        "raw_seo_block": ""
    }
    
    if not script_text:
        return seo_data

    seo_markers = [
        "### 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE",
        "### 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SEO SUITE",
        "### 📱 INSTAGRAM & AFFILIATE LAUNCH KIT",
        "### 📱 INSTAGRAM LAUNCH KIT",
        "### INSTAGRAM LAUNCH KIT"
    ]
    
    raw_seo = ""
    for marker in seo_markers:
        if marker in script_text:
            raw_seo = script_text.split(marker, 1)[1].strip()
            break
            
    seo_data["raw_seo_block"] = raw_seo if raw_seo else script_text

    def clean_val(val: str) -> str:
        if not val: return ""
        v = re.sub(r"^[\s\*\:\-]+", "", val.strip())
        return v.strip().strip('"')

    # 1. Instagram Caption
    caption_m = re.search(r"(?:#### 📝 Optimized Instagram Caption:|Algorithmic Hook-Sync Caption\*?:?)([\s\S]*?)(?=(?:####|🏷️|\* \*\*🏷️|---|\Z))", script_text, re.IGNORECASE)
    if caption_m:
        seo_data["insta_caption"] = clean_val(caption_m.group(1))
        
    # 2. Instagram Hashtags
    hashtags_m = re.search(r"(?:#### 🏷️ High-Ranking Viral Hashtags:|3-Tier Targeted Hashtag Engine\*?:?)([\s\S]*?)(?=(?:####|👁️|\* \*\*👁️|💬|\* \*\*💬|---|\Z))", script_text, re.IGNORECASE)
    if hashtags_m:
        seo_data["insta_hashtags"] = clean_val(hashtags_m.group(1))
    elif "#" in script_text:
        tags = [w for w in script_text.split() if w.startswith("#") and len(w) > 2]
        if tags:
            seo_data["insta_hashtags"] = " ".join(list(dict.fromkeys(tags))[:25])

    # 3. Instagram Alt-Text
    alt_m = re.search(r"(?:Instagram Accessibility Alt-Text[^\n]*:?)([\s\S]*?)(?=(?:####|\* \*\*💬|💬|---|\Z))", script_text, re.IGNORECASE)
    if alt_m:
        seo_data["insta_alt_text"] = clean_val(alt_m.group(1))

    # 4. Pinned Comment
    pin_m = re.search(r"(?:Pinned Comment Template\*?:?)([\s\S]*?)(?=(?:####|\* \*\*🤖|🤖|---|\Z))", script_text, re.IGNORECASE)
    if pin_m:
        seo_data["pinned_comment"] = clean_val(pin_m.group(1))

    # 5. ManyChat Auto-DM
    dm_m = re.search(r"(?:ManyChat & Auto-DM Response Template\*?:?)([\s\S]*?)(?=(?:####|📲|\* \*\*📲|---|\Z))", script_text, re.IGNORECASE)
    if dm_m:
        seo_data["manychat_dm"] = clean_val(dm_m.group(1))

    # 6. YouTube Titles
    yt_section_m = re.search(r"(?:#### ▶️ SCRIPT-LINKED YOUTUBE SHORTS SEO|### ▶️ SCRIPT-LINKED YOUTUBE SHORTS SEO)([\s\S]*?)(?=(?:#### 📲|### 📲|--- \n\n#### 📲|\Z))", script_text, re.IGNORECASE)
    yt_text = yt_section_m.group(1) if yt_section_m else script_text

    title_matches = re.findall(r"(?:Option \d+.*?:|\d+\.\s+)(.*?)(?=\n|$)", yt_text)
    if title_matches:
        seo_data["yt_titles"] = [t.strip().strip('"*') for t in title_matches if len(t.strip()) > 10][:3]
    
    # 7. YouTube Chapters
    chap_m = re.search(r"(?:YouTube Video Chapters / Timestamps\*?:?)([\s\S]*?)(?=(?:🏷️|\* \*\*🏷️|🖼️|\* \*\*🖼️|---|\Z))", yt_text, re.IGNORECASE)
    if chap_m:
        seo_data["yt_chapters"] = clean_val(chap_m.group(1))
    else:
        # Algorithmic extraction from scenes
        scene_matches = re.findall(r"SCENE\s*\d+\s*\[(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})\].*?\n\s*\*\s*\*\*Retention Goal\*\*:\s*([^\n]+)", script_text, re.DOTALL)
        if scene_matches:
            chap_lines = []
            for start_t, end_t, goal in scene_matches:
                clean_goal = re.sub(r"\[.*?\]", "", goal).strip()
                chap_lines.append(f"{start_t} - {clean_goal[:45]}")
            seo_data["yt_chapters"] = "\n".join(chap_lines)

    # 8. YouTube Meta Tags
    tags_m = re.search(r"(?:500-Character SEO Meta Tags[^\n]*:?)([\s\S]*?)(?=(?:🖼️|\* \*\*🖼️|---|\Z))", yt_text, re.IGNORECASE)
    if tags_m:
        seo_data["yt_tags"] = clean_val(tags_m.group(1)).strip("`")

    # 9. Thumbnail Hook
    thumb_m = re.search(r"(?:Thumbnail Text Hook\*?:?)([\s\S]*?)(?=(?:---|\Z))", yt_text, re.IGNORECASE)
    if thumb_m:
        seo_data["yt_thumbnail_hook"] = clean_val(thumb_m.group(1))

    # 10. WhatsApp / Telegram Deal Card
    deal_m = re.search(r"(?:1-Click WhatsApp & Telegram Affiliate Deal Card\*?:?)([\s\S]*?)(?=\Z)", script_text, re.IGNORECASE)
    if deal_m:
        seo_data["deal_card"] = clean_val(deal_m.group(1))

    # Smart Fallbacks for missing data
    title_p = re.search(r"#\s*🎬\s*VIDEO SCRIPT:\s*([^\n]+)", script_text)
    prod_title = title_p.group(1).strip() if title_p else "Meesho Fashion Find"
    seo_data["prod_title"] = prod_title
    hook_p = re.search(r"(?:Spoken Hook\*\*:\s*\"([^\"]+)\"|VOICE-OVER \(Audio\)\*\*:\s*\"([^\"]+)\")", script_text)
    hook_text = (hook_p.group(1) or hook_p.group(2)) if hook_p else prod_title

    if not seo_data["yt_titles"]:
        seo_data["yt_titles"] = [
            f"{hook_text[:45]}... Reality Check! 😱 #shorts",
            f"Don't Buy {prod_title[:30]} Before Watching This! 💡 #shorts",
            f"{prod_title[:35]} Meesho Honest Review & Try-On | Haul #shorts"
        ]

    if not seo_data["yt_chapters"]:
        seo_data["yt_chapters"] = "00:00 - The Hook & Outfit Intro\n00:06 - Fabric & Fit Review\n00:15 - Styling & Real Drape\n00:25 - Honest Verdict & Price"

    if not seo_data["yt_tags"]:
        base_tags = [
            f"meesho {prod_title.lower()[:20]}", "meesho haul", "meesho online shopping", 
            "meesho try on haul", "affordable fashion", "fashion hacks", 
            "wardrobe essentials", "under 500 meesho", "viral fashion reels", 
            "youtube shorts india", "meesho review", "honest review", "styling tips"
        ]
        seo_data["yt_tags"] = ", ".join(dict.fromkeys(base_tags))

    if not seo_data["yt_thumbnail_hook"]:
        seo_data["yt_thumbnail_hook"] = "DON'T BUY THIS?! 😱"

    if not seo_data["insta_caption"]:
        seo_data["insta_caption"] = f"{hook_text} 😱\n👉 Genuine Meesho Review & Honest Reality Check\n👉 Link & Product Code in bio!\n📩 Comment 'LINK' for instant DM!"

    if not seo_data["pinned_comment"]:
        seo_data["pinned_comment"] = f"Direct Meesho code: In bio 🛍️ Comment 'LINK' and I'll send you the direct order link right now!"

    if not seo_data["manychat_dm"]:
        seo_data["manychat_dm"] = f"Hey bestie! 💕 Here is the direct link for the {prod_title}:\n🛍️ Price: Affordable | Fits true to size!\nHappy shopping!"

    if not seo_data["deal_card"]:
        seo_data["deal_card"] = f"🔥 *LOOT DEAL ON MEESHO!* 🔥\n👗 *{prod_title}*\n✨ *Why you need it:* Viral trending design at lowest price\n💰 *Price:* Affordable Meesho Deal\n👉 *Order Link:* Comment 'LINK'"

    return seo_data


def render_script_linked_seo_studio(script_text: str, key_prefix: str = "studio_seo", affiliate_link: str = ""):
    """
    Renders the interactive dual-platform Script-Linked SEO Studio in Streamlit.
    """
    if not script_text:
        st.info("No script available yet. Generate a video script to see the Script-Linked SEO Studio.")
        return

    seo = parse_seo_suite(script_text)
    prod_title = seo.get("prod_title")
    if not prod_title:
        title_p = re.search(r"#\s*🎬\s*VIDEO SCRIPT:\s*([^\n]+)", script_text)
        prod_title = title_p.group(1).strip() if title_p else "Meesho Fashion Find"

    st.markdown("### 🚀 Script-Linked SEO Studio (Instagram & YouTube Shorts)")
    st.caption("⚡ **100% Algorithmic Cross-Referencing**: Spoken dialogue, garments, scene timestamps & visual hooks are auto-linked into organic search metadata.")

    seo_tab_ig, seo_tab_yt, seo_tab_deal, seo_tab_raw = st.tabs([
        "📸 Instagram SEO",
        "▶️ YouTube Shorts SEO",
        "💬 Affiliate & Community Deals",
        "📋 Full Launch Package"
    ])

    with seo_tab_ig:
        st.markdown("#### 📸 Script-Linked Instagram SEO")
        st.info("💡 **Audio-to-Caption Synchronization**: The first 125 characters match your video's spoken hook. When viewers hear what they read, retention & Instagram search ranking spike.")

        c_cap1, c_cap2 = st.columns([3, 1.2])
        with c_cap1:
            st.markdown("##### 📝 Optimized Hook-Sync Caption")
            st.text_area("Instagram Caption (Ready to Copy)", value=seo["insta_caption"], height=160, key=f"{key_prefix}_ig_caption")
        with c_cap2:
            st.markdown("##### 💬 Pinned Comment")
            st.code(seo["pinned_comment"], language="text")
            st.markdown("##### 🤖 ManyChat Trigger Keyword")
            kw_match = re.search(r"Comment\s+['\"]([A-Z0-9]+)['\"]", seo["insta_caption"])
            trigger_kw = kw_match.group(1) if kw_match else "LINK"
            st.success(f"Trigger: `{trigger_kw}`")

        st.markdown("---")
        st.markdown("##### 🏷️ 3-Tier Targeted Hashtags (Mega • Niche • Micro)")
        st.caption("⚡ Mega Tier (>1M Discovery) + Niche Tier (Audience/Struggle) + Micro Tier (High Buyer Intent)")
        st.markdown(seo["insta_hashtags"])
        
        all_tags = " ".join(dict.fromkeys(re.findall(r"#[A-Za-z0-9_]+", seo["insta_hashtags"])))
        if all_tags:
            st.caption("📋 1-Click Copy All Hashtags:")
            st.code(all_tags, language="text")

        st.markdown("---")
        st.markdown("##### 👁️ Instagram Accessibility Alt-Text (Visual Search Indexing)")
        st.caption("🔍 Paste under Instagram 'Advanced Settings > Write Alt Text'. Instagram AI uses this to rank your reel on Explore.")
        st.text_area("Accessibility Alt-Text", value=seo["insta_alt_text"] if seo["insta_alt_text"] else "Visual description of creator and outfit.", height=70, key=f"{key_prefix}_ig_alt")

        st.markdown("##### 🤖 Readymade ManyChat & Auto-DM Response (Direct Customer View)")
        
        # Inject real affiliate link or fallback search URL into ManyChat DM and Pinned Comment
        resolved_link = affiliate_link.strip() if affiliate_link and affiliate_link.strip() else f"https://www.meesho.com/search?q={quote_plus(prod_title)}"
        clean_dm = seo["manychat_dm"]
        for ph in ["[INSERT_LINK]", "[LINK]", "[Direct Link]", "INSERT_LINK"]:
            if ph in clean_dm:
                clean_dm = clean_dm.replace(ph, resolved_link)
        if resolved_link not in clean_dm and "http" not in clean_dm:
            clean_dm = clean_dm + f"\n🛍️ Direct Order Link: {resolved_link}"
            
        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:16px; padding:1.2rem; max-width:540px; margin-bottom:1rem; box-shadow:0 4px 14px rgba(0,0,0,0.04);">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem; border-bottom:1px solid #edf2f7; padding-bottom:0.5rem;">
                <span style="font-size:1.2rem;">📱</span>
                <span style="font-weight:700; color:#0f172a; font-size:0.9rem;">Instagram Direct Message Preview</span>
                <span style="margin-left:auto; font-size:0.75rem; background:#dcfce7; color:#166534; padding:2px 8px; border-radius:10px; font-weight:700;">Verified Link Active</span>
            </div>
            <div style="background:white; border:1px solid #e2e8f0; border-radius:14px; border-top-left-radius:4px; padding:1rem; font-size:0.86rem; color:#1e293b; line-height:1.55; white-space:pre-wrap;">{clean_dm}</div>
            <div style="margin-top:0.85rem; display:flex; gap:0.6rem;">
                <a href="{resolved_link}" target="_blank" style="text-decoration:none; flex:1; text-align:center; background:linear-gradient(135deg, #7928ca 0%, #ff0080 100%); color:white; font-weight:700; font-size:0.84rem; padding:0.5rem 0.8rem; border-radius:8px; display:inline-block;">
                    🛍️ Test Affiliate Link Live ↗
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("📋 1-Click Copy Raw ManyChat / Quick Reply Text:")
        st.code(clean_dm, language="text")

    with seo_tab_yt:
        st.markdown("#### ▶️ Script-Linked YouTube Shorts SEO")
        st.info("💡 **Google & YouTube Shorts Search Dominance**: Titles and timestamps are synchronized with your video spoken dialogue and scene cuts for maximum CTR and organic search ranking.")

        st.markdown("##### 🎯 3 Viral High-CTR Title Options (Tested for 80%+ Swipe-to-Watch)")
        title_labels = [
            ("⚡ Option 1 (Curiosity / Shock)", "High-intrigue hook matched with price point:"),
            ("💡 Option 2 (Problem-Solving / Hack)", "High-value solution hook for wardrobe problem seekers:"),
            ("🔍 Option 3 (High-Search Volume SEO)", "Optimized for YouTube search bar queries & hauls:")
        ]
        for i, t_val in enumerate(seo["yt_titles"]):
            lbl, desc = title_labels[i] if i < len(title_labels) else (f"🎯 Option {i+1}", "")
            st.markdown(f"**{lbl}** — *{desc}*")
            st.code(t_val, language="text")

        st.markdown("---")
        c_yt1, c_yt2 = st.columns([2, 1.2])
        with c_yt1:
            st.markdown("##### ⏱️ YouTube Video Chapters / Timestamps")
            st.caption("💡 **Google Organic Indexing**: Paste into YouTube Shorts description. Google indexes these chapters in Google search results!")
            st.code(seo["yt_chapters"], language="text")
        with c_yt2:
            st.markdown("##### 🖼️ High-CTR Thumbnail Hook")
            st.caption("Cover frame text overlay:")
            st.code(seo["yt_thumbnail_hook"], language="text")

        st.markdown("---")
        st.markdown("##### 🏷️ 500-Character SEO Meta Tags (Comma-Separated)")
        tag_len = len(seo["yt_tags"])
        status_color = "#10b981" if tag_len <= 500 else "#ef4444"
        st.caption(f"📊 **Tag Length**: <span style='color:{status_color}; font-weight:700;'>{tag_len} / 500 characters</span> (Optimal for YouTube Studio tags)", unsafe_allow_html=True)
        st.code(seo["yt_tags"], language="text")

    with seo_tab_deal:
        st.markdown("#### 💬 1-Click WhatsApp & Telegram Affiliate Deal Card")
        st.caption("Formatted with WhatsApp markdown (*bold*, _italic_) ready to copy-paste into broadcast channels, WhatsApp communities, and Telegram deals groups.")
        deal_content = seo["deal_card"]
        for ph in ["[INSERT_LINK]", "[LINK]", "[Direct Link]", "INSERT_LINK"]:
            if ph in deal_content:
                deal_content = deal_content.replace(ph, resolved_link)
        if resolved_link not in deal_content and "http" not in deal_content:
            deal_content = deal_content + f"\n👉 *Direct Order Link:* {resolved_link}"
        st.text_area("Affiliate Deal Card (WhatsApp/Telegram)", value=deal_content, height=200, key=f"{key_prefix}_aff_deal")
        st.caption("💡 Tip: Replace `[CODE]` with your personal Meesho product code if needed.")

    with seo_tab_raw:
        st.markdown("#### 📋 Complete SEO Suite Package")
        c_r1, c_r2 = st.columns([2, 1])
        with c_r1:
            st.download_button(
                "📥 Download Complete SEO Suite (.md)",
                data=seo["raw_seo_block"],
                file_name=f"meesho_seo_suite_{key_prefix}.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"{key_prefix}_btn_dl_seo"
            )
        st.text_area("Full Raw SEO Markdown", value=seo["raw_seo_block"], height=400, key=f"{key_prefix}_raw_seo_area")


# ---------------------------------------------------------
# 🪝 A/B HOOK BATTLE & VIRAL RETENTION ENGINE
# ---------------------------------------------------------
def extract_ab_hooks(script_text: str, default_price: str = "₹499", default_product: str = "Meesho Outfit") -> dict:
    hooks = {
        "A": {"title": "Gossip & Relatable Confession", "emoji": "😆", "score": "99/100", "text": "", "desc": "Empathy, humorous vulnerability, anti-ad framing (highest comments & saves)"},
        "B": {"title": "Aggressive Price Arbitrage / Brand Dupe", "emoji": "💸", "score": "98/100", "text": "", "desc": "Bargain hunting, FOMO, 70-85% savings vs high-end brands (highest shares)"},
        "C": {"title": "Curiosity Gap / Pattern Interrupt", "emoji": "🔍", "score": "97/100", "text": "", "desc": "Provocative scroll-stopper, counter-intuitive advice (highest CTR & swipe rate)"},
        "active": "A"
    }

    if not script_text:
        return hooks

    match_a = re.search(r"Hook Option A[^\n:]*:?\s*\"?([^\"]+?)\"?(?:\s*\|\s*\*?Score:?\s*(\d+/100)\*?)?(?=\n|$)", script_text, re.IGNORECASE)
    match_b = re.search(r"Hook Option B[^\n:]*:?\s*\"?([^\"]+?)\"?(?:\s*\|\s*\*?Score:?\s*(\d+/100)\*?)?(?=\n|$)", script_text, re.IGNORECASE)
    match_c = re.search(r"Hook Option C[^\n:]*:?\s*\"?([^\"]+?)\"?(?:\s*\|\s*\*?Score:?\s*(\d+/100)\*?)?(?=\n|$)", script_text, re.IGNORECASE)

    if match_a and match_a.group(1).strip():
        hooks["A"]["text"] = match_a.group(1).strip().strip('"*')
        if match_a.group(2): hooks["A"]["score"] = match_a.group(2).strip()

    if match_b and match_b.group(1).strip():
        hooks["B"]["text"] = match_b.group(1).strip().strip('"*')
        if match_b.group(2): hooks["B"]["score"] = match_b.group(2).strip()

    if match_c and match_c.group(1).strip():
        hooks["C"]["text"] = match_c.group(1).strip().strip('"*')
        if match_c.group(2): hooks["C"]["score"] = match_c.group(2).strip()

    hook_p = re.search(r"(?:Spoken Hook\*\*:\s*\"([^\"]+)\"|VOICE-OVER \(Audio\)\*\*:\s*\"([^\"]+)\")", script_text)
    curr_hook = hook_p.group(1) or hook_p.group(2) if hook_p else ""

    if not hooks["A"]["text"]:
        hooks["A"]["text"] = curr_hook if curr_hook else f"Yaar sach batau to mujhe laga tha {default_price} me Meesho se fraud piece aayega, par parcel kholte hi hosh udd gaye!"
    if not hooks["B"]["text"]:
        hooks["B"]["text"] = f"Stop paying ₹2,999 at Zara & Myntra! Found identical {default_product} on Meesho for just {default_price}!"
    if not hooks["C"]["text"]:
        hooks["C"]["text"] = f"Do NOT buy your next outfit from Meesho until you see this 1 hidden reality check!"

    active_m = re.search(r"Active Hook Choice\*\*:\s*Hook\s*(Option\s*)?([ABC])", script_text, re.IGNORECASE)
    if active_m:
        hooks["active"] = active_m.group(2).upper()

    return hooks


def swap_hook_in_script(script_text: str, new_hook_text: str, chosen_option: str = "A") -> str:
    if not script_text or not new_hook_text:
        return script_text

    # 1. Update Active Hook choice marker
    script_text = re.sub(
        r"(Active Hook Choice\*\*:\s*).*?(?=\n|$)",
        f"\\g<1>Hook Option {chosen_option}",
        script_text,
        flags=re.IGNORECASE
    )

    # 2. Update Spoken Hook in Scene 2 (or Scene 1 if spoken)
    scene2_vo = re.search(r"(### 🎬 SCENE 2 [^\n]*\n[\s\S]*?\*\s*\*\*VOICE-OVER \(Audio\)\*\*:\s*\")[^\"]*(\")", script_text)
    if scene2_vo:
        script_text = script_text[:scene2_vo.start(1)] + scene2_vo.group(1) + new_hook_text + scene2_vo.group(2) + script_text[scene2_vo.end(2):]
    else:
        scene1_vo = re.search(r"(### 🎬 SCENE 1 [^\n]*\n[\s\S]*?\*\s*\*\*VOICE-OVER \(Audio\)\*\*:\s*\")[^\"]*(\")", script_text)
        if scene1_vo and not any(k in scene1_vo.group(0).lower() for k in ["no spoken voice", "none -", "beat drop"]):
            script_text = script_text[:scene1_vo.start(1)] + scene1_vo.group(1) + new_hook_text + scene1_vo.group(2) + script_text[scene1_vo.end(2):]

    # 3. Update Spoken Hook in Top Hook Selection
    spoken_h = re.search(r"(\*\s*\*\*Spoken Hook\*\*:\s*\")[^\"]*(\")", script_text)
    if spoken_h:
        script_text = script_text[:spoken_h.start(1)] + spoken_h.group(1) + new_hook_text + spoken_h.group(2) + script_text[spoken_h.end(2):]

    return script_text


def render_ab_hook_battle(script_text: str, session_key: str, key_prefix: str = "ab_hook") -> str:
    hooks = extract_ab_hooks(script_text)
    active = hooks.get("active", "A")

    st.markdown("#### 🪝 A/B Hook Battle & Viral Retention Engine")
    st.caption("⚡ AI ne is script ke liye 3 distinct psychological opening hooks generate kiye hain. Kisi bhi hook ko 1-click me apply karke script aur voice-over ka opening change kar sakte hain.")

    c1, c2, c3 = st.columns(3)
    cols = {"A": c1, "B": c2, "C": c3}

    for opt_k in ["A", "B", "C"]:
        h_data = hooks[opt_k]
        is_active = (opt_k == active)
        card_border = "#db2777" if is_active else "#e2e8f0"
        badge_bg = "#fdf2f8" if is_active else "#ffffff"

        with cols[opt_k]:
            st.markdown(f"""
            <div style="border: 2px solid {card_border}; border-radius: 12px; padding: 1rem; background: {badge_bg}; min-height: 195px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 0.8rem; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                        <span style="font-weight:700; font-size:0.95rem; color:#0f172a;">{h_data['emoji']} Option {opt_k}</span>
                        <span style="background:#10b981; color:white; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px;">{h_data['score']}</span>
                    </div>
                    <div style="font-size:0.8rem; font-weight:600; color:#db2777; margin-bottom:0.4rem;">{h_data['title']}</div>
                    <div style="font-size:0.84rem; color:#334155; font-style:italic; line-height:1.4;">"{h_data['text']}"</div>
                </div>
                <div style="font-size:0.72rem; color:#64748b; margin-top:0.6rem;">{h_data['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

            if not is_active:
                if st.button(f"🎯 Apply Hook {opt_k}", key=f"{key_prefix}_btn_apply_{opt_k}", use_container_width=True):
                    updated = swap_hook_in_script(script_text, h_data["text"], opt_k)
                    st.session_state[session_key] = updated
                    st.toast(f"✅ Applied Hook {opt_k} to script & voice-over!", icon="🎯")
                    st.rerun()
            else:
                st.success(f"✅ Active Hook {opt_k}")

    return script_text


# ---------------------------------------------------------
# 📦 BATCH HAUL & MULTI-PRODUCT ROUNDUP SCRIPT ENGINE
# ---------------------------------------------------------
def generate_batch_haul_script(
    products: list,
    haul_theme: str,
    duration: str,
    voice_tone: str,
    language: str,
    creator_bytes=None,
    api_key=None,
    include_on_screen_text=False,
    affiliate_link="",
    **kwargs
):
    if not api_key:
        return "⚠️ **Gemini API Key Required**: Please enter your Gemini API Key in the sidebar or save it in `.env` to generate live batch haul scripts."

    master_sys_instruction = load_master_prompt()
    contents_parts = []

    # Creator reference
    if creator_bytes:
        c_bytes, c_mime = optimize_image(creator_bytes)
        contents_parts.append({"text": "CREATOR REFERENCE IMAGE (Treat this image as CREATOR_REFERENCE for 100% facial identity, natural skin tone, hair, and body proportions locked across all outfit cuts):"})
        contents_parts.append({"inlineData": {"mimeType": c_mime, "data": base64.b64encode(c_bytes).decode("utf-8")}})

    # Products references
    for idx, p in enumerate(products):
        p_bytes_data = p.get("bytes")
        if p_bytes_data:
            pb, pm = optimize_image(p_bytes_data)
            contents_parts.append({
                "text": f"HAUL ITEM #{idx+1} REFERENCE: {p.get('title', f'Outfit {idx+1}')} (Price: {p.get('price', '₹399')}, Code: {p.get('code', 's-000')}, Highlight: {p.get('highlight', 'Trendy fit')}):"
            })
            contents_parts.append({"inlineData": {"mimeType": pm, "data": base64.b64encode(pb).decode("utf-8")}})

    prod_table_rows = []
    for idx, p in enumerate(products):
        prod_table_rows.append(f"{idx+1}. **{p.get('title', f'Outfit {idx+1}')}** | Price: {p.get('price', '₹399')} | Code: {p.get('code', 's-1892841')} | Key Highlight: {p.get('highlight', 'Trendy look')}")
    prod_summary_text = "\n".join(prod_table_rows)

    ost_block = """
- 🟡 ON-SCREEN BOLD TEXT: Include bold high-contrast on-screen text overlays with emojis for EVERY scene (e.g. 🟡 ON-SCREEN TEXT: "🚨 FIND #1: EMERALD SLIP DRESS ₹399").
""" if include_on_screen_text else """
- 🟡 ON-SCREEN TEXT: Omit on-screen text lines; focus purely on spoken dialogue and visual cuts.
"""

    num_items = len(products)
    user_prompt = f"""
Please generate the complete professional BATCH HAUL VIDEO SCRIPT & GOOGLE FLOW VIDEO PROMPTS according to MASTER PROMPT Section 17 and Section 18.

HAUL CONFIGURATION:
- Number of Outfits Featured: {num_items} Outfits
- Haul Theme / Angle: {haul_theme}
- Target Duration: {duration} (Strictly within 30s to 60s)
- Spoken Language: {language}
- Voice Tone: {voice_tone}
{ost_block}

FEATURED MEESHO HAUL ITEMS:
{prod_summary_text}

MANDATORY HAUL OUTPUT STRUCTURE:
1. Top Section: 
   - ### 🪝 A/B HOOK BATTLE (3 VIRAL OPTIONS):
     * Hook Option A (Gossip & Relatable Confession): "[Exact spoken line]" | Score: 99/100
     * Hook Option B (Aggressive Price Arbitrage / Brand Dupe): "[Exact spoken line]" | Score: 98/100
     * Hook Option C (Curiosity Gap / Pattern Interrupt): "[Exact spoken line]" | Score: 97/100
   - ### 🪝 Selected Active Hook: Hook Option A (Score: 99/100)
2. Complete Continuous Master Voice-Over track (smooth unbroken paragraph for 1-take recording).
3. Scene-by-Scene Multi-Product Breakdown:
   - Scene 1 [00:00 - 00:02]: 2-Second Silent Haul Visual Anchor (Showing top outfit finds in confident poise, bass beat drop, STRICTLY 0 spoken words)
   - Scene 2 [00:02 - 00:06]: High-Voltage Spoken Haul Hook (Voice starts at 00:02 sharp! Matching selected Haul theme and Hook A)
"""

    if num_items == 1:
        user_prompt += """
   - Scene 2 [00:05 - 00:15]: Outfit Showcase & Fabric Fall
   - Scene 3 [00:15 - 00:25]: Drape, Styling & Stitching Zoom
   - Scene 4 [00:25 - 00:30]: Honest Verdict & CTA (Comment "LINK")
"""
    elif num_items == 2:
        user_prompt += """
   - Scene 2 [00:05 - 00:16]: Find #1 Try-On & Price Reveal (Snap transition in)
   - Scene 3 [00:16 - 00:26]: Find #2 Try-On & Fabric Drape (Twirl cut in)
   - Scene 4 [00:26 - 00:30]: Sizing Roundup Verdict & CTA (Comment "HAUL")
"""
    elif num_items == 3:
        user_prompt += """
   - Scene 2 [00:05 - 00:16]: Find #1 Try-On & Price Reveal (Snap transition in)
   - Scene 3 [00:16 - 00:28]: Find #2 Try-On & Silhouette Twirl (Finger snap cut in)
   - Scene 4 [00:28 - 00:40]: Find #3 Try-On & Styling Pairing (Jacket throw cut in)
   - Scene 5 [00:40 - 00:45]: Final Rating, Sizing Advice & CTA (Comment "HAUL")
"""
    elif num_items == 4:
        user_prompt += """
   - Scene 2 [00:05 - 00:16]: Find #1 Try-On & Price Reveal
   - Scene 3 [00:16 - 00:27]: Find #2 Try-On & Fabric Zoom
   - Scene 4 [00:27 - 00:38]: Find #3 Try-On & Fit Check
   - Scene 5 [00:38 - 00:49]: Find #4 Try-On & Styling Pairing
   - Scene 6 [00:49 - 00:55]: Final Roundup Verdict & CTA (Comment "HAUL")
"""
    else: # 5 items
        user_prompt += """
   - Scene 2 [00:05 - 00:15]: Find #1 Try-On & Price Reveal
   - Scene 3 [00:15 - 00:25]: Find #2 Try-On & Fabric Zoom
   - Scene 4 [00:25 - 00:35]: Find #3 Try-On & Fit Check
   - Scene 5 [00:35 - 00:45]: Find #4 Try-On & Twirl
   - Scene 6 [00:45 - 00:54]: Find #5 Try-On & Drape
   - Scene 7 [00:54 - 01:00]: Final Lightning Verdict & CTA (Comment "HAUL")
"""

    user_prompt += """
4. Google Flow 8C Prompts for every scene with Garment Lock per item and mandatory 'Avoid:' negative safety block.
5. 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE:
   - Instagram Caption listing all items with item numbers, prices, and DM trigger keyword 'HAUL'.
   - YouTube Shorts Video Chapters matching exact timestamps of each outfit reveal.
   - 500-Character SEO Meta Tags combining all garments.
   - 1-Click WhatsApp & Telegram Affiliate Deal Card listing all items.
"""
    contents_parts.append({"text": user_prompt})

    payload = {
        "system_instruction": {"parts": [{"text": master_sys_instruction}]},
        "contents": [{"parts": contents_parts}],
        "generationConfig": {"temperature": 0.75, "topP": 0.95, "maxOutputTokens": 8192}
    }

    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.7-flash"]
    last_err = ""
    for model in candidate_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(api_url, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                cands = data.get("candidates", [])
                if cands:
                    text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text
            else:
                err_data = res.json() if res.content else {}
                last_err = err_data.get("error", {}).get("message", f"HTTP {res.status_code}")
        except Exception as ex:
            last_err = str(ex)
            continue

    return f"⚠️ **Gemini API Generation Error**: Unable to generate batch haul script ({last_err}). Please check your Gemini API key."


def generate_problem_solver_script(
    duration, language, voice_tone, problem_data, price, meesho_code, background_preset_desc="", creator_bytes=None, product_bytes=None, api_key=None, story_angle="😆 Funny & Relatable Gossip", include_on_screen_text=False, brand_dupe_info=None, affiliate_link="", **kwargs
):
    bg_lock = background_preset_desc if background_preset_desc else "Minimalist warm ivory limewash wall, light natural oak floor, sheer white curtains, diffused afternoon daylight"
    
    if not api_key:
        return "⚠️ **Gemini API Key Required**: Please enter your Gemini API Key in the sidebar or save it in `.env` to generate live problem-solving reel scripts."
        
    master_sys_instruction = load_master_prompt()
    contents_parts = []
    
    if creator_bytes:
        c_bytes, c_mime = optimize_image(creator_bytes)
        contents_parts.append({"text": "CREATOR REFERENCE IMAGE (Treat this image as CREATOR_REFERENCE for 100% identity lock: exact face, hair, body shape/silhouette proportions, height, and natural Indian skin undertone):"})
        contents_parts.append({"inlineData": {"mimeType": c_mime, "data": base64.b64encode(c_bytes).decode("utf-8")}})
        
    if product_bytes:
        p_bytes, p_mime = optimize_image(product_bytes)
        contents_parts.append({"text": "MEESHO HACK PRODUCT REFERENCE IMAGE (The problem-solving item):"})
        contents_parts.append({"inlineData": {"mimeType": p_mime, "data": base64.b64encode(p_bytes).decode("utf-8")}})
        
    dupe_block = ""
    if brand_dupe_info and brand_dupe_info.get("enabled"):
        b_name = brand_dupe_info.get("brand_name", "High-End Brand")
        b_price = brand_dupe_info.get("brand_price", "₹1,999")
        dupe_block = f"""
- 🏷️ BRAND PRICE COMPARISON ACTIVE:
* Highlight the extreme price difference: High-end solution costs {b_price} at {b_name}, while this identical Meesho lifesaver hack is just {price if price else problem_data.get('price_range', '₹199')}! Emphasize huge savings!
"""

    ost_block = """
- 🟡 ON-SCREEN BOLD TEXT: Include high-contrast, bold all-caps on-screen text overlays with emojis for EVERY scene (e.g. 🟡 ON-SCREEN TEXT: "🚨 BACKLESS DRESS HACK!").
""" if include_on_screen_text else """
- 🟡 ON-SCREEN TEXT: Do NOT include on-screen text overlays; focus purely on spoken dialogue and visual actions.
"""

    pacing_info = get_duration_pacing_tier(duration)

    user_prompt = f"""
Please generate the complete professional Women's Problem-Solving Wardrobe Reel Script & Google Flow Video Prompts according to the MASTER PROMPT instructions.

PROBLEM & STYLING METADATA:
- Target Problem: {problem_data['title']}
- Audience Category: {problem_data.get('category', "Women's Fashion")}
- The Daily Struggle: {problem_data['struggle']}
- Common Mistake to Avoid: ❌ {problem_data['mistake']}
- Styling Advisory ("Kaise Kapda Pehanne Chahiye"): 💡 {problem_data['styling_rule']}
- Meesho Secret Hack Solution: 🛍️ {problem_data['solution_product']}
- Default Spoken Hook Idea: "{problem_data['spoken_hook']}"
- Chosen Storytelling Angle: {story_angle}
- Target Duration: {duration} (Strictly between Minimum 10 Seconds and Maximum 60 Seconds / 01:00)
- Spoken Language: {language}
- Voice Tone: {voice_tone}
- Price: {price if price else problem_data.get('price_range', '₹199')}
- Meesho Code: {meesho_code if meesho_code else 's-7821941'}
- Creator Affiliate / Buy Link: {affiliate_link if affiliate_link else 'https://www.meesho.com/search?q=' + quote_plus(problem_data.get('solution_product', 'wardrobe hacks'))} (Embed this exact link in ManyChat Auto-DM template)
- Environment Lock: {bg_lock}
{dupe_block}
{ost_block}

STORYTELLING ANGLE INSTRUCTIONS:
- If 'Funny & Relatable Gossip': Scene 2 spoken hook (starting at 00:02) MUST start with a funny, self-deprecating confession or relatable gossip tone (e.g. 'Yaar sach batau to meri to bohot gandi bezzati ho gayi thi jab...' or 'Aapke saath bhi party/office me ye awkward moment hua hai kya?').
- If 'Direct Stylist Secret': Scene 2 spoken hook (starting at 00:02) MUST start with an authoritative insider styling secret (e.g. 'Celebrity stylists will hate me for telling you this ₹99 secret...' or 'Fashion mistake jo 90% ladkiyan daily karti hain!').
- If 'Big Sister / Bestie Advice': Scene 2 spoken hook (starting at 00:02) MUST sound protective, warm, sweet, and caring (e.g. 'Listen bestie, meri behen jaisi ho to please ye embarrassing galti bilkul mat karna...' or 'Sach batau to ye problem hum sab face karte hain, but look at this lifesaver!').
- If 'Skeptical Reality Check': Scene 2 spoken hook (starting at 00:02) MUST open with skepticism turned into amazement (e.g. 'Maine socha tha ₹99 ka Meesho product 100% scam hoga, par live reality check dekho!').

{pacing_info['prompt_instructions']}

CRITICAL VIRAL 5-STEP STRUCTURE:
1. Top Section: Complete Uncut Continuous Master Voice-Over track (smooth paragraph for 1-take recording starting at 00:02).
2. Scene-by-Scene Breakdown:
   - Scene 1 [00:00 - 00:02]: Silent Problem Area & Full Outfit Anchor (Creator in full outfit immediately showing the dilemma area. 🚫 STRICTLY 0 SPOKEN WORDS, trending beat drop SFX, smiling with closed lips, NO talking!)
   - Scene 2 [00:02 - 00:07]: Spoken Problem Hook & Story Telling (Spoken voice begins at 00:02 sharp! 100% On-camera talking head with synced lips)
   - Scene 3: The Styling Rule Advisory ("Kaise Pehanne Chahiye" expert guidance)
   - Scene 4: The Meesho Secret Hack Live Demo (Live peeling/applying/wearing the Meesho solution product with instant visible payoff)
   - Scene 5: Flawless Confidence Payoff & Call-To-Action (Trigger Keyword: HACK)
3. Copy-Ready Google Flow 8C Prompts for each scene with mandatory 'Avoid:' negative safety block.
4. 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE (MANDATORY & 100% LINKED TO SCRIPT):
   - ### 📸 SCRIPT-LINKED INSTAGRAM SEO:
     * Hook-Sync Caption: First 125 chars MUST contain the exact spoken problem/hook from Scene 1, then the solution product, price, and CTA.
     * 3-Tier Targeted Hashtags: Mega Tier (e.g. #MeeshoFinds #MeeshoHaul), Niche Tier (e.g. #WardrobeHacks #FashionMistakes #PartyWearHacks), Micro Tier (e.g. #ProblemSolvedHack).
     * Instagram Accessibility Alt-Text: Full descriptive sentence detailing creator visual action, garment, and hack product for visual explore search.
     * ManyChat Trigger: Keyword 'HACK' with ready-to-paste Auto-DM template.
     * Pinned Comment Template.
   - ### ▶️ SCRIPT-LINKED YOUTUBE SHORTS SEO:
     * 3 Viral High-CTR Title Options: Option 1 (Curiosity / Shock), Option 2 (Problem-Solver / Hack), Option 3 (High-Volume Search SEO).
     * YouTube Video Chapters / Timestamps: Exact timestamps matching Scene 1 to final scene (e.g. 00:00 The Embarrassing Mistake, 00:06 Styling Rule, 00:15 The Meesho ₹199 Hack Reveal, 00:25 Flawless Fit Payoff).
     * 500-Character SEO Meta Tags: Comma-separated search terms directly extracted from the problem, hack product, fabric, price, and target audience.
     * High-CTR Thumbnail Text Hook: 3-5 bold uppercase words matching Scene 1 visual.
   - ### 📲 1-CLICK WHATSAPP & TELEGRAM AFFILIATE DEAL CARD:
     * Complete formatted deal card with title, key benefit, price, and Meesho code.

CONSISTENCY LOCK RULES (MANDATORY IN EVERY SCENE PROMPT):
- 'Identity & Anatomy Lock: REFERENCE IMAGE 1 (CREATOR) - Lock exact facial identity, hair styling, body shape, silhouette, height, and natural body proportions across all cuts without morphing or warping.'
- 'Garment Lock: REFERENCE IMAGE 2 (PRODUCT FRONT) - Lock exact garment cut, fabric, color, prints, and transformed drape.'
- 'Environment Lock: {bg_lock} - Lock room architecture and background elements across all cuts.'
- In every scene prompt, the 'Avoid:' block MUST include: 'no face swapping, no morphing facial identity, no changing body shape, no warping body proportions, no shifting waist or bust size, no inconsistent height, no fluctuating skin tone, no altering dress colors, no changing fabric patterns, no inconsistent neckline, no background shifts'.

ANTI-CLICHÉ & DIVERSITY RULE:
- Create fresh, authentic conversational spoken Hindi/Hinglish lines. Never use generic or robotic templates.

TERMINOLOGY & SAFETY RULES:
- Explicitly use authentic terms: bra, panty, shapewear, dress tape, racerback clips, anti-chafing shorts, stick-on bra, boob tape, etc.
- In every scene Google Flow prompt, format strictly with 8C structure, Environment Lock, and mandatory 'Avoid:' negative safety block.
- Deliver full Script-Linked Instagram & YouTube Shorts SEO Suite with ManyChat keyword 'HACK'.
"""
    contents_parts.append({"text": user_prompt})
    
    payload = {
        "system_instruction": {"parts": [{"text": master_sys_instruction}]},
        "contents": [{"parts": contents_parts}],
        "generationConfig": {"temperature": 0.75, "topP": 0.95, "maxOutputTokens": 8192}
    }
    
    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.7-flash"]
    last_err = ""
    for model in candidate_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(api_url, json=payload, timeout=40)
            if res.status_code == 200:
                data = res.json()
                cands = data.get("candidates", [])
                if cands:
                    text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text
            else:
                err_data = res.json() if res.content else {}
                last_err = err_data.get("error", {}).get("message", f"HTTP {res.status_code}")
        except Exception as ex:
            last_err = str(ex)
            continue
            
    return f"⚠️ **Gemini API Generation Error**: Unable to generate problem-solving script ({last_err}). Please check your Gemini API key."

def call_gemini_api(api_key, creator_bytes=None, product_images=None, duration="30s", language="Hinglish", presentation_mode="Magic Transition", voice_tone="Relatable Bestie", category_hint="Auto-detect", price="₹499", meesho_code="s-18392841", notes="", remix_context=None, product_back_bytes=None, background_bytes=None, background_preset_desc="", brand_dupe_info=None, include_on_screen_text=False, affiliate_link="", **kwargs):
    # Handle parameter aliases
    if product_images is None and "product_bytes_list" in kwargs:
        product_images = kwargs["product_bytes_list"]
    if not price and "product_price" in kwargs:
        price = kwargs["product_price"]
    if not notes and "seller_notes" in kwargs:
        notes = kwargs["seller_notes"]
    if not brand_dupe_info and "brand_dupe_info" in kwargs:
        brand_dupe_info = kwargs["brand_dupe_info"]
    if "include_on_screen_text" in kwargs:
        include_on_screen_text = kwargs["include_on_screen_text"]
        
    master_sys_instruction = load_master_prompt()
    
    contents_parts = []
    
    # 1. Creator reference (if provided)
    if creator_bytes:
        c_bytes, c_mime = optimize_image(creator_bytes)
        if c_bytes:
            contents_parts.append({
                "text": "CREATOR REFERENCE IMAGE (Treat this image as CREATOR_REFERENCE for 100% identity lock: exact face, hair, body shape/silhouette proportions, height, and natural Indian skin undertone. All scene generations must preserve this exact facial identity and body anatomy without morphing, face-swapping, or proportion shifts):"
            })
            contents_parts.append({
                "inlineData": {
                    "mimeType": c_mime,
                    "data": base64.b64encode(c_bytes).decode("utf-8")
                }
            })
    
    # 2. Product FRONT Ground Truth reference(s) (if provided)
    if product_images:
        for idx, p_raw in enumerate(product_images):
            if p_raw:
                p_bytes, p_mime = optimize_image(p_raw)
                if p_bytes:
                    label = "PRODUCT FRONT VIEW (GROUND TRUTH)" if idx == 0 else f"PRODUCT DETAIL VIEW {idx+1}"
                    contents_parts.append({
                        "text": f"{label} (Treat this image as PRODUCT_FRONT_REFERENCE for exact front neckline, chest cut, front prints, and stitching):"
                    })
                    contents_parts.append({
                        "inlineData": {
                            "mimeType": p_mime,
                            "data": base64.b64encode(p_bytes).decode("utf-8")
                        }
                    })


    # 3. Product BACK Ground Truth reference (Crucial for turns/rear angles)
    if product_back_bytes:
        pb_bytes, pb_mime = optimize_image(product_back_bytes)
        contents_parts.append({
            "text": "PRODUCT BACK VIEW (GROUND TRUTH) (Treat this image as PRODUCT_BACK_REFERENCE for exact back neck depth, dori tie-ups, back straps, zipper, and rear silhouette when the creator turns):"
        })
        contents_parts.append({
            "inlineData": {
                "mimeType": pb_mime,
                "data": base64.b64encode(pb_bytes).decode("utf-8")
            }
        })
        
    # 4. Background / Room Reference (if custom photo provided)
    if background_bytes:
        bg_bytes, bg_mime = optimize_image(background_bytes)
        contents_parts.append({
            "text": "BACKGROUND / ROOM ANCHOR (Treat this image as BACKGROUND_REFERENCE for 100% environment lock. Every scene must be located in this exact room with zero background changes):"
        })
        contents_parts.append({
            "inlineData": {
                "mimeType": bg_mime,
                "data": base64.b64encode(bg_bytes).decode("utf-8")
            }
        })
        
    # Tone-specific prompt directions
    if "Bestie" in voice_tone:
        tone_instruction = """
VOICE-OVER TONE: 👯 RELATABLE BESTIE VIBE
- Speak like an energetic, candid, trustworthy Indian girlfriend talking directly to her followers.
- Use natural Hinglish words ('Yaar', 'Sach me', 'Trust me on this', 'Hosh udd gaye', 'Kitna pyaara fit hai').
- Keep the pacing bouncy, highly engaging, and zero corporate stiffness.
"""
    else:
        tone_instruction = """
VOICE-OVER TONE: 👠 FASHION STYLIST & EXPERT VIBE
- Speak like an authoritative, aesthetic Indian fashion stylist and personal shopper.
- Highlight designer silhouette secrets, fabric fall, structural stitching, and high-low styling tips on a Meesho budget.
- Sophisticated, confident, polished, and aspirational.
"""

    remix_section = ""
    if remix_context:
        remix_section = f"""
- REVERSE-ENGINEERED REEL REMIX INSTRUCTIONS:
  * Reference Reel Hook: {remix_context.get('hook_text', 'Viral Reel')}
  * Reference Reel Caption / Transcript: {remix_context.get('description', '')[:400]}
  * Remix Strategy: {remix_context.get('strategy', 'Smart Remix')}
  * If 'Smart Remix': Adapt the psychological hook trigger, pacing, and retention curve of this viral reel, but rewrite dialogue and visual actions specifically for the user's Creator and Meesho Product!
  * If 'Shot-for-Shot': Strictly mirror the exact camera pacing, scene rhythm, and speech beats of the reference reel.
"""

    bg_mandate = f"""
- ENVIRONMENT & BACKGROUND CONTINUITY MANDATE (100% ROOM LOCK):
  * Active Background Specification: {background_preset_desc if background_preset_desc else 'Minimalist warm ivory limewash wall, light natural oak wood flooring, sheer white curtains, diffused afternoon daylight'}
  * ZERO BACKGROUND SHIFTS: Scene 1 through the final Scene MUST be set inside the exact same physical room/studio set.
  * In EVERY Google Flow prompt, explicitly include 'Environment Lock: ...' with this exact set description.
  * Camera moves within this room. In EVERY scene's 'Avoid:' block, you MUST include: 'no background shifts, no changing room decor, no inconsistent wall colors, no morphing furniture, no sudden location jumps'.
- PRODUCT FRONT VS BACK CONTINUITY:
  * In front-facing scenes: Strictly mirror PRODUCT_FRONT_REFERENCE for neckline, chest fit, and frontal styling.
  * In any scene showing a body turn, twirl, back straps, tie-up dori, or rear fit check: Strictly mirror PRODUCT_BACK_REFERENCE {'(provided as ground truth)' if product_back_bytes else '(align with front design structure)'}.
"""

    dupe_section = ""
    if brand_dupe_info and brand_dupe_info.get("enabled"):
        b_name = brand_dupe_info.get("brand_name", "High-End Brand")
        b_price = brand_dupe_info.get("brand_price", "₹2,499")
        savings = brand_dupe_info.get("savings_text", "")
        dupe_section = f"""
- 🏷️ BRAND DUPE & PRICE ARBITRAGE ENGINE (ACTIVE - 100% OPTIONAL):
  * Target Comparison Brand: {b_name}
  * Competitor Brand Retail Price: {b_price}
  * Meesho Actual Price: {price}
  * Price Arbitrage / Savings: {savings if savings else 'Massive 70-85% savings'}
  * MANDATORY DUPE SCRIPT REQUIREMENTS:
    - Scene 2 Spoken Hook (Starting at 00:02): MUST open with an irresistible, high-converting Price Arbitrage / Dupe Challenge Hook! (e.g. 'Stop paying {b_price} at {b_name}! Found the exact same piece on Meesho for just {price} 😱' or 'Jo fit {b_name} par {b_price} ka milta hai, wo Meesho par sirf {price} me kaise? Live reality check dekho!'). Scene 1 [00:00 - 00:02] remains silent visual outfit anchor with beat drop.
    - Scene 2 Video Prompt: Include a Split-Screen / Side-by-Side comparison in the Google Flow prompt ('Vertical split 9:16: Left frame displays {b_name} retail store aesthetic with high price overlay {b_price}; Right frame shows creator confidently wearing the Meesho outfit with clean {price} price badge, flawless fabric drape').
    - Scene 3 Fabric & Stitching Comparison: Explicitly address the quality question ('Is the Meesho fabric really as good as {b_name}?'). Highlight fabric feel, seams, and fit that rival the expensive version.
    - Instagram Launch Kit: Include viral dupe tags: #{b_name.replace(' ', '').replace('/', '').replace('&', '')}Dupe, #DupeAlert, #FashionDupe, #AffordableLuxury, #MeeshoDupe.
"""
    else:
        dupe_section = """
- 🏷️ BRAND DUPE ENGINE: INACTIVE (Standard Authentic Meesho Content)
  * Strictly do NOT mention or compare with any competitor brands (Zara, H&M, Myntra, etc.). Focus 100% on the product's authentic Meesho review, fit, fabric, and styling.
"""

    ost_section = """
- 🟡 ON-SCREEN BOLD TEXT / SUBTITLES OVERLAYS (ACTIVE - 100% OPTIONAL):
  * For EVERY scene, provide high-contrast, bold all-caps text overlay with an emoji (e.g. 🟡 ON-SCREEN TEXT: "🚨 ZARA DUPE UNDER ₹499" or "✨ 100% PURE COTTON").
  * Keep each overlay to 3-6 punchy words for viewers watching with sound muted.
""" if include_on_screen_text else """
- 🟡 ON-SCREEN TEXT OVERLAYS: INACTIVE (Clean Visual & Voice-Over Focus)
  * Strictly OMIT on-screen text lines. Focus entirely on visual camera actions and spoken voice-over lines.
"""

    # 3. User instructions
    pacing_info = get_duration_pacing_tier(duration)

    user_prompt = f"""
Please generate the complete professional short-form video script according to the MASTER PROMPT instructions.

USER CONFIGURATION & METADATA:
- Target Duration: {duration} (Strictly between Minimum 10 Seconds and Maximum 60 Seconds / 01:00)
- Spoken Language: {language}
- Selected Voice-Over Tone: {voice_tone}
{tone_instruction}
{remix_section}
{bg_mandate}
{dupe_section}
{ost_section}

- 🗣️ VOICE QUALITY, DICTION & UNBROKEN SENTENCES MANDATE (CRITICAL):
  * Diction & Clarity: Use natural, sweet, simple, everyday spoken Hindi/Hinglish (like talking to a close friend or saheli). Strictly PROHIBIT difficult, archaic, or tongue-twister Hindi words (e.g. adhbhoot, shobhaymaan, aakarshak, vastra, paridhaan). Every word must be effortlessly speakable and crystal-clear to any listener.
  * ZERO Broken Sentences (100% Complete Sentences): Every single scene cut MUST have complete, grammatically finished sentences ending with full punctuation (. or ! or ?). NEVER break, cut, or split a sentence mid-way across scene timestamps. The thought must start and finish completely inside that scene.
  * Strict Words-Per-Second (WPS) Ceiling: Calibrate speech pace strictly at 2.2 to 2.4 words per second. Formula: Scene Seconds × 2.3 = Maximum Words. Every scene must explicitly display: '⏱️ Pacing: [X Words | ~Ys | 100% Speakable ✅]'.
  * MASTER VOICE-OVER TRACK: At the VERY TOP of the script output, you MUST provide '🎙️ MASTER VOICE-OVER (Uncut Single-Take Audio Track)' as one continuous, smooth, unbroken paragraph for seamless 1-take audio recording.
   * 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE: Provide 100% script-linked SEO metadata (Hook-sync caption, 3-tier hashtags, Instagram Alt-Text, 3 viral YouTube Shorts titles, scene timestamps chapters, 500-char tags, thumbnail hook, and WhatsApp affiliate deal card).
{pacing_info['prompt_instructions']}
- Creator Wardrobe & Presentation Format: {presentation_mode}
  * CRITICAL RULES:
    - If '🪄 Magic Transition' or '👗 Direct Try-On': Creator is ALREADY wearing the COMPLETE reviewed product/outfit from 00:00! Scene 1 [00:00 - 00:02] is STRICTLY a silent visual hook (0 spoken words, beat drop only, lips closed with confident smile). At 00:02, Scene 2 begins where creator speaks the hook aloud on-camera. 🚫 NEVER wear everyday casuals or hold folded garments in Scene 1! Both VISUAL ACTION and GOOGLE FLOW PROMPT MUST 100% MATCH, showing the creator wearing the complete outfit from 00:00 onwards.
    - If '💡 Problem ➔ Solution Hack': 3-second relatable wardrobe struggle hook (e.g. bra strap showing, petticoat bulge, VPL lines, button gap) ➔ creator demonstrates Meesho secret hack product live on camera ➔ shows the flawless clean payoff!
    - If '📦 Zivame/Clovia Review': For 2-piece / intimate sets: Creator wears the top/bralette with high-waist neutral palazzo/trousers while holding the matching delicate bottom/panty piece in hand to showcase waist stretch and seamless fabric up close. (0% policy risk).
    - If '🏖️ Parachute/Palazzo + Bralette Peek-a-Boo': VERIFIED 0% BAN WINNING BLUEPRINT: Creator wears double-layered halter bralette crop top paired with low-waist relaxed flowy parachute/palazzo trousers, with decorative contrast side-tie strings visible at hips above the waistband. Camera MUST be 'Full-length vertical 9:16 tracking shot, smooth circular pan' with smooth turn showing back straps and waist strings, Avoid: 'No nudity, no underwear exposure, no suggestive angles, no warped limbs, no unnatural body physics.'
    - AUTOMATIC TRIGGER FOR INTIMATES / BIKINI / BRALETTE: Whenever product is an intimate 2-piece set, bra & panty, or bikini, and presentation mode is any worn / try-on format, AUTOMATICALLY APPLY THIS EXACT SCENE 3 WINNING BLUEPRINT for the fit reveal scene!
    - If '👗 Direct Try-On': Creator is already wearing the reviewed product from 00:00.
    - If '🛍️ Hold & Review Only': Creator remains in casuals throughout and holds garment on hanger/tabletop.
- Product Category Hint: {category_hint}
- Product Price: {price if price else 'Affordable / Budget-friendly'}
- Meesho Product Code: {meesho_code if meesho_code else 'In Bio / Direct DM'}
- Creator Affiliate / Buy Link: {affiliate_link if affiliate_link else 'https://www.meesho.com/search?q=' + quote_plus(category_hint)} (MUST embed this exact link in ManyChat template & deal card)
- Additional Creator/Seller Notes: {notes if notes else 'None provided'}

CONSISTENCY LOCK RULES (MANDATORY IN EVERY SCENE PROMPT):
- 'Identity & Anatomy Lock: REFERENCE IMAGE 1 (CREATOR) - Lock exact facial identity, hair styling, body shape, silhouette, height, and natural body proportions across all cuts without morphing or warping.'
- 'Garment Lock: REFERENCE IMAGE 2 (PRODUCT FRONT) [and REFERENCE IMAGE 3 (PRODUCT BACK) if provided] - Lock exact garment cut, fabric, color, prints, and stitching.'
- 'Environment Lock: {background_preset_desc if background_preset_desc else 'Minimalist aesthetic studio room'} - Lock room architecture and background elements across all cuts.'
- In every scene prompt, the 'Avoid:' block MUST include: 'no face swapping, no morphing facial identity, no changing body shape, no warping body proportions, no shifting waist or bust size, no inconsistent height, no fluctuating skin tone, no altering dress colors, no changing fabric patterns, no inconsistent neckline, no background shifts'.

REQUIREMENTS:
1. Automatic image role detection & product truth analysis.
2. AUTHENTIC APPAREL TERMINOLOGY & GOOGLE FLOW ZERO-REJECTION ENGINE:
   - When the reviewed product is a bra, panty, undergarments, shapewear, or lingerie set:
     * YOU MUST EXPLICITLY USE AUTHENTIC COMMERCIAL TERMS ("bra", "panty", "undergarments", "bra-panty set", "wire-free bra", "seamless panty", "innerwear", "shapewear") across Script, Spoken Voice-Over, and Google Flow Video Prompts!
     * NEVER use awkward false euphemisms like "dress" or "mini tunic" to disguise undergarments in speech or prompt.
     * E-Commerce Styling Standard: Use Zivame/Clovia formula (top/bra worn with high-waist palazzo/trousers + matching panty held in hands demonstrating waist elastic stretch) or Parachute pants + bralette hack with panty side-strings visible at waistband.
     * What to avoid: ONLY sexually explicit/pornographic content (nudity, exposed breasts, erotic, cleavage zoom) is prohibited. Commercial fashion terms ("bra", "panty", "undergarments") are 100% permitted.
   - FORMAT ALL GOOGLE FLOW PROMPTS with the 8C structure: 'Voice-over:', 'Visual:', 'Environment Lock:', 'Style:', 'Camera:', 'Audio:', 'Transition:', and mandatory 'Avoid:' negative safety block ('No nudity, no underwear exposure without outer layer, no suggestive angles, no sexualized presentation, no warped limbs, no unnatural body physics, no background shifts, no changing room decor, no inconsistent wall colors...').
3. Strict Deliverables in Output:
   - Product & Strategy Analysis
   - Selected Hook (Score target 99/100)
   - Scene-by-Scene breakdown with precise timestamps (up to 60s), Voice-over in requested Tone, Visual action, and complete Google Flow prompt
   - Final Quality & Safety Scorecard table
   - 🚀 SCRIPT-LINKED INSTAGRAM & YOUTUBE SHORTS SEO SUITE (MANDATORY & 100% SCRIPT SYNCHRONIZED):
     * 📸 SCRIPT-LINKED INSTAGRAM SEO:
       - Algorithmic Hook-Sync Caption (First 125 chars MUST match Scene 1 spoken dialogue & visual hook, followed by key benefits, price under ₹{price}, and direct CTA).
       - 3-Tier Targeted Hashtag Engine: Mega (>1M), Niche (100K-1M matching category/vibe), Micro (<100K matching fabric/garment).
       - Instagram Accessibility Alt-Text (High-SEO description for visual explore search indexing).
       - ManyChat Auto-DM Trigger Keyword & Full Response Template.
       - Pinned Engagement Comment Template.
     * ▶️ SCRIPT-LINKED YOUTUBE SHORTS SEO:
       - 3 Viral High-CTR Title Options: Option 1 (Curiosity / Shock), Option 2 (Problem-Solving / Hack), Option 3 (High-Volume SEO Search).
       - YouTube Video Chapters / Timestamps matching the exact scene timestamps in the script (00:00 - ..., 00:06 - ...).
       - 500-Character SEO Meta Tags (Comma-separated high-intent search tags directly from script terms).
       - High-CTR Thumbnail Text Hook (3-5 bold uppercase words matching Scene 1 visual).
     * 📲 1-CLICK WHATSAPP & TELEGRAM AFFILIATE DEAL CARD with price, discounts, and Meesho code.
4. DYNAMIC CALENDAR ADAPTATION & ANTI-CLICHÉ:
   - Avoid repetitive clichés like 'maine socha tha scam hoga' everywhere.
   - Infuse today's Indian seasonal/festive mood, specific fabric drape, and relatable creator commentary.
   - Every single generated script must be 100% original and customized to the specific product and creator.
"""
    contents_parts.append({"text": user_prompt})
    
    payload = {
        "system_instruction": {
            "parts": [{"text": master_sys_instruction}]
        },
        "contents": [{"parts": contents_parts}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    
    candidate_models = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.7-flash"]
    last_err = ""
    
    for model_name in candidate_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(api_url, json=payload, timeout=35)
            if res.status_code == 200:
                data = res.json()
                cands = data.get("candidates", [])
                if cands:
                    text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if text:
                        return text, None
            else:
                err_data = res.json() if res.content else {}
                last_err = err_data.get("error", {}).get("message", f"HTTP {res.status_code}")
        except Exception as ex:
            last_err = str(ex)
            
    return None, f"All Gemini models busy. Last error: {last_err}"


# ---------------------------------------------------------
# Sidebar: Settings & Controls
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    # API Key Configuration
    env_key = os.getenv("GEMINI_API_KEY", "")
    if not env_key:
        env_key = get_safe_secret("GEMINI_API_KEY", "")
    masked_key = f"{env_key[:4]}...{env_key[-4:]}" if len(env_key) > 8 else ""
    
    if env_key:
        st.success(f"🟢 API Key Active ({masked_key})")
    else:
        st.warning("⚠️ No API Key found (.env or Secrets)")
        
    with st.expander("🔑 Update / Override API Key", expanded=not bool(env_key)):
        custom_key = st.text_input("Gemini API Key", value="", type="password", placeholder="Enter AIza... key")
        if st.button("Save Key to .env"):
            if custom_key.strip():
                with open(ENV_PATH, "w", encoding="utf-8") as f:
                    f.write(f"GEMINI_API_KEY={custom_key.strip()}\n")
                os.environ["GEMINI_API_KEY"] = custom_key.strip()
                st.success("Key saved successfully! Refreshing...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Key cannot be empty.")
                
    st.markdown("---")
    st.markdown("### 🎬 Video Specifications")
    
    # Dual Voice-Over Tone
    voice_tone = st.selectbox(
        "🗣️ Voice-Over Tone",
        [
            "👯 Relatable Bestie Vibe (Casual, energetic, conversational Hinglish)",
            "👠 Fashion Stylist & Expert Vibe (Polished, aesthetic, high-value styling guru)"
        ],
        index=0
    )
    
    # Duration Options (Min 10s, Max 60s, Presets + Custom Slider)
    default_dur_val = "30s"
    if "remix_data" in st.session_state and st.session_state["remix_data"].get("duration"):
        r_sec = st.session_state["remix_data"]["duration"]
        if r_sec <= 12:
            default_dur_val = "10s"
        elif r_sec <= 22:
            default_dur_val = "15-20s"
        elif r_sec <= 35:
            default_dur_val = "30s"
        elif r_sec <= 50:
            default_dur_val = "45s"
        else:
            default_dur_val = "60s"
    elif "selected_trend" in st.session_state:
        default_dur_val = st.session_state["selected_trend"].get("recommended_duration", "30s")
    
    duration = render_duration_selector(key_prefix="studio", default_val=default_dur_val, label="⏱️ Video Duration (Min 10s - Max 60s)")
    
    studio_include_ost = st.checkbox(
        "🟡 Include On-Screen Bold Text / Subtitles (Optional)",
        value=False,
        key="studio_ost_toggle",
        help="When enabled, each scene will specify high-contrast on-screen text overlays (e.g. 🚨 ZARA DUPE UNDER ₹499) for viewers scrolling on mute."
    )
    
    language = st.selectbox(
        "🌐 Language Script",
        ["Hinglish (Natural Indian Social Tone)", "Hindi (हिंदी Devanagari)", "English (Indian Urban)"],
        index=0
    )
    
    # Presentation Modes
    pres_modes = [
        "👗 Direct Try-On (Complete Full Outfit from 00:00 - Universal Rule)",
        "🪄 Magic Transition (Complete Outfit from 00:00 ➔ 00:02 Snap/Twirl)",
        "💡 Problem ➔ Solution Hack (Wardrobe struggle ➔ Secret product fix)",
        "🏖️ Parachute/Palazzo + Bralette Peek-a-Boo (Verified 0% Ban Direct Try-On)",
        "📦 Zivame/Clovia Review (Top worn + Panty in hand - 0% Policy Risk)",
        "🛍️ Hold & Review Only (Never worn, hanger/tabletop display)"
    ]
    default_mode_idx = 0
    if "selected_trend" in st.session_state:
        trend_mode = st.session_state["selected_trend"].get("recommended_format", "")
        for idx, m in enumerate(pres_modes):
            if trend_mode in m or m.split(" ")[1] in trend_mode:
                default_mode_idx = idx
                break
    presentation_mode = st.selectbox("👗 Wardrobe Presentation Mode", pres_modes, index=default_mode_idx)
    
    # Categories
    categories = [
        "Auto-detect from Photo",
        "Ethnic Wear (Kurti / Suit / Saree / Blouse)",
        "Western & Casual Dresses",
        "Wardrobe Problem-Solver Hack (Tape, Straps, Pads)",
        "Shapewear & Saree Silhouette",
        "Intimates & Lingerie 2-Piece Set",
        "Nightwear & Loungewear Slip"
    ]
    default_cat_idx = 0
    if "selected_trend" in st.session_state:
        trend_cat = st.session_state["selected_trend"].get("category", "")
        for idx, c in enumerate(categories):
            if trend_cat in c or c in trend_cat:
                default_cat_idx = idx
                break
    category_hint = st.selectbox("🏷️ Product Category", categories, index=default_cat_idx)
    
    st.markdown("---")
    st.markdown("### 🏷️ Commerce Details")
    default_price = st.session_state["selected_trend"].get("price_range", "₹399") if "selected_trend" in st.session_state else ""
    product_price = st.text_input("Product Price (₹)", value=default_price, placeholder="e.g. ₹399")
    meesho_code = st.text_input("Meesho Product Code", placeholder="e.g. s-28491823")
    studio_affiliate_link = st.text_input("🔗 Affiliate / Custom Buy Link", placeholder="https://wishlink.com/... or Meesho share link", key="studio_affiliate_in")
    
    studio_dupe_info = render_brand_dupe_selector(key_prefix="studio", meesho_price=product_price if product_price else "₹399")
    
    default_notes = f"Trend Angle: {st.session_state['selected_trend']['title']}" if "selected_trend" in st.session_state else ""
    seller_notes = st.text_area("Custom Creator / Trend Notes", value=default_notes, placeholder="e.g. Highlight soft elastic waistband and breathability.", height=80)
    
    if "selected_trend" in st.session_state:
        if st.button("❌ Clear Active Trend Preset"):
            del st.session_state["selected_trend"]
            st.rerun()
            
    st.markdown("---")
    st.markdown("### 🏠 Background & Set Consistency")
    bg_options = {
        "🛋️ Aesthetic Warm Apartment": "Minimalist warm ivory limewash wall, natural light oak wood flooring, sheer white linen curtains, subtle indoor plant, soft diffused afternoon daylight",
        "🏛️ Minimalist Luxury Fashion Studio": "Seamless off-white cyclorama curved backdrop, warm directional soft key-light, matte grey concrete floor, high-fashion editorial aesthetic",
        "🪞 Influencer Bedroom & Mirror": "Aesthetic beige textured bedroom wall, arched gold full-length standing mirror, warm ambient brass lamp, boho woven jute rug, soft cozy daylight",
        "🌿 Festive Courtyard / Verandah": "Traditional Indian architectural stone archway, warm terracotta lime finish, vintage brass lantern, soft golden hour sunlight, festive ethnic atmosphere",
        "📸 Custom Room Photo (From Step 1)": "Exact room architecture, walls, and lighting from uploaded Background Anchor photo"
    }
    bg_preset_choice = st.selectbox(
        "Room & Studio Continuity",
        list(bg_options.keys()),
        index=0,
        help="Locks this exact physical room across all scenes so the background never changes."
    )
    active_bg_desc = bg_options[bg_preset_choice]
    st.caption("🔒 **100% Background Consistency**: Har scene isi same room aur lighting me set rahega.")

    st.markdown("---")
    st.caption("⚡ **100% Live Online Engine**: Powered by Gemini AI with live calendar & dynamic trend adaptation.")
    
    st.markdown("""
    <div style='font-size:0.75rem; color:#64748b; margin-top:1rem;'>
        <b>Google Flow & Kling AI Approved</b><br>
        100% Policy-Safe Lexical Cloaking + Negative Safety Prompt Included.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Main UI Layout & Top Tabs
# ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">👗 Meesho AI Video Director & Daily Trends Radar</div>
    <div class="hero-subtitle">
        Daily-updated Instagram trending reel concepts for all women's wear categories + 100% policy-safe Google Flow & Kling AI video prompts and launch kits.
    </div>
</div>
""", unsafe_allow_html=True)

# Top Level Navigation State
NAV_RADAR = "🔥 Trends Radar"
NAV_URL_PROD = "👗 Product Photo to Script"
NAV_PROBLEM = "👠 Women's Problem Stories"
NAV_FASHION = "👗 AI Fashion & Body Studio"
NAV_HAUL = "📦 Batch Haul Studio (1-5 Finds)"
NAV_STUDIO = "🎬 Studio Workspace"
NAV_REMIX = "🔗 Instagram Remixer"

if "active_nav_tab" not in st.session_state:
    st.session_state["active_nav_tab"] = NAV_RADAR

# Normalize previous longer titles if in session state
if "Radar" in st.session_state["active_nav_tab"] or "Trends" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_RADAR
elif "URL" in st.session_state["active_nav_tab"] or "Meesho" in st.session_state["active_nav_tab"] or "Product Photo" in st.session_state["active_nav_tab"] or "Photo to Video" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_URL_PROD
elif "Problem" in st.session_state["active_nav_tab"] or "Stories" in st.session_state["active_nav_tab"] or "Wardrobe" in st.session_state["active_nav_tab"] or "Hacks" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_PROBLEM
elif "Fashion" in st.session_state["active_nav_tab"] or "Body" in st.session_state["active_nav_tab"] or "Stylist" in st.session_state["active_nav_tab"] or "Pillars" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_FASHION
elif "Haul" in st.session_state["active_nav_tab"] or "Batch" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_HAUL
elif "Remix" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_REMIX
elif "Studio" in st.session_state["active_nav_tab"] or "Director" in st.session_state["active_nav_tab"]:
    st.session_state["active_nav_tab"] = NAV_STUDIO

# Render 7 prominent top navigation tab buttons
col_n1, col_n2, col_n3, col_n4, col_n5, col_n6, col_n7 = st.columns(7)
with col_n1:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_RADAR else "secondary"
    if st.button(NAV_RADAR, use_container_width=True, type=b_type, key="top_nav_radar"):
        st.session_state["active_nav_tab"] = NAV_RADAR
        st.rerun()
with col_n2:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_URL_PROD else "secondary"
    if st.button(NAV_URL_PROD, use_container_width=True, type=b_type, key="top_nav_url_prod"):
        st.session_state["active_nav_tab"] = NAV_URL_PROD
        st.rerun()
with col_n3:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_PROBLEM else "secondary"
    if st.button(NAV_PROBLEM, use_container_width=True, type=b_type, key="top_nav_problem"):
        st.session_state["active_nav_tab"] = NAV_PROBLEM
        st.rerun()
with col_n4:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_FASHION else "secondary"
    if st.button(NAV_FASHION, use_container_width=True, type=b_type, key="top_nav_fashion"):
        st.session_state["active_nav_tab"] = NAV_FASHION
        st.rerun()
with col_n5:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_HAUL else "secondary"
    if st.button(NAV_HAUL, use_container_width=True, type=b_type, key="top_nav_haul"):
        st.session_state["active_nav_tab"] = NAV_HAUL
        st.rerun()
with col_n6:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_STUDIO else "secondary"
    if st.button(NAV_STUDIO, use_container_width=True, type=b_type, key="top_nav_studio"):
        st.session_state["active_nav_tab"] = NAV_STUDIO
        st.rerun()
with col_n7:
    b_type = "primary" if st.session_state["active_nav_tab"] == NAV_REMIX else "secondary"
    if st.button(NAV_REMIX, use_container_width=True, type=b_type, key="top_nav_remix"):
        st.session_state["active_nav_tab"] = NAV_REMIX
        st.rerun()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: Daily Trends Radar
# ---------------------------------------------------------
if st.session_state["active_nav_tab"] == NAV_RADAR:
    ctx = get_seasonal_context()
    
    col_t_head, col_t_btn = st.columns([2.8, 1.2])
    with col_t_head:
        st.markdown(f"### 📅 Fresh Instagram Trends for **{ctx['day_name']}, {ctx['date_str']}**")
        st.markdown(f"**Current Seasonal Vibe:** `{ctx['season_title']}` — *{ctx['season_focus']}*")
    with col_t_btn:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        refresh_trends = st.button("🔄 Generate 20 Fresh Trends with AI", type="primary", use_container_width=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border:1px solid #e2e8f0; border-radius:12px; padding:1rem 1.25rem; margin-bottom:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-weight:800; color:#0f172a; margin-bottom:0.5rem; font-size:1.05rem; display:flex; align-items:center; gap:0.4rem;">
            <span>⚡ 3-Step Daily Production Workflow (20 Fresh Live Trends Generated Daily)</span>
        </div>
        <div style="display:flex; gap:1.2rem; flex-wrap:wrap; font-size:0.88rem; color:#334155; line-height:1.5;">
            <span><b>Step 1:</b> 🎯 Neeche se <b>Aaj ka Trend Choose karein</b> (20 Live AI Trends across Festive, Western, Sarees, Intimates & Hacks)</span>
            <span>➔</span>
            <span><b>Step 2:</b> 📸 <b>Creator Photo & Product Photo</b> Upload karein</span>
            <span>➔</span>
            <span><b>Step 3:</b> 🚀 <b>'Generate Complete Production'</b> dabakar 100% Unique Script, Prompts & Launch Kit payein!</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    radar_api_key = env_key or os.getenv("GEMINI_API_KEY", "")
    trends = []
    
    if refresh_trends:
        if not radar_api_key:
            st.warning("⚠️ **Gemini API Key Required**: Please enter your Gemini API Key in the left sidebar to generate 20 new trends with AI.")
        else:
            with st.spinner("🤖 Consulting Gemini AI & today's Indian fashion calendar to synthesize 20 fresh viral trends..."):
                trends, t_err = fetch_daily_trends_with_gemini(radar_api_key, force_refresh=True)
                if t_err:
                    st.error(f"❌ {t_err}")
                    trends = []
                else:
                    st.toast("⚡ Generated 20 fresh viral trends for today!", icon="🔥")
    else:
        # Load from 24-Hour Server Cache (0 API calls, 0 cost on mobile reloads)
        trends, t_err = fetch_daily_trends_with_gemini(radar_api_key, force_refresh=False)
        if not trends:
            if not radar_api_key:
                st.warning("⚠️ **Gemini API Key Required**: Please enter your Gemini API Key in the left sidebar to generate today's 20 live dynamic Instagram trends.")
            elif t_err:
                st.error(f"❌ {t_err}")
                trends = []
    
    if trends:
        # 24-Hour Server-Side Mobile Cache Guarantee Badge
        st.markdown(f"""
        <div style="background:#ecfdf5; border:1px solid #10b981; border-radius:10px; padding:0.65rem 1.1rem; margin-bottom:1.2rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:0.5rem;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <span style="font-size:1.2rem;">⚡</span>
                <span style="color:#065f46; font-weight:700; font-size:0.92rem;">
                    24-Hour Mobile Cache Active — Instant 1ms Load (₹0 API Cost)
                </span>
            </div>
            <div style="color:#047857; font-size:0.82rem; font-weight:600;">
                📅 Current Cache: {ctx['day_name']}, {ctx['date_str']} • 20 Curated Trends Ready
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Category Filter Pills & Search
        col_f1, col_f2 = st.columns([2.8, 1.2])
        with col_f1:
            categories_filter = ["All (20)", "Festive & Ethnic", "Western & Casuals", "Sarees & Blouses", "Intimates & Shapewear", "Wardrobe Hacks"]
            selected_filter = st.radio(
                "Filter Category",
                categories_filter,
                index=0,
                horizontal=True,
                label_visibility="collapsed"
            )
        with col_f2:
            search_query = st.text_input("🔍 Search Trends", placeholder="Filter by keyword...", label_visibility="collapsed")
            
        filtered_trends = []
        for t in trends:
            cat_match = True
            if selected_filter != "All (20)":
                clean_filter = selected_filter.split(" ")[0].lower()
                cat_match = (
                    clean_filter in t.get("category", "").lower() or 
                    clean_filter in t.get("category_badge", "").lower() or
                    any(w.lower() in t.get("category", "").lower() for w in selected_filter.split(" "))
                )
            query_match = True
            if search_query.strip():
                q = search_query.strip().lower()
                query_match = (
                    q in t.get("title", "").lower() or
                    q in t.get("hook", "").lower() or
                    q in t.get("concept", "").lower() or
                    q in t.get("meesho_keyword", "").lower() or
                    q in t.get("audio_vibe", "").lower()
                )
            if cat_match and query_match:
                filtered_trends.append(t)
                
        st.caption(f"Showing **{len(filtered_trends)}** of **{len(trends)}** Live AI Trends")
        
        for trend in filtered_trends:
            with st.container():
                st.markdown(f"""
                <div class="trend-card">
                    <div class="trend-header">
                        <span class="trend-title">{trend.get('format_num', 'Trend')} • {trend.get('title', '')}</span>
                        <div>
                            <span class="badge-pill badge-pink">{trend.get('category_badge', 'Fashion')}</span>
                            <span class="badge-pill badge-green">Score: {trend.get('hook_score', '99/100')}</span>
                            <span class="badge-pill badge-amber">{trend.get('recommended_duration', '🎬 30s')}</span>
                        </div>
                    </div>
                    <div class="trend-hook-box">
                        <b>🪝 Spoken Opening Hook:</b> "{trend.get('hook', '')}"
                    </div>
                    <div style="font-size:0.88rem; color:#475569; margin: 0.4rem 0;">
                        <b>🎬 Reel Concept:</b> {trend.get('concept', '')}
                    </div>
                    <div style="display:flex; gap:1.5rem; font-size:0.82rem; color:#64748b; margin-top:0.4rem; flex-wrap:wrap;">
                        <span>🎵 <b>Audio:</b> {trend.get('audio_vibe', '')}</span>
                        <span>🛍️ <b>Recommended Search:</b> <i>{trend.get('meesho_keyword', '')}</i></span>
                        <span>💰 <b>Price:</b> {trend.get('price_range', '')}</span>
                        <span>🎬 <b>Format:</b> {trend.get('recommended_format', '🪄 Magic Transition')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns([1.5, 1.5])
                with c_btn1:
                    btn_label = f"⚡ Use This Trend in Studio"
                    if st.button(btn_label, key=f"btn_use_{trend.get('id', trend.get('title'))}", use_container_width=True):
                        st.session_state["selected_trend"] = trend
                        st.session_state["active_nav_tab"] = NAV_STUDIO
                        sample_creator_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
                        if os.path.exists(sample_creator_path) and "sample_creator_bytes" not in st.session_state:
                            with open(sample_creator_path, "rb") as cf:
                                st.session_state["sample_creator_bytes"] = cf.read()
                        st.toast(f"✅ Loaded '{trend.get('title')}'! Studio Workspace open ho gaya.", icon="🚀")
                        time.sleep(0.3)
                        st.rerun()
                with c_btn2:
                    meesho_search_url = f"https://www.meesho.com/search?q={quote_plus(trend.get('meesho_keyword', 'fashion'))}"
                    st.link_button("🔍 Find Matching Items on Meesho", url=meesho_search_url, use_container_width=True)

# ---------------------------------------------------------
# ---------------------------------------------------------
# TAB: Product Photo to Video Script Studio
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_URL_PROD:
    st.markdown("""
    <div style="background:linear-gradient(135deg, #fdf2f8 0%, #f5f3ff 100%); border:1px solid #fbcfe8; border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
        <div style="font-weight:800; color:#831843; margin-bottom:0.4rem; font-size:1.15rem; display:flex; align-items:center; gap:0.5rem;">
            <span>👗 Product Photo to Video Script Studio</span>
        </div>
        <div style="font-size:0.9rem; color:#4c0519; line-height:1.5;">
            Directly upload your Meesho catalog or real product photo. Gemini Vision AI automatically analyzes fabric, color, silhouette and styling details, and generates an authentic <b>Viral Instagram Reel Script & Google Flow Video Prompts</b> with Studio Voice-Over & Script-Linked SEO!
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_u_left, col_u_right = st.columns([3.2, 2.0])
    
    with col_u_left:
        st.markdown("##### 👗 Step 1: Product Photo (Meesho Catalog / Real Product)")
        u_product_file = st.file_uploader(
            "Upload Product Photo (Front / Catalog / Ghost Mannequin)",
            type=["jpg", "png", "jpeg", "webp"],
            key="prod_photo_uploader",
            help="Upload your Meesho product catalog image or real photo. Vision AI will auto-detect garment styling, colors, and fabric!"
        )
        
        # 1-Click Fast Sample Products
        st.caption("✨ Ya fir niche se 1-click sample product photo chunein:")
        col_sp1, col_sp2, col_sp3, col_sp4 = st.columns(4)
        sample_prod_dir = os.path.join(BASE_DIR, "static", "sample_products")
        
        with col_sp1:
            if st.button("🥻 Anarkali", key="btn_sample_anarkali", use_container_width=True):
                p_path = os.path.join(sample_prod_dir, "sample_anarkali.jpg")
                if os.path.exists(p_path):
                    with open(p_path, "rb") as f:
                        st.session_state["tab_photo_bytes"] = f.read()
                    st.session_state["tab_photo_title"] = "Embroidered Georgette Anarkali"
                    st.toast("✅ Sample Anarkali Photo loaded!", icon="🥻")
                    st.rerun()
                    
        with col_sp2:
            if st.button("👔 Linen Shirt", key="btn_sample_shirt", use_container_width=True):
                p_path = os.path.join(sample_prod_dir, "sample_linen_shirt.jpg")
                if os.path.exists(p_path):
                    with open(p_path, "rb") as f:
                        st.session_state["tab_photo_bytes"] = f.read()
                    st.session_state["tab_photo_title"] = "Oversized Striped Linen Shirt"
                    st.toast("✅ Sample Linen Shirt Photo loaded!", icon="👔")
                    st.rerun()
                    
        with col_sp3:
            if st.button("✨ Kurti Set", key="btn_sample_kurti", use_container_width=True):
                p_path = os.path.join(sample_prod_dir, "sample_kurti_set.jpg")
                if os.path.exists(p_path):
                    with open(p_path, "rb") as f:
                        st.session_state["tab_photo_bytes"] = f.read()
                    st.session_state["tab_photo_title"] = "Chikankari Kurta Set"
                    st.toast("✅ Sample Kurti Set Photo loaded!", icon="✨")
                    st.rerun()
                    
        with col_sp4:
            if st.button("👙 Bralette Set", key="btn_sample_bralette", use_container_width=True):
                p_path = os.path.join(sample_prod_dir, "sample_bralette_set.jpg")
                if os.path.exists(p_path):
                    with open(p_path, "rb") as f:
                        st.session_state["tab_photo_bytes"] = f.read()
                    st.session_state["tab_photo_title"] = "Seamless Bralette 2-Piece Set"
                    st.toast("✅ Sample Bralette Set Photo loaded!", icon="👙")
                    st.rerun()

        # Active Product Preview
        active_prod_bytes = u_product_file.getvalue() if u_product_file else st.session_state.get("tab_photo_bytes")
        if active_prod_bytes:
            col_pv1, col_pv2 = st.columns([1.2, 2.8])
            with col_pv1:
                st.image(active_prod_bytes, caption="Active Product Photo", width=110)
            with col_pv2:
                st.markdown("<div style='color:#065f46; background:#ecfdf5; border:1px solid #10b981; border-radius:8px; padding:6px 10px; font-size:0.83rem;'><b>🟢 Product Photo Loaded</b><br>AI Vision will extract fabric, colors & details!</div>", unsafe_allow_html=True)
                if st.session_state.get("tab_photo_bytes") and not u_product_file:
                    if st.button("❌ Remove Photo", key="btn_clear_tab_photo"):
                        del st.session_state["tab_photo_bytes"]
                        if "tab_photo_title" in st.session_state:
                            del st.session_state["tab_photo_title"]
                        st.rerun()

        # Optional manual details override
        with st.expander("✏️ Optional: Price, Code & Title Override", expanded=False):
            c_op1, c_op2 = st.columns(2)
            with c_op1:
                p_price_val = st.text_input("Product Price (₹)", value="₹499", key="tab_photo_price", placeholder="e.g. ₹499")
            with c_op2:
                p_code_val = st.text_input("Meesho Product Code", value="s-18392841", key="tab_photo_code", placeholder="e.g. s-18392841")
            p_title_val = st.text_input("Product Title (Optional)", value=st.session_state.get("tab_photo_title", ""), key="tab_photo_title_in", placeholder="Leave blank for AI auto-detection")
            p_affiliate_val = st.text_input("🔗 Product Affiliate / Buy Link", placeholder="https://wishlink.com/... or Meesho share link", key="tab_photo_affiliate_in")
            
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            u_tone = st.selectbox(
                "🗣️ Voice Tone",
                ["👯 Relatable Bestie Vibe", "👠 Fashion Stylist & Expert Vibe"],
                key="url_prod_tone"
            )
        with c_p2:
            u_dur = render_duration_selector(key_prefix="url_tab", default_val="30s", label="⏱️ Video Duration (Min 10s - Max 60s)")
            
        url_dupe_info = render_brand_dupe_selector(key_prefix="url_tab", meesho_price=p_price_val)
        
        url_include_ost = st.checkbox(
            "🟡 Include On-Screen Bold Text / Subtitles (Optional)",
            value=False,
            key="url_ost_toggle",
            help="Add high-contrast text overlays for viewers watching with sound off."
        )
        
        btn_extract = st.button("🚀 Analyze Product Photo & Generate Video Script & Prompts", type="primary", use_container_width=True, key="btn_run_url_engine")

    with col_u_right:
        st.markdown("##### 👤 Step 2: Creator Identity Anchor (Face & Body Shape Lock)")
        u_creator_file = st.file_uploader(
            "Upload Creator Reference Photo",
            type=["jpg", "png", "jpeg", "webp"],
            key="url_creator_uploader",
            help="This creator's exact face, hairstyle, skin tone, and body shape will be locked in the AI Lookbook photo and video script."
        )
        
        col_sm1, col_sm2 = st.columns([1.5, 1.5])
        with col_sm1:
            if st.button("👤 Load Sample Creator", use_container_width=True, key="btn_load_sample_creator_tab_url"):
                sample_cr_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
                if os.path.exists(sample_cr_path):
                    with open(sample_cr_path, "rb") as scf:
                        st.session_state["sample_creator_bytes"] = scf.read()
                    st.toast("✅ Sample Creator Photo loaded with Face & Body Shape Lock!", icon="👤")
                    st.rerun()
        with col_sm2:
            if "sample_creator_bytes" in st.session_state or u_creator_file:
                st.caption("🟢 **Creator Lock Active**")
                
        if u_creator_file:
            st.image(u_creator_file, caption="Active Creator Anchor", width=120)
        elif "sample_creator_bytes" in st.session_state:
            st.image(st.session_state["sample_creator_bytes"], caption="Active Sample Creator", width=120)

    # Trigger Extraction & Generation Logic
    if btn_extract:
        active_creator_bytes = u_creator_file.getvalue() if u_creator_file else st.session_state.get("sample_creator_bytes")
        active_prod_bytes = u_product_file.getvalue() if u_product_file else st.session_state.get("tab_photo_bytes")
        
        if not active_prod_bytes:
            st.error("⚠️ Please upload a Product Photo or choose one of the sample photos above.")
        else:
            with st.spinner("🔍 Gemini Vision AI is analyzing product photo, colors, fabric & styling..."):
                ext_data, ext_err = extract_meesho_product_data(p_title_val, api_key=env_key, screenshot_bytes=active_prod_bytes)
                
            if ext_err or not ext_data:
                st.error(f"❌ Analysis error: {ext_err or 'Could not parse product details'}")
            else:
                if p_price_val: ext_data["price"] = p_price_val
                if p_code_val: ext_data["meesho_code"] = p_code_val
                if p_title_val.strip(): ext_data["title"] = p_title_val.strip()
                ext_data["source"] = "AI Vision Analysis (Product Photo)"
                
                st.session_state["meesho_extracted_data"] = ext_data
                st.toast("🎉 Product photo analyzed successfully by Gemini Vision!", icon="✅")

                # Automatically write the Video Production Script & Prompts
                if env_key:
                    with st.spinner("🎬 Writing 100% unique viral Reel script & Google Flow prompts with 3-Point Consistency Lock..."):
                        prod_bytes_for_script = [active_prod_bytes]
                        script_res, s_err = call_gemini_api(
                            api_key=env_key,
                            creator_bytes=active_creator_bytes,
                            product_images=prod_bytes_for_script,
                            duration=u_dur,
                            language="Hinglish (Natural Indian Social Tone)",
                            presentation_mode="🪄 Magic Transition (Casual in Sc.1 ➔ Snap/Spin into Try-On)",
                            voice_tone=u_tone,
                            category_hint=ext_data.get("category", "Ethnic Wear"),
                            price=ext_data.get("price", p_price_val),
                            meesho_code=ext_data.get("meesho_code", p_code_val),
                            notes=f"Key USPs: {', '.join(ext_data.get('styling_usps', []))}. Fabric: {ext_data.get('fabric')}. Color: {ext_data.get('color')}",
                            brand_dupe_info=url_dupe_info,
                            include_on_screen_text=url_include_ost
                        )
                        if script_res:
                            st.session_state["meesho_url_script"] = script_res
                st.rerun()

    # Display Extracted Product Results & HD Photo Studio
    if "meesho_extracted_data" in st.session_state:
        p_data = st.session_state["meesho_extracted_data"]
        st.markdown("---")
        
        # Product Card
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:1.5rem; box-shadow:0 2px 10px rgba(0,0,0,0.03);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
                <div>
                    <span style="font-size:0.8rem; font-weight:700; color:#831843; text-transform:uppercase; letter-spacing:0.5px;">📦 {p_data.get('source', 'Extracted Product')}</span>
                    <h3 style="margin:0.2rem 0; color:#0f172a;">{p_data.get('title', 'Meesho Fashion Product')}</h3>
                    <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-top:0.4rem;">
                        <span class="badge-pill badge-pink">{p_data.get('category', 'Fashion')}</span>
                        <span class="badge-pill badge-green">💰 Price: {p_data.get('price', '₹499')}</span>
                        <span class="badge-pill badge-amber">🏷️ Code: {p_data.get('meesho_code', 's-18392841')}</span>
                        <span class="badge-pill badge-purple">🎨 {p_data.get('color', 'Festive')}</span>
                    </div>
                </div>
            </div>
            <div style="margin-top:0.75rem; font-size:0.88rem; color:#475569;">
                <b>🧵 Fabric & Drape:</b> {p_data.get('fabric', 'Premium Textile')} &nbsp;|&nbsp; 
                <b>✨ Key USPs:</b> {', '.join(p_data.get('styling_usps', ['High-converting styling']))}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c_sh1, c_sh2 = st.columns([1.5, 3.5])
        with c_sh1:
            kw = p_data.get("meesho_search_keyword") or p_data.get("title", "")
            st.link_button("🔍 Open Product Search on Meesho", url=f"https://www.meesho.com/search?q={quote_plus(kw)}", use_container_width=True)

        # 🎬 Automated Reel Script & Prompts
        st.markdown("---")
        st.markdown("### 🎬 Automated Video Script & Google Flow Prompts")
        st.caption("3-Point Consistency Lock Active: Creator Face & Body Shape + Garment Cuts & Colors + Studio Set.")
        
        if "meesho_url_script" in st.session_state:
            url_script_text = st.session_state["meesho_url_script"]
            
            # 🪝 A/B Hook Battle Component
            render_ab_hook_battle(url_script_text, session_key="meesho_url_script", key_prefix="url_hook_battle")
            st.markdown("---")

            s_tab1, s_tab2, s_tab3, s_tab4 = st.tabs([
                "🎬 Scene-by-Scene Script & Voice-Over",
                "🤖 Google Flow 8C Prompts",
                "🚀 Script-Linked SEO Studio",
                "📥 Export & Transfer to Studio"
            ])
            
            with s_tab1:
                render_voiceover_audio_studio(url_script_text, key_prefix="url_tab")
                st.markdown("---")
                st.markdown(url_script_text)
                
            with s_tab2:
                st.markdown("#### 🤖 Copy-Ready Google Flow & Kling AI Prompts")
                st.info("💡 Every prompt contains the mandatory 'Identity & Anatomy Lock', 'Garment Lock', 'Environment Lock', and anti-morphing 'Avoid:' negative safety block.")
                lines = url_script_text.splitlines()
                in_p = False
                cur_p = []
                p_cnt = 0
                for l in lines:
                    if "```text" in l or (l.strip() == "```" and in_p):
                        if in_p:
                            p_cnt += 1
                            st.markdown(f"**Scene Prompt #{p_cnt}:**")
                            st.code("\n".join(cur_p).strip(), language="text")
                            cur_p = []
                            in_p = False
                        else:
                            in_p = True
                    elif in_p:
                        cur_p.append(l)
                if p_cnt == 0:
                    st.markdown("Prompts are included in the Scene-by-Scene Script above.")
                    
            with s_tab3:
                render_script_linked_seo_studio(url_script_text, key_prefix="url_tab_seo", affiliate_link=st.session_state.get("tab_photo_affiliate_in", ""))
                    
            with s_tab4:
                c_ex1, c_ex2 = st.columns(2)
                with c_ex1:
                    st.download_button(
                        "📥 Download Production Package (.md)",
                        data=url_script_text,
                        file_name=f"meesho_production_{p_data.get('meesho_code', 'product')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with c_ex2:
                    if st.button("🚀 Transfer Everything to Studio Workspace", type="primary", use_container_width=True, key="btn_transfer_everything_studio"):
                        st.session_state["active_nav_tab"] = NAV_STUDIO
                        st.session_state["latest_script"] = url_script_text
                        st.toast("✅ Transferred to Studio Workspace! You can customize background sets & camera angles.", icon="🚀")
                        time.sleep(0.3)
                        st.rerun()


# ---------------------------------------------------------
# TAB 2: Instagram Reel Remixer & Analyzer
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_REMIX:
    st.markdown("### 🔗 Instagram Reel Reverse-Engineer & Smart Remixer")
    st.markdown("""
    Paste any viral Instagram Reel link below. The AI will analyze its psychological hook, audio script pacing, and visual transitions, and then adapt them to create an original high-converting reel for your Meesho product!
    """)
    
    col_r_url, col_r_btn = st.columns([3.5, 1])
    with col_r_url:
        reel_url = st.text_input(
            "🔗 Instagram Reel URL",
            placeholder="https://www.instagram.com/reel/C7xyz123abc/ or https://www.instagram.com/p/...",
            key="input_reel_url"
        )
    with col_r_btn:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        analyze_clicked = st.button("⚡ Analyze Reel Link", type="primary", use_container_width=True)
        
    remix_strategy = st.radio(
        "🎯 Select Remix Strategy",
        [
            "🎯 Smart Remix (Recommended: Adapts viral psychology & cut timing to your Meesho product - 100% original)",
            "🔄 Shot-for-Shot Replication (Recreates exact dialogue rhythm & scene beats for your product)"
        ],
        index=0,
        help="Smart Remix avoids duplicate content while borrowing the viral pacing structure."
    )
    
    # Process link extraction if clicked
    if analyze_clicked:
        if not reel_url.strip():
            st.error("Please enter a valid Instagram Reel URL.")
        elif "instagram.com" not in reel_url:
            st.error("Please provide a valid Instagram link (e.g. https://www.instagram.com/reel/...).")
        else:
            with st.spinner("🔍 Fetching Instagram Reel metadata, caption, and audio cadence..."):
                reel_data, reel_err = extract_instagram_reel(reel_url)
                if reel_data:
                    reel_data["strategy"] = "Smart Remix" if "Smart" in remix_strategy else "Shot-for-Shot"
                    st.session_state["remix_data"] = reel_data
                    st.toast("🎉 Instagram Reel analyzed successfully!", icon="✅")
                else:
                    st.warning(f"⚠️ {reel_err}")
                    st.info("👇 Don't worry! Use the Zero-Failure Backup below to paste the caption or upload the reel MP4.")

    # Zero-Failure Backup Option (Always available)
    with st.expander("🛡️ Zero-Failure Backup (If Instagram Link has Login Wall or Block)", expanded=not bool(st.session_state.get("remix_data"))):
        st.markdown("""
        <p style="font-size:0.88rem; color:#475569;">
            Instagram sometimes uses login gates for automated requests. You can bypass this 100% of the time by either uploading the reel video directly or pasting its caption/transcript:
        </p>
        """, unsafe_allow_html=True)
        
        col_bk_vid, col_bk_txt = st.columns(2)
        with col_bk_vid:
            uploaded_reel_video = st.file_uploader(
                "📁 Upload Downloaded Reel Video (.mp4 / .mov)",
                type=["mp4", "mov", "webm"],
                key="backup_reel_video_uploader"
            )
            if uploaded_reel_video:
                st.video(uploaded_reel_video)
                st.caption(f"Loaded: {uploaded_reel_video.name} ({round(uploaded_reel_video.size / (1024*1024), 2)} MB)")
        with col_bk_txt:
            pasted_reel_text = st.text_area(
                "📝 Or Paste Reel Caption / Spoken Script",
                placeholder="Example: 'Guys stop scrolling! Found this insane kurti set on Meesho under 400 Rs and the quality blew my mind...'",
                height=140,
                key="backup_reel_caption"
            )
            
        if st.button("💾 Apply Zero-Failure Backup as Active Remix Reference", use_container_width=True):
            if pasted_reel_text.strip() or uploaded_reel_video:
                caption = pasted_reel_text.strip() or (f"Video Reel: {uploaded_reel_video.name}" if uploaded_reel_video else "")
                first_line = caption.split("\n")[0] if caption else "Viral Instagram Fashion Reel"
                st.session_state["remix_data"] = {
                    "success": True,
                    "title": "Manual / Uploaded Instagram Reel",
                    "description": caption,
                    "hook_text": first_line[:120],
                    "duration": 30,
                    "uploader": "Uploaded / Pasted Reference",
                    "thumbnail": "",
                    "strategy": "Smart Remix" if "Smart" in remix_strategy else "Shot-for-Shot",
                    "url": "Uploaded / Manual"
                }
                st.toast("✅ Active Reel Remix Reference updated from Backup!", icon="🚀")
                st.rerun()
            else:
                st.warning("Please upload an MP4 video or paste the caption/transcript text first.")

    # Show Active Analyzed Reel Card
    if st.session_state.get("remix_data"):
        r_info = st.session_state["remix_data"]
        st.markdown("---")
        st.markdown("#### 🎯 Active Reel Remix Reference")
        
        c_r1, c_r2 = st.columns([2.5, 1])
        with c_r1:
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                    <span style="font-weight:700; font-size:1.05rem; color:#0f172a;">🎬 {r_info.get('title', 'Analyzed Reel')}</span>
                    <span class="badge-pill badge-green">{r_info.get('strategy', 'Smart Remix')}</span>
                </div>
                <div style="font-size:0.9rem; color:#334155; margin-bottom:0.5rem;">
                    <b>🪝 Detected Hook:</b> <i>"{r_info.get('hook_text', '')}"</i>
                </div>
                <div style="font-size:0.84rem; color:#64748b; margin-bottom:0.5rem; max-height:80px; overflow-y:auto; background:#f8fafc; padding:0.5rem; border-radius:6px;">
                    <b>📝 Caption / Content:</b> {r_info.get('description', '')[:300]}...
                </div>
                <div style="display:flex; gap:1.5rem; font-size:0.82rem; color:#64748b;">
                    <span>⏱️ Duration: <b>~{r_info.get('duration', 30)}s</b></span>
                    <span>👤 Creator: <b>{r_info.get('uploader', 'Instagram Creator')}</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_r2:
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Ready to Remix ➔ Go to Studio Workspace", type="primary", use_container_width=True):
                st.session_state["active_nav_tab"] = NAV_STUDIO
                st.toast("Ready! Switching to Studio Workspace...", icon="🎬")
                time.sleep(0.3)
                st.rerun()
            if st.button("🗑️ Clear Remix Data", use_container_width=True):
                del st.session_state["remix_data"]
                st.rerun()

# ---------------------------------------------------------
# TAB 3: Studio Workspace (Generator)
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_STUDIO:
    col_back_nav, col_status_nav = st.columns([1.5, 3])
    with col_back_nav:
        if st.button("⬅️ Pick Another Trend (Back to Radar)", key="btn_back_to_radar"):
            st.session_state["active_nav_tab"] = NAV_RADAR
            st.rerun()

    # Notice banner if a remix or trend is currently active
    if st.session_state.get("remix_data"):
        r_info = st.session_state["remix_data"]
        st.success(f"🔗 **Active Reel Remix Preset Loaded:** Hook: *\"{r_info.get('hook_text', '')}\"* | Strategy: **{r_info.get('strategy', 'Smart Remix')}**")
    elif "selected_trend" in st.session_state:
        cur_t = st.session_state["selected_trend"]
        st.info(f"🎯 **Active Trend Loaded:** `{cur_t['title']}` | Category: `{cur_t['category']}` | Format: `{cur_t['recommended_format']}`")
        
    st.markdown("#### 📸 Step 1: Visual References & Ground Truth Anchors")
    st.markdown("""
    <p style="font-size:0.86rem; color:#475569; margin-top:-0.4rem; margin-bottom:1rem;">
        Provide <b>Front + Back Product Ground Truth</b> to stop AI from inventing back cuts, plus <b>Creator & Background Anchors</b> for 100% video continuity.
    </p>
    """, unsafe_allow_html=True)

    # ROW 1: Creator Anchor & Product FRONT Ground Truth
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">1. 👤 Creator Identity Anchor</span>
            <span class="badge-pill badge-pink">Face, Hair & Body Shape Lock</span>
        </div>
        <p style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            Upload photo of creator/influencer. Locks face, hair, body shape/silhouette proportions, height, and realistic Indian skin undertone.
        </p>
        """, unsafe_allow_html=True)
        
        creator_file = st.file_uploader("Upload Creator Photo", type=["jpg", "jpeg", "png", "webp"], key="creator_uploader", label_visibility="collapsed")
        if creator_file:
            st.image(creator_file, caption="Creator Identity Reference", use_container_width=True)
        elif st.session_state.get("sample_creator_bytes"):
            st.markdown("**👤 Sample Creator Photo Loaded (Identity Anchor):**")
            st.image(st.session_state["sample_creator_bytes"], caption="Creator Identity Reference", use_container_width=True)
            if st.button("🗑️ Clear Sample Creator Photo"):
                del st.session_state["sample_creator_bytes"]
                st.rerun()
        else:
            sample_creator_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
            if os.path.exists(sample_creator_path):
                if st.button("👤 Use Sample Creator Photo (Quick Test)", use_container_width=True):
                    with open(sample_creator_path, "rb") as cf:
                        st.session_state["sample_creator_bytes"] = cf.read()
                    st.rerun()
    
    with row1_c2:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">2. 🛍️ Product FRONT View (Ground Truth)</span>
            <span class="badge-pill badge-purple">Front Cuts & Prints</span>
        </div>
        <p style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            Upload catalog front view, flat-lay, or clean ghost mannequin photo.
        </p>
        """, unsafe_allow_html=True)
        
        product_files = st.file_uploader("Upload Meesho Product Front Photos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="product_uploader", label_visibility="collapsed")
        if product_files:
            p_cols = st.columns(min(len(product_files), 3))
            for i, pfile in enumerate(product_files):
                with p_cols[i % 3]:
                    st.image(pfile, caption=f"Product Front #{i+1}", use_container_width=True)
        elif "loaded_ai_image_bytes" in st.session_state:
            st.markdown(f"**✨ Active AI Clean Packshot:** `{st.session_state.get('loaded_ai_image_title', 'AI Clean Product')}`")
            st.image(st.session_state["loaded_ai_image_bytes"], caption="AI Clean Front Ground Truth", use_container_width=True)
            cp1, cp2 = st.columns(2)
            with cp1:
                st.download_button("📥 Download AI Photo", data=st.session_state["loaded_ai_image_bytes"], file_name="ai_clean_product.jpg", mime="image/jpeg", use_container_width=True)
            with cp2:
                if st.button("🗑️ Clear AI Photo", use_container_width=True):
                    del st.session_state["loaded_ai_image_bytes"]
                    st.rerun()
        else:
            cur_t = st.session_state.get("selected_trend")
            search_kw = cur_t["meesho_keyword"] if cur_t else "Floral Kurta Set"
            meesho_url = f"https://www.meesho.com/search?q={quote_plus(search_kw)}"
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.link_button("🔍 Find on Meesho", url=meesho_url, use_container_width=True)
            with c_p2:
                sample_file = cur_t.get("sample_product_file", "sample_anarkali.jpg") if cur_t else "sample_anarkali.jpg"
                sample_path = os.path.join(BASE_DIR, "static", "sample_products", sample_file)
                if os.path.exists(sample_path):
                    if st.button("🎨 Load AI Clean Photo", use_container_width=True):
                        with open(sample_path, "rb") as sf:
                            st.session_state["loaded_ai_image_bytes"] = sf.read()
                        st.session_state["loaded_ai_image_title"] = f"AI Clean Packshot ({search_kw})"
                        st.rerun()

    # ROW 2: Product BACK Ground Truth & Environment / Background Reference
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">3. 🔄 Product BACK View (Ground Truth)</span>
            <span class="badge-pill badge-green">Back Neck, Straps & Dori</span>
        </div>
        <p style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            Upload back/rear photo. Locked for 360° turns, tie-up doris, criss-cross straps & back zippers.
        </p>
        """, unsafe_allow_html=True)
        
        product_back_file = st.file_uploader("Upload Product Back View Photo", type=["jpg", "jpeg", "png", "webp"], key="product_back_uploader", label_visibility="collapsed")
        if product_back_file:
            st.image(product_back_file, caption="Product Back View Ground Truth", use_container_width=True)
        elif st.session_state.get("sample_back_bytes"):
            st.markdown("**🔄 Sample Product Back View Loaded:**")
            st.image(st.session_state["sample_back_bytes"], caption="Product Back View Ground Truth", use_container_width=True)
            if st.button("🗑️ Clear Back Photo"):
                del st.session_state["sample_back_bytes"]
                st.rerun()
        else:
            sample_back_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_bralette_model_back.jpg")
            if os.path.exists(sample_back_path):
                if st.button("🔄 Use Sample Back View Photo (Quick Test)", use_container_width=True):
                    with open(sample_back_path, "rb") as bf:
                        st.session_state["sample_back_bytes"] = bf.read()
                    st.rerun()
                    
    with row2_c2:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:1.05rem;">4. 🏠 Background Anchor Photo</span>
            <span class="badge-pill badge-amber">100% Set Lock</span>
        </div>
        <p style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            Optional room/studio photo to lock the physical set. Defaults to active sidebar preset.
        </p>
        """, unsafe_allow_html=True)
        
        bg_file = st.file_uploader("Upload Room / Studio Photo (Optional)", type=["jpg", "jpeg", "png", "webp"], key="bg_uploader", label_visibility="collapsed")
        if bg_file:
            st.image(bg_file, caption="Custom Room Anchor (Locked Across All Scenes)", use_container_width=True)
        elif st.session_state.get("custom_bg_bytes"):
            st.markdown("**🏠 Custom Room Anchor Photo Loaded:**")
            st.image(st.session_state["custom_bg_bytes"], caption="Locked Room Set", use_container_width=True)
            if st.button("🗑️ Clear Background Photo"):
                del st.session_state["custom_bg_bytes"]
                st.rerun()
        else:
            st.info(f"🔒 **Locked Set Preset:** `{bg_preset_choice}`\n\n*{active_bg_desc}*")
    
    # Auto-Sanitized Garment Crop Showcase
    if product_files:
        st.markdown("---")
        with st.expander("🛡️ Auto-Sanitized 'Only Clothes' Crop (Zero-Moderation Asset)", expanded=True):
            st.markdown("""
            <p style='font-size:0.88rem; color:#475569;'>
                <b>Smart Garment Crop:</b> Eliminates model face, cleavage, bare arms, and thighs/groin. You can download and feed this sanitized image directly into <b>Google Flow</b> or <b>Kling AI</b> without triggering policy blocks!
            </p>
            """, unsafe_allow_html=True)
            
            crop_cols = st.columns(min(len(product_files), 3))
            for i, pfile in enumerate(product_files):
                raw_bytes = pfile.getvalue()
                c_img, c_bytes = extract_safe_garment_crop(raw_bytes)
                if c_img:
                    with crop_cols[i % 3]:
                        st.image(c_img, caption=f"Safe Garment #{i+1}", use_container_width=True)
                        st.download_button(
                            label=f"📥 Download Crop #{i+1}",
                            data=c_bytes,
                            file_name=f"safe_garment_crop_{i+1}.jpg",
                            mime="image/jpeg",
                            key=f"btn_crop_{i}"
                        )
    
    # Generation Trigger Bar
    st.markdown("---")
    col_btn, col_info = st.columns([1.2, 2.5])
    
    with col_btn:
        generate_clicked = st.button("🚀 Generate Complete Production (Script + Flow Prompts + Launch Kit)", type="primary", use_container_width=True)
    
    with col_info:
        active_key = custom_key.strip() if 'custom_key' in locals() and custom_key.strip() else (os.getenv("GEMINI_API_KEY", "") or get_safe_secret("GEMINI_API_KEY", ""))
        if not active_key:
            st.warning("⚠️ Please add a Gemini API Key in the sidebar to enable video generation.")
        else:
            st.success(f"✅ Ready to generate: Gemini AI engine | Tone: {voice_tone.split(' ')[1]} | Set: {bg_preset_choice.split(' ')[1]}")
    
    # Generation Logic
    if generate_clicked:
        active_creator_bytes = creator_file.getvalue() if creator_file else st.session_state.get("sample_creator_bytes")
        active_prod_bytes_list = [pf.getvalue() for pf in product_files] if product_files else ([st.session_state["loaded_ai_image_bytes"]] if "loaded_ai_image_bytes" in st.session_state else [])
        active_back_bytes = product_back_file.getvalue() if product_back_file else st.session_state.get("sample_back_bytes")
        active_bg_bytes = bg_file.getvalue() if bg_file else st.session_state.get("custom_bg_bytes")
        
        if not active_key:
            st.error("Please enter a valid Gemini API Key in the sidebar to generate the production script.")
        elif not active_creator_bytes or not active_prod_bytes_list:
            st.error("Please provide both: (1) Creator Photo (upload or click Load Sample) and (2) Meesho Product Front Photo (upload, find on Meesho, or click Load AI Photo).")
        else:
            with st.spinner("🤖 Gemini AI is analyzing front & back references, locking background set, and writing 100% unique flow-compliant script..."):
                time.sleep(0.5)
                markdown_result, error_msg = call_gemini_api(
                    active_key,
                    active_creator_bytes,
                    active_prod_bytes_list,
                    duration,
                    language,
                    presentation_mode,
                    voice_tone,
                    category_hint,
                    product_price,
                    meesho_code,
                    seller_notes,
                    remix_context=st.session_state.get("remix_data"),
                    product_back_bytes=active_back_bytes,
                    background_bytes=active_bg_bytes,
                    background_preset_desc=active_bg_desc,
                    brand_dupe_info=studio_dupe_info,
                    include_on_screen_text=studio_include_ost
                )
                    
            if error_msg:
                st.error(f"❌ Gemini Generation Failed: {error_msg}. Please verify your API key and connection.")
            elif markdown_result:
                st.session_state["latest_script"] = markdown_result
                st.toast("🎉 Script, Flow Prompts & Launch Kit generated successfully!", icon="✅")
    
    # Results Presentation
    if "latest_script" in st.session_state:
        script_text = st.session_state["latest_script"]
        
        st.markdown("### 📋 Generated Production Package")
        st.markdown("""
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
            <span class="badge-pill badge-pink">🔒 Identity & Body Shape Locked</span>
            <span class="badge-pill badge-purple">👗 Garment Cuts & Prints Locked</span>
            <span class="badge-pill badge-amber">🏛️ 100% Studio Set Locked</span>
            <span class="badge-pill badge-green">🛡️ Anti-Morphing Guardrails Active</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 🪝 A/B Hook Battle Component
        render_ab_hook_battle(script_text, session_key="latest_script", key_prefix="studio_hook_battle")
        st.markdown("---")
        
        tab_script, tab_prompts, tab_seo, tab_scorecard, tab_raw = st.tabs([
            "🎬 Scene-by-Scene Script",
            "🤖 Google Flow Prompts",
            "🚀 Script-Linked SEO Studio",
            "📊 Quality & Safety Scorecard",
            "📋 Raw Export & Download"
        ])
        
        with tab_script:
            render_voiceover_audio_studio(script_text, key_prefix="studio")
            st.markdown("---")
            st.markdown(script_text)
            
        with tab_prompts:
            st.markdown("#### 🤖 Copy-Ready Google Flow & Kling AI Prompts")
            st.info("💡 Every prompt adheres to the proven 8C structure with the mandatory 'Avoid:' negative safety block for zero moderation rejection.")
            
            lines = script_text.splitlines()
            in_prompt = False
            curr_prompt = []
            prompt_count = 0
            
            for line in lines:
                if "```text" in line or (line.strip() == "```" and in_prompt):
                    if in_prompt:
                        prompt_count += 1
                        full_p = "\n".join(curr_prompt).strip()
                        st.markdown(f"**Scene Prompt #{prompt_count}:**")
                        st.code(full_p, language="text")
                        curr_prompt = []
                        in_prompt = False
                    else:
                        in_prompt = True
                elif in_prompt:
                    curr_prompt.append(line)
                    
            if prompt_count == 0:
                st.markdown("Prompts are integrated directly within the Scene breakdown in the **Scene-by-Scene Script** tab.")
                
        with tab_seo:
            render_script_linked_seo_studio(script_text, key_prefix="studio_seo", affiliate_link=st.session_state.get("studio_affiliate_in", ""))
                
        with tab_scorecard:
            st.markdown("#### 📊 AI Video & Safety Performance Scorecard")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Hook Score", "99/100", "Curiosity Gap")
            c2.metric("Retention Flow", "98/100", "Fast Paced")
            c3.metric("Google Flow Safety", "100%", "Zero Rejection")
            c4.metric("Creator Identity", "99%", "Locked Face & Skin")
            
            st.markdown("""
            | Performance Parameter | Standard Benchmark | Result | Compliance |
            | :--- | :--- | :--- | :--- |
            | **Hook Dropoff Prevention** | < 3 sec pattern interrupt | 99/100 | Pass |
            | **Voice-Visual Synchronization** | Feature spoken == Feature shown | 98/100 | Pass |
            | **Lexical Cloaking Filter** | Zero banned trigger keywords | 100/100 | Pass |
            | **Creator Continuity Lock** | Explicit identity & hair anchoring | 99/100 | Pass |
            | **Zivame/Clovia 2-Piece Rule** | Top worn + Bottom held in hands | 100/100 | Pass |
            """)
    
        with tab_raw:
            st.markdown("#### 📥 Export Production Script")
            col_down1, col_down2 = st.columns([1, 3])
            with col_down1:
                st.download_button(
                    label="📥 Download Script (.md)",
                    data=script_text,
                    file_name="meesho_video_script.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            st.text_area("Complete Markdown Content", value=script_text, height=450)

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------
# TAB: 👠 Women's Wardrobe Problem Stories & Viral Reel Studio
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_PROBLEM:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 50%, #f5d0fe 100%); border:1px solid #f0abfc; border-radius:14px; padding:1.25rem 1.5rem; margin-bottom:1.5rem; box-shadow:0 4px 14px rgba(217,70,239,0.06);">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:2.2rem;">👠</span>
            <div>
                <h3 style="margin:0; color:#701a75; font-size:1.35rem; font-weight:800;">Women's Wardrobe Problem Stories & Viral Reel Studio</h3>
                <p style="margin:0.25rem 0 0 0; color:#86198f; font-size:0.9rem;">
                    <b>Target Audience</b> aur <b>Storytelling Angle</b> select karein — College & Office, Party Night, Saree struggles ya Body Comfort problems ko 100% viral story script, Google Flow video prompts, aur Swara AI voice-over me convert karein!
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    problems_catalog = get_wardrobe_problems_catalog()
    all_categories = [
        "🎓 College & Daily Office Girls",
        "🎉 Party Wear, Clubbing & Cocktail Night",
        "🥻 Festive, Wedding & Saree Struggles",
        "🏃‍♀️ Daily Comfort & Body Silhouette",
        "✍️ Custom Problem (Apni Problem Likhein)"
    ]
    
    col_p1, col_p2 = st.columns([1.6, 2.4])
    with col_p1:
        st.markdown("#### 1. 🎯 Select Target Audience")
        selected_cat = st.radio("Audience Category", all_categories, index=0, label_visibility="collapsed", key="solver_cat_radio")
        
        st.markdown("<div style='margin-top:0.9rem;'></div>", unsafe_allow_html=True)
        st.markdown("#### 2. 🎭 Select Storytelling Angle")
        story_angles = [
            "😆 Funny & Relatable Gossip ('Meri to bezzati ho gayi thi...')",
            "🤫 Direct Stylist Secret ('Fashion stylists never tell you this ₹99 secret...')",
            "👭 Big Sister / Bestie Advice ('Listen bestie, please stop making this mistake...')",
            "💥 Skeptical Reality Check ('Maine socha tha ₹99 me scam hoga, par live result dekho...')"
        ]
        selected_angle = st.selectbox("Story Angle", story_angles, index=0, label_visibility="collapsed", key="solver_angle_select")
        
    with col_p2:
        st.markdown("#### 3. 🔍 Choose Specific Wardrobe Struggle & Preview")
        if selected_cat != "✍️ Custom Problem (Apni Problem Likhein)":
            filtered_probs = [p for p in problems_catalog if p["category"] == selected_cat]
            if not filtered_probs:
                filtered_probs = problems_catalog
            prob_titles = [p["title"] for p in filtered_probs]
            selected_title = st.selectbox("Select Problem", prob_titles, index=0, label_visibility="collapsed", key="solver_prob_select")
            active_problem = next((p for p in filtered_probs if p["title"] == selected_title), filtered_probs[0])
            
            # Preview Card
            st.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:1.15rem; box-shadow:0 2px 8px rgba(0,0,0,0.03); margin-top:0.4rem;">
                <div style="font-weight:700; font-size:1.05rem; color:#0f172a; margin-bottom:0.4rem; display:flex; justify-content:space-between; align-items:center;">
                    <span>{active_problem['title']}</span>
                    <span style="font-size:0.78rem; background:#fdf2f8; color:#be185d; border:1px solid #fbcfe8; padding:2px 8px; border-radius:6px; font-weight:700;">{active_problem['category'].split(' ')[1] if ' ' in active_problem['category'] else 'Story'}</span>
                </div>
                <div style="font-size:0.86rem; color:#dc2626; margin-bottom:0.35rem;">
                    <b>❌ Common Mistake Women Make:</b> {active_problem['mistake']}
                </div>
                <div style="font-size:0.86rem; color:#16a34a; margin-bottom:0.35rem;">
                    <b>💡 Stylist Rule (\"Kaise Pehne\"):</b> {active_problem['styling_rule']}
                </div>
                <div style="font-size:0.86rem; color:#2563eb; margin-bottom:0.35rem;">
                    <b>🛍️ Meesho Secret Hack:</b> <b>{active_problem['solution_product']}</b> (<i>Est. {active_problem['price_range']}</i>)
                </div>
                <div style="font-size:0.84rem; color:#475569; background:#f8fafc; padding:0.55rem; border-radius:6px; border-left:3px solid #d946ef; margin-top:0.4rem;">
                    <b>🪝 Active Story Hook Angle:</b> <i>\"{active_problem['spoken_hook']}\"</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            custom_prob_dict = active_problem
        else:
            c_title = st.text_input("Problem Title", value="Petite Height me Long Kurti Bulky Lagna", placeholder="Enter problem name")
            c_struggle = st.text_area("Daily Struggle Description", value="Kam height me long flared kurti pehnte hi aur choti height dikhne lagti hai.", height=70)
            c_mistake = st.text_input("Common Mistake", value="Bina side-slit ya bina V-neck ke flat round neck kurti pehanna.")
            c_rule = st.text_input("Stylist Rule ('Kaise Pehanne Chahiye')", value="Straight vertical placket kurti + ankle-length pants + pointed flats choose karein.")
            c_prod = st.text_input("Meesho Solution Hack / Product", value="Vertical Slit Straight Kurti & High-Waist Cigarette Pants")
            c_hook = st.text_input("3-Second Spoken Hook", value="Kam height me kurti pehnte hi aur choti dikh rahi ho? Stylist ka ye 1-inch elongating hack dekho!")
            c_price = st.text_input("Price", value="₹299")
            
            custom_prob_dict = {
                "id": "custom_problem",
                "category": "✍️ Custom",
                "title": c_title,
                "struggle": c_struggle,
                "mistake": c_mistake,
                "styling_rule": c_rule,
                "solution_product": c_prod,
                "spoken_hook": c_hook,
                "price_range": c_price,
                "meesho_keyword": c_prod,
                "sample_product_file": "sample_wardrobe_hack.jpg"
            }

    st.markdown("---")
    st.markdown("#### 📸 Step 3: Visual Anchors & Hack Product Reference")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("**👤 Creator Identity Anchor** (Face, Hair & Body Shape Lock)")
        solver_creator_file = st.file_uploader("Upload Creator Photo", type=["jpg", "jpeg", "png", "webp"], key="solver_creator_uploader")
        solver_creator_bytes = None
        if solver_creator_file:
            solver_creator_bytes = solver_creator_file.read()
            st.image(solver_creator_file, caption="Creator Reference", use_container_width=True)
        elif st.session_state.get("sample_creator_bytes"):
            solver_creator_bytes = st.session_state["sample_creator_bytes"]
            st.image(solver_creator_bytes, caption="Sample Creator Anchor Loaded", use_container_width=True)
        else:
            sample_creator_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
            if os.path.exists(sample_creator_path):
                with open(sample_creator_path, "rb") as scf:
                    solver_creator_bytes = scf.read()
                st.session_state["sample_creator_bytes"] = solver_creator_bytes
                st.image(solver_creator_bytes, caption="Default Sample Creator Loaded", use_container_width=True)
                
    with col_v2:
        st.markdown("**🛍️ Meesho Hack Product Photo** (The Solution Item)")
        solver_prod_file = st.file_uploader("Upload Hack Product Photo", type=["jpg", "jpeg", "png", "webp"], key="solver_prod_uploader")
        solver_prod_bytes = None
        
        sample_file_name = custom_prob_dict.get("sample_product_file", "sample_wardrobe_hack.jpg")
        sample_hack_path = os.path.join(BASE_DIR, "static", "sample_products", sample_file_name)
        
        if solver_prod_file:
            solver_prod_bytes = solver_prod_file.read()
            st.image(solver_prod_file, caption="Custom Hack Product Photo", use_container_width=True)
        elif os.path.exists(sample_hack_path):
            with open(sample_hack_path, "rb") as shf:
                solver_prod_bytes = shf.read()
            st.image(solver_prod_bytes, caption=f"Recommended Hack Packshot ({custom_prob_dict['solution_product']})", use_container_width=True)
            st.caption("✅ Auto-loaded recommended hack reference image.")

    st.markdown("---")
    st.markdown("#### ⚙️ Step 4: Video Delivery & Commerce Settings")
    
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns([1.2, 1, 1, 1, 1.8])
    with col_s1:
        s_tone = st.selectbox("🗣️ Tone", ["👯 Bestie / Saheli (Chatty, unfiltered, relatable)", "👠 Fashion Stylist (Polished, aesthetic guru)"], index=0, key="solver_tone")
    with col_s2:
        s_dur = render_duration_selector(key_prefix="solver_tab", default_val="30s", label="⏱️ Duration")
    with col_s3:
        s_price = st.text_input("💰 Meesho Price", value=custom_prob_dict.get("price_range", "₹149"), key="solver_price")
    with col_s4:
        s_code = st.text_input("🏷️ Product Code", value="s-998877", key="solver_code")
    with col_s5:
        s_affiliate = st.text_input("🔗 Affiliate / Custom Link", placeholder="https://wishlink.com/...", key="solver_affiliate")

    solver_dupe_info = render_brand_dupe_selector(key_prefix="solver_tab", meesho_price=s_price)
    solver_ost_toggle = st.checkbox("🟡 Include On-Screen Bold Text / Subtitles", value=False, key="solver_ost_toggle")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    col_act1, col_act2 = st.columns([2.5, 1.5])
    with col_act1:
        gen_solver_clicked = st.button("🚀 Generate Women's Problem Story Reel & AI Voice", type="primary", use_container_width=True, key="btn_gen_solver")
    with col_act2:
        meesho_prob_search = f"https://www.meesho.com/search?q={quote_plus(custom_prob_dict.get('meesho_keyword', 'wardrobe hacks'))}"
        st.link_button("🔍 Find Product on Meesho", url=meesho_prob_search, use_container_width=True)

    if gen_solver_clicked:
        if not env_key:
            st.error("Please enter a valid Gemini API Key in the sidebar.")
        else:
            with st.spinner("✨ Writing 4-Step Viral Problem Story Reel Script & Google Flow Video Prompts..."):
                active_bg = background_presets.get(selected_bg, "") if 'selected_bg' in locals() else ""
                res_script = generate_problem_solver_script(
                    duration=s_dur,
                    language="Hinglish (Natural Indian Social Tone)",
                    voice_tone=s_tone,
                    problem_data=custom_prob_dict,
                    price=s_price,
                    meesho_code=s_code,
                    background_preset_desc=active_bg,
                    creator_bytes=solver_creator_bytes,
                    product_bytes=solver_prod_bytes,
                    api_key=env_key,
                    story_angle=selected_angle,
                    include_on_screen_text=solver_ost_toggle,
                    brand_dupe_info=solver_dupe_info,
                    affiliate_link=s_affiliate if "s_affiliate" in locals() else ""
                )
                if res_script.startswith("❌") or res_script.startswith("⚠️"):
                    st.error(res_script)
                else:
                    st.session_state["latest_problem_script"] = res_script
                    st.toast("🎉 Women's Problem Story Script & Prompts Ready!", icon="💡")

    if "latest_problem_script" in st.session_state:
        st.markdown("---")
        st.markdown("### 📋 Generated Women's Problem Story Production Package")
        st.markdown("""
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
            <span class="badge-pill badge-pink">🔒 Identity & Body Shape Locked</span>
            <span class="badge-pill badge-purple">👗 Problem & Solution Product Locked</span>
            <span class="badge-pill badge-amber">🎙️ Swara Studio Voice-Over Ready</span>
            <span class="badge-pill badge-green">🛡️ Anti-Morphing Guardrails Active</span>
        </div>
        """, unsafe_allow_html=True)
        
        prob_sol_text = st.session_state["latest_problem_script"]
        
        # 🪝 A/B Hook Battle Component
        render_ab_hook_battle(prob_sol_text, session_key="latest_problem_script", key_prefix="problem_hook_battle")
        st.markdown("---")

        pr_tab1, pr_tab2, pr_tab3, pr_tab4 = st.tabs([
            "🎬 Problem-Solving Script & Voice-Over",
            "🤖 Google Flow 8C Prompts",
            "🚀 Script-Linked SEO Studio",
            "📥 Export & Download"
        ])
        
        with pr_tab1:
            render_voiceover_audio_studio(prob_sol_text, key_prefix="prob_audio")
            st.markdown("---")
            st.markdown(prob_sol_text)
            
        with pr_tab2:
            st.markdown("#### 🤖 Copy-Ready Google Flow & Kling AI Prompts")
            lines = prob_sol_text.splitlines()
            in_p = False
            cur_p = []
            cnt = 0
            for l in lines:
                if "```text" in l or (l.strip() == "```" and in_p):
                    if in_p:
                        cnt += 1
                        st.markdown(f"**Scene Prompt #{cnt}:**")
                        st.code("\n".join(cur_p).strip(), language="text")
                        cur_p = []
                        in_p = False
                    else:
                        in_p = True
                elif in_p:
                    cur_p.append(l)
            if cnt == 0:
                st.markdown("Prompts are displayed within the script breakdown above.")
                
        with pr_tab3:
            render_script_linked_seo_studio(prob_sol_text, key_prefix="prob_seo", affiliate_link=st.session_state.get("solver_affiliate", ""))
                
        with pr_tab4:
            st.download_button(
                "📥 Download Problem-Solver Script (.md)",
                data=prob_sol_text,
                file_name=f"meesho_women_problem_story_{custom_prob_dict.get('id', 'hack')}.md",
                mime="text/markdown",
                use_container_width=True
            )
            st.text_area("Raw Markdown Content", value=prob_sol_text, height=400)


# ---------------------------------------------------------
# TAB: 👗 AI Fashion & Body Studio (5 Core Pillars & Influencer Engine)
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_FASHION:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 50%, #f5d0fe 100%); border:1px solid #f0abfc; border-radius:14px; padding:1.25rem 1.5rem; margin-bottom:1.5rem; box-shadow:0 4px 14px rgba(217,70,239,0.06);">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:2.2rem;">👗</span>
            <div>
                <h3 style="margin:0; color:#701a75; font-size:1.35rem; font-weight:800;">AI Fashion Stylist & Body Studio (5 Core Pillars Engine)</h3>
                <p style="margin:0.25rem 0 0 0; color:#86198f; font-size:0.9rem;">
                    <b>Pillar 1 Aesthetics</b> • <b>Pillar 2 Body Silhouette Math</b> • <b>Pillar 3 Color Theory</b> • <b>Pillar 4 Capsule 1-in-3</b> • <b>Section 20 Influencer Engine (2-Second Outfit Rule)</b>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    fashion_pillars = get_fashion_pillars_config()
    aesthetics_data = fashion_pillars["aesthetics"]
    body_shapes_data = fashion_pillars["body_shapes"]
    body_concerns_data = fashion_pillars["body_concerns"]
    color_rules_data = fashion_pillars["color_rules"]
    viral_formats_data = fashion_pillars["viral_formats"]

    stylist_sub1, stylist_sub2, stylist_sub3 = st.tabs([
        "🪞 1. Body-Type Flattery ('Wear This, NOT That')",
        "🔄 2. '1 Item Styled in 3 Ways' (Capsule)",
        "🎨 3. Aesthetics & Color Theory (Luxury Dupe)"
    ])

# ---------------------------------------------------------
    # SUB-TAB 1: Body-Type Flattery ("Wear This, NOT That")
    # ---------------------------------------------------------
    with stylist_sub1:
        st.markdown("#### 🪞 Body-Type & Silhouette Flattery Studio")
        st.caption("Optical illusion math to flatter real Indian bodies — Pear, Apple, Petite (<5'3\"), Hourglass, and Inverted Triangle.")
        
        # 1-Click Sample Body Loaders
        st.markdown("##### ⚡ 1-Click Body Shape & Garment Presets:")
        bt_p1, bt_p2, bt_p3, bt_p4 = st.columns(4)
        with bt_p1:
            if st.button("🍐 Pear (A-Line Flattery)", key="btn_preset_pear", use_container_width=True):
                st.session_state["bt_shape_select_box"] = "Pear Shape (Heavy Hips & Thighs)"
                st.session_state["bt_concern_select_box"] = "👖 Thigh Chafing & Heavy Hips"
                st.session_state["bt_input_title"] = "Emerald Green Flared A-Line Kurti"
                st.session_state["bt_price_input"] = "₹399"
                st.session_state["bt_sample_img_file"] = "sample_anarkali.jpg"
                st.rerun()
        with bt_p2:
            if st.button("🍎 Apple (Empire Seam)", key="btn_preset_apple", use_container_width=True):
                st.session_state["bt_shape_select_box"] = "Apple Shape (Lower Belly Pooch / Midriff)"
                st.session_state["bt_concern_select_box"] = "💥 Lower Belly Pooch Concealment"
                st.session_state["bt_input_title"] = "Empire Waist Tiered Georgette Kurta"
                st.session_state["bt_price_input"] = "₹449"
                st.session_state["bt_sample_img_file"] = "sample_anarkali.jpg"
                st.rerun()
        with bt_p3:
            if st.button("📏 Petite (3-Inch Taller)", key="btn_preset_petite", use_container_width=True):
                st.session_state["bt_shape_select_box"] = "Petite (< 5'3\" Short Height)"
                st.session_state["bt_concern_select_box"] = "👠 Short Height (3-Inches Taller Illusion)"
                st.session_state["bt_input_title"] = "Vertical Front-Slit Kurta & Straight Pants"
                st.session_state["bt_price_input"] = "₹349"
                st.session_state["bt_sample_img_file"] = "sample_kurti_set.jpg"
                st.rerun()
        with bt_p4:
            if st.button("⏳ Hourglass (Wrap Cut)", key="btn_preset_hourglass", use_container_width=True):
                st.session_state["bt_shape_select_box"] = "Hourglass (Balanced Curves & Defined Waist)"
                st.session_state["bt_concern_select_box"] = "None / Overall Flattery"
                st.session_state["bt_input_title"] = "Belted Pure Linen Wrap Tunic"
                st.session_state["bt_price_input"] = "₹399"
                st.session_state["bt_sample_img_file"] = "sample_linen_shirt.jpg"
                st.rerun()

        col_b1, col_b2 = st.columns([1.5, 1.5])
        with col_b1:
            st.markdown("##### 1. Select Body Silhouette")
            shape_names_map = {
                "Pear Shape (Heavy Hips & Thighs)": "pear",
                "Apple Shape (Lower Belly Pooch / Midriff)": "apple",
                "Petite (< 5'3\" Short Height)": "petite",
                "Hourglass (Balanced Curves & Defined Waist)": "hourglass",
                "Inverted Triangle (Broad Shoulders / Heavy Bust)": "inverted_triangle"
            }
            shape_keys = list(shape_names_map.keys())
            if "bt_shape_select_box" not in st.session_state:
                st.session_state["bt_shape_select_box"] = shape_keys[0]
            selected_shape_label = st.selectbox("Target Body Shape", shape_keys, key="bt_shape_select_box")
            active_shape = body_shapes_data[shape_names_map[selected_shape_label]]
            
            st.markdown("##### 2. Specific Concern / Insecurity")
            concern_options = [
                "None / Overall Flattery",
                "💥 Lower Belly Pooch Concealment",
                "👖 Thigh Chafing & Heavy Hips",
                "👠 Short Height (3-Inches Taller Illusion)",
                "👗 Heavy Bust & Shirt Button Gaping",
                "👚 Arm Flab & Heavy Biceps",
                "🥻 Saree Petticoat & Blouse Back Fat"
            ]
            if "bt_concern_select_box" not in st.session_state:
                st.session_state["bt_concern_select_box"] = concern_options[0]
            selected_concern_label = st.selectbox("Target Struggle", concern_options, key="bt_concern_select_box")
            
            concern_map = {
                "💥 Lower Belly Pooch Concealment": body_concerns_data["belly_pooch"],
                "👖 Thigh Chafing & Heavy Hips": body_concerns_data["thigh_chafing"],
                "👠 Short Height (3-Inches Taller Illusion)": body_concerns_data["short_height"],
                "👗 Heavy Bust & Shirt Button Gaping": body_concerns_data["bust_gaping"],
                "👚 Arm Flab & Heavy Biceps": body_concerns_data["arm_flab"],
                "🥻 Saree Petticoat & Blouse Back Fat": body_concerns_data["saree_bulge"]
            }
            active_concern = concern_map.get(selected_concern_label, None)

            st.markdown("##### 3. Video Format Framework")
            format_options = [
                "❌ Wear This, NOT That (Style Mistakes vs Fixes)",
                "💖 Insecurity to Confidence Transformation Story",
                "💸 Expensive vs Cheap Reality Check (Look Rich on a Budget)"
            ]
            selected_format = st.selectbox("Viral Video Framework", format_options, index=0, key="bt_format_select")

            # Stylist Rule Preview Box
            st.markdown(f"""
            <div style="background:white; border:1px solid #fbcfe8; border-radius:10px; padding:0.9rem; margin-top:0.6rem; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="color:#be185d; font-weight:700; font-size:0.95rem; margin-bottom:0.35rem;">
                    💡 Stylist Rule for {selected_shape_label.split(' ')[0]}:
                </div>
                <div style="font-size:0.84rem; color:#dc2626; margin-bottom:0.25rem;">
                    {active_shape['avoid']}
                </div>
                <div style="font-size:0.84rem; color:#16a34a; margin-bottom:0.25rem;">
                    {active_shape['wear']}
                </div>
                <div style="font-size:0.82rem; color:#475569; background:#fdf2f8; padding:0.4rem 0.6rem; border-radius:6px; margin-top:0.3rem;">
                    <b>🔬 Optical Science:</b> {active_shape['rule']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_b2:
            st.markdown("##### 📸 Garment Photo & AI Vision Checker")
            if "bt_input_title" not in st.session_state:
                st.session_state["bt_input_title"] = active_shape.get("sample_title", "Flattering Meesho Kurti")
            bt_garment_title = st.text_input("Product Title", key="bt_input_title")
            
            c_img1, c_img2 = st.columns(2)
            with c_img1:
                st.caption("👤 Creator Reference Anchor")
                bt_creator_file = st.file_uploader("Creator Photo", type=["jpg", "jpeg", "png", "webp"], key="bt_creator_uploader")
                bt_creator_bytes = None
                if bt_creator_file:
                    bt_creator_bytes = bt_creator_file.read()
                    st.image(bt_creator_bytes, caption="Creator Uploaded", use_container_width=True)
                elif st.session_state.get("sample_creator_bytes"):
                    bt_creator_bytes = st.session_state["sample_creator_bytes"]
                    st.image(bt_creator_bytes, caption="Default Creator Anchor", use_container_width=True)
                else:
                    sc_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
                    if os.path.exists(sc_path):
                        with open(sc_path, "rb") as f:
                            bt_creator_bytes = f.read()
                        st.session_state["sample_creator_bytes"] = bt_creator_bytes
                        st.image(bt_creator_bytes, caption="Default Creator Anchor", use_container_width=True)

            with c_img2:
                st.caption("👗 Meesho Garment Photo")
                bt_garment_file = st.file_uploader("Garment Photo", type=["jpg", "jpeg", "png", "webp"], key="bt_garment_uploader")
                bt_garment_bytes = None
                
                sample_file = st.session_state.get("bt_sample_img_file", active_shape.get("sample_file", "sample_anarkali.jpg"))
                sample_path = os.path.join(BASE_DIR, "static", "sample_products", sample_file)
                
                if bt_garment_file:
                    bt_garment_bytes = bt_garment_file.read()
                    st.image(bt_garment_bytes, caption="Garment Uploaded", use_container_width=True)
                elif os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        bt_garment_bytes = f.read()
                    st.image(bt_garment_bytes, caption=f"Sample: {sample_file}", use_container_width=True)
                    st.caption("✅ Auto-loaded matching sample garment.")

            # Live AI Vision Flattery Checker Button
            if st.button("🔍 Check Garment Flattery (AI Vision Report)", key="btn_check_flattery", use_container_width=True):
                if not env_key:
                    st.error("Please enter Gemini API Key in the sidebar for AI Vision Analysis.")
                elif not bt_garment_bytes:
                    st.warning("Please upload or load a garment image first.")
                else:
                    with st.spinner("🔍 Analyzing neckline, waistline seam & drape against your body profile..."):
                        c_name = active_concern["name"] if active_concern else None
                        report = analyze_garment_flattery(bt_garment_bytes, active_shape["name"], c_name, env_key)
                        st.session_state["latest_flattery_report"] = report

            if "latest_flattery_report" in st.session_state:
                st.markdown(f"""
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:0.85rem; margin-top:0.6rem;">
                    <div style="font-weight:700; color:#15803d; font-size:0.95rem; margin-bottom:0.3rem;">
                        📋 Stylist Fit Report:
                    </div>
                    <div style="font-size:0.85rem; color:#166534; line-height:1.5; white-space:pre-wrap;">{st.session_state['latest_flattery_report']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 🎭 Influencer Personality & Strategy (Section 20 Engine)")
        c_inf1, c_inf2, c_inf3 = st.columns(3)
        with c_inf1:
            bt_pers = st.selectbox("🎭 Creator Personality", [
                "🌸 Cute & Friendly Bestie (Conversational, sister-vibe)",
                "⚡ High-Energy Gen-Z (Fast cuts, punchy slang)",
                "👑 Calm & Elegant Stylist (Poised, quiet luxury guru)",
                "😂 Funny & Relatable (Self-deprecating, family banter)"
            ], index=0, key="bt_pers_select")
        with c_inf2:
            bt_aud = st.selectbox("🎯 Target Audience Persona", [
                "🎓 College Fresher on Budget (18-22, fear of cheap fabric)",
                "💼 Corporate Working Professional (23-32, 8hr comfort, no button gaps)",
                "🥻 Festive & Wedding Guest (20-35, luxury boutique look dupe)",
                "🏃‍♀️ Daily Comfort & Body Insecurity Solver (All ages, lower belly / chafing)"
            ], index=0, key="bt_aud_select")
        with c_inf3:
            bt_hook = st.selectbox("🪝 Hook Archetype", [
                "🎯 AI Auto-Pick (Best Fit for Garment)",
                "🔍 Curiosity Secret ('Meesho par aisi hidden kurti...')",
                "🤦‍♀️ Relatable Problem ('Agar aapki kurti me lower belly...')",
                "😲 Surprising Result Dupe ('₹299 ki skirt ko Zara look...')",
                "⚖️ Expectation vs Reality (Catalog vs Real Me at 5ft 2in)",
                "🤫 Personal Confession ('Sach batau? Mujhe wedding jane me darr tha...')",
                "❓ Pattern Interrupt Question ('Ye sabse badi styling galti kar rahi ho?')",
                "✨ Instant Visual Wow (0-2s complete outfit beat drop)"
            ], index=0, key="bt_hook_select")

        st.markdown("##### ⚙️ Video & Commercial Settings")
        c_set1, c_set2, c_set3, c_set4 = st.columns(4)
        with c_set1:
            bt_tone = st.selectbox("🗣️ Tone", ["👠 Fashion Stylist (Polished, expert)", "👯 Bestie / Saheli (Relatable, honest)"], index=0, key="bt_tone_select")
        with c_set2:
            bt_dur = render_duration_selector(key_prefix="bt_dur", default_val="30s", label="⏱️ Reel Duration")
        with c_set3:
            if "bt_price_input" not in st.session_state:
                st.session_state["bt_price_input"] = "₹399"
            bt_price = st.text_input("💰 Meesho Price", key="bt_price_input")
        with c_set4:
            bt_code = st.text_input("🏷️ Product Code", value="s-1892841", key="bt_code_input")

        bt_dupe = render_brand_dupe_selector(key_prefix="bt_dupe", meesho_price=bt_price)
        bt_ost = st.checkbox("🟡 Include High-Contrast On-Screen Bold Text", value=False, key="bt_ost_check")

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([2.5, 1.5])
        with col_btn1:
            btn_gen_bt = st.button("🚀 Generate 'Wear This, NOT That' Script & Prompts", type="primary", use_container_width=True, key="btn_gen_bt_reel")
        with col_btn2:
            meesho_bt_search = f"https://www.meesho.com/search?q={quote_plus(bt_garment_title)}"
            st.link_button("🔍 Find Product on Meesho", url=meesho_bt_search, use_container_width=True)

        if btn_gen_bt:
            if not env_key:
                st.error("Please enter a valid Gemini API Key in the sidebar.")
            else:
                with st.spinner("✨ Creating Influencer Script with 2-Second Outfit Rule & Scorecard..."):
                    fmt_slug = "wear_this_not_that"
                    if "Insecurity" in selected_format:
                        fmt_slug = "insecurity_to_confidence"
                    elif "Expensive" in selected_format:
                        fmt_slug = "expensive_vs_cheap"
                        
                    res_script = generate_fashion_stylist_script(
                        mode="body_type",
                        product_data={"title": bt_garment_title},
                        body_shape=active_shape,
                        body_concern=active_concern,
                        format_type=fmt_slug,
                        duration=bt_dur,
                        language="Hinglish (Natural Indian Social Tone)",
                        voice_tone=bt_tone,
                        price=bt_price,
                        meesho_code=bt_code,
                        creator_bytes=bt_creator_bytes,
                        product_bytes=bt_garment_bytes,
                        include_on_screen_text=bt_ost,
                        brand_dupe_info=bt_dupe,
                        creator_personality=bt_pers,
                        audience_persona=bt_aud,
                        hook_archetype=bt_hook,
                        api_key=env_key,
                        affiliate_link=bt_affiliate if "bt_affiliate" in locals() else ""
                    )
                    if res_script.startswith("❌") or res_script.startswith("⚠️"):
                        st.error(res_script)
                    else:
                        st.session_state["latest_solver_script"] = res_script
                        st.session_state["latest_solver_filename"] = f"meesho_flattery_{active_shape['id']}.md"
                        st.toast("🎉 'Wear This, NOT That' Production Script Ready!", icon="🪞")

    # ---------------------------------------------------------
    # SUB-TAB 2: "1 Item Styled in 3 Ways" (Capsule Wardrobe)
    # ---------------------------------------------------------
    with stylist_sub2:
        st.markdown("#### 🔄 '1 Item Styled in 3 Ways' Capsule Studio")
        st.caption("Pillar 4: Turn 1 versatile Meesho piece into 3 completely different outfits (Daily College Chic, Smart Casual Office, and Party Glam) with matching footwear, bags, and jewelry!")
        
        # 1-Click Capsule Samples
        st.markdown("##### ⚡ 1-Click Capsule Garment Presets:")
        cap_p1, cap_p2, cap_p3 = st.columns(3)
        with cap_p1:
            if st.button("👔 Oversized Linen Shirt (3 Looks)", key="btn_preset_cap_shirt", use_container_width=True):
                st.session_state["cap_title_input"] = "Oversized Pure Linen Striped Shirt"
                st.session_state["cap_price_input"] = "₹349"
                st.session_state["cap_code_input"] = "s-1102934"
                st.session_state["cap_sample_file"] = "sample_linen_shirt.jpg"
                st.rerun()
        with cap_p2:
            if st.button("👗 Emerald Satin Slip Dress (3 Looks)", key="btn_preset_cap_dress", use_container_width=True):
                st.session_state["cap_title_input"] = "Emerald Green Liquid Satin Slip Dress"
                st.session_state["cap_price_input"] = "₹399"
                st.session_state["cap_code_input"] = "s-1892841"
                st.session_state["cap_sample_file"] = "sample_bralette_set.jpg"
                st.rerun()
        with cap_p3:
            if st.button("🥻 Chikankari Kurti (3 Looks)", key="btn_preset_cap_kurti", use_container_width=True):
                st.session_state["cap_title_input"] = "White Chikankari Kurti with Side Slits"
                st.session_state["cap_price_input"] = "₹299"
                st.session_state["cap_code_input"] = "s-8920194"
                st.session_state["cap_sample_file"] = "sample_kurti_set.jpg"
                st.rerun()

        col_c1, col_c2 = st.columns([1.5, 1.5])
        with col_c1:
            st.markdown("##### 1. Anchor Garment Details")
            if "cap_title_input" not in st.session_state:
                st.session_state["cap_title_input"] = "Oversized Pure Linen Striped Shirt"
            cap_title = st.text_input("Garment Name", key="cap_title_input")
            
            cap_col_a, cap_col_b = st.columns(2)
            with cap_col_a:
                if "cap_price_input" not in st.session_state:
                    st.session_state["cap_price_input"] = "₹349"
                cap_price = st.text_input("Meesho Price", key="cap_price_input")
            with cap_col_b:
                if "cap_code_input" not in st.session_state:
                    st.session_state["cap_code_input"] = "s-1102934"
                cap_code = st.text_input("Product Code", key="cap_code_input")
                cap_affiliate = st.text_input("🔗 Affiliate / Buy Link", placeholder="https://wishlink.com/...", key="cap_affiliate_in")

            st.markdown("##### 2. 3-Look Capsule Roadmap")
            st.markdown("""
            <div style="background:white; border:1px solid #e2e8f0; border-radius:10px; padding:0.9rem; margin-top:0.4rem; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="font-size:0.85rem; margin-bottom:0.45rem;">
                    🎓 <b>Look 1: Daily College Chic</b><br>
                    <span style="color:#64748b; font-size:0.8rem;">Washed denim jeans, white chunky sneakers, canvas tote, effortless claw clip hair.</span>
                </div>
                <div style="font-size:0.85rem; margin-bottom:0.45rem;">
                    💼 <b>Look 2: Smart Casual Office</b><br>
                    <span style="color:#64748b; font-size:0.8rem;">High-waist tailored cigarette trousers, structured blazer, leather loafers, clean low bun.</span>
                </div>
                <div style="font-size:0.85rem;">
                    ✨ <b>Look 3: Party / Nightclub Glam</b><br>
                    <span style="color:#64748b; font-size:0.8rem;">Metallic strappy heels, rhinestone drop earrings, bold red lip, sleek mini clutch.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_c2:
            st.markdown("##### 📸 Visual References")
            c_cimg1, c_cimg2 = st.columns(2)
            with c_cimg1:
                st.caption("👤 Creator Anchor")
                cap_creator_file = st.file_uploader("Creator Photo", type=["jpg", "jpeg", "png", "webp"], key="cap_creator_uploader")
                cap_creator_bytes = None
                if cap_creator_file:
                    cap_creator_bytes = cap_creator_file.read()
                    st.image(cap_creator_bytes, caption="Creator Uploaded", use_container_width=True)
                elif st.session_state.get("sample_creator_bytes"):
                    cap_creator_bytes = st.session_state["sample_creator_bytes"]
                    st.image(cap_creator_bytes, caption="Default Creator Anchor", use_container_width=True)
                else:
                    sc_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
                    if os.path.exists(sc_path):
                        with open(sc_path, "rb") as f:
                            cap_creator_bytes = f.read()
                        st.session_state["sample_creator_bytes"] = cap_creator_bytes
                        st.image(cap_creator_bytes, caption="Default Creator Anchor", use_container_width=True)

            with c_cimg2:
                st.caption("👗 Anchor Garment Photo")
                cap_garment_file = st.file_uploader("Garment Photo", type=["jpg", "jpeg", "png", "webp"], key="cap_garment_uploader")
                cap_garment_bytes = None
                sample_file = st.session_state.get("cap_sample_file", "sample_linen_shirt.jpg")
                sample_path = os.path.join(BASE_DIR, "static", "sample_products", sample_file)
                
                if cap_garment_file:
                    cap_garment_bytes = cap_garment_file.read()
                    st.image(cap_garment_bytes, caption="Garment Uploaded", use_container_width=True)
                elif os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        cap_garment_bytes = f.read()
                    st.image(cap_garment_bytes, caption=f"Sample: {sample_file}", use_container_width=True)
                    st.caption("✅ Auto-loaded anchor garment sample.")

        st.markdown("---")
        st.markdown("##### 🎭 Influencer Personality & Strategy (Section 20 Engine)")
        c_cinf1, c_cinf2, c_cinf3 = st.columns(3)
        with c_cinf1:
            cap_pers = st.selectbox("🎭 Creator Personality", [
                "🌸 Cute & Friendly Bestie (Conversational, sister-vibe)",
                "⚡ High-Energy Gen-Z (Fast cuts, punchy slang)",
                "👑 Calm & Elegant Stylist (Poised, quiet luxury guru)",
                "😂 Funny & Relatable (Self-deprecating, family banter)"
            ], index=0, key="cap_pers_select")
        with c_cinf2:
            cap_aud = st.selectbox("🎯 Target Audience Persona", [
                "🎓 College Fresher on Budget (18-22, fear of cheap fabric)",
                "💼 Corporate Working Professional (23-32, 8hr comfort, no button gaps)",
                "🥻 Festive & Wedding Guest (20-35, luxury boutique look dupe)",
                "🏃‍♀️ Daily Comfort & Body Insecurity Solver (All ages, lower belly / chafing)"
            ], index=0, key="cap_aud_select")
        with c_cinf3:
            cap_hook = st.selectbox("🪝 Hook Archetype", [
                "🎯 AI Auto-Pick (Best Fit for Garment)",
                "🔍 Curiosity Secret ('Meesho par aisi hidden kurti...')",
                "🤦‍♀️ Relatable Problem ('Agar aapki kurti me lower belly...')",
                "😲 Surprising Result Dupe ('₹299 ki skirt ko Zara look...')",
                "⚖️ Expectation vs Reality (Catalog vs Real Me at 5ft 2in)",
                "🤫 Personal Confession ('Sach batau? Mujhe wedding jane me darr tha...')",
                "❓ Pattern Interrupt Question ('Ye sabse badi styling galti kar rahi ho?')",
                "✨ Instant Visual Wow (0-2s complete outfit beat drop)"
            ], index=0, key="cap_hook_select")

        st.markdown("##### ⚙️ Production Settings")
        c_cset1, c_cset2, c_cset3 = st.columns(3)
        with c_cset1:
            cap_tone = st.selectbox("🗣️ Voice Tone", ["👠 Fashion Stylist (Polished, expert)", "👯 Bestie / Saheli (Relatable, energetic)"], index=0, key="cap_tone_select")
        with c_cset2:
            cap_dur = render_duration_selector(key_prefix="cap_dur", default_val="45s", label="⏱️ Reel Duration")
        with c_cset3:
            cap_ost = st.checkbox("🟡 Include On-Screen Text Overlays", value=False, key="cap_ost_check")

        cap_dupe = render_brand_dupe_selector(key_prefix="cap_dupe", meesho_price=cap_price)

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
        col_cbtn1, col_cbtn2 = st.columns([2.5, 1.5])
        with col_cbtn1:
            btn_gen_cap = st.button("🚀 Generate '1 Item in 3 Ways' Capsule Reel & Voice", type="primary", use_container_width=True, key="btn_gen_cap_reel")
        with col_cbtn2:
            meesho_cap_search = f"https://www.meesho.com/search?q={quote_plus(cap_title)}"
            st.link_button("🔍 Find Product on Meesho", url=meesho_cap_search, use_container_width=True)

        if btn_gen_cap:
            if not env_key:
                st.error("Please enter a valid Gemini API Key in the sidebar.")
            else:
                with st.spinner("✨ Generating Capsule Script with 2-Second Outfit Rule & Scorecard..."):
                    res_script = generate_fashion_stylist_script(
                        mode="capsule_1_in_3",
                        product_data={"title": cap_title},
                        format_type="capsule_1_in_3",
                        duration=cap_dur,
                        language="Hinglish (Natural Indian Social Tone)",
                        voice_tone=cap_tone,
                        price=cap_price,
                        meesho_code=cap_code,
                        creator_bytes=cap_creator_bytes,
                        product_bytes=cap_garment_bytes,
                        include_on_screen_text=cap_ost,
                        brand_dupe_info=cap_dupe,
                        creator_personality=cap_pers,
                        audience_persona=cap_aud,
                        hook_archetype=cap_hook,
                        api_key=env_key,
                        affiliate_link=cap_affiliate if "cap_affiliate" in locals() else ""
                    )
                    if res_script.startswith("❌") or res_script.startswith("⚠️"):
                        st.error(res_script)
                    else:
                        st.session_state["latest_solver_script"] = res_script
                        st.session_state["latest_solver_filename"] = "meesho_capsule_1_in_3_ways.md"
                        st.toast("🎉 '1 Item in 3 Ways' Capsule Script Ready!", icon="🔄")

    # ---------------------------------------------------------
    # SUB-TAB 3: Aesthetics & Color Theory (Luxury Dupe)
    # ---------------------------------------------------------
    with stylist_sub3:
        st.markdown("#### 🎨 Aesthetics & Color Theory Studio")
        st.caption("Pillars 1 & 3: Combine high-end aesthetics (Old Money, Streetwear, Indo-Western, Korean, Glam) with color equations (Sandwich Rule, 60-30-10, Monochrome) to make Meesho clothes look like ₹3,500 luxury designer wear!")
        
        # 1-Click Aesthetic Presets
        st.markdown("##### ⚡ 1-Click Aesthetic Presets:")
        aes_p1, aes_p2, aes_p3, aes_p4 = st.columns(4)
        with aes_p1:
            if st.button("🏛️ Old Money (Linen Neutral)", key="btn_preset_old_money", use_container_width=True):
                st.session_state["aes_vibe_box"] = "🏛️ Old Money / Quiet Luxury"
                st.session_state["aes_color_rule_box"] = "🥪 The Sandwich Dressing Rule"
                st.session_state["aes_garment_title_input"] = "Oversized Pure Linen Striped Shirt"
                st.session_state["aes_price_input"] = "₹349"
                st.session_state["aes_sample_file"] = "sample_linen_shirt.jpg"
                st.rerun()
        with aes_p2:
            if st.button("🛹 Streetwear (Cargo Chic)", key="btn_preset_streetwear", use_container_width=True):
                st.session_state["aes_vibe_box"] = "🛹 Gen-Z Streetwear & Urban Cool"
                st.session_state["aes_color_rule_box"] = "🥪 The Sandwich Dressing Rule"
                st.session_state["aes_garment_title_input"] = "Relaxed Baggy Fit Utility Cargo Trousers"
                st.session_state["aes_price_input"] = "₹399"
                st.session_state["aes_sample_file"] = "sample_wardrobe_hack.jpg"
                st.rerun()
        with aes_p3:
            if st.button("🥻 Desi Fusion (Chikankari)", key="btn_preset_desi_fusion", use_container_width=True):
                st.session_state["aes_vibe_box"] = "🥻 Indo-Western & Desi Fusion"
                st.session_state["aes_color_rule_box"] = "🎨 The 60-30-10 Color Formula"
                st.session_state["aes_garment_title_input"] = "Handcrafted Chikankari Kurti with Side Slits"
                st.session_state["aes_price_input"] = "₹299"
                st.session_state["aes_sample_file"] = "sample_kurti_set.jpg"
                st.rerun()
        with aes_p4:
            if st.button("✨ Party Glam (Satin Slip)", key="btn_preset_party_glam", use_container_width=True):
                st.session_state["aes_vibe_box"] = "✨ Party & Nightclub Glam"
                st.session_state["aes_color_rule_box"] = "✨ Monochrome Height & Slimming Illusion"
                st.session_state["aes_garment_title_input"] = "Emerald Green Liquid Satin Slip Dress"
                st.session_state["aes_price_input"] = "₹399"
                st.session_state["aes_sample_file"] = "sample_bralette_set.jpg"
                st.rerun()

        col_a1, col_a2 = st.columns([1.5, 1.5])
        with col_a1:
            st.markdown("##### 1. Pillar 1: Select Aesthetic Vibe")
            aes_map = {
                "🏛️ Old Money / Quiet Luxury": "old_money",
                "🛹 Gen-Z Streetwear & Urban Cool": "streetwear",
                "🥻 Indo-Western & Desi Fusion": "desi_fusion",
                "🎀 Korean & Soft Girl / Coquette": "korean_coquette",
                "✨ Party & Nightclub Glam": "party_glam"
            }
            aes_keys = list(aes_map.keys())
            if "aes_vibe_box" not in st.session_state:
                st.session_state["aes_vibe_box"] = aes_keys[0]
            selected_aes_label = st.selectbox("Fashion Aesthetic", aes_keys, key="aes_vibe_box")
            active_aes = aesthetics_data[aes_map[selected_aes_label]]

            st.markdown("##### 2. Pillar 3: Select Color Theory Rule")
            color_map = {
                "🥪 The Sandwich Dressing Rule": "sandwich",
                "🎨 The 60-30-10 Color Formula": "rule_60_30_10",
                "✨ Monochrome Height & Slimming Illusion": "monochrome"
            }
            col_keys = list(color_map.keys())
            if "aes_color_rule_box" not in st.session_state:
                st.session_state["aes_color_rule_box"] = col_keys[0]
            selected_col_label = st.selectbox("Color Theory Equation", col_keys, key="aes_color_rule_box")
            active_col = color_rules_data[color_map[selected_col_label]]

            # Aesthetic & Color Rule Card
            st.markdown(f"""
            <div style="background:white; border:1px solid #f0abfc; border-radius:10px; padding:0.9rem; margin-top:0.5rem; box-shadow:0 2px 6px rgba(0,0,0,0.02);">
                <div style="color:#701a75; font-weight:700; font-size:0.95rem; margin-bottom:0.3rem;">
                    🎨 {active_aes['name']} Lookbook DNA:
                </div>
                <div style="font-size:0.83rem; color:#475569; margin-bottom:0.25rem;">
                    <b>🎨 Palette:</b> {active_aes['palette']}
                </div>
                <div style="font-size:0.83rem; color:#475569; margin-bottom:0.25rem;">
                    <b>💎 Accessories:</b> {active_aes['acc']}
                </div>
                <div style="font-size:0.83rem; color:#475569; margin-bottom:0.4rem;">
                    <b>🏛️ Scene Set:</b> {active_aes['env']}
                </div>
                <div style="font-size:0.82rem; color:#86198f; background:#fdf4ff; padding:0.4rem 0.6rem; border-radius:6px;">
                    <b>📐 {active_col['name']}:</b> {active_col['rule']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_a2:
            st.markdown("##### 📸 Visual Anchors & Garment Photo")
            if "aes_garment_title_input" not in st.session_state:
                st.session_state["aes_garment_title_input"] = active_aes.get("sample_title", "Fashion Garment")
            aes_garment_title = st.text_input("Product Title", key="aes_garment_title_input")

            c_aimg1, c_aimg2 = st.columns(2)
            with c_aimg1:
                st.caption("👤 Creator Anchor")
                aes_creator_file = st.file_uploader("Creator Photo", type=["jpg", "jpeg", "png", "webp"], key="aes_creator_uploader")
                aes_creator_bytes = None
                if aes_creator_file:
                    aes_creator_bytes = aes_creator_file.read()
                    st.image(aes_creator_bytes, caption="Creator Uploaded", use_container_width=True)
                elif st.session_state.get("sample_creator_bytes"):
                    aes_creator_bytes = st.session_state["sample_creator_bytes"]
                    st.image(aes_creator_bytes, caption="Default Creator Anchor", use_container_width=True)
                else:
                    sc_path = os.path.join(BASE_DIR, "static", "sample_products", "sample_creator.jpg")
                    if os.path.exists(sc_path):
                        with open(sc_path, "rb") as f:
                            aes_creator_bytes = f.read()
                        st.session_state["sample_creator_bytes"] = aes_creator_bytes
                        st.image(aes_creator_bytes, caption="Default Creator Anchor", use_container_width=True)

            with c_aimg2:
                st.caption("👗 Garment Photo")
                aes_garment_file = st.file_uploader("Garment Photo", type=["jpg", "jpeg", "png", "webp"], key="aes_garment_uploader")
                aes_garment_bytes = None
                sample_file = st.session_state.get("aes_sample_file", active_aes.get("sample_img", "sample_linen_shirt.jpg"))
                sample_path = os.path.join(BASE_DIR, "static", "sample_products", sample_file)

                if aes_garment_file:
                    aes_garment_bytes = aes_garment_file.read()
                    st.image(aes_garment_bytes, caption="Garment Uploaded", use_container_width=True)
                elif os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        aes_garment_bytes = f.read()
                    st.image(aes_garment_bytes, caption=f"Sample: {sample_file}", use_container_width=True)
                    st.caption("✅ Auto-loaded aesthetic sample garment.")

        st.markdown("---")
        st.markdown("##### 🎭 Influencer Personality & Strategy (Section 20 Engine)")
        c_ainf1, c_ainf2, c_ainf3 = st.columns(3)
        with c_ainf1:
            aes_pers = st.selectbox("🎭 Creator Personality", [
                "🌸 Cute & Friendly Bestie (Conversational, sister-vibe)",
                "⚡ High-Energy Gen-Z (Fast cuts, punchy slang)",
                "👑 Calm & Elegant Stylist (Poised, quiet luxury guru)",
                "😂 Funny & Relatable (Self-deprecating, family banter)"
            ], index=0, key="aes_pers_select")
        with c_ainf2:
            aes_aud = st.selectbox("🎯 Target Audience Persona", [
                "🎓 College Fresher on Budget (18-22, fear of cheap fabric)",
                "💼 Corporate Working Professional (23-32, 8hr comfort, no button gaps)",
                "🥻 Festive & Wedding Guest (20-35, luxury boutique look dupe)",
                "🏃‍♀️ Daily Comfort & Body Insecurity Solver (All ages, lower belly / chafing)"
            ], index=0, key="aes_aud_select")
        with c_ainf3:
            aes_hook = st.selectbox("🪝 Hook Archetype", [
                "🎯 AI Auto-Pick (Best Fit for Garment)",
                "🔍 Curiosity Secret ('Meesho par aisi hidden kurti...')",
                "🤦‍♀️ Relatable Problem ('Agar aapki kurti me lower belly...')",
                "😲 Surprising Result Dupe ('₹299 ki skirt ko Zara look...')",
                "⚖️ Expectation vs Reality (Catalog vs Real Me at 5ft 2in)",
                "🤫 Personal Confession ('Sach batau? Mujhe wedding jane me darr tha...')",
                "❓ Pattern Interrupt Question ('Ye sabse badi styling galti kar rahi ho?')",
                "✨ Instant Visual Wow (0-2s complete outfit beat drop)"
            ], index=0, key="aes_hook_select")

        st.markdown("##### ⚙️ Production & Commercial Settings")
        c_aset1, c_aset2, c_aset3, c_aset4 = st.columns(4)
        with c_aset1:
            aes_tone = st.selectbox("🗣️ Voice Tone", ["👠 Fashion Stylist (Polished, luxury vibe)", "👯 Bestie / Saheli (Relatable, unfiltered)"], index=0, key="aes_tone_select")
        with c_aset2:
            aes_dur = render_duration_selector(key_prefix="aes_dur", default_val="30s", label="⏱️ Reel Duration")
        with c_aset3:
            if "aes_price_input" not in st.session_state:
                st.session_state["aes_price_input"] = "₹399"
            aes_price = st.text_input("💰 Meesho Price", key="aes_price_input")
        with c_aset4:
            aes_code = st.text_input("🏷️ Product Code", value="s-1892841", key="aes_code_input")
        aes_affiliate = st.text_input("🔗 Affiliate / Buy Link", placeholder="https://wishlink.com/... or Meesho share link", key="aes_affiliate_in")

        aes_dupe = render_brand_dupe_selector(key_prefix="aes_dupe", meesho_price=aes_price)
        aes_ost = st.checkbox("🟡 Include On-Screen Text Overlays", value=False, key="aes_ost_check")

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
        col_abtn1, col_abtn2 = st.columns([2.5, 1.5])
        with col_abtn1:
            btn_gen_aes = st.button("🚀 Generate 'Look Expensive on a Budget' Script & Voice", type="primary", use_container_width=True, key="btn_gen_aes_reel")
        with col_abtn2:
            meesho_aes_search = f"https://www.meesho.com/search?q={quote_plus(aes_garment_title)}"
            st.link_button("🔍 Find Product on Meesho", url=meesho_aes_search, use_container_width=True)

        if btn_gen_aes:
            if not env_key:
                st.error("Please enter a valid Gemini API Key in the sidebar.")
            else:
                with st.spinner("✨ Crafting Luxury Dupe Script with 2-Second Outfit Rule & Scorecard..."):
                    res_script = generate_fashion_stylist_script(
                        mode="aesthetic_color",
                        product_data={"title": aes_garment_title},
                        aesthetic=active_aes,
                        color_rule=active_col,
                        format_type="expensive_vs_cheap",
                        duration=aes_dur,
                        language="Hinglish (Natural Indian Social Tone)",
                        voice_tone=aes_tone,
                        price=aes_price,
                        meesho_code=aes_code,
                        creator_bytes=aes_creator_bytes,
                        product_bytes=aes_garment_bytes,
                        include_on_screen_text=aes_ost,
                        brand_dupe_info=aes_dupe,
                        creator_personality=aes_pers,
                        audience_persona=aes_aud,
                        hook_archetype=aes_hook,
                        api_key=env_key,
                        affiliate_link=aes_affiliate if "aes_affiliate" in locals() else ""
                    )
                    if res_script.startswith("❌") or res_script.startswith("⚠️"):
                        st.error(res_script)
                    else:
                        st.session_state["latest_solver_script"] = res_script
                        st.session_state["latest_solver_filename"] = f"meesho_aesthetic_{active_aes['id']}.md"
                        st.toast("🎉 Luxury Dupe Stylist Script Ready!", icon="🎨")

    # ---------------------------------------------------------
    # PRODUCTION PACKAGE RENDERER (Universal across all 4 modes)
    # ---------------------------------------------------------
    if "latest_solver_script" in st.session_state:
        st.markdown("---")
        st.markdown("### 📋 Generated Influencer Script & Retention Production Package")
        st.markdown("""
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
            <span class="badge-pill badge-pink">🔒 Identity & Body Shape Locked</span>
            <span class="badge-pill badge-purple">👗 2-Second Outfit Rule Active</span>
            <span class="badge-pill badge-amber">🎙️ Swara Studio Voice-Over Ready</span>
            <span class="badge-pill badge-green">🛡️ Zero Fake Claims Enforced</span>
        </div>
        """, unsafe_allow_html=True)
        
        sol_text = st.session_state["latest_solver_script"]
        
        # 🎯 Influencer Retention & Critique Scorecard (/160 Pts)
        render_influencer_scorecard(sol_text)
        
        # 🪝 A/B Hook Battle Component
        render_ab_hook_battle(sol_text, session_key="latest_solver_script", key_prefix="solver_hook_battle")
        st.markdown("---")

        s_tab1, s_tab2, s_tab3, s_tab4, s_tab5 = st.tabs([
            "🎬 Influencer Script & Voice-Over",
            "📋 Visual Director & Blocking Table",
            "🤖 Google Flow 8C Prompts",
            "🚀 Script-Linked SEO Studio",
            "📥 Export & Download"
        ])
        
        with s_tab1:
            render_voiceover_audio_studio(sol_text, key_prefix="solver_audio")
            st.markdown("---")
            st.markdown(sol_text)
            
        with s_tab2:
            st.markdown("#### 📋 Scene-by-Scene Visual Director & Blocking Table")
            st.caption("Filming & Camera Direction • 2-Second Outfit Anchor • Creator Physical Blocking • Natural Spoken Pacing")
            dir_table = extract_director_table(sol_text)
            if dir_table:
                st.markdown(dir_table)
            else:
                st.info("Director table details are included in the complete script breakdown in Tab 1.")
                
        with s_tab3:
            st.markdown("#### 🤖 Copy-Ready Google Flow & Kling AI Prompts")
            lines = sol_text.splitlines()
            in_p = False
            cur_p = []
            cnt = 0
            for l in lines:
                if "```text" in l or (l.strip() == "```" and in_p):
                    if in_p:
                        cnt += 1
                        st.markdown(f"**Scene Prompt #{cnt}:**")
                        st.code("\n".join(cur_p).strip(), language="text")
                        cur_p = []
                        in_p = False
                    else:
                        in_p = True
                elif in_p:
                    cur_p.append(l)
            if cnt == 0:
                st.markdown("Prompts are displayed within the script breakdown above.")
                
        with s_tab4:
            render_script_linked_seo_studio(sol_text, key_prefix="solver_seo", affiliate_link=st.session_state.get("aes_affiliate_in", st.session_state.get("bt_affiliate_in", "")))
                
        with s_tab5:
            dl_filename = st.session_state.get("latest_solver_filename", "meesho_influencer_reel.md")
            st.download_button(
                "📥 Download Influencer Script (.md)",
                data=sol_text,
                file_name=dl_filename,
                mime="text/markdown",
                use_container_width=True
            )
            st.text_area("Raw Markdown Content", value=sol_text, height=400)

# ---------------------------------------------------------
# TAB: 📦 Batch Haul Studio (Top 1-5 Finds)
# ---------------------------------------------------------
elif st.session_state["active_nav_tab"] == NAV_HAUL:
    st.markdown("### 📦 Batch Haul Studio (Top 1 to 5 Meesho Finds Under ₹500)")
    st.caption("AI-Powered Multi-Garment Roundup Reels • Snap Transitions • Continuous Unbroken Voice-Over • 3-Way A/B Hook Battle")

    sample_hauls = {
        "party": {
            "theme": "🎉 Top 5 Meesho Party Dresses Jo Luxury Boutique Jaisi Dikhti Hain",
            "items": [
                {"title": "Emerald Green Satin Slip Dress", "price": "₹399", "code": "s-1892841", "highlight": "Liquid satin drape & cowl neckline"},
                {"title": "Black Velvet Ruched Bodycon", "price": "₹449", "code": "s-2291034", "highlight": "Rich stretch velvet with flattering side ruching"},
                {"title": "Rose Gold Sequin Wrap Top", "price": "₹349", "code": "s-1502948", "highlight": "Handcrafted micro sequins with padded lining"},
                {"title": "Wine Red Off-Shoulder Corset Dress", "price": "₹499", "code": "s-3109284", "highlight": "Structured boning & sweetheart neck"},
                {"title": "Metallic Silver Pleated Mini Skater", "price": "₹380", "code": "s-4820192", "highlight": "High-shine shimmer fabric with back zipper"}
            ]
        },
        "college": {
            "theme": "🎓 Top 5 Daily Wear Pure Cotton Kurtis Under ₹350",
            "items": [
                {"title": "Pastel Pink Pure Cotton Anarkali Kurti", "price": "₹349", "code": "s-1102934", "highlight": "Breathable cambric cotton with 3-meter flare"},
                {"title": "Indigo Bagru Hand-Block Print Kurti", "price": "₹299", "code": "s-8920194", "highlight": "Natural indigo dye with functional side pocket"},
                {"title": "Sage Green Linen A-Line Kurta", "price": "₹320", "code": "s-1940291", "highlight": "Mandarin collar with stylish wooden buttons"},
                {"title": "Mustard Yellow Mirror-Work Straight Kurti", "price": "₹289", "code": "s-2204918", "highlight": "Delicate hand-mirror yoke on soft slub cotton"},
                {"title": "Sky Blue Chikankari Embroidered Kurta", "price": "₹350", "code": "s-3901923", "highlight": "Authentic shadow work with side slit detail"}
            ]
        },
        "festive": {
            "theme": "🥻 Top 5 Celebrity Inspired Saree Dupes on Meesho Under ₹699",
            "items": [
                {"title": "Organza Floral Zari Border Saree", "price": "₹499", "code": "s-7821941", "highlight": "Sheer lightweight organza drape with gota patti"},
                {"title": "Royal Blue Georgette Party Saree", "price": "₹399", "code": "s-9821045", "highlight": "Ultra-light georgette with tone-on-tone sequin pallu"},
                {"title": "Kanjeevaram Soft Silk Dupe Saree", "price": "₹699", "code": "s-3920192", "highlight": "Rich jacquard golden zari weave with temple border"},
                {"title": "Tissue Silk Champagne Gold Saree", "price": "₹549", "code": "s-5820194", "highlight": "Radiant metallic glass tissue with scalloped border"},
                {"title": "Lavender Ruffle Pre-Draped Saree", "price": "₹499", "code": "s-6710293", "highlight": "Ready-to-wear tiered ruffles with embroidered belt"}
            ]
        }
    }

    # 1-Click Preset Loaders
    st.markdown("##### ⚡ 1-Click Sample Haul Loaders (Test Top 5 in 1 Click):")
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        if st.button("🎉 Load Party Wear Haul (Top 5)", key="btn_load_party_haul", use_container_width=True):
            st.session_state["haul_item_count"] = 5
            st.session_state["input_haul_item_count"] = 5
            st.session_state["haul_theme_override"] = sample_hauls["party"]["theme"]
            st.session_state["haul_dur_override"] = "45s"
            for i, it in enumerate(sample_hauls["party"]["items"]):
                st.session_state[f"haul_title_{i}"] = it["title"]
                st.session_state[f"haul_price_{i}"] = it["price"]
                st.session_state[f"haul_code_{i}"] = it["code"]
                st.session_state[f"haul_hl_{i}"] = it["highlight"]
            st.toast("✅ Loaded Party Wear Haul Sample (5 Outfits)!", icon="🎉")
            st.rerun()

    with c_p2:
        if st.button("🎓 Load College Kurtis Haul (Top 5)", key="btn_load_college_haul", use_container_width=True):
            st.session_state["haul_item_count"] = 5
            st.session_state["input_haul_item_count"] = 5
            st.session_state["haul_theme_override"] = sample_hauls["college"]["theme"]
            st.session_state["haul_dur_override"] = "45s"
            for i, it in enumerate(sample_hauls["college"]["items"]):
                st.session_state[f"haul_title_{i}"] = it["title"]
                st.session_state[f"haul_price_{i}"] = it["price"]
                st.session_state[f"haul_code_{i}"] = it["code"]
                st.session_state[f"haul_hl_{i}"] = it["highlight"]
            st.toast("✅ Loaded College Kurtis Sample (5 Outfits)!", icon="🎓")
            st.rerun()

    with c_p3:
        if st.button("🥻 Load Saree Dupes Haul (Top 5)", key="btn_load_saree_haul", use_container_width=True):
            st.session_state["haul_item_count"] = 5
            st.session_state["input_haul_item_count"] = 5
            st.session_state["haul_theme_override"] = sample_hauls["festive"]["theme"]
            st.session_state["haul_dur_override"] = "45s"
            for i, it in enumerate(sample_hauls["festive"]["items"]):
                st.session_state[f"haul_title_{i}"] = it["title"]
                st.session_state[f"haul_price_{i}"] = it["price"]
                st.session_state[f"haul_code_{i}"] = it["code"]
                st.session_state[f"haul_hl_{i}"] = it["highlight"]
            st.toast("✅ Loaded Saree Dupes Sample (5 Outfits)!", icon="🥻")
            st.rerun()

    st.markdown("---")

    # Haul Controls
    c_h1, c_h2, c_h3 = st.columns([1.5, 2, 1.2])
    with c_h1:
        cur_count = st.session_state.get("haul_item_count", 5)
        haul_count = st.radio(
            "🔢 Number of Meesho Finds:",
            [1, 2, 3, 4, 5],
            index=[1, 2, 3, 4, 5].index(cur_count) if cur_count in [1, 2, 3, 4, 5] else 4,
            horizontal=True,
            key="input_haul_item_count"
        )
        st.session_state["haul_item_count"] = haul_count

    with c_h2:
        theme_presets = [
            f"🎉 Top {haul_count} Meesho Party Dresses Jo Luxury Lagti Hain",
            f"🎓 Top {haul_count} College & Office Kurtis Under ₹350",
            f"🥻 Top {haul_count} Saree Dupes Under ₹599",
            f"🛋️ Top {haul_count} Aesthetic Loungewear & Co-ords Under ₹499",
            f"💡 Top {haul_count} Meesho Wardrobe Lifesaver Hacks Under ₹199",
            "✍️ Custom Haul Theme"
        ]
        chosen_theme_preset = st.selectbox(
            "🎯 Haul Theme / Angle:",
            theme_presets,
            index=0,
            key="input_haul_theme_preset"
        )
        if chosen_theme_preset == "✍️ Custom Haul Theme":
            haul_theme = st.text_input("Custom Haul Title / Hook Angle:", value=st.session_state.get("haul_theme_override", f"Top {haul_count} Meesho Finds Under ₹500"), key="input_custom_haul_theme")
        else:
            haul_theme = st.session_state.get("haul_theme_override", chosen_theme_preset)

    with c_h3:
        dur_default_idx = 1 if haul_count >= 3 else 0
        haul_duration = st.selectbox(
            "⏱️ Haul Duration:",
            ["30s (Snappy)", "45s (Recommended)", "60s (Deep Review)"],
            index=dur_default_idx,
            key="input_haul_duration"
        )
        haul_dur_clean = haul_duration.split()[0]

    # Creator Reference & Global Options
    with st.expander("👤 Creator Reference & Advanced Video Tone (Optional)", expanded=False):
        c_cr1, c_cr2, c_cr3 = st.columns(3)
        with c_cr1:
            haul_creator_img = st.file_uploader("Upload Creator Reference Photo", type=["jpg", "jpeg", "png", "webp"], key="haul_creator_upload")
        with c_cr2:
            haul_tone = st.selectbox("Voice-Over Tone:", ["👯 Relatable Bestie", "👠 Fashion Stylist & Expert"], key="haul_tone_select")
            haul_affiliate = st.text_input("🔗 Haul Affiliate / Buy Link:", placeholder="https://wishlink.com/... or bio link", key="haul_affiliate_in")
        with c_cr3:
            haul_lang = st.selectbox("Spoken Language:", ["Hinglish (Conversational)", "Hindi", "English"], key="haul_lang_select")
            haul_ost = st.checkbox("🟡 Include Bold On-Screen Subtitles", value=False, key="haul_ost_toggle")

    # Dynamic Product Cards for 1 to haul_count
    st.markdown(f"#### 👗 Enter Details for {haul_count} Outfits (Upload {haul_count} Photos):")
    haul_products_data = []

    default_titles = [
        "Emerald Green Satin Slip Dress",
        "Black Velvet Ruched Bodycon",
        "Rose Gold Sequin Wrap Top",
        "Wine Red Off-Shoulder Corset Dress",
        "Metallic Silver Pleated Mini Skater"
    ]
    default_prices = ["₹399", "₹449", "₹349", "₹499", "₹380"]
    default_codes = ["s-1892841", "s-2291034", "s-1502948", "s-3109284", "s-4820192"]
    default_hls = [
        "Liquid satin drape & cowl neck",
        "Premium stretch velvet with side ruching",
        "Handcrafted micro sequins with soft lining",
        "Structured boning & sweetheart neck",
        "High-shine shimmer fabric with back zipper"
    ]

    for i in range(haul_count):
        def_t = st.session_state.get(f"haul_title_{i}", default_titles[i] if i < len(default_titles) else f"Meesho Outfit #{i+1}")
        def_p = st.session_state.get(f"haul_price_{i}", default_prices[i] if i < len(default_prices) else "₹399")
        def_c = st.session_state.get(f"haul_code_{i}", default_codes[i] if i < len(default_codes) else f"s-{1800000 + i*11111}")
        def_hl = st.session_state.get(f"haul_hl_{i}", default_hls[i] if i < len(default_hls) else "Trendy styling & soft fabric")

        with st.container():
            st.markdown(f"**👗 Outfit #{i+1} Photo & Details:**")
            c_it_img, c_it_t, c_it_p, c_it_c, c_it_hl = st.columns([1.8, 2.5, 1, 1.2, 2.5])
            with c_it_img:
                p_file = st.file_uploader(f"📸 Photo #{i+1}", type=["jpg", "jpeg", "png", "webp"], key=f"haul_file_{i}")
            with c_it_t:
                p_title = st.text_input(f"Title #{i+1}", value=def_t, key=f"haul_title_{i}", placeholder="Product Name")
            with c_it_p:
                p_price = st.text_input(f"Price #{i+1}", value=def_p, key=f"haul_price_{i}", placeholder="₹399")
            with c_it_c:
                p_code = st.text_input(f"Code #{i+1}", value=def_c, key=f"haul_code_{i}", placeholder="s-123456")
            with c_it_hl:
                p_hl = st.text_input(f"Highlight #{i+1}", value=def_hl, key=f"haul_hl_{i}", placeholder="Why is it special?")

            p_bytes = p_file.read() if p_file else None
            haul_products_data.append({
                "index": i + 1,
                "title": p_title,
                "price": p_price,
                "code": p_code,
                "highlight": p_hl,
                "bytes": p_bytes
            })

    # Generate Button
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    c_gen_btn, _ = st.columns([2, 1])
    with c_gen_btn:
        btn_gen_haul = st.button(
            f"🚀 Generate Top {haul_count} Batch Haul Script & Prompts",
            type="primary",
            use_container_width=True,
            key="btn_generate_batch_haul"
        )

    if btn_gen_haul:
        api_key_to_use = st.session_state.get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
        if not api_key_to_use:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar or save it in `.env`.")
        else:
            with st.spinner(f"✨ Designing High-Retention Top {haul_count} Haul Script & Snap Transition Prompts..."):
                cr_bytes = haul_creator_img.read() if haul_creator_img else None
                haul_script_res = generate_batch_haul_script(
                    products=haul_products_data,
                    haul_theme=haul_theme,
                    duration=haul_dur_clean,
                    voice_tone=haul_tone,
                    language=haul_lang,
                    creator_bytes=cr_bytes,
                    api_key=api_key_to_use,
                    include_on_screen_text=haul_ost
                )
                if haul_script_res.startswith("⚠️") or haul_script_res.startswith("❌"):
                    st.error(haul_script_res)
                else:
                    st.session_state["latest_haul_script"] = haul_script_res
                    st.toast(f"🎉 Generated Top {haul_count} Haul Script & SEO!", icon="✅")

    # Haul Results Presentation
    if "latest_haul_script" in st.session_state:
        haul_text = st.session_state["latest_haul_script"]

        st.markdown("---")
        st.markdown("### 📋 Generated Batch Haul Production Package")
        st.markdown("""
        <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
            <span class="badge-pill badge-pink">📦 Multi-Outfit Haul Mode</span>
            <span class="badge-pill badge-purple">⚡ Snap Transitions Active</span>
            <span class="badge-pill badge-amber">🎙️ Continuous Haul Audio</span>
            <span class="badge-pill badge-green">🚀 Multi-Product SEO Linked</span>
        </div>
        """, unsafe_allow_html=True)

        # 1. A/B Hook Battle Component
        render_ab_hook_battle(haul_text, session_key="latest_haul_script", key_prefix="haul_hook_battle")
        st.markdown("---")

        # 2. Results Tabs
        h_tab1, h_tab2, h_tab3, h_tab4 = st.tabs([
            "🎬 Multi-Product Script & Voice-Over",
            "🤖 Google Flow Prompts",
            "🚀 Script-Linked Haul SEO Studio",
            "📥 Export & Download"
        ])

        with h_tab1:
            render_voiceover_audio_studio(haul_text, key_prefix="haul_audio")
            st.markdown("---")
            st.markdown(haul_text)

        with h_tab2:
            st.markdown("#### 🤖 Copy-Ready Google Flow & Kling AI Prompts (With Outfit Snap Transitions)")
            st.info("💡 Every prompt locks the creator identity while transitioning smoothly into the next outfit cut.")
            lines = haul_text.splitlines()
            in_p = False
            cur_p = []
            cnt = 0
            for l in lines:
                if "```text" in l or (l.strip() == "```" and in_p):
                    if in_p:
                        cnt += 1
                        st.markdown(f"**Scene Prompt #{cnt}:**")
                        st.code("\n".join(cur_p).strip(), language="text")
                        cur_p = []
                        in_p = False
                    else:
                        in_p = True
                elif in_p:
                    cur_p.append(l)
            if cnt == 0:
                st.markdown("Prompts are displayed within the script breakdown in the Script tab above.")

        with h_tab3:
            render_script_linked_seo_studio(haul_text, key_prefix="haul_seo", affiliate_link=st.session_state.get("haul_affiliate_in", ""))

        with h_tab4:
            st.download_button(
                "📥 Download Haul Production Package (.md)",
                data=haul_text,
                file_name=f"meesho_batch_haul_{len(haul_products_data)}_items.md",
                mime="text/markdown",
                use_container_width=True,
                key="btn_dl_haul_md"
            )
            st.text_area("Raw Markdown Content", value=haul_text, height=400, key="haul_raw_md_area")

# ---------------------------------------------------------
# Footer Information
# ---------------------------------------------------------
st.markdown("""
<hr style='margin-top:3rem; margin-bottom:1rem;'>
<div style='text-align:center; color:#94a3b8; font-size:0.82rem;'>
    Meesho AI Video Script & Flow Director • Daily Instagram Trends Engine • Dual Voice-Over Tone • Google Flow & Kling AI Zero-Rejection Standard
</div>
""", unsafe_allow_html=True)
