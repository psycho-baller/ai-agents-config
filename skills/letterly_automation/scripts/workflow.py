import os
import shutil
import subprocess
import sys

def run_workflow():
    vault_root = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # We assume the caller provides the python path or we use the current one
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

    # 2. Run Semantic Linker
    print("
--- Step 2: Running Semantic Linker ---")
    linker_script = os.path.join(script_dir, "linker.py")
    subprocess.run([python_exe, linker_script, vault_root], cwd=vault_root)

    # 3. Move processed files
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
