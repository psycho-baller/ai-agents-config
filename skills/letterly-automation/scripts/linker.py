#!/usr/bin/env python3
import sqlite3
import struct
import math
import os
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

# Configuration
VECTOR_DIM = 384
VECTOR_SIZE_BYTES = VECTOR_DIM * 4
CHUNK_SIZE = 1024
SIMILARITY_THRESHOLD = 0.45
TOP_K = 5

def load_vectors(conn):
    """Loads all vectors and metadata into memory."""
    print("Loading metadata...")
    cur = conn.cursor()
    cur.execute("SELECT rowid, notePath FROM embedding_metadata")
    rowid_to_path = {row[0]: row[1] for row in cur.fetchall()}

    print("Loading vectors...")
    cur.execute("SELECT rowid, vectors FROM note_embeddings_vector_chunks00")
    rowid_to_vector = {}

    for chunk_row in cur.fetchall():
        chunk_id = chunk_row[0]
        blob = chunk_row[1]
        num_vectors = len(blob) // VECTOR_SIZE_BYTES
        for i in range(num_vectors):
            global_rowid = (chunk_id - 1) * CHUNK_SIZE + (i + 1)
            if global_rowid in rowid_to_path:
                start = i * VECTOR_SIZE_BYTES
                end = start + VECTOR_SIZE_BYTES
                vec_bytes = blob[start:end]
                vector = list(struct.unpack(f'{VECTOR_DIM}f', vec_bytes))
                rowid_to_vector[global_rowid] = vector

    return rowid_to_vector, rowid_to_path

def cosine_similarity(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def normalize(v):
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0: return v
    return [x / norm for x in v]

def append_to_file(filepath, text):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if "## Related Notes" in content:
            return
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        print(f"  Error writing to {filepath}: {e}")

def process_files(rowid_to_vector, rowid_to_path, vault_root):
    print("Normalizing vectors...")
    for rid in rowid_to_vector:
        rowid_to_vector[rid] = normalize(rowid_to_vector[rid])

    updates_count = 0
    all_items = list(rowid_to_vector.items())

    for current_rowid, current_vector in rowid_to_vector.items():
        current_path = rowid_to_path[current_rowid]
        if not current_path.startswith("unprocessed"):
            continue

        full_path = os.path.join(vault_root, current_path)
        if not os.path.exists(full_path):
            continue

        scores = []
        for other_rowid, other_vector in all_items:
            if current_rowid == other_rowid:
                continue
            score = cosine_similarity(current_vector, other_vector)
            if score >= SIMILARITY_THRESHOLD:
                scores.append((score, other_rowid))

        scores.sort(key=lambda x: x[0], reverse=True)
        top_matches = scores[:TOP_K]

        if not top_matches:
            continue

        print(f"Linking: {current_path}")
        new_content = """

## Related Notes
"""
        links_added = 0
        for score, rid in top_matches:
            match_path = rowid_to_path[rid]
            match_name = os.path.basename(match_path)
            if match_name.endswith(".md"):
                match_name = match_name[:-3]
            new_content += f"- [[{match_name}]]\n"
            links_added += 1

        if links_added > 0:
            append_to_file(full_path, new_content)
            updates_count += 1
    print(f"Finished. Updated {updates_count} files.")

def main(vault_root):
    db_path = os.path.join(vault_root, ".nexus/cache.db")
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        rowid_to_vector, rowid_to_path = load_vectors(conn)
        conn.close()
        process_files(rowid_to_vector, rowid_to_path, vault_root)
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    v_root = sys.argv[1] if len(sys.argv) > 1 else get_vault_root()
    main(v_root)
