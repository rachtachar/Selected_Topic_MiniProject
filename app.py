"""
Streamlit Coding Assistant UI — Powered by HybridRAG (Vector + Graph) & Local LLM.
Run:
    python -m streamlit run app.py
"""
import os
import sys
import time
import json
from pathlib import Path

# Windows Terminal UTF-8 encoding fix
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import streamlit as st

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Coding Assistant | Hybrid RAG",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS Styling ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    .badge-vector {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #0284c7;
        color: white;
    }
    .badge-graph {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #7c3aed;
        color: white;
    }
    .badge-general {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #059669;
        color: white;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ─── Cached Engine Loader ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initializing HybridRAG Engine (Vector + Graph)...")
def get_hybrid_rag(llm_model: str, temperature: float, version: str = "v5_hf_codesearchnet"):
    """
    Load HybridRAG instance once per Streamlit server session.
    Avoids expensive re-initialization on every user interaction.
    """
    try:
        import importlib
        import hybrid_rag
        importlib.reload(hybrid_rag)
        from hybrid_rag import HybridRAG
        return HybridRAG(
            vector_db_path="vector_db",
            graph_db_path="graph_db",
            llm_model=llm_model,
            embed_model="nomic-embed-text",
            temperature=temperature,
        ), None
    except Exception as e:
        return None, str(e)



# ─── Load Metadata if exists ──────────────────────────────────────────────────
metadata = {}
meta_file = Path("index_metadata.json")
if meta_file.exists():
    try:
        metadata = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception:
        pass


# ─── Session State Initialization ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_count" not in st.session_state:
    st.session_state.query_count = 0

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## AI Coding Assistant")
    st.markdown("Local RAG for Source Code & General Chat")
    st.markdown("---")

    # Mode Switcher: RAG vs General Chat
    st.markdown("### Chat Mode")
    assistant_mode = st.radio(
        "Select Assistant Mode",
        options=["Codebase RAG", "General Chat"],
        index=0,
        horizontal=True,
    )

    is_rag_mode = (assistant_mode == "Codebase RAG")

    st.markdown("---")

    # Engine Settings
    st.markdown("### Engine Settings")
    selected_model = st.selectbox(
        "LLM Model",
        options=["qwen2.5-coder:7b", "llama3.1:8b", "qwen2.5:14b"],
        index=0,
    )
    temp_val = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)

    force_route = None
    top_k = 4
    if is_rag_mode:
        mode_choice = st.radio(
            "RAG Routing Strategy",
            options=["Auto (Hybrid Router)", "Vector Search Only", "Graph DB Only"],
            index=0,
        )
        mode_map = {
            "Auto (Hybrid Router)": None,
            "Vector Search Only": "vector",
            "Graph DB Only": "graph",
        }
        force_route = mode_map[mode_choice]
        top_k = st.slider("Context Chunks (k)", 1, 8, 4)
    else:
        st.info("General Chat Mode is active. Responses come directly from LLM without querying codebase.")

    st.markdown("---")

    # Codebase & Dataset Management
    st.markdown("### Codebase / Dataset")
    dataset_presets = {
        "CodeSearchNet (Hugging Face)": "./online_dataset/src/codesearchnet",
        "Requests Library (GitHub v2.32.3)": "./online_dataset/src/requests",
        "Custom Directory Path": "custom",
    }
    
    current_proj_path = metadata.get("project_path", "")
    default_ds_idx = 0
    if "requests" in current_proj_path.lower():
        default_ds_idx = 1

    selected_dataset = st.selectbox(
        "Choose Codebase to Index",
        options=list(dataset_presets.keys()),
        index=default_ds_idx,
    )

    target_codebase_dir = dataset_presets[selected_dataset]
    if target_codebase_dir == "custom":
        target_codebase_dir = st.text_input("Enter directory path:", value="./online_dataset/src")

    if st.button("Read & Index Codebase", use_container_width=True):
        if not Path(target_codebase_dir).exists():
            st.error(f"Directory not found: '{target_codebase_dir}'")
        else:
            with st.spinner(f"Reading & indexing '{Path(target_codebase_dir).name}' into Vector + Graph DB..."):
                try:
                    get_hybrid_rag.clear()
                    from setup import run_setup
                    new_meta = run_setup(target_codebase_dir)
                    st.success(f"Indexed {new_meta.get('files_count', '?')} files successfully!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error during indexing: {ex}")

    st.markdown("---")

    # Codebase Index Status
    st.markdown("### Index Statistics")
    v_ok = Path("vector_db").exists()
    g_ok = Path("graph_db").exists()

    col1, col2 = st.columns(2)
    with col1:
        v_status = "<span style='color:#4ade80; font-weight:600;'>[Ready]</span>" if v_ok else "<span style='color:#f87171;'>[Missing]</span>"
        st.markdown(f"<div class='metric-card'><b>Vector DB</b><br>{v_status}</div>", unsafe_allow_html=True)
    with col2:
        g_status = "<span style='color:#4ade80; font-weight:600;'>[Ready]</span>" if g_ok else "<span style='color:#f87171;'>[Missing]</span>"
        st.markdown(f"<div class='metric-card'><b>Graph DB</b><br>{g_status}</div>", unsafe_allow_html=True)

    if metadata:
        with st.expander("Codebase Details", expanded=False):
            st.markdown(f"**Target:** `{Path(metadata.get('project_path', '')).name}`")
            st.markdown(f"**Files:** `{metadata.get('files_count', '?')}` files")
            st.markdown(f"**Chunks:** `{metadata.get('chunks_count', '?')}` vectors")
            g_stats = metadata.get("graph_stats", {})
            st.markdown(f"**Functions:** `{g_stats.get('functions', '?')}`")
            st.markdown(f"**Classes:** `{g_stats.get('classes', '?')}`")
            st.markdown(f"**Calls:** `{g_stats.get('calls', '?')}` relations")
            st.markdown(f"**Imports:** `{g_stats.get('imports', '?')}` relations")
            st.caption(f"Indexed at: {metadata.get('indexed_at', '?')}")

    # Session Statistics (Session 13 Feature 3)
    user_queries = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    assistant_times = [
        m.get("metadata", {}).get("elapsed", 0.0)
        for m in st.session_state.messages
        if m["role"] == "assistant" and "metadata" in m and m.get("metadata", {}).get("elapsed")
    ]
    avg_elapsed = (sum(assistant_times) / len(assistant_times)) if assistant_times else 0.0

    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric("Total Queries", max(st.session_state.query_count, len(user_queries)))
    with stat_col2:
        st.metric("Avg Time", f"{avg_elapsed:.2f}s")

    # Search History
    if user_queries:
        with st.expander(f"Search History ({len(user_queries)})", expanded=False):
            for idx, q_text in enumerate(user_queries, 1):
                st.markdown(f"**{idx}.** {q_text}")

    # Export Chat to Markdown (Session 13 Feature 3)
    if st.session_state.messages:
        export_lines = ["# Coding Assistant - Conversation Export\n\n"]
        for m in st.session_state.messages:
            role_name = "User" if m["role"] == "user" else "Assistant"
            export_lines.append(f"### {role_name}\n\n{m['content']}\n\n")
            if m.get("metadata"):
                meta = m["metadata"]
                export_lines.append(f"> Mode: `{meta.get('source', '')}` | Elapsed: `{meta.get('elapsed', 0)}s` | Router: {meta.get('reason', '')}\n\n")
        export_md = "".join(export_lines)
        st.download_button(
            label="Export Conversation (.md)",
            data=export_md,
            file_name="coding_assistant_chat.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")

    # Quick Prompts
    st.markdown("### Quick Test Prompts")
    if is_rag_mode:
        if "requests" in current_proj_path.lower():
            sample_prompts = [
                "How does PreparedRequest.prepare_url work in models.py?",
                "Who calls Session.send?",
                "What modules does sessions.py import?",
                "How does HTTPBasicAuth format Authorization header in auth.py?",
                "Write a custom BearerTokenAuth class inheriting from AuthBase",
            ]
        else:
            sample_prompts = [
                "How does post_content work in data_pipeline.py?",
                "Who calls bulk_load?",
                "What modules does network_client.py import?",
                "How does matchall in string_utils.py scan for regex patterns?",
                "Write a custom data loader function using bulk_load",
            ]
    else:
        sample_prompts = [
            "Explain the difference between mutable and immutable in Python",
            "What are Python decorators and how do they work?",
            "How does HTTPS encryption and handshake work?",
            "Write a binary search algorithm in Python",
            "What are Python generators and the yield keyword?",
        ]

    for p in sample_prompts:
        if st.button(p, key=f"btn_{p}", use_container_width=True):
            st.session_state.quick_prompt = p
            st.rerun()

    st.markdown("---")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.session_state.quick_prompt = None
        st.rerun()


