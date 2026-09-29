"""
Hybrid RAG Engine: Vector Search (FAISS) + Code Graph (Kuzu) + Local LLM (Ollama).
Provides intelligent question routing and multi-modal code retrieval.
"""
import os
import sys
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Windows Terminal UTF-8 encoding fix
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import kuzu



class QuestionRouter:
    """
    Intelligent router classifying programming questions into 'graph' (structural)
    or 'vector' (semantic / code content).
    """

    GRAPH_KEYWORDS = [
        # English structural keywords
        "calls", "called by", "calling", "caller", "callee",
        "uses", "used by",
        "imports", "imported by", "import",
        "inherits", "extends", "subclass", "superclass",
        "depends on", "dependency", "dependencies",
        "impact", "impacts", "affects", "affected by",
        "who calls", "what calls", "which functions call",
        "what functions", "which functions", "in which file",
        "where is", "defined in", "relationship", "relationships",
        "call graph", "dependency graph", "hierarchy",
        # Thai structural keywords
        "เรียก", "ถูกเรียก", "ใครเรียก", "ฟังก์ชันไหนเรียก",
        "ใช้", "ถูกใช้",
        "กระทบ", "ผลกระทบ",
        "ความสัมพันธ์", "ขึ้นอยู่กับ", "อ้างอิง",
        "โครงสร้าง", "นำเข้า", "อยู่ที่ไฟล์ไหน",
    ]

    VECTOR_KEYWORDS = [
        "how does", "how to", "explain", "what is", "why does",
        "algorithm", "implement", "example", "write", "generate",
        "syntax", "error", "debug", "refactor", "unit test",
        "ทำงานอย่างไร", "อธิบาย", "เขียนโค้ด", "ตัวอย่าง",
    ]

    def classify(self, question: str) -> str:
        """Classify question into 'graph' or 'vector'."""
        return self.classify_with_reason(question)["route"]

    def classify_with_reason(self, question: str) -> Dict[str, str]:
        """Classify question and return routing decision with explanation."""
        q_lower = question.lower()

        # 1. Match Graph keywords first
        for kw in self.GRAPH_KEYWORDS:
            if kw in q_lower:
                return {
                    "route": "graph",
                    "reason": f"Matched structural keyword: '{kw}'",
                    "question": question,
                }

        # 2. Match Vector keywords
        for kw in self.VECTOR_KEYWORDS:
            if kw in q_lower:
                return {
                    "route": "vector",
                    "reason": f"Matched content keyword: '{kw}'",
                    "question": question,
                }

        # Default fallback to vector search
        return {
            "route": "vector",
            "reason": "Default semantic code search (no explicit graph relationship found)",
            "question": question,
        }


