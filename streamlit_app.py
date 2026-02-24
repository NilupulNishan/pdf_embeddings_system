"""
Streamlit UI for Production-grade PDF Query System
- Select collection (single/all)
- Chat interface
- Show sources (nice UI with clickable page chips)
- Optional: Build/refresh index by running processing pipeline
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Optional, Any, Dict, List

import streamlit as st

# ------------------------------------------------------------
# Path setup (same idea as your scripts)
# ------------------------------------------------------------
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ------------------------------------------------------------
# Your imports
# ------------------------------------------------------------
from src.retriever import SmartRetriever, MultiCollectionRetriever
from src.storage_manager import StorageManager
from src.source_formatter import SourceFormatter

try:
    from scripts.process_pdfs import main as process_main
    HAS_PROCESSOR = True
except Exception:
    HAS_PROCESSOR = False

# ------------------------------------------------------------
# Logging (quiet UI)
# ------------------------------------------------------------
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Page config + light UI tweaks
# ------------------------------------------------------------
st.set_page_config(
    page_title="PDF Query System",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      /* keep it clean + light */
      .block-container { padding-top: 1.2rem; }
      [data-testid="stSidebar"] { width: 340px; }
      .stChatMessage { border-radius: 14px; }

      /* sources UI */
      .src-wrap { margin-top: 0.25rem; }
      .src-card {
        border: 1px solid rgba(49, 51, 63, 0.12);
        background: rgba(255, 255, 255, 0.85);
        border-radius: 14px;
        padding: 12px 14px;
        margin: 10px 0;
      }
      .src-head {
        display:flex; align-items:center; justify-content:space-between;
        gap: 10px;
        margin-bottom: 8px;
      }
      .src-title {
        font-weight: 650;
        font-size: 0.98rem;
        line-height: 1.2;
      }
      .src-meta {
        font-size: 0.85rem;
        opacity: 0.75;
        white-space: nowrap;
      }
      .src-chips { display:flex; flex-wrap:wrap; gap: 8px; margin-top: 6px; }
      .src-chip {
        display:inline-flex;
        align-items:center;
        gap: 6px;
        border: 1px solid rgba(49, 51, 63, 0.16);
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 0.88rem;
        text-decoration: none !important;
        color: inherit !important;
        background: rgba(255, 255, 255, 0.9);
      }
      .src-chip:hover { border-color: rgba(49, 51, 63, 0.30); }
      .src-chip small { opacity: 0.7; font-size: 0.8rem; }
      .src-linkcode {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        font-size: 0.78rem;
        opacity: 0.75;
        margin-top: 8px;
        overflow-wrap: anywhere;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def get_collections() -> list[str]:
    sm = StorageManager()
    return sm.list_collections()


def init_retriever(selected: Optional[str]):
    """
    selected:
      - None => MultiCollectionRetriever
      - str  => SmartRetriever(collection)
    """
    if selected:
        return SmartRetriever(selected, verbose=False)
    return MultiCollectionRetriever(verbose=False)


def run_query(retriever: Any, query: str):
    """
    Mirrors your CLI logic:
      - MultiCollectionRetriever => query_best
      - SmartRetriever => query
    """
    if isinstance(retriever, MultiCollectionRetriever):
        return retriever.query_best(query)
    return retriever.query(query)


def get_sources_json(formatter: SourceFormatter, response) -> Dict[str, Any]:
    """
    Preferred: structured sources for Streamlit UI.
    """
    try:
        return formatter.format_for_json(response.source_nodes)
    except Exception:
        return {
            "filename": "unknown.pdf",
            "total_pages_referenced": 0,
            "page_ranges": [],
            "has_links": False,
        }


def render_sources_from_json(src: Dict[str, Any], *, title: str = "Sources"):
    """
    Render sources as a clean card with clickable 'page chips' from already-built JSON.
    """
    filename = src.get("filename") or "unknown.pdf"
    ranges: List[Dict[str, Any]] = src.get("page_ranges") or []
    total_pages = src.get("total_pages_referenced", 0)
    has_links = bool(src.get("has_links"))

    if not ranges:
        st.info("No page information available for this answer.")
        return

    st.markdown('<div class="src-wrap">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="src-card">
          <div class="src-head">
            <div class="src-title">📄 {title}: {filename}</div>
            <div class="src-meta">{total_pages} page(s){' • clickable' if has_links else ''}</div>
          </div>
          <div class="src-chips">
        """,
        unsafe_allow_html=True,
    )

    for r in ranges:
        page_text = r.get("page_text", "Page")
        link = r.get("link")

        if link:
            st.markdown(
                f'<a class="src-chip" href="{link}" target="_blank">🔗 {page_text}</a>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="src-chip">📄 {page_text} <small>(no link)</small></span>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # Optional raw links (handy if link opening is blocked)
    if has_links:
        raw_links = [r.get("link") for r in ranges if r.get("link")]
        raw_links = [l for l in raw_links if l]
        if raw_links:
            joined = "<br/>".join(raw_links[:6])
            st.markdown(f'<div class="src-linkcode">{joined}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close card
    st.markdown("</div>", unsafe_allow_html=True)  # close wrap


def ensure_state():
    if "collections" not in st.session_state:
        st.session_state.collections = []
    if "selected_collection" not in st.session_state:
        st.session_state.selected_collection = None  # None = ALL
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "formatter" not in st.session_state:
        st.session_state.formatter = SourceFormatter()
    if "messages" not in st.session_state:
        # list[{"role": "user"|"assistant", "content": str, "sources_json": dict|None}]
        st.session_state.messages = []


def load_or_refresh_collections():
    try:
        st.session_state.collections = get_collections()
        return True, None
    except Exception as e:
        logger.error("Failed to list collections", exc_info=True)
        return False, str(e)


def rebuild_retriever():
    try:
        st.session_state.retriever = init_retriever(st.session_state.selected_collection)
        return True, None
    except Exception as e:
        logger.error("Failed to init retriever", exc_info=True)
        return False, str(e)


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
ensure_state()

# Sidebar
with st.sidebar:
    st.title("📘 PDF Query System")
    st.caption("Production UI (Collections + RAG Query)")

    colA, colB = st.columns(2)
    with colA:
        if st.button("🔄 Refresh", use_container_width=True):
            ok, err = load_or_refresh_collections()
            if ok:
                st.success("Collections refreshed.")
            else:
                st.error(f"Failed to refresh: {err}")

    with colB:
        if HAS_PROCESSOR:
            if st.button("🧱 Build Index", use_container_width=True):
                with st.spinner("Processing PDFs and building embeddings..."):
                    try:
                        code = process_main()  # runs your pipeline
                        if code == 0:
                            st.success("Index build complete.")
                        else:
                            st.warning("Index build finished with warnings/errors. Check logs.")
                    except Exception as e:
                        st.error(f"Index build failed: {e}")

                # After building, refresh collections + retriever
                ok, _ = load_or_refresh_collections()
                if ok:
                    if (
                        st.session_state.selected_collection is not None
                        and st.session_state.selected_collection not in st.session_state.collections
                    ):
                        st.session_state.selected_collection = None
                    rebuild_retriever()
        else:
            st.button("🧱 Build Index", use_container_width=True, disabled=True)
            st.caption("Enable: import your processing pipeline main() in this file.")

    st.divider()

    # Load collections if empty
    if not st.session_state.collections:
        ok, err = load_or_refresh_collections()
        if not ok:
            st.error("Error accessing database.")
            st.code(err or "Unknown error")
            st.info("Run your processing pipeline first: `python scripts/process_pdfs.py`")
            st.stop()

    if not st.session_state.collections:
        st.warning("No collections found.")
        st.info("Run: `python scripts/process_pdfs.py` then refresh.")
        st.stop()

    # Collection select (ALL + individual)
    options = ["Search ALL collections"] + st.session_state.collections
    current = 0
    if st.session_state.selected_collection in st.session_state.collections:
        current = 1 + st.session_state.collections.index(st.session_state.selected_collection)

    selection = st.selectbox(
        "Collection",
        options=options,
        index=current,
        help="Choose a single collection or search across all collections.",
    )

    new_selected = None if selection == "Search ALL collections" else selection

    if new_selected != st.session_state.selected_collection or st.session_state.retriever is None:
        st.session_state.selected_collection = new_selected
        ok, err = rebuild_retriever()
        if ok:
            st.success(f"Connected: {new_selected}" if new_selected else "Connected: ALL collections")
        else:
            st.error(f"Failed to initialize retriever: {err}")
            st.stop()

    st.divider()
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.success("Cleared chat history.")


# Main area header
title_left, title_right = st.columns([0.75, 0.25])
with title_left:
    st.markdown("## 💬 Ask your PDFs")
    if st.session_state.selected_collection:
        st.caption(f"Searching in: **{st.session_state.selected_collection}**")
    else:
        st.caption("Searching in: **ALL collections**")

with title_right:
    st.markdown("")
    st.markdown("")

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources_json"):
            with st.expander("Sources", expanded=False):
                render_sources_from_json(msg["sources_json"])


# Chat input
query = st.chat_input("Type your question… (e.g., 'How do I reset the device?')")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    # Run retrieval
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                response = run_query(st.session_state.retriever, query)

                if getattr(response, "retrieval_successful", False):
                    answer = getattr(response, "answer", "")
                    st.markdown(answer if answer else "_(No answer text returned.)_")

                    # If multi-collection response has collection name, show it
                    coll_name = getattr(response, "collection_name", None)
                    if coll_name and st.session_state.selected_collection is None:
                        st.caption(f"Best match from: **{coll_name}**")

                    sources_json = get_sources_json(st.session_state.formatter, response)

                    with st.expander("Sources", expanded=False):
                        render_sources_from_json(sources_json)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources_json": sources_json}
                    )
                else:
                    err = getattr(response, "error_message", "Unknown error")
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ {err}"})

            except Exception as e:
                logger.error("Query failed", exc_info=True)
                st.error(str(e))
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {e}"})