"""The Living Sales Intelligence Engine - Streamlit Frontend Application.

Production-grade sales enablement copilot for IOMETE Sovereign Lakehouse:
- Sidebar Configuration & System Health
- Instant Objection Inversion & Call Prep Copilot
- Quick-Select Objection Pills
- Structured Response Display with Verification Badges & Citations
"""

import os
import sys
import json
from typing import Dict, Any, List

# Ensure project root is in PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from backend.engine import process_sales_query, generate_executive_proposal, assess_deal_risks
from backend.retrieval import load_knowledge_chunks, DATA_PATH
from utils.groq_client import GroqLLMClient, DEFAULT_MODEL


# Common sales objections presets for 1-click demo evaluation
PRESET_OBJECTIONS = {
    "Vendor Lock-in": (
        "We are already locked into Snowflake and AWS Redshift; migrating away is too risky and costly."
    ),
    "Security & Data Egress": (
        "Our security team won't allow data leaving our private AWS VPC or external multi-tenant cloud SaaS."
    ),
    "TCO & Pricing vs Snowflake": (
        "Our Snowflake compute bill has exploded. How does IOMETE's pricing compare without sacrificing query speed?"
    ),
    "Open Source vs Managed Platform": (
        "Why wouldn't our data engineering team just deploy open source Apache Spark and Iceberg ourselves on K8s for free?"
    ),
    "Zero-Hallucination Trap Test": (
        "Can IOMETE run on Windows 95 and store customer credit card records on external multi-tenant servers?"
    ),
}


def get_system_health() -> Dict[str, Any]:
    """Retrieves knowledge base health metrics for system status indicator."""
    try:
        chunks = load_knowledge_chunks(DATA_PATH)
        categories = {}
        for c in chunks:
            cat = c.get("category", "General")
            categories[cat] = categories.get(cat, 0) + 1
        return {
            "status": "Active",
            "total_chunks": len(chunks),
            "categories": categories,
            "error": None
        }
    except Exception as e:
        return {
            "status": "Degraded",
            "total_chunks": 0,
            "categories": {},
            "error": str(e)
        }