class HybridRAG:
    """
    Unified Hybrid RAG Engine combining FAISS Vector Store, Kuzu Graph DB,
    and Ollama Qwen2.5-Coder model.
    """

    def __init__(
        self,
        vector_db_path: str = "vector_db",
        graph_db_path: str = "graph_db",
        llm_model: str = "qwen2.5-coder:7b",
        embed_model: str = "nomic-embed-text",
        temperature: float = 0.2,
    ):
        self.vector_db_path = vector_db_path
        self.graph_db_path = graph_db_path
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.router = QuestionRouter()

        print(f"[HybridRAG] Initializing with {llm_model} and {embed_model}...")

        # 1. Load Vector DB
        if not Path(vector_db_path).exists():
            raise FileNotFoundError(f"Vector DB directory not found: '{vector_db_path}'. Run setup.py first.")
        
        self.embeddings = OllamaEmbeddings(model=embed_model)
        self.vectorstore = FAISS.load_local(
            vector_db_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        # 2. Connect to Graph DB
        if not Path(graph_db_path).exists():
            raise FileNotFoundError(f"Graph DB directory not found: '{graph_db_path}'. Run setup.py first.")
        
        self.db = kuzu.Database(graph_db_path, read_only=True)
        self.conn = kuzu.Connection(self.db)

        # 3. Initialize LLM
        self.llm = ChatOllama(model=llm_model, temperature=temperature)
        print("[HybridRAG] Engine initialized and ready.")

    def _extract_entity(self, question: str) -> Optional[str]:
        """Extract potential function, class, or module identifier from question text."""
        # Check quoted names like 'calculate_volatility' or `execute_order`
        quoted = re.findall(r"['\"`](\w+)['\"`]", question)
        if quoted:
            return quoted[0]

        # Check snake_case or CamelCase words (excluding common stop words)
        stop_words = {
            "who", "what", "which", "where", "how", "why", "does", "do", "call", "calls",
            "called", "use", "uses", "used", "import", "imports", "imported", "function",
            "class", "module", "file", "method", "system", "code", "python", "the", "this"
        }
        tokens = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", question)
        for token in reversed(tokens):
            if token.lower() not in stop_words and len(token) > 2:
                return token
        return None

    def _vector_query(self, question: str, k: int = 4, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Perform semantic similarity search on vector store and query LLM with conversation history."""
        docs = self.vectorstore.similarity_search(question, k=k)

        context_blocks = []
        doc_metas = []
        for i, d in enumerate(docs, 1):
            meta = d.metadata
            func_name = meta.get("function", "snippet")
            file_name = meta.get("file", "unknown")
            line_no = meta.get("line", "?")
            doc_metas.append({
                "function": func_name,
                "file": file_name,
                "line": line_no,
                "type": meta.get("type", "Code"),
                "code": meta.get("code", d.page_content),
            })
            context_blocks.append(
                f"--- Document [{i}]: {func_name} ({file_name}:{line_no}) ---\n{d.page_content}"
            )

        context_str = "\n\n".join(context_blocks)

        sys_msg = (
            "You are an expert AI Coding Assistant and Software Architect.\n"
            "Answer the question clearly and accurately using the provided codebase context.\n"
            "Always reference the specific files, classes, and functions from the context.\n"
            "If code examples are needed, provide well-formatted, production-quality Python code blocks.\n\n"
            f"Context:\n{context_str}"
        )
        messages = [SystemMessage(content=sys_msg)]
        if history:
            for m in history[-6:]:
                r = m.get("role")
                c = m.get("content", "")
                if r == "user":
                    messages.append(HumanMessage(content=c))
                elif r == "assistant":
                    messages.append(AIMessage(content=c))
        messages.append(HumanMessage(content=question))

        response = self.llm.invoke(messages)

        return {
            "answer": response.content,
            "source": "vector",
            "docs": doc_metas,
            "raw_context": context_str,
        }

    def _graph_query(self, question: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Perform structural Cypher queries on Kuzu graph DB and query LLM with conversation history."""
        entity = self._extract_entity(question)
        q_lower = question.lower()
        graph_results = []
        retrieved_docs = []

        if any(w in q_lower for w in ["call", "calls", "called", "เรียก", "ใช้"]):
            if entity:
                # 1. Who calls this function?
                q1 = (
                    "MATCH (caller:Function)-[:CALLS]->(callee:Function) "
                    "WHERE callee.name ENDS WITH $name "
                    "RETURN caller.name AS caller, callee.name AS callee, caller.file AS file, caller.line AS line"
                )
                df1 = self.conn.execute(q1, {"name": entity}).get_as_df()
                if not df1.empty:
                    graph_results.append(f"Functions CALLING '{entity}':\n{df1.to_string(index=False)}")
                    for _, row in df1.iterrows():
                        if row["file"]:
                            retrieved_docs.append({
                                "function": row["caller"],
                                "file": row["file"],
                                "line": row["line"],
                                "type": "Caller",
                                "code": f"# Caller function: {row['caller']}",
                            })

                # 2. What does this function call?
                q2 = (
                    "MATCH (caller:Function)-[:CALLS]->(callee:Function) "
                    "WHERE caller.name ENDS WITH $name "
                    "RETURN caller.name AS caller, callee.name AS callee, caller.file AS file, caller.line AS line"
                )
                df2 = self.conn.execute(q2, {"name": entity}).get_as_df()
                if not df2.empty:
                    graph_results.append(f"Functions CALLED BY '{entity}':\n{df2.to_string(index=False)}")
                    for _, row in df2.iterrows():
                        if row["file"]:
                            retrieved_docs.append({
                                "function": row["caller"],
                                "file": row["file"],
                                "line": row["line"],
                                "type": "CalleeHost",
                                "code": f"# Host function: {row['caller']} calls {row['callee']}",
                            })

        # 3. Check Module imports and dependencies
        if any(w in q_lower for w in ["import", "imports", "depend", "dependency", "นำเข้า", "ขึ้นอยู่กับ"]):
            if entity:
                q3 = (
                    "MATCH (m:Module)-[:IMPORTS]->(dep:Module) "
                    "WHERE m.name = $name OR dep.name = $name "
                    "RETURN m.name AS module, dep.name AS dependency"
                )
                df3 = self.conn.execute(q3, {"name": entity}).get_as_df()
                if not df3.empty:
                    graph_results.append(f"Module import relationships for '{entity}':\n{df3.to_string(index=False)}")
            else:
                q3 = "MATCH (m:Module)-[:IMPORTS]->(dep:Module) WHERE m.filepath <> '' RETURN m.name AS module, dep.name AS dependency LIMIT 25"
                df3 = self.conn.execute(q3).get_as_df()
                if not df3.empty:
                    graph_results.append(f"Overall Module Imports:\n{df3.to_string(index=False)}")

        # 4. Check Class definitions
        if any(w in q_lower for w in ["class", "classes", "คลาส"]):
            q4 = "MATCH (c:Class)-[:CLASS_DEFINED_IN]->(m:Module) RETURN c.name AS class_name, m.name AS module, c.file AS file, c.line AS line LIMIT 25"
            df4 = self.conn.execute(q4).get_as_df()
            if not df4.empty:
                graph_results.append(f"Class Definitions:\n{df4.to_string(index=False)}")

        # Fallback if no specific relation matched
        if not graph_results:
            q_fallback = (
                "MATCH (a:Function)-[:CALLS]->(b:Function) "
                "WHERE a.file <> '' "
                "RETURN a.name AS caller, b.name AS callee "
                "LIMIT 20"
            )
            df_fallback = self.conn.execute(q_fallback).get_as_df()
            if not df_fallback.empty:
                graph_results.append(f"Sample Call Relationships in codebase:\n{df_fallback.to_string(index=False)}")
            else:
                graph_results.append("No direct graph relationships found matching query.")

        graph_context = "\n\n".join(graph_results)

        # Also supplement with semantic search for entity code if found
        if entity:
            semantic_supplement = self.vectorstore.similarity_search(entity, k=2)
            for d in semantic_supplement:
                retrieved_docs.append({
                    "function": d.metadata.get("function", entity),
                    "file": d.metadata.get("file", ""),
                    "line": d.metadata.get("line", 1),
                    "type": d.metadata.get("type", "CodeSnippet"),
                    "code": d.metadata.get("code", d.page_content),
                })

        sys_msg = (
            "You are a Software Architecture and Code Structure Assistant.\n"
            "Answer the question using the extracted Code Graph relationships.\n"
            "Explain the calling relationships, dependencies, and file structural flow clearly.\n"
            "If functions or modules call each other, explain the interaction pipeline step-by-step.\n\n"
            f"Graph Data:\n{graph_context}"
        )
        messages = [SystemMessage(content=sys_msg)]
        if history:
            for m in history[-6:]:
                r = m.get("role")
                c = m.get("content", "")
                if r == "user":
                    messages.append(HumanMessage(content=c))
                elif r == "assistant":
                    messages.append(AIMessage(content=c))
        messages.append(HumanMessage(content=question))

        response = self.llm.invoke(messages)

        return {
            "answer": response.content,
            "source": "graph",
            "docs": retrieved_docs,
            "graph_context": graph_context,
        }

    def direct_chat(
        self,
        question: str,
        history: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Direct chat with LLM with multi-turn conversational memory (without RAG).
        """
        t0 = time.time()
        sys_msg = system_prompt or (
            "You are a helpful, knowledgeable, and polite AI assistant. "
            "Maintain conversational context from previous messages and answer questions clearly."
        )
        messages = [SystemMessage(content=sys_msg)]
        if history:
            for m in history[-10:]:
                r = m.get("role")
                c = m.get("content", "")
                if r == "user":
                    messages.append(HumanMessage(content=c))
                elif r == "assistant":
                    messages.append(AIMessage(content=c))
        messages.append(HumanMessage(content=question))

        response = self.llm.invoke(messages)
        elapsed = round(time.time() - t0, 2)

        return {
            "answer": response.content,
            "source": "general_chat",
            "elapsed": elapsed,
            "reason": "Direct LLM (General Chat with Memory)",
            "docs": [],
            "graph_context": "",
            "question": question,
        }

    def query(
        self,
        question: str,
        force_route: Optional[str] = None,
        k: int = 4,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Main query entrypoint.
        Routes question to Vector or Graph retriever, queries Ollama with conversation history.
        """
        t0 = time.time()

        if force_route in ("vector", "graph"):
            route = force_route
            routing_reason = f"Manually overridden to '{force_route}'"
        else:
            routing_info = self.router.classify_with_reason(question)
            route = routing_info["route"]
            routing_reason = routing_info["reason"]

        if route == "graph":
            res = self._graph_query(question, history=history)
        else:
            res = self._vector_query(question, k=k, history=history)

        elapsed = round(time.time() - t0, 2)
        res["elapsed"] = elapsed
        res["reason"] = routing_reason
        res["question"] = question
        return res


