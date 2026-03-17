#!/usr/bin/env python3
"""Links notes in unprocessed/ against the full vault using Smart Connections embeddings."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.smart_connections import (
    get_vault_root,
    load_note_embeddings,
    normalize,
    cosine_similarity,
    wait_for_sc_indexing,
)

SIMILARITY_THRESHOLD = 0.45
TOP_K = 5


def append_related_notes(filepath, links):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if "## Related Notes" in content:
            return False
        section = "\n\n## Related Notes\n" + "".join(f"- [[{name}]]\n" for name in links)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(section)
        return True
    except Exception as e:
        print(f"  Error writing to {filepath}: {e}")
        return False


def process_files(embeddings, vault_root):
    print(f"Loaded {len(embeddings)} embeddings. Linking notes in 'unprocessed/'...")
    normed = {path: normalize(vec) for path, vec in embeddings.items()}

    updates = 0
    for current_path, current_vec in normed.items():
        if not current_path.startswith("unprocessed"):
            continue
        full_path = os.path.join(vault_root, current_path)
        if not os.path.exists(full_path):
            continue

        scores = [
            (cosine_similarity(current_vec, other_vec), other_path)
            for other_path, other_vec in normed.items()
            if other_path != current_path and cosine_similarity(current_vec, other_vec) >= SIMILARITY_THRESHOLD
        ]
        scores.sort(reverse=True)
        top = scores[:TOP_K]

        if not top:
            continue

        names = [os.path.splitext(os.path.basename(p))[0] for _, p in top]
        print(f"  Linking: {current_path} -> {names}")
        if append_related_notes(full_path, names):
            updates += 1

    print(f"Finished. Updated {updates} file(s).")


def main(vault_root, wait_for_files=None):
    if wait_for_files:
        wait_for_sc_indexing(vault_root, wait_for_files)

    try:
        embeddings = load_note_embeddings(vault_root)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    process_files(embeddings, vault_root)


if __name__ == "__main__":
    v_root = sys.argv[1] if len(sys.argv) > 1 else get_vault_root()
    files_to_wait = sys.argv[2:] if len(sys.argv) > 2 else None
    main(v_root, wait_for_files=files_to_wait)
