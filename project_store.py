"""
Project Storage & Export Engine.
Handles JSON export, project save/load, and local caching.
"""
import os
import json
from typing import Dict, Any, Optional, List
from ..models.project import ProjectState

STORAGE_DIR = r"d:\meesho\.lifestyle_projects"
os.makedirs(STORAGE_DIR, exist_ok=True)

class ProjectStore:
    @staticmethod
    def save_project(project: ProjectState) -> str:
        """Saves project state as JSON file."""
        filename = f"{project.project_id}.json"
        filepath = os.path.join(STORAGE_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, indent=2, ensure_ascii=False)
        return filepath

    @staticmethod
    def load_project(project_id: str) -> Optional[ProjectState]:
        """Loads project state by ID."""
        filename = f"{project_id}.json" if not project_id.endswith(".json") else project_id
        filepath = os.path.join(STORAGE_DIR, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ProjectState.from_dict(data)

    @staticmethod
    def list_projects() -> List[Dict[str, str]]:
        """Lists all saved project files."""
        res = []
        if not os.path.exists(STORAGE_DIR):
            return res
        for f in os.listdir(STORAGE_DIR):
            if f.endswith(".json"):
                p_id = f[:-5]
                try:
                    with open(os.path.join(STORAGE_DIR, f), "r", encoding="utf-8") as fp:
                        d = json.load(fp)
                    res.append({
                        "project_id": p_id,
                        "project_name": d.get("project_name", "Untitled"),
                        "updated_at": d.get("updated_at", ""),
                        "status": d.get("approval_status", "draft")
                    })
                except Exception:
                    res.append({"project_id": p_id, "project_name": p_id, "updated_at": "", "status": "draft"})
        return sorted(res, key=lambda x: x["updated_at"], reverse=True)

    @staticmethod
    def export_as_json_string(project: ProjectState) -> str:
        """Exports clean, indented JSON string for 1-click download."""
        return json.dumps(project.to_dict(), indent=2, ensure_ascii=False)
