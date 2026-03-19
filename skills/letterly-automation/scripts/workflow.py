import os
import shutil
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.smart_connections import get_vault_root

def run_workflow():
    vault_root = get_vault_root()
    print(f"Detected Vault Root: {vault_root}")

    # Use a stable python version
    python_exe = "python3.12"

    # Define paths to sub-skills
    # Sub-skills reside in ../ai-agents-config/skills
    skills_dir = "/Users/rami/Documents/life-os/ai-agents-config/skills"
    
    export_script = os.path.join(skills_dir, "letterly-export", "scripts", "export.py")
    process_script = os.path.join(skills_dir, "letterly-process", "scripts", "process.py")
    link_script = os.path.join(skills_dir, "obsidian-semantic-linker", "scripts", "link_notes.py")

    # Ensure PYTHONPATH is set for sub-processes to find 'utils'
    env = os.environ.copy()
    root_dir = os.path.dirname(skills_dir) # .agents
    # Actually 'utils' is in audio-processing/utils
    project_root = os.path.dirname(root_dir)
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    unprocessed_dir = os.path.join(vault_root, "unprocessed")
    if not os.path.exists(unprocessed_dir):
        os.makedirs(unprocessed_dir, exist_ok=True)

    csv_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".csv") and f.startswith("Letterly-export")]

    # 1. Export if needed
    if not csv_files:
        print("\n--- Step 1: No CSV found. Running Export Sub-Skill ---")
        subprocess.run([python_exe, export_script, vault_root], cwd=vault_root, env=env)

    # 2. Process
    print("\n--- Step 2: Running Process Sub-Skill ---")
    subprocess.run([python_exe, process_script, vault_root], cwd=vault_root, env=env)

    new_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".md")]
    if not new_files:
        print("No new magic notes found in unprocessed/. Workflow complete.")
        return

    # vault-relative paths for indexing wait
    new_vault_paths = [f"unprocessed/{f}" for f in new_files]

    # 3. Link
    print("\n--- Step 3: Running Semantic Linker Sub-Skill ---")
    linker_cmd = [python_exe, link_script, vault_root] + new_vault_paths
    subprocess.run(linker_cmd, cwd=vault_root, env=env)

    # 4. Deliver
    print("\n--- Step 4: Moving linked files to Transcriptions ---")
    dest_dir = os.path.join(vault_root, "My Outputs/Transcriptions")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    moved_count = 0
    skipped_count = 0
    for filename in os.listdir(unprocessed_dir):
        if filename.endswith(".md"):
            src_path = os.path.join(unprocessed_dir, filename)
            
            # Read file to check for links
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "## Related Notes" in content:
                    dest_path = os.path.join(dest_dir, filename)
                    shutil.move(src_path, dest_path)
                    print(f"Moved linked note: {filename}")
                    moved_count += 1
                else:
                    print(f"Skipped (no links yet): {filename}")
                    skipped_count += 1
            except Exception as e:
                print(f"Error checking {filename}: {e}")

    print(f"\nWorkflow Summary:")
    print(f"- Moved to Transcriptions: {moved_count}")
    print(f"- Remaining in unprocessed (pending links): {skipped_count}")

if __name__ == "__main__":
    run_workflow()