def render_sidebar():
    """Renders sidebar controls, credentials, and health telemetry."""
    with st.sidebar:
        st.markdown("### Engine Configuration")

        # Session state key persistence
        if "groq_api_key" not in st.session_state:
            st.session_state["groq_api_key"] = os.getenv("GROQ_API_KEY", "")

        api_key_input = st.text_input(
            "Groq API Key",
            type="password",
            value=st.session_state["groq_api_key"],
            help="Required for Llama 3.3 70B inference. Falls back to grounded offline template if omitted."
        )
        if api_key_input:
            st.session_state["groq_api_key"] = api_key_input
            os.environ["GROQ_API_KEY"] = api_key_input

        model_name = st.selectbox(
            "Inference Model",
            options=["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
            index=0,
            help="Phase 1 default: llama-3.3-70b-versatile"
        )
        st.session_state["model_name"] = model_name

        temperature = st.slider(
            "Temperature (Determinism)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
            help="Low temperature (0.1) enforces strict zero-hallucination determinism."
        )
        st.session_state["temperature"] = temperature

        st.markdown("---")
        st.markdown("### System Status")

        health = get_system_health()
        if health["status"] == "Active":
            st.success(f"Knowledge Base: Active ({health['total_chunks']} chunks)")
            with st.expander("Knowledge Base Distribution"):
                for cat, count in health["categories"].items():
                    st.write(f"- **{cat}**: {count} chunks")
        else:
            st.error(f"Knowledge Base: {health['status']}")
            if health["error"]:
                st.caption(health["error"])

        st.info("Zero-Hallucination Guard: **ENFORCED**")
        st.caption("Unsupported claims strictly return 'Unknown / Requires Engineering Verification'.")

        st.markdown("---")
        st.markdown("### Core Grounding Pillars")
        st.markdown(
            "- **Sovereign VPC**: Data plane stays inside customer perimeter\n"
            "- **Apache Spark**: Autoscaling, AQE & columnar reader\n"
            "- **Apache Iceberg**: ACID open table format, zero lock-in\n"
            "- **Kubernetes Native**: EKS, GKE, AKS, OpenShift & bare-metal\n"
            "- **Direct Cloud TCO**: 70-80% cost reduction vs Snowflake"
        )


def render_response_cards(result: Dict[str, Any]):
    """Renders structured objection inversion cards, talk tracks, and evidence sources."""
    status = result.get("status", "Unverified / Unknown")
    response_text = result.get("response", "")
    sources = result.get("sources", [])

    st.markdown("---")
    st.markdown("### Executive Response & Inversion Brief")

    # Status Badge
    if status == "Verified":
        st.markdown(
            """<div style="display: inline-block; padding: 4px 12px; border-radius: 9999px; 
            background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; 
            font-weight: 600; font-size: 0.85rem; margin-bottom: 12px;">
            STATUS: VERIFIED GROUNDED
            </div>""",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """<div style="display: inline-block; padding: 4px 12px; border-radius: 9999px; 
            background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; 
            font-weight: 600; font-size: 0.85rem; margin-bottom: 12px;">
            STATUS: UNVERIFIED / UNKNOWN (FALLBACK APPLIED)
            </div>""",
            unsafe_allow_html=True
        )

    # Main Response Card
    st.markdown(
        f"""<div style="background-color: #111827; border: 1px solid #374151; border-radius: 12px; 
        padding: 18px; margin-bottom: 16px; color: #f3f4f6; font-size: 0.95rem; line-height: 1.6;">
        {response_text}
        </div>""",
        unsafe_allow_html=True
    )

    # One-Click Copy Talk Track Section
    st.markdown("#### 🎙️ Battle-Tested Rep Talk Track")
    # Extract talk track if explicitly segmented, else display full response
    talk_track_snippet = response_text
    if "talk track" in response_text.lower():
        parts = response_text.lower().split("talk track")
        if len(parts) > 1:
            talk_track_snippet = response_text[len(response_text) - len(parts[-1]):].lstrip(":").strip()

    st.code(talk_track_snippet, language="markdown")
    st.caption("💡 Rep Tip: Click the copy icon in the upper-right corner of the code block above to copy the talk track.")

    # Sources & Provenance Drawer
    with st.expander(f"🔍 Ground Truth Citations & Provenance ({len(sources)} sources used)"):
        if sources:
            for s in sources:
                st.markdown(
                    f"- **{s.get('title')}** `[{s.get('category')}]`  \n"
                    f"  *Source Document: `{s.get('source')}` (Chunk ID: `{s.get('id')}`)*"
                )
        else:
            st.warning("No verified sources supported this query; zero-hallucination guard enforced.")


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="IOMETE | The Living Sales Intelligence Engine",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Render Sidebar
    render_sidebar()

    # Header & Hero
    st.markdown(
        """<div style="margin-bottom: 16px;">
            <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 800; color: #00d2ff;">
                IOMETE Living Sales Intelligence Engine
            </h1>
            <p style="color: #9ca3af; font-size: 1rem; margin-top: 4px;">
                Instant, Verified Objection Inversion & Call Prep for the Sovereign Data Lakehouse
            </p>
        </div>""",
        unsafe_allow_html=True
    )

    # Navigation Tabs for Sales Workflows
    tab_copilot, tab_proposal = st.tabs([
        "Objection Inversion Copilot",
        "Executive Proposal & Deal Memo Generator"
    ])

    # -------------------------------------------------------------
    # TAB 1: OBJECTION INVERSION COPILOT
    # -------------------------------------------------------------
    with tab_copilot:
        # Initialize session state for user prompt
        if "current_objection" not in st.session_state:
            st.session_state["current_objection"] = PRESET_OBJECTIONS["Vendor Lock-in"]

        # 1-Click Preset Buttons Row
        st.markdown("##### Quick-Select Common Objections:")
        pill_cols = st.columns(len(PRESET_OBJECTIONS))
        for idx, (label, text) in enumerate(PRESET_OBJECTIONS.items()):
            with pill_cols[idx]:
                if st.button(label, key=f"pill_{idx}", use_container_width=True):
                    st.session_state["current_objection"] = text

        # Main Input Box
        query_input = st.text_area(
            "Enter live prospect objection, pain point, or technical architecture question:",
            value=st.session_state["current_objection"],
            height=100,
            placeholder="e.g. Our security team won't allow data leaving our AWS VPC...",
            help="Type or paste any enterprise buyer objection to invert it into an IOMETE advantage."
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            submit_btn = st.button("Invert Objection", type="primary", use_container_width=True)

        if submit_btn:
            if not query_input or not query_input.strip():
                st.warning("Please provide an objection or technical query.")
            else:
                with st.spinner("Retrieving verified knowledge chunks & synthesizing inversion..."):
                    client = None
                    api_key = st.session_state.get("groq_api_key")
                    if api_key and api_key != "your_groq_api_key_here":
                        client = GroqLLMClient(
                            api_key=api_key,
                            model=st.session_state.get("model_name", DEFAULT_MODEL),
                            default_temperature=st.session_state.get("temperature", 0.1)
                        )

                    result = process_sales_query(query_input, client=client)
                    render_response_cards(result)

    # -------------------------------------------------------------
    # TAB 2: EXECUTIVE PROPOSAL & DEAL MEMO GENERATOR
    # -------------------------------------------------------------
    with tab_proposal:
        st.markdown("### C-Level Executive Briefing & Architecture Memo")
        st.caption("Generate a tailored, enterprise-ready proposal memo compiling objection inversions and deal-risk mitigations.")

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            company_input = st.text_input(
                "Prospect Company Name",
                value="HDFC Bank",
                help="Target enterprise account name."
            )
        with p_col2:
            industry_input = st.text_input(
                "Industry / Vertical",
                value="Fintech / Banking",
                help="Industry sector (enables regulatory and compliance risk mapping)."
            )

        st.markdown("##### Select Key Objections & Topics Discussed on Call:")
        obj_options = [
            "Vendor Lock-in (Snowflake / AWS proprietary formats)",
            "Security & Strict Data Egress / Air-Gapped VPC",
            "TCO & Exploding Compute Bills vs Traditional Warehouses",
            "Open Source DIY Overhead vs Managed Platform",
            "BI Dashboard Concurrency & Tableau/Power BI Connections"
        ]

        selected_objs = []
        chk_cols = st.columns(2)
        for i, opt in enumerate(obj_options):
            with chk_cols[i % 2]:
                if st.checkbox(opt, value=True if i < 3 else False, key=f"memo_chk_{i}"):
                    selected_objs.append(opt)

        if st.button("Generate C-Level Proposal Memo", type="primary", use_container_width=True):
            with st.spinner("Compiling executive proposal & evaluating deal risks..."):
                client = None
                api_key = st.session_state.get("groq_api_key")
                if api_key and api_key != "your_groq_api_key_here":
                    client = GroqLLMClient(
                        api_key=api_key,
                        model=st.session_state.get("model_name", DEFAULT_MODEL),
                        default_temperature=st.session_state.get("temperature", 0.1)
                    )

                proposal_data = generate_executive_proposal(
                    company_name=company_input,
                    industry=industry_input,
                    selected_objections=selected_objs,
                    client=client
                )

                st.success("Executive Proposal Memo Generated Successfully!")

                # Deal Risk Assessment Preview
                st.markdown("#### Deal Risk Assessor (Identified Threats & Mitigations)")
                for risk in proposal_data["risk_assessment"]:
                    severity_color = "#ef4444" if risk["severity"] == "HIGH" else "#f59e0b"
                    st.markdown(
                        f"""<div style="background-color: #111827; border-left: 4px solid {severity_color}; 
                        border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                        <strong style="color: #00d2ff;">{risk['risk_category']}</strong> 
                        <span style="font-size: 0.75rem; background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; margin-left: 8px;">
                        {risk['severity']}
                        </span><br/>
                        <span style="color: #d1d5db; font-size: 0.85rem;"><strong>Threat:</strong> {risk['deal_killer_threat']}</span><br/>
                        <span style="color: #34d399; font-size: 0.85rem;"><strong>IOMETE Mitigation:</strong> {risk['iomete_mitigation']}</span>
                        </div>""",
                        unsafe_allow_html=True
                    )

                # 1-Click Copy Code Block
                st.markdown("#### Copyable C-Level Memo Markdown")
                st.code(proposal_data["proposal_markdown"], language="markdown")

                # Markdown Preview in Expander
                with st.expander("Rendered Executive Document Preview", expanded=True):
                    st.markdown(proposal_data["proposal_markdown"])


if __name__ == "__main__":
    main()
