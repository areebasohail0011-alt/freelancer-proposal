import os

import streamlit as st

# Streamlit secrets ko environment variables mein copy karo
try:
    for k, v in st.secrets.items():
        os.environ.setdefault(k, str(v))
except Exception:
    pass

from crew_app import run_proposal_crew  # noqa: E402

st.set_page_config(page_title="Freelancer Proposal Team", page_icon="💼", layout="wide")
st.title("💼 Freelancer Proposal Team")
st.caption("3 CrewAI agents: Job Analyzer → Pricing Strategist → Proposal Writer (Gemini)")

col1, col2 = st.columns(2)
with col1:
    job_post = st.text_area("Job post (paste here)", height=300)
with col2:
    profile = st.text_area(
        "Your profile (name, skills, experience)",
        height=200,
        placeholder="Ali, Python developer, 3 years, built chatbots and Streamlit apps...",
    )
    hourly_rate = st.number_input("Your hourly rate (USD)", min_value=3.0, value=15.0, step=1.0)

if st.button("Generate Proposal", type="primary"):
    if not job_post.strip() or not profile.strip():
        st.warning("Job post aur profile dono bharo.")
    elif not os.environ.get("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY secrets mein set nahi hai.")
    else:
        try:
            with st.spinner("Agents kaam kar rahe hain..."):
                out = run_proposal_crew(job_post, profile, hourly_rate)
            tab1, tab2, tab3 = st.tabs(["📋 Analysis", "💰 Pricing", "✉️ Proposal"])
            with tab1:
                a = out["analysis"]
                st.write(a.summary)
                st.markdown("**Required skills:** " + ", ".join(a.required_skills))
                st.markdown("**Deliverables:**\n" + "\n".join(f"- {x}" for x in a.deliverables))
                st.markdown("**Client pain points:**\n" + "\n".join(f"- {x}" for x in a.client_pain_points))
                st.markdown("**Red flags:**\n" + ("\n".join(f"- {x}" for x in a.red_flags) or "- None"))
                st.metric("Estimated hours", a.estimated_hours)
            with tab2:
                p = out["pricing"]
                c1, c2, c3 = st.columns(3)
                c1.metric("Price (USD)", f"${p.recommended_price_usd:,.0f}")
                c2.metric("Timeline (days)", p.timeline_days)
                c3.metric("Model", p.pricing_model)
                st.write(p.reasoning)
            with tab3:
                st.write(out["proposal"])
                st.download_button("Download proposal", out["proposal"], file_name="proposal.txt")
        except Exception as e:
            st.error(f"Error: {e}")
