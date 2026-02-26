#!/usr/bin/env python3
import sqlite3
import struct
import math
import os
import sys
import time

# Import centralized utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.browser import get_vault_root

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

def process_files(rowid_to_vector, rowid_to_path, vault_root, target_dir="unprocessed"):
    print(f"Normalizing vectors and searching for notes in '{target_dir}'...")
    for rid in rowid_to_vector:
        rowid_to_vector[rid] = normalize(rowid_to_vector[rid])
        
    updates_count = 0
    all_items = list(rowid_to_vector.items()) 
    
    for current_rowid, current_vector in rowid_to_vector.items():
        current_path = rowid_to_path[current_rowid]
        
        # Only process files in the target directory (usually 'unprocessed')
        if not current_path.startswith(target_dir):
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
        new_content = "\n\n## Related Notes\n"
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
    return updates_count

def wait_for_indexing(conn, filenames, timeout=60):
    """
    Polls the database until all provided filenames are found in embedding_metadata.
    """
    print(f"Waiting for Obsidian to index {len(filenames)} new files...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        cur = conn.cursor()
        cur.execute("SELECT notePath FROM embedding_metadata WHERE notePath LIKE 'unprocessed/%'")
        indexed_paths = {os.path.basename(row[0]) for row in cur.fetchall()}
        
        missing = [f for f in filenames if f not in indexed_paths]
        if not missing:
            print("All files indexed!")
            return True
            
        print(f"Still waiting for {len(missing)} files to be indexed... ({int(timeout - (time.time() - start_time))}s remaining)")
        time.sleep(5)
        # Re-open connection to refresh cache if needed (depends on SQLite mode)
        # But usually a new cursor is enough.
        
    print(f"Warning: Indexing timed out. Proceeding with {len(filenames) - len(missing)} linked files.")
    return False

def main(vault_root, wait_for_files=None):
    db_path = os.path.join(vault_root, ".nexus/cache.db")
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        
        if wait_for_files:
            wait_for_indexing(conn, wait_for_files)
            
        rowid_to_vector, rowid_to_path = load_vectors(conn)
        conn.close()
        
        count = process_files(rowid_to_vector, rowid_to_path, vault_root)
        print(f"Finished. Updated {count} files.")
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    v_root = sys.argv[1] if len(sys.argv) > 1 else get_vault_root()
    # If filenames are passed as arguments, we wait for them
    files_to_wait = sys.argv[2:] if len(sys.argv) > 2 else None
    main(v_root, wait_for_files=files_to_wait)
