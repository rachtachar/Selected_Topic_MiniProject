"""
Setup Script: Codebase Indexing into Vector DB (FAISS) & Graph DB (Kuzu).
Usage:
    python setup.py --project ./sample_codebase
    python setup.py --project . --output_dir .
"""
import os
import sys
import argparse
import ast as ast_module
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Windows Terminal UTF-8 encoding fix
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from ast_parser import CodeGraphBuilder


VECTOR_DB_DIR = "vector_db"
GRAPH_DB_DIR = "graph_db"
METADATA_FILE = "index_metadata.json"
EMBED_MODEL = "nomic-embed-text"
SKIP_DIRS = {
    ".venv", "venv", "__pycache__", ".git", ".mypy_cache",
    "node_modules", "dist", "build", ".tox", ".pytest_cache", ".gemini",
    "session_12_hybrid_rag-20260926T010738Z-1-001",
    "session_13_coding_assistant_ui-20260926T010749Z-1-001",
}


def collect_python_files(project_path: str) -> List[str]:
    """Scan and collect all Python files excluding virtual environments and cache."""
    py_files = []
    p = Path(project_path).resolve()
    for root, dirs, files in os.walk(str(p)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in files:
            if fname.endswith(".py"):
                full_path = os.path.join(root, fname)
                py_files.append(full_path)
    return py_files


def extract_chunks(filepath: str) -> List[Dict[str, Any]]:
    """Extract functions, classes, and module-level code as structured chunks."""
    chunks = []
    try:
        source = Path(filepath).read_text(encoding="utf-8", errors="replace")
        tree = ast_module.parse(source)
        lines = source.splitlines()

        for node in ast_module.walk(tree):
            if isinstance(node, (ast_module.FunctionDef, ast_module.AsyncFunctionDef, ast_module.ClassDef)):
                start = node.lineno - 1
                end = getattr(node, "end_lineno", start + 25)
                code_snippet = "\n".join(lines[start:end])
                chunks.append({
                    "name": node.name,
                    "code": code_snippet,
                    "line": node.lineno,
                    "type": type(node).__name__,
                    "file": str(Path(filepath).as_posix()),
                })

        # Fallback if no function or class definitions found
        if not chunks and source.strip():
            chunks.append({
                "name": Path(filepath).stem,
                "code": source[:4000],
                "line": 1,
                "type": "ModuleSnippet",
                "file": str(Path(filepath).as_posix()),
            })
    except Exception as e:
        print(f"  Warning: parse error in {filepath}: {e}")
    return chunks


def build_vector_db(py_files: List[str], output_dir: str) -> int:
    """Build and save FAISS vector store index using nomic-embed-text."""
    print(f"\n[1/2] Building Vector DB with {EMBED_MODEL}...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    docs: List[Document] = []

    for filepath in py_files:
        chunks = extract_chunks(filepath)
        for chunk in chunks:
            # Enrich content with contextual header for superior semantic retrieval
            header = f"# {chunk['type']} {chunk['name']} in {chunk['file']}:{chunk['line']}\n"
            docs.append(Document(
                page_content=header + chunk["code"],
                metadata={
                    "file": chunk["file"],
                    "function": chunk["name"],
                    "line": chunk["line"],
                    "type": chunk["type"],
                    "code": chunk["code"],
                },
            ))
        rel_path = os.path.relpath(filepath)
        print(f"  [OK] Parsed: {rel_path} ({len(chunks)} chunks)")

    if not docs:
        print("  No code chunks found — skipping FAISS build")
        return 0

    print(f"\n  Embedding {len(docs)} code chunks into FAISS index...")
    t0 = time.time()
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(output_dir)
    elapsed = round(time.time() - t0, 2)
    print(f"  [OK] Vector DB saved to '{output_dir}' ({len(docs)} chunks embedded in {elapsed}s)")
    return len(docs)



def build_graph_db(project_path: str, output_dir: str) -> Dict[str, int]:
    """Build and save Kuzu graph database using CodeGraphBuilder."""
    print(f"\n[2/2] Building Graph DB with Kuzu...")
    t0 = time.time()
    builder = CodeGraphBuilder(db_path=output_dir, clear_existing=True)
    builder.parse_directory(project_path, skip_dirs=SKIP_DIRS)
    summary = builder.get_summary()
    elapsed = round(time.time() - t0, 2)
    print(f"  [OK] Graph DB saved to '{output_dir}' in {elapsed}s")
    print(f"    - Functions: {summary['functions']}")
    print(f"    - Modules:   {summary['modules']}")
    print(f"    - Classes:   {summary['classes']}")
    print(f"    - Calls:     {summary['calls']}")
    print(f"    - Imports:   {summary['imports']}")
    return summary


def run_setup(project_path: str, output_base_dir: str = ".") -> None:
    """Run end-to-end codebase indexing pipeline."""
    start_time = time.time()
    project_path = os.path.abspath(project_path)
    output_base_dir = os.path.abspath(output_base_dir)

    print("=" * 60)
    print("Codebase Indexing Pipeline (Vector + Graph)")
    print("=" * 60)
    print(f"Target Project : {project_path}")
    print(f"Output Base    : {output_base_dir}")

    vector_path = os.path.join(output_base_dir, VECTOR_DB_DIR)
    graph_path = os.path.join(output_base_dir, GRAPH_DB_DIR)
    os.makedirs(vector_path, exist_ok=True)
    # Note: Kuzu handles graph_path creation directly whether as directory or file


    py_files = collect_python_files(project_path)
    if not py_files:
        print(f"Error: No Python files found in '{project_path}'")
        return
    print(f"Found {len(py_files)} Python files to index")

    # 1. Build Vector DB
    n_chunks = build_vector_db(py_files, vector_path)

    # 2. Build Graph DB
    graph_stats = build_graph_db(project_path, graph_path)

    total_time = round(time.time() - start_time, 2)

    # 3. Save Metadata State
    meta_info = {
        "project_path": project_path,
        "indexed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files_count": len(py_files),
        "chunks_count": n_chunks,
        "embedding_model": EMBED_MODEL,
        "vector_db_path": str(Path(vector_path).as_posix()),
        "graph_db_path": str(Path(graph_path).as_posix()),
        "graph_stats": graph_stats,
        "total_indexing_time_seconds": total_time,
    }
    meta_path = os.path.join(output_base_dir, METADATA_FILE)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2)

    print("\n" + "=" * 60)
    print("Indexing Complete!")
    print(f"  Files Indexed   : {len(py_files)}")
    print(f"  Chunks Created  : {n_chunks}")
    print(f"  Metadata Saved  : {meta_path}")
    print(f"  Total Duration  : {total_time}s")
    print("=" * 60)

    print("\nNext step:")
    print("  python -m streamlit run app.py")
    return meta_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index codebase into Vector & Graph DB")
    parser.add_argument("--project", "-p", default="./sample_codebase", help="Path to project directory")
    parser.add_argument("--output_dir", "-o", default=".", help="Base output directory")
    args = parser.parse_args()

    run_setup(args.project, args.output_dir)
