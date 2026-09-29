# Local Hybrid RAG Coding Assistant (Vector + Graph)
> **Mini Project — DSSI3: Selected Topics in Data Science & AI**  
> **Topic:** LLM for Code Generation & Understanding with Web UI (Local Hybrid RAG Engine)

---

## สรุปภาพรวมของ Mini Project (Project Summary)

โครงงานนี้คือการพัฒนาระบบ **AI Coding Assistant** ที่รันบนเครื่อง Local 100% (ข้อมูลโค้ดไม่รั่วไหล ปลอดภัย และไม่มีค่าใช้จ่าย API) โดยใช้สถาปัตยกรรม **Hybrid RAG** ผสานระหว่าง:
1. **Vector Retrieval (FAISS + nomic-embed-text):** สกัดและค้นหาความหมายเชิงบริบท (Semantic Code Search), คำอธิบายการทำงานของอัลกอริทึม และตรรกะภายในฟังก์ชัน
2. **Graph Retrieval (Kuzu Graph DB + AST):** สกัดโครงสร้างความสัมพันธ์ของโค้ด (Structural Relationships) เช่น ฟังก์ชันไหนเรียกฟังก์ชันไหน (CALLS), โมดูลไหนเชื่อมโยงกัน (IMPORTS), คลาสถูกนิยามที่ใด (DEFINED_IN)
3. **Question Router:** ตัวจำแนกประเภทคำถามอัตโนมัติ เพื่อเลือกเส้นทางการดึงข้อมูลที่เหมาะสมที่สุด
4. **Local LLM (qwen2.5-coder:7b):** โมเดลสำหรับวิเคราะห์ สรุป และสร้างโค้ดที่มีประสิทธิภาพสูง
5. **Streamlit Web UI:** หน้าจอแชทสำหรับรับ Prompt ที่รองรับการแสดงผลการตัดสินใจของ Router, เวลาประมวลผล (Response Time), และ Source Code Snippet พร้อมหมายเลขบรรทัดอ้างอิง
6. **Dual Chat Modes:** มีปุ่มสลับโหมดระหว่าง **Codebase RAG** (ค้นหาและวิเคราะห์โค้ด) และ **General Chat** (พูดคุยทั่วไปหรือถามความรู้พื้นฐานกับ LLM โดยตรงโดยไม่ต้องสืบค้น Codebase)


---



---

## โครงสร้างโปรเจกต์และชุดข้อมูลทดสอบ (Online Dataset)

### ข้อมูลที่มาของ Dataset จาก Hugging Face พร้อม Static Links
โปรเจกต์นี้ใช้ชุดข้อมูล Benchmark ระดับโลกจาก Hugging Face Hub:
* **Hugging Face Hub:** [mteb/CodeSearchNetRetrieval](https://huggingface.co/datasets/mteb/CodeSearchNetRetrieval)
* **Dataset Type:** MTEB Benchmark for Text & Code Retrieval (Python Subset)
* **Direct Corpus Parquet (Static):** [0.parquet (Corpus)](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-corpus/test/0.parquet)
* **Direct Queries Parquet (Static):** [0.parquet (Queries)](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-queries/test/0.parquet)
* **Direct Qrels Parquet (Static):** [0.parquet (Qrels)](https://huggingface.co/api/datasets/mteb/CodeSearchNetRetrieval/parquet/python-qrels/test/0.parquet)

```text
mini_project/
├── online_dataset/                # [Hugging Face Dataset] mteb/CodeSearchNetRetrieval
│   └── src/codesearchnet/         # 8 โมดูล Python โครงสร้างจริงที่ดึงจาก Hugging Face
│
├── vector_db/                     # FAISS Vector Index (63 Chunks ฝังด้วย nomic-embed-text)
├── graph_db                       # Kuzu Graph DB (61 Functions, 372 Calls, 46 Imports)
│
├── fetch_hf_dataset.py            # สคริปต์ดาวน์โหลดข้อมูลจาก Hugging Face Parquet API
├── ast_parser.py                  # AST Parser สกัด Function, Calls, Imports ลง Kuzu
├── hybrid_rag.py                  # Engine หลัก: QuestionRouter, Vector/Graph Retriever, Ollama
├── setup.py                       # สคริปต์ Index Codebase ครั้งเดียวลง Disk พร้อมบันทึก Metadata
├── app.py                         # Streamlit Chat UI รองรับโหมด Vector/Graph และแสดง Sources
│
├── test_dataset.md                # เอกสารชุดข้อมูลทดสอบ 10 Test Cases และผลการประเมิน
├── hw13_qa_results.md             # ตารางประเมินผล QA Results 10 ข้อพร้อมการวิเคราะห์ (Session 13)
├── hw13_qa_results.csv            # ตารางสรุปผลทดสอบรูปแบบ CSV สำหรับเปิดใน Excel / Sheets
├── questions_for_demo.txt         # ไฟล์รวมคำถามพร้อมก๊อปปี้ไปวางเทสหน้าเว็บ
├── requirements.txt               # รายการ Dependencies ทั้งหมด
├── run.bat                        # สคริปต์คลิกเดียวเปิดแอปบน Windows
└── README.md                      # คู่มือโปรเจกต์และการนำเสนอ
```

---

## ความต้องการของระบบ (Prerequisites & Installation)

### 1. ติดตั้ง Ollama และดึงโมเดลที่จำเป็น
```bash
# ตรวจสอบการทำงานของ Ollama
ollama serve

# ดึงโมเดล Local LLM และ Embedding
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
```

### 2. ติดตั้ง Python Dependencies
```bash
pip install -r requirements.txt
```

---

## วิธีการรันระบบ (How to Run)

### ขั้นตอนที่ 1: สแกนและเตรียมฐานข้อมูล (Index Codebase)
รันคำสั่งด้านล่างเพียงครั้งเดียว ระบบจะแปลงโค้ดใน `online_dataset/src/requests` เป็นทั้ง Vector Store และ Code Graph:
```bash
python setup.py --project ./online_dataset/src/requests
```
*ตัวอย่างผลลัพธ์:*
* สแกนพบ 18 ไฟล์ Python
* บันทึก 287 Code Chunks ลง `vector_db/`
* บันทึก 221 ฟังก์ชัน, 44 คลาส, 730 ความสัมพันธ์ Call, และ 133 Imports ลง `graph_db`

### ขั้นตอนที่ 2: เปิดหน้าต่างแอปพลิเคชัน (Streamlit UI)
สามารถเปิดแอปได้ 2 วิธี:
* **วิธีที่ 1 (สะดวกที่สุด):** ดับเบิ้ลคลิกไฟล์ `run.bat`
* **วิธีที่ 2:** รันคำสั่งผ่าน Command Line:
```bash
python -m streamlit run app.py
```
เปิดเบราว์เซอร์ไปที่: `http://localhost:8501`

---
