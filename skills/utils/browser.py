import os

def get_shared_context_path():
    """Returns the absolute path to the centralized Chrome user data directory."""
    # Centralized location for all browser-based skills
    path = "/Users/rami/Documents/life-os/ai-agents-config/shared_browser_context"
    os.makedirs(path, exist_ok=True)
    return path

def get_vault_root():
    """Centralized vault root detection for all skills."""
    candidates = [
        os.getcwd(),
        "/Users/rami/Documents/life-os/Obsidian",
        "/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian"
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, ".nexus/cache.db")):
            return c
    return os.getcwd()
