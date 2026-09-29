"""
Fetch and prepare Hugging Face mteb/CodeSearchNetRetrieval dataset for Local Hybrid RAG.
Downloads Python corpus and queries from Hugging Face Parquet.
"""
import os
import re
import json
from pathlib import Path
import pandas as pd

HF_CORPUS_URL = "https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet"
HF_QUERIES_URL = "https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet"
HF_QRELS_URL = "https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet"

OUTPUT_DIR = Path("online_dataset/src/codesearchnet")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("[1/4] Downloading dataset from Hugging Face MTEB...")
df_corpus = pd.read_parquet(HF_CORPUS_URL)
df_queries = pd.read_parquet(HF_QUERIES_URL)
df_qrels = pd.read_parquet(HF_QRELS_URL)

print(f"Loaded: Corpus={len(df_corpus)}, Queries={len(df_queries)}, Qrels={len(df_qrels)}")

# Select top 50 well-formed functions covering multiple domains
# Group them into meaningful Python modules
categories = {
    "network_client.py": [],
    "data_pipeline.py": [],
    "file_storage.py": [],
    "string_utils.py": [],
    "database_ops.py": [],
    "crypto_security.py": [],
    "system_process.py": [],
    "api_handlers.py": [],
}

cat_keys = list(categories.keys())

# Save query mapping for benchmark
benchmark_qa = []

count = 0
for idx, row in df_corpus.iterrows():
    code = row["text"].strip()
    c_id = row["id"]
    
    # Simple syntax validation
    if not code.startswith("def ") and not code.startswith("async def "):
        continue
    
    # Assign to one of the module categories
    mod_name = cat_keys[count % len(cat_keys)]
    categories[mod_name].append({
        "id": c_id,
        "code": code,
        "index": idx
    })
    
    # Check if this corpus id has a matching query in qrels
    matched_qrels = df_qrels[df_qrels["corpus-id"] == c_id]
    if not matched_qrels.empty:
        q_id = matched_qrels.iloc[0]["query-id"]
        q_row = df_queries[df_queries["id"] == q_id]
        if not q_row.empty:
            q_text = q_row.iloc[0]["text"].strip()
            benchmark_qa.append({
                "query": q_text,
                "file": mod_name,
                "corpus_id": c_id,
                "score": int(matched_qrels.iloc[0]["score"])
            })

    count += 1
    if count >= 60:
        break

# Write out Python modules
for mod_name, func_list in categories.items():
    file_path = OUTPUT_DIR / mod_name
    header = f'"""\nModule: {mod_name}\nSourced from Hugging Face: mteb/CodeSearchNetRetrieval\n"""\nimport os\nimport sys\nimport re\nimport json\nimport time\n\n'
    body = "\n\n".join([item["code"] for item in func_list])
    file_path.write_text(header + body + "\n", encoding="utf-8")
    print(f"  Saved {mod_name}: {len(func_list)} functions")

# Save benchmark metadata
bench_file = Path("online_dataset/hf_benchmark_qa.json")
bench_file.write_text(json.dumps(benchmark_qa[:20], indent=2, ensure_ascii=False), encoding="utf-8")
print(f"[Done] Created {len(categories)} Python modules in {OUTPUT_DIR}")
print(f"[Done] Saved {len(benchmark_qa)} benchmark Q&A pairs from Hugging Face.")