# ─── Main Interface Header ────────────────────────────────────────────────────
header_title = "Hybrid RAG Coding Assistant" if is_rag_mode else "General AI Chat Assistant"
header_sub = (
    "Combines Semantic Vector Search (FAISS) + Structural Code Graph (Kuzu) + Local Qwen2.5-Coder"
    if is_rag_mode else
    "Direct conversation with Local LLM for general programming, logic, and technical questions"
)

st.markdown(f'<div class="main-header">{header_title}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{header_sub}</div>', unsafe_allow_html=True)

# Load engine
rag, load_err = get_hybrid_rag(selected_model, temp_val, version="v5_hf_codesearchnet")

if load_err or rag is None:
    st.error(f"[Error] Failed to initialize Engine: {load_err}")
    st.info("Run 'python setup.py --project ./online_dataset/src/requests' to build indices first, and ensure 'ollama serve' is running.")
    st.stop()


# ─── Render Chat History ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("metadata"):
            meta = msg["metadata"]
            source = meta.get("source", "vector")
            elapsed = meta.get("elapsed", 0.0)
            reason = meta.get("reason", "")
            docs = meta.get("docs", [])
            graph_ctx = meta.get("graph_context", "")

            # Badge styling based on mode
            if source == "graph":
                badge_class = "badge-graph"
                badge_label = "[Graph Mode]"
            elif source == "general_chat":
                badge_class = "badge-general"
                badge_label = "[General Chat]"
            else:
                badge_class = "badge-vector"
                badge_label = "[Vector Mode]"

            st.markdown(
                f'<span class="{badge_class}">{badge_label}</span> &nbsp; '
                f'<span style="color:#94a3b8; font-size:0.85rem;">Time: {elapsed}s &nbsp;|&nbsp; <em>{reason}</em></span>',
                unsafe_allow_html=True,
            )

            # Sources Expander (if RAG retrieved any)
            if docs or graph_ctx:
                expander_title = f"Retrieved References & Sources ({len(docs)} items)"
                with st.expander(expander_title):
                    if graph_ctx:
                        st.markdown("**Graph Relational Context:**")
                        st.code(graph_ctx, language="text")

                    for i, d in enumerate(docs, 1):
                        f_name = d.get("function", "N/A")
                        f_path = d.get("file", "N/A")
                        l_num = d.get("line", "?")
                        d_type = d.get("type", "Snippet")
                        code_body = d.get("code", "")

                        st.markdown(f"**[{i}] {d_type}: `{f_name}`** (`{Path(f_path).name}:{l_num}`)")
                        st.caption(f"Path: `{f_path}`")
                        if code_body:
                            st.code(code_body, language="python")


