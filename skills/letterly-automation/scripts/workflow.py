import os
import shutil
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.smart_connections import get_vault_root

def run_workflow():
    vault_root = get_vault_root()
    print(f"Detected Vault Root: {vault_root}")

    # Use the shared python executable from the venv
    python_exe = sys.executable

    # Define paths to sub-skills
    skills_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    export_script = os.path.join(skills_dir, "letterly-export", "scripts", "export.py")
    process_script = os.path.join(skills_dir, "letterly-process", "scripts", "process.py")
    link_script = os.path.join(skills_dir, "obsidian-semantic-linker", "scripts", "link_notes.py")

    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    if not os.path.exists(unprocessed_dir):
        os.makedirs(unprocessed_dir, exist_ok=True)

    csv_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".csv") and f.startswith("Letterly-export")]

    # 1. Export if needed
    if not csv_files:
        print("\n--- Step 1: No CSV found. Running Export Sub-Skill ---")
        subprocess.run([python_exe, export_script, vault_root], cwd=vault_root)

    # 2. Process
    print("\n--- Step 2: Running Process Sub-Skill ---")
    subprocess.run([python_exe, process_script, vault_root], cwd=vault_root)

    new_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".md")]
    if not new_files:
        print("No new magic notes found in unprocessed/. Workflow complete.")
        return

    # vault-relative paths for indexing wait
    new_vault_paths = [f"unprocessed/{f}" for f in new_files]

    # 3. Link
    print("\n--- Step 3: Running Semantic Linker Sub-Skill ---")
    linker_cmd = [python_exe, link_script, vault_root] + new_vault_paths
    subprocess.run(linker_cmd, cwd=vault_root)

    # 4. Deliver
    print("\n--- Step 4: Moving files to Transcriptions ---")
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

    print(f"\nWorkflow Complete. Moved {moved_count} files to {dest_dir}")

if __name__ == "__main__":
    run_workflow()
