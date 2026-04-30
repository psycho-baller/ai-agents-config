import argparse
import os
import json
import shutil
import subprocess
import sys

SKILLS_DIR = "/Users/rami/Documents/life-os/ai-agents-config/skills"

sys.path.append(SKILLS_DIR)
from utils.smart_connections import get_vault_root

def run_workflow(mode="full"):
    vault_root = get_vault_root()
    print(f"Detected Vault Root: {vault_root}")

    # Use a stable python version
    python_exe = "python3.12"

    # Define paths to sub-skills
    # Sub-skills reside in ../ai-agents-config/skills
    skills_dir = SKILLS_DIR
    
    export_script = os.path.join(skills_dir, "letterly-export", "scripts", "export.py")
    process_script = os.path.join(skills_dir, "letterly-process", "scripts", "process.py")
    metadata_script = os.path.join(skills_dir, "generate-metadata", "scripts", "generate_metadata.py")
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

    if mode in ("full", "prepare"):
        # 1. Export if needed
        if not csv_files:
            print("\n--- Step 1: No CSV found. Running Export Sub-Skill ---")
            subprocess.run([python_exe, export_script, vault_root], cwd=vault_root, env=env)

        # 2. Process
        print("\n--- Step 2: Running Process Sub-Skill ---")
        subprocess.run([python_exe, process_script, vault_root], cwd=vault_root, env=env)
    else:
        print("\n--- Skipping Export and Process. Finishing Existing Markdown Files. ---")

    new_files = [f for f in os.listdir(unprocessed_dir) if f.endswith(".md")]
    if not new_files:
        print("No new magic notes found in unprocessed/. Workflow complete.")
        return

    # vault-relative paths for indexing wait
    new_vault_paths = [f"unprocessed/{f}" for f in new_files]

    if mode == "prepare":
        print("\nPrepare mode complete. Run generate-metadata on these files, then rerun with --mode finish:")
        for path in new_vault_paths:
            print(f"- {path}")
        return

    # 3. Validate generated metadata
    print("\n--- Step 3: Validating Generated Metadata ---")
    full_paths = [os.path.join(vault_root, path) for path in new_vault_paths]
    metadata_cmd = [python_exe, metadata_script, "validate", "--json"] + full_paths
    metadata_result = subprocess.run(metadata_cmd, cwd=vault_root, env=env, capture_output=True, text=True)
    if metadata_result.stderr:
        print(metadata_result.stderr)

    valid_metadata_paths = set()
    try:
        metadata_report = json.loads(metadata_result.stdout or "{}")
        for item in metadata_report.get("files", []):
            if item.get("valid"):
                valid_metadata_paths.add(os.path.abspath(item["path"]))
            else:
                print(f"Metadata invalid, leaving unprocessed: {os.path.basename(item.get('path', 'unknown'))}")
                for error in item.get("errors", []):
                    print(f"  - {error}")
    except json.JSONDecodeError as e:
        print(f"Metadata validation output could not be parsed: {e}")

    valid_vault_paths = [
        path for path in new_vault_paths
        if os.path.abspath(os.path.join(vault_root, path)) in valid_metadata_paths
    ]

    if not valid_vault_paths:
        print("No files with valid generated metadata. Leaving markdown files in unprocessed/.")
        return

    # 4. Link
    print("\n--- Step 4: Running Semantic Linker Sub-Skill ---")
    linker_cmd = [python_exe, link_script, vault_root] + valid_vault_paths
    subprocess.run(linker_cmd, cwd=vault_root, env=env)

    # 5. Deliver
    print("\n--- Step 5: Moving metadata-ready files to Transcriptions ---")
    dest_dir = os.path.join(vault_root, "My Outputs/Transcriptions")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    moved_count = 0
    skipped_count = 0
    for filename in os.listdir(unprocessed_dir):
        if filename.endswith(".md"):
            src_path = os.path.join(unprocessed_dir, filename)

            try:
                if os.path.abspath(src_path) in valid_metadata_paths:
                    dest_path = os.path.join(dest_dir, filename)
                    shutil.move(src_path, dest_path)
                    print(f"Moved metadata-ready note: {filename}")
                    moved_count += 1
                else:
                    print(f"Skipped (metadata invalid or missing): {filename}")
                    skipped_count += 1
            except Exception as e:
                print(f"Error checking {filename}: {e}")

    print(f"\nWorkflow Summary:")
    print(f"- Moved to Transcriptions: {moved_count}")
    print(f"- Remaining in unprocessed (pending metadata): {skipped_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run the Letterly transcription workflow")
    parser.add_argument(
        "--mode",
        choices=["full", "prepare", "finish"],
        default="full",
        help="prepare creates markdown, finish validates/links/delivers after generated metadata exists",
    )
    args = parser.parse_args()
    run_workflow(mode=args.mode)