# ─── Chat Input Handler ───────────────────────────────────────────────────────
input_placeholder = (
    "Ask about codebase (e.g. algorithms, who calls what, functions)..."
    if is_rag_mode else
    "Ask any general programming or conversational question..."
)
prompt = st.chat_input(input_placeholder)

# If quick prompt was clicked, use it
if st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if prompt:
    # 1. Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Query engine (RAG vs Direct Chat) with Conversational Memory
    with st.chat_message("assistant"):
        spinner_msg = (
            "Analyzing codebase (Vector + Graph) and generating answer..."
            if is_rag_mode else
            "Generating answer from LLM..."
        )
        # Prior chat messages for multi-turn conversational context
        prev_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        with st.spinner(spinner_msg):
            try:
                if is_rag_mode:
                    res = rag.query(prompt, force_route=force_route, k=top_k, history=prev_history)
                else:
                    if hasattr(rag, "direct_chat"):
                        res = rag.direct_chat(prompt, history=prev_history)
                    else:
                        t0 = time.time()
                        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                        sys_msg = (
                            "You are a helpful, knowledgeable, and polite AI assistant. "
                            "Maintain conversational context from previous messages and answer questions clearly."
                        )
                        messages = [SystemMessage(content=sys_msg)]
                        for m in prev_history[-10:]:
                            r = m.get("role")
                            c = m.get("content", "")
                            if r == "user":
                                messages.append(HumanMessage(content=c))
                            elif r == "assistant":
                                messages.append(AIMessage(content=c))
                        messages.append(HumanMessage(content=prompt))
                        resp = rag.llm.invoke(messages)
                        res = {
                            "answer": resp.content,
                            "source": "general_chat",
                            "elapsed": round(time.time() - t0, 2),
                            "reason": "Direct LLM (General Chat with Memory)",
                            "docs": [],
                            "graph_context": "",
                            "question": prompt,
                        }



                answer = res.get("answer", "No answer generated.")
                source = res.get("source", "vector")
                elapsed = res.get("elapsed", 0.0)
                reason = res.get("reason", "")
                docs = res.get("docs", [])
                graph_ctx = res.get("graph_context", "")

                st.markdown(answer)

                if source == "graph":
                    badge_class = "badge-graph"
                    badge_label = "[Graph Mode]"
                elif source == "general_chat":
                    badge_class = "badge-general"
                    badge_label = "[General Chat]"
                else:
                    badge_class = "badge-vector"
                    badge_label = "[Vector Mode]"

                st.markdown(
                    f'<span class="{badge_class}">{badge_label}</span> &nbsp; '
                    f'<span style="color:#94a3b8; font-size:0.85rem;">Time: {elapsed}s &nbsp;|&nbsp; <em>{reason}</em></span>',
                    unsafe_allow_html=True,
                )

                if docs or graph_ctx:
                    with st.expander(f"Retrieved References & Sources ({len(docs)} items)"):
                        if graph_ctx:
                            st.markdown("**Graph Relational Context:**")
                            st.code(graph_ctx, language="text")

                        for i, d in enumerate(docs, 1):
                            f_name = d.get("function", "N/A")
                            f_path = d.get("file", "N/A")
                            l_num = d.get("line", "?")
                            d_type = d.get("type", "Snippet")
                            code_body = d.get("code", "")

                            st.markdown(f"**[{i}] {d_type}: `{f_name}`** (`{Path(f_path).name}:{l_num}`)")
                            st.caption(f"Path: `{f_path}`")
                            if code_body:
                                st.code(code_body, language="python")

                # 3. Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "metadata": {
                        "source": source,
                        "elapsed": elapsed,
                        "reason": reason,
                        "docs": docs,
                        "graph_context": graph_ctx,
                    }
                })
                st.session_state.query_count += 1
                st.rerun()

            except Exception as e:
                err_msg = f"[Error] Error processing query: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                    "metadata": {"source": "error", "elapsed": 0.0, "reason": str(e), "docs": []}
                })
                st.session_state.query_count += 1
                st.rerun()
