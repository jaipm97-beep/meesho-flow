# 👗 Meesho AI Video Script & Flow Director

A powerful Streamlit-based AI video production engine designed for fashion creators, e-commerce brands, and affiliate marketers to generate high-converting short-form video scripts (10s to 60s Instagram Reels & YouTube Shorts), zero-moderation Google Flow & Kling AI video prompts, neural studio voice-overs, and automated affiliate launch packages.

---

## 🌟 Key Features

### 1. 🔇 2-Second Silent Visual Outfit Hook (00:00 - 00:02)
- **Zero Spoken Words in Scene 1**: Opening frame shows the creator wearing the **COMPLETE, fully-styled outfit from head-to-toe** with a confident poise, micro-spin, or dramatic flare reveal.
- **Trending Bass Beat Drop**: Features an energetic whoosh or beat drop SFX. Lips are closed with a warm, confident smile (creator is NOT speaking).
- **Spoken Voice Begins at 00:02 Sharp**: Audio dialogue and on-camera speech start precisely at `00:02` in Scene 2, eliminating early voice crowding and maximizing 3-second reel retention.

### 2. 👄 100% On-Camera Talking Head & Continuous Lip-Sync (Rule 10 & 11)
- **Eliminates the Uncanny Valley**: From Scene 2 onwards, the creator looks directly into the camera lens with active, continuous lip synchronization articulating every spoken word aloud.
- **Zero Frozen Mouth Cuts**: Eliminates closed/frozen mouth when audio is playing.
- **Strict Mathematical WPS Ceilings**: Scene-by-scene word ceilings (~2.3 words per second) calibrated so creators never rush or cram 20 words into a 5-second scene.

### 3. 🔗 Creator Affiliate Link & Live Instagram DM Preview Mockup
- **Multi-Studio Affiliate Support**: Dedicated `🔗 Product Affiliate / Buy Link` input across all 5 studios.
- **Automated ManyChat Auto-DM & Deal Card Injection**: Automatically replaces `[INSERT_LINK]` with the creator's real affiliate/Wishlink link (or fallback live Meesho search URL).
- **Interactive Instagram DM Preview**: In-app mobile chat preview with a 1-click **`🛍️ Test Affiliate Link Live ↗`** button and copyable raw text.

### 4. 🎙️ Neural Studio AI Voice-Over Generator (.mp3 Player & Export)
- Powered by Microsoft Edge Neural TTS:
  - 👩 **Swara (`hi-IN-SwaraNeural`)**: India's #1 natural, sweet, and expressive creator voice.
  - 👩 **Neerja (`en-IN-NeerjaNeural`)**: Polished Indian urban fashion stylist.
  - 👨 **Madhur (`hi-IN-MadhurNeural`)**: Deep, clear male voice.
- **Built-in 2-Second Silent Pause**: Automatically inserts a 2000ms pause matching the 2-second silent visual outfit hook.

### 5. 🚀 Dual-Platform Script-Linked SEO Studio (Instagram & YouTube Shorts)
- **Algorithmic Hook-Sync Captions**: First 125 characters match the video's spoken dialogue for audio-to-text algorithm dominance.
- **3-Tier Targeted Hashtags**: Mega (>1M), Niche (100K-1M), and Micro (<100K) intent tags.
- **Instagram Accessibility Alt-Text**: Visual search indexing for Explore page discovery.
- **YouTube Shorts Suite**: 3 high-CTR viral titles, exact video chapters/timestamps for Google search indexing, and 500-character meta tags.

### 6. 👗 5 Specialized Studios
1. **🎬 Studio Workspace**: Custom script generation with duration sliders (10s to 60s), tone selectors, and dupe comparison.
2. **📸 Meesho Catalog / Photo to Script**: Direct photo upload with instant A/B hook battles and Flow prompts.
3. **👠 Women's Problem Stories Studio**: Targeted solutions for party wear, office, saree, and daily comfort struggles.
4. **✨ Aesthetic & Styling Solutions Studio**: Trend-focused styling transformations.
5. **🛍️ Batch Haul Studio**: Multi-product batch reviews (1 to 5 outfits) with seamless snap transitions.

---

## 🛠️ Deploy on Streamlit Community Cloud

1. Fork or upload this repository to your GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New App**.
3. Select your repository and set `Main file path` to `streamlit_app.py`.
4. In **Advanced Settings > Secrets**, add your Gemini API Key:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```
5. Click **Deploy**!

---

## 💻 Local Development Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Streamlit
streamlit run streamlit_app.py
```
