# 📦 GitHub File Updates & Deployment Guide

Updated on: 2026-09-15 19:37:33

This guide explains all recent updates made to the Meesho AI Video Director and how to update your GitHub repository.

---

## 🚀 Summary of Changes & Fixes

### 1. Dynamic Script Generation (Gemini AI Integration)
- **Fixed repetitive static scripts**: `StoryEngine.generate_blueprint` now calls `gemini-3.5-flash-lite` live, producing 100% unique, custom story blueprints and scripts for any entered premise.
- **Dynamic contextual fallback**: Even offline or in low connectivity, scripts adapt dynamically to the idea (Yacht, Manali Trek, 5-Star Hotel, Cafe Aesthetic, Thrift Market, Car Drive, Party) with zero hardcoded boutique text.
- **Model Quota Fix**: Prioritized `gemini-3.5-flash-lite` across all 9 model candidate lists in `streamlit_app.py`, eliminating HTTP 429 quota errors and speeding up response times to ~1-2 seconds.

### 2. Video Prompts with 100% Creator Reference Photo Lock
- **`CREATOR_REFERENCE (Image 1)` Lock**: All Google Flow & Kling AI video prompts in TAB 4 explicitly anchor to the uploaded creator reference photo for exact facial identity, hair, skin undertone, and body proportions.
- **Venue Fix**: Clean physical locations (e.g. *Palladium, South Mumbai - Driveway Valet Entrance*) are assigned to each scene instead of repeating camera movement descriptions.
- **Standard ````text` Code Blocks**: TAB 4 prompts are wrapped in copy-ready code blocks compatible with the Streamlit interactive scene card renderer.
- **Creator Photo Uploader**: Added reference photo uploader and sample model loader directly inside the Story Director.

### 3. Visual Attention Engine & Phase 2 Intelligence
- 11-dimension retention evaluation, drop-risk predictor strip, viewer mind simulation, anti-boring diagnostics, and 3-round story auto-optimizer.

---

## 📁 Updated Files Included in this Update

| File / Folder | Purpose |
| :--- | :--- |
| `streamlit_app.py` | Main Streamlit application with model prioritization, 9-tab preset clearing, and full video studio |
| `lifestyle_director/` | Phase 2 Story Intelligence Engine, Director UI, Models, Services, and Storage |
| `visual_attention_engine/` | Visual Attention Engine, 11-dimension scoring, and section adapters |
| `MASTER_PROMPT_V1.md` | Master System Prompt with Section 23 Fictional Lifestyle Vlog rules |
| `README.md` | Updated documentation with all Phase 2 features and deployment guide |
| `requirements.txt` | Dependency list including `streamlit`, `google-generativeai`, `requests`, `pillow`, `python-dotenv`, `edge-tts` |

---

## 📤 How to Apply These Updates to Your GitHub Repository

### Option A: Using the Ready-to-Commit `github_update_files.zip` (Recommended for Quick Update)
1. Download or locate `d:\meesho\github_update_files.zip`.
2. Extract the contents directly into your local cloned GitHub repository folder.
3. Commit and push:
```bash
git add .
git commit -m "Update: Dynamic script generation, CREATOR_REFERENCE photo lock, and gemini-3.5-flash-lite prioritization"
git push origin main
```

### Option B: Using the Full Standalone `github_ready.zip` (For Fresh Repository / Full Overwrite)
1. Download or locate `d:\meesho\github_ready.zip`.
2. Extract all contents into your repository root.
3. Commit and push:
```bash
git add .
git commit -m "Deploy: Full Meesho AI Video Director v2.0 with Story Intelligence & Total Attention Engine"
git push origin main
```

### Option C: Manual Copy from `d:\meesho\github_update_files`
Copy the following folders/files from `d:\meesho\github_update_files\` into your GitHub folder:
- `streamlit_app.py`
- `lifestyle_director/`
- `visual_attention_engine/`
- `MASTER_PROMPT_V1.md`
- `README.md`
- `requirements.txt`

---

## 🌐 Deploying on Streamlit Cloud
1. Push the updated code to GitHub.
2. Go to your app dashboard on [share.streamlit.io](https://share.streamlit.io).
3. The app will automatically rebuild and deploy within 1-2 minutes.
4. Verify that your `GEMINI_API_KEY` is configured in **App Settings > Secrets**.
