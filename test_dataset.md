# Online Test Dataset & Benchmark Evaluation (Hugging Face)
**Project:** Local Hybrid RAG Coding Assistant (Vector + Graph)  
**Dataset Name:** `mteb/CodeSearchNetRetrieval` (Official Hugging Face MTEB Retrieval Benchmark)  
**Subset:** `python-corpus`, `python-queries`, `python-qrels`  
**License:** MIT  
**Platform:** Hugging Face Datasets Hub  

---

## แหล่งที่มาและ Static Links บน Hugging Face (Permanent URLs)

ชุดข้อมูลที่นำมาใช้ทดสอบระบบ เป็น Open-Source Python Code Retrieval Benchmark ระดับโลกที่โฮสต์อยู่บน Hugging Face Hub อย่างเป็นทางการ:

| ประเภทข้อมูล | ลิงก์ถาวรบน Hugging Face (Static Link) | รายละเอียด |
| :--- | :--- | :--- |
| **Hugging Face Dataset Card** | [https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval](https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval) | หน้าหลัก Dataset บน Hugging Face Hub |
| **Python Corpus Parquet** | [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet) | ลิงก์ตรงดาวน์โหลดไฟล์ Parquet ของ Code Corpus |
| **Python Queries Parquet** | [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet) | ลิงก์ตรงดาวน์โหลดคู่คำถาม Benchmark สำหรับ Search |
| **Python Qrels Parquet** | [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet) | ตารางเฉลยความเกี่ยวข้อง (Ground Truth Relevance) |

---

## สถิติผลการ Indexing บน Codebase จริง

* **จำนวนไฟล์ Python ที่ Index:** 8 โมดูล (`src/codesearchnet/*.py`)
* **จำนวน Vector Chunks (FAISS):** 63 Chunks (Embedded ด้วย `nomic-embed-text`)
* **โครงสร้าง Graph Database (Kuzu):**
  * **Functions Indexed:** 61 ฟังก์ชัน
  * **Modules Indexed:** 8 โมดูล
  * **Function Calls (Edges):** 372 ความสัมพันธ์
  * **Module Imports (Edges):** 46 ความสัมพันธ์
* **เวลาที่ใช้ในการ Index ทั้งหมด:** ~10.3 วินาที

---

## โครงสร้างโมดูลหลักของ Dataset (`src/codesearchnet/`)

| โมดูล | หน้าที่และฟังก์ชันสำคัญ | ที่มาของโค้ดต้นฉบับ |
| :--- | :--- | :--- |
| `network_client.py` | `sina_download_by_vid`, `upsert_document`, `task_failed_deps` | `you-get`, `apache/airflow` |
| `data_pipeline.py` | `post_content`, `clear_dag_runs`, `print_stats`, `resetdb` | `you-get`, `apache/airflow` |
| `file_storage.py` | `get_video_url_from_video_id`, `get_document`, `make_aware` | `you-get`, `apache/airflow` |
| `string_utils.py` | `matchall`, `execute`, `_get_field`, `get_conn` | `you-get`, `apache/airflow` |
| `database_ops.py` | `bulk_load`, `cbs_download`, `is_bucket_updated`, `publish` | `apache/airflow` |
| `crypto_security.py` | `export_instance`, `list_py_file_paths`, `next_execution` | `apache/airflow` |
| `system_process.py` | `bulk_load`, `_wanmen_get_title_by_json_topic_part`, `chain` | `apache/airflow` |
| `api_handlers.py` | `closest_ds_partition`, `get_database_hook`, `get_head` | `apache/airflow` |

---

## ชุดคำถามทดสอบระบบ 10 ข้อ (Test Suite)

1. `How does post_content work in data_pipeline.py?` (Vector)
2. `Who calls bulk_load?` (Graph)
3. `How does matchall in string_utils.py scan for regex patterns?` (Vector)
4. `What modules does network_client.py import?` (Graph)
5. `How does closest_ds_partition in api_handlers.py find the target date?` (Vector)
6. `Which functions call Sina video downloader?` (Graph)
7. `Explain how export_instance works in crypto_security.py` (Vector)
8. `What does data_pipeline.py import?` (Graph)
9. `How does get_video_url_from_video_id work in file_storage.py?` (Vector)
10. `Show the function relationships in database_ops.py` (Graph)
