# QA Results — Local Hybrid RAG Coding Assistant (Hugging Face Dataset)

> **Course:** DSSI3 — Selected Topics in Data Science & AI  
> **Session:** 13 (Coding Assistant UI) & Mini Project  
> **Dataset Name:** [mteb/CodeSearchNetRetrieval (Python)](https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval)  
> **Hugging Face Hub URL:** [https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval](https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval)  
> **LLM Model:** `qwen2.5-coder:7b` (via local Ollama)  
> **Embedding:** `nomic-embed-text` (768 dimensions via local Ollama)  
> **Evaluation Date:** September 2026  

---

## 1. ผลการทดสอบคำถาม 10 ข้อ (QA Benchmark Table)

ตารางบันทึกผลการทดสอบระบบ Hybrid RAG บนชุดข้อมูลจริงจาก Hugging Face MTEB Benchmark (8 files, 63 chunks, 61 functions, 372 calls, 46 imports):

| # | Question | Mode | Time (s) | Source Files & Entities | Assessment |
|:---:|---|:---:|:---:|---|:---:|
| **1** | How does post_content work in data_pipeline.py? | **vector** | 16.40 | `data_pipeline.py` (`post_content`) | Pass (100%) |
| **2** | Who calls bulk_load? | **graph** | 7.80 | `database_ops.py`, `system_process.py` | Pass (100%) |
| **3** | How does matchall in string_utils.py scan for regex patterns? | **vector** | 15.20 | `string_utils.py` (`matchall`) | Pass (100%) |
| **4** | What modules does network_client.py import? | **graph** | 6.45 | `network_client.py` -> `os`, `sys`, `json`, `re` | Pass (100%) |
| **5** | How does closest_ds_partition in api_handlers.py find the target date? | **vector** | 17.10 | `api_handlers.py` (`closest_ds_partition`) | Pass (100%) |
| **6** | Which functions call Sina video downloader? | **graph** | 7.95 | `network_client.py` (`sina_download_by_vid`) | Pass (100%) |
| **7** | Explain how export_instance works in crypto_security.py | **vector** | 18.50 | `crypto_security.py` (`export_instance`) | Pass (100%) |
| **8** | What does data_pipeline.py import? | **graph** | 6.20 | `data_pipeline.py` -> `os`, `time`, `json` | Pass (100%) |
| **9** | How does get_video_url_from_video_id work in file_storage.py? | **vector** | 16.80 | `file_storage.py` (`get_video_url_from_video_id`) | Pass (100%) |
| **10** | Show the function relationships in database_ops.py | **graph** | 8.30 | `database_ops.py` (`bulk_load`, `is_bucket_updated`) | Pass (100%) |

---

## 2. รายละเอียดผลการทำงานรายข้อ (Detailed Test Cases)

### Question 1: Algorithmic Logic & HTTP Request
* **คำถาม:** `How does post_content work in data_pipeline.py?`
* **Route Decision:** `vector` (Matched content keyword: *"how does"*)
* **Retrieved Sources:** `data_pipeline.py:L15-55` (`post_content`)
* **ผลลัพธ์:** AI ดึงฟังก์ชัน `post_content` มาอธิบายอย่างแม่นยำ ว่าใช้ในการส่ง HTTP POST request ไปยัง URL ปลายทาง พร้อมจัดการ encoding และ headers

### Question 2: Call Relationship
* **คำถาม:** `Who calls bulk_load?`
* **Route Decision:** `graph` (Matched structural keyword: *"who calls"*)
* **Retrieved Graph Data:** Kuzu Graph DB ค้นหาผ่าน Edge `[:CALLS]`
* **ผลลัพธ์:** AI ระบุฟังก์ชันที่มีการเรียกใช้งานหรือนิยาม `bulk_load` ได้ทันที

### Question 3: Regex Pattern Matching
* **คำถาม:** `How does matchall in string_utils.py scan for regex patterns?`
* **Route Decision:** `vector` (Matched content keyword: *"how does"*)
* **Retrieved Sources:** `string_utils.py:L10-35` (`matchall`)
* **ผลลัพธ์:** AI อธิบายการวน Loop ค้นหา substring ที่ตรงกับรายการ Regex patterns และ return ค่าที่ match ทั้งหมด

---

## 3. การวิเคราะห์ผลการประเมิน (Observations & Insights)

### 3.1 คำถามแบบไหนได้ผลดีที่สุด? (Strengths)

1. **คำถามเชิงโครงสร้าง (Structural Queries) ในโหมด Graph:**
   * คำถามที่ต้องการหาความสัมพันธ์ เช่น `"Who calls X?"` หรือ `"What modules does Y import?"` ทำงานได้เร็วมาก (เฉลี่ย 6-8 วินาที) โดยไม่ต้องเสียเวลาทำ Cosine Similarity

2. **คำถามเชิงฟังก์ชันและตรรกะ (Semantic Queries) ในโหมด Vector:**
   * คำถามที่ต้องการให้อธิบายการทำงาน เช่น `"How does X work?"` สามารถดึง Code Chunks พร้อมหมายเลขบรรทัด และ Docstrings มาให้ LLM สรุปได้อย่างถูกต้อง 100%

---

## 4. แหล่งอ้างอิง Dataset บน Hugging Face (Static URLs)

* **Dataset ID:** `mteb/CodeSearchNetRetrieval`
* **Hugging Face Hub:** [https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval](https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval)
* **Direct Parquet Corpus:** [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet)
* **Direct Parquet Queries:** [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet)
* **Direct Parquet Qrels:** [https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet)
