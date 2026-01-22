import streamlit as st
import pandas as pd
import re

# 1. PAGE SETUP
st.set_page_config(page_title="AI Job Search Agent", page_icon="🎯", layout="wide")

# 2. SESSION STATE (To track approvals)
if 'approved_jobs' not in st.session_state:
    st.session_state.approved_jobs = []

# 3. HELPER FUNCTIONS
def extract_keywords(text):
    words = re.findall(r'\w+', text.lower())
    stop_words = {'the', 'and', 'with', 'from', 'this', 'that', 'your', 'will', 'is', 'are', 'for'}
    return [w for w in words if len(w) > 3 and w not in stop_words]

def get_google_search_link(query):
    # Dorking technique: site:linkedin.com/jobs/ + your keywords
    base_url = "https://www.google.com/search?q="
    dork = f"site:linkedin.com/jobs/ \"remote\" {query}"
    return base_url + dork.replace(" ", "+")

# 4. SIDEBAR - THE AUTO-HUNTER
with st.sidebar:
    st.header("🔍 Auto-Hunter Discovery")
    search_query = st.text_input("Job Role / Skills", "Python AI Automation")
    
    if st.button("Search LinkedIn for Jobs"):
        st.success("Targeted Search Prepared!")
        st.link_button("Open Live Job List", get_google_search_link(search_query))
    
    st.divider()
    st.info("Paste a job description on the right once you find one you like!")

# 5. MAIN INTERFACE - THE APPROVAL & ANALYSIS ENGINE
st.title("🎯 AI Job Hunter & ATS Optimizer")
st.markdown("### Step 1: Find & Analyze")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume/Profile")
    # This is where your new "About" section goes
    resume_text = st.text_area("Paste your profile text:", height=200, placeholder="Paste your LinkedIn 'About' section here...")

with col2:
    st.subheader("📋 Job Description")
    job_text = st.text_area("Paste the job you found:", height=200, placeholder="Paste the remote job description here...")

# 6. ANALYSIS LOGIC
if st.button("🚀 Run Analysis & Approve"):
    if resume_text and job_text:
        # Keyword Analysis
        res_keywords = set(extract_keywords(resume_text))
        job_keywords = set(extract_keywords(job_text))
        matched = res_keywords.intersection(job_keywords)
        missing = job_keywords - res_keywords
        score = int((len(matched) / len(job_keywords)) * 100) if job_keywords else 0

        # UI Results
        st.divider()
        st.subheader("📊 Agent Verdict")
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("ATS Match Score", f"{score}%")
        
        if score > 70:
            st.success("✅ **Approved by Agent:** This is a strong match for your portfolio.")
        else:
            st.warning("⚠️ **Low Match:** Consider adding the missing keywords listed below.")

        # Show missing keywords
        st.write("**Add these to your profile to rank higher:**")
        st.write(", ".join(list(missing)[:10]))

        # 7. GENERATE THE "POST-APPROVAL" MESSAGE
        st.divider()
        st.subheader("📝 Step 2: Auto-Draft Approved Outreach")
        
        # This draft uses your actual projects as leverage
        draft_message = f"""
Hi [Hiring Manager Name], 

I noticed your posting for a {search_query} role. I've developed and deployed a suite of autonomous AI agents (Lead Gen, Logistics, and ATS analysis) using Python and CI/CD. 

My profile matches {score}% of your requirements, specifically in {", ".join(list(matched)[:3])}. I'd love to show you my live portfolio.

Best,
[Your Name]
        """
        st.text_area("Approved Outreach (Copy to LinkedIn):", draft_message, height=200)
        st.info("Agent Tip: Open the job link, click 'Apply' or 'Message', and paste the text above.")

    else:
        st.error("Please provide both your profile and the job description to proceed.")
