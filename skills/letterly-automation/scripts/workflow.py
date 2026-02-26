import os
import shutil
import subprocess
import sys

def get_vault_root():
    candidates = [
        os.getcwd(),
        "/Users/rami/Documents/life-os/Obsidian",
        "/Users/rami/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian"
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, ".nexus/cache.db")):
            return c
    return os.getcwd()

def run_workflow():
    vault_root = get_vault_root()
    print(f"Detected Vault Root: {vault_root}")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable
    
    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    if not os.path.exists(unprocessed_dir):
        os.makedirs(unprocessed_dir, exist_ok=True)
        
    csv_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".csv") and f.startswith("Letterly-export")]
    
    # 0. Export if needed
    if not csv_files:
        print("--- Step 0: No CSV found. Running Exporter ---")
        exporter_script = os.path.join(script_dir, "exporter.py")
        subprocess.run([python_exe, exporter_script, vault_root], cwd=vault_root)

    # 1. Process the CSV
    print("
--- Step 1: Processing Letterly CSV ---")
    processor_script = os.path.join(script_dir, "processor.py")
    subprocess.run([python_exe, processor_script, vault_root], cwd=vault_root)

    # Identify files that were just created in unprocessed
    new_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".md")]
    
    if not new_files:
        print("No new magic notes found. Workflow complete.")
        return

    # 2. Run Semantic Linker (The global one)
    print("
--- Step 2: Running Semantic Linker ---")
    # Point to the global linker skill
    global_linker = "/Users/rami/Documents/life-os/ai-agents-config/skills/obsidian-semantic-linker/scripts/link_notes.py"
    
    # We pass the vault root and the names of new files so the linker can wait for indexing
    linker_cmd = [python_exe, global_linker, vault_root] + new_files
    subprocess.run(linker_cmd, cwd=vault_root)

    # 3. Move processed files to My Outputs/Transcriptions
    print("
--- Step 3: Moving files to Transcriptions ---")
    dest_dir = os.path.join(vault_root, "My Outputs/Transcriptions")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
        
    moved_count = 0
    for filename in os.listdir(unprocessed_dir):
        if filename.endswith(".md"):
            src_path = os.path.join(unprocessed_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            shutil.move(src_path, dest_path)
            print(f"Moved: {filename}")
            moved_count += 1
            
    print(f"
Workflow Complete. Moved {moved_count} files to {dest_dir}")

if __name__ == "__main__":
    run_workflow()
