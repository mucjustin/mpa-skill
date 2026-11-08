"""Cross-platform workspace configuration (replaces the former PowerShell scripts).

Config resolution: MPA_WORKSPACE_CONFIG → platform default:
  macOS   ~/Library/Application Support/mpa-skill/config.json
  Windows %APPDATA%\\mpa-skill\\config.json
  Linux   $XDG_CONFIG_HOME/mpa-skill/config.json (default ~/.config)
"""
from __future__ import annotations

import json
import os
import platform
import sys
import urllib.request
from pathlib import Path

from .core import EvidenceError

CONFIG_KEYS = ("workspace_root", "obsidian_vault", "zotero_executable",
               "zotero_attachments", "research_data", "research_projects")
SUBDIRS = {"obsidian_vault": "Obsidian", "zotero_attachments": "ZoteroAttachments",
           "research_data": "ResearchData", "research_projects": "ResearchProjects"}
ZOTERO_PING = "http://127.0.0.1:23119/connector/ping"


def default_config_path() -> Path | None:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "mpa-skill" / "config.json"
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        return Path(appdata) / "mpa-skill" / "config.json" if appdata else None
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "mpa-skill" / "config.json"


def resolve_config_path(explicit=None) -> Path | None:
    raw = explicit or os.environ.get("MPA_WORKSPACE_CONFIG")
    if raw:
        return Path(os.path.expandvars(raw)).expanduser().resolve()
    path = default_config_path()
    return path.resolve() if path else None


def zotero_candidates():
    if sys.platform == "darwin":
        return [Path("/Applications/Zotero.app"), Path.home() / "Applications" / "Zotero.app"]
    if os.name == "nt":
        out = []
        for var, rel in (("ProgramFiles", "Zotero/zotero.exe"),
                         ("ProgramFiles(x86)", "Zotero/zotero.exe"),
                         ("LOCALAPPDATA", "Programs/Zotero/zotero.exe")):
            if os.environ.get(var):
                out.append(Path(os.environ[var]) / rel)
        return out
    return [Path("/usr/bin/zotero"), Path("/usr/local/bin/zotero"), Path("/opt/zotero/zotero"),
            Path.home() / "Zotero" / "zotero"]


def initialize_workspace(workspace_root, config_path=None, zotero=None, dry_run=False):
    root = Path(os.path.expandvars(str(workspace_root))).expanduser().resolve()
    if root == Path(root.anchor):
        raise EvidenceError("Workspace root must not be a filesystem root.")
    if root.is_file():
        raise EvidenceError("Workspace root points to an existing file.")
    config = resolve_config_path(config_path)
    if config is None:
        raise EvidenceError("--config is required when no default config location is available.")
    if config.exists():
        raise EvidenceError(f"Config already exists: {config}. Choose another --config to "
                            "preserve the existing configuration.")
    if zotero:
        zotero_path = str(Path(zotero).expanduser().resolve())
    else:
        found = next((p for p in zotero_candidates() if p.exists()), None)
        zotero_path = str(found) if found else ""
    paths = {"workspace_root": str(root), "zotero_executable": zotero_path}
    for key, name in SUBDIRS.items():
        paths[key] = str(root / name)
    paths = {k: paths[k] for k in CONFIG_KEYS}
    directories = [paths["workspace_root"]] + [paths[k] for k in SUBDIRS]
    if not dry_run:
        for d in directories:
            Path(d).mkdir(parents=True, exist_ok=True)
        config.parent.mkdir(parents=True, exist_ok=True)
        # "x" mode: never overwrite a config created concurrently.
        with config.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(paths, ensure_ascii=False, indent=2) + "\n")
    return {"config_path": str(config), "workspace_root": str(root),
            "zotero_executable": zotero_path, "created": not dry_run,
            "directories": directories}


def _zotero_connector_reachable(timeout=1.0):
    try:
        with urllib.request.urlopen(ZOTERO_PING, timeout=timeout) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def inspect_environment(config_path=None, probe_zotero=True):
    """Read-only check of configured paths and optional Zotero connector."""
    config = resolve_config_path(config_path)
    found = bool(config and config.is_file())
    data = {}
    if found:
        try:
            data = json.loads(config.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise EvidenceError(f"Config is not valid JSON: {config}") from exc

    def is_dir(key):
        value = data.get(key)
        return bool(value) and Path(value).is_dir()

    zotero = data.get("zotero_executable") or ""
    return {
        "platform": platform.system(),
        "python": platform.python_version(),
        "config_path": str(config) if config else "",
        "config_found": found,
        "missing_keys": [k for k in CONFIG_KEYS if found and k not in data],
        "workspace_root_exists": is_dir("workspace_root"),
        "obsidian_vault_exists": is_dir("obsidian_vault"),
        "zotero_attachments_exists": is_dir("zotero_attachments"),
        "research_data_exists": is_dir("research_data"),
        "research_projects_exists": is_dir("research_projects"),
        "zotero_executable_configured": bool(zotero),
        "zotero_executable_exists": bool(zotero) and Path(zotero).exists(),
        "zotero_connector_reachable": _zotero_connector_reachable() if probe_zotero else None,
        "read_only": True,
    }
