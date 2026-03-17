import os
import shutil
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.smart_connections import get_vault_root


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
        print("\n--- Step 0: No CSV found. Running Exporter ---")
        exporter_script = os.path.join(script_dir, "exporter.py")
        subprocess.run([python_exe, exporter_script, vault_root], cwd=vault_root)

    # 1. Process the CSV
    print("\n--- Step 1: Processing Letterly CSV ---")
    processor_script = os.path.join(script_dir, "processor.py")
    subprocess.run([python_exe, processor_script, vault_root], cwd=vault_root)

    # identify new .md files just created in unprocessed/
    new_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".md")]

    if not new_files:
        print("No new magic notes found. Workflow complete.")
        return

    # vault-relative paths for wait_for_sc_indexing
    new_vault_paths = [f"unprocessed/{f}" for f in new_files]

    # 2. Run Semantic Linker
    print("\n--- Step 2: Running Semantic Linker ---")
    global_linker = "/Users/rami/Documents/life-os/ai-agents-config/skills/obsidian-semantic-linker/scripts/link_notes.py"
    linker_cmd = [python_exe, global_linker, vault_root] + new_vault_paths
    subprocess.run(linker_cmd, cwd=vault_root)

    # 3. Move processed files to My Outputs/Transcriptions
    print("\n--- Step 3: Moving files to Transcriptions ---")
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
