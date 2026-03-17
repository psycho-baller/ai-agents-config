#!/usr/bin/env python3
"""Find notes similar to a given file using Smart Connections embeddings.

Supports two modes:
  note  - compares whole-note vectors
  block - compares per-heading vectors, surfaces which section matches which note
  both  - runs both (default)
"""
import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.smart_connections import (
    get_vault_root,
    load_note_embeddings,
    load_block_embeddings,
    normalize,
    cosine_similarity,
)


def resolve_note_path(file_arg, vault_root):
    """Return a vault-relative path from an absolute, cwd-relative, or vault-relative input."""
    if os.path.isabs(file_arg):
        try:
            rel = os.path.relpath(file_arg, vault_root)
            # relpath can produce '../...' if outside vault
            if not rel.startswith(".."):
                return rel
        except ValueError:
            pass
        return file_arg
    abs_path = os.path.abspath(file_arg)
    if os.path.exists(abs_path):
        rel = os.path.relpath(abs_path, vault_root)
        if not rel.startswith(".."):
            return rel
    # assume it's already vault-relative
    return file_arg


def note_level(target_path, embeddings, threshold, top_k):
    """Return [(score, path)] sorted descending."""
    if target_path not in embeddings:
        return None  # not indexed

    target_vec = normalize(embeddings[target_path])
    scores = [
        (cosine_similarity(target_vec, normalize(vec)), path)
        for path, vec in embeddings.items()
        if path != target_path
    ]
    scores = [(s, p) for s, p in scores if s >= threshold]
    scores.sort(reverse=True)
    return scores[:top_k]


def block_level(target_path, blocks, threshold, top_k):
    """Return [(score, note_path, src_heading, tgt_heading)] sorted descending.

    Aggregates block-to-block scores: each candidate note gets the score of its
    best-matching block pair. Uses a slightly lower threshold for block comparisons
    since block vectors represent smaller, more focused content.
    """
    target_blocks = {k: v for k, v in blocks.items() if v["path"] == target_path}
    if not target_blocks:
        return None  # no blocks indexed for this note

    # pre-normalize target block vectors
    target_normed = [
        (normalize(b["vec"]), k)
        for k, b in target_blocks.items()
    ]

    # score every other block against every target block; keep best per note
    note_best = {}  # note_path -> (score, src_block_key, tgt_block_key)
    for cand_key, cand_block in blocks.items():
        cand_path = cand_block["path"]
        if cand_path == target_path:
            continue
        cand_vec = normalize(cand_block["vec"])
        for src_vec, src_key in target_normed:
            score = cosine_similarity(src_vec, cand_vec)
            if score >= threshold:
                if cand_path not in note_best or score > note_best[cand_path][0]:
                    note_best[cand_path] = (score, src_key, cand_key)

    results = sorted(note_best.items(), key=lambda x: x[1][0], reverse=True)
    return [
        (score, path, src_key, tgt_key)
        for path, (score, src_key, tgt_key) in results[:top_k]
    ]


def fmt_heading(block_key):
    """Extract just the heading chain from a block key like 'note.md#H1#H2'."""
    if "#" not in block_key:
        return "(full note)"
    parts = block_key.split("#", 1)[1]
    return parts[:60] or "(root section)"


def main():
    parser = argparse.ArgumentParser(description="Find notes similar to a given file")
    parser.add_argument("file", help="Note path (absolute, cwd-relative, or vault-relative)")
    parser.add_argument("--vault", help="Vault root (auto-detected if omitted)")
    parser.add_argument(
        "--mode",
        choices=["note", "block", "both"],
        default="both",
        help="Similarity mode (default: both)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.45,
        help="Minimum similarity score, 0-1 (default: 0.45)",
    )
    parser.add_argument("--top", type=int, default=10, help="Results to show (default: 10)")
    args = parser.parse_args()

    vault_root = args.vault or get_vault_root()
    note_path = resolve_note_path(args.file, vault_root)

    print(f"Vault : {vault_root}")
    print(f"Note  : {note_path}")
    print()

    if args.mode in ("note", "both"):
        print("=== Note-level similarity ===")
        embeddings = load_note_embeddings(vault_root)
        results = note_level(note_path, embeddings, args.threshold, args.top)
        if results is None:
            print(f"  '{note_path}' is not indexed by Smart Connections yet.")
        elif not results:
            print("  No similar notes above threshold.")
        else:
            for score, path in results:
                name = os.path.splitext(os.path.basename(path))[0]
                print(f"  {score:.3f}  {name}")
                print(f"         {path}")
        print()

    if args.mode in ("block", "both"):
        # use slightly lower threshold for blocks (more focused content)
        block_threshold = args.threshold * 0.85
        print(f"=== Block-level similarity (threshold {block_threshold:.2f}) ===")
        blocks = load_block_embeddings(vault_root)
        results = block_level(note_path, blocks, block_threshold, args.top)
        if results is None:
            print(f"  No blocks indexed for '{note_path}'.")
        elif not results:
            print("  No similar blocks above threshold.")
        else:
            for score, path, src_key, tgt_key in results:
                name = os.path.splitext(os.path.basename(path))[0]
                src_h = fmt_heading(src_key)
                tgt_h = fmt_heading(tgt_key)
                print(f"  {score:.3f}  {name}")
                print(f"         your section : {src_h}")
                print(f"         their section: {tgt_h}")
                print(f"         {path}")


if __name__ == "__main__":
    main()
